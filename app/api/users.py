import re

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app import app, get_db
from app.crud.user import get_user_by_phone, create_user as crud_create_user, update_user as crud_update_user, \
    get_current_active_user, set_active_chat
from crud.chat import get_chat
from models import User
from schemas import UserCreate, User as UserSchema, User2 as User2Schema


@app.post("/users/", response_model=UserSchema, summary="Регистрируем пользователя", tags=['User'])
def create_profile(user: UserCreate, db: Session = Depends(get_db)):
    user.phone = re.sub("[^0-9]", "", user.phone)
    db_user = get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud_create_user(db=db, user=user)


@app.put("/users", response_model=UserSchema, summary="Редактируем свой профиль", tags=['User'])
def update_profile(user: UserCreate, db: Session = Depends(get_db), old_user: User = Depends(get_current_active_user)):
    if not old_user:
        raise HTTPException(status_code=401, detail="You are not logged in")
    if user.phone != old_user.phone:
        db_user: User = get_user_by_phone(db, phone=user.phone)
        if db_user:
            raise HTTPException(status_code=400, detail="User with this phone already exist")
    user.phone = re.sub("[^0-9]", "", user.phone)
    return crud_update_user(db, old_user.id, user.phone, user.name, user.password)


@app.get("/users/set_active_chat/{chat_id}", response_model=User2Schema, summary="Выбрать чат", tags=['User'])
def select_chat(chat_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
    chat = get_chat(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return set_active_chat(db, user.id, chat_id)
