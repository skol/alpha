from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app import app, get_db
from crud.chat import get_chat_by_name, create_chat as crud_create_chat, add_group_member
from crud.user import get_current_active_user, get_user
from models import User
from schemas import Chat2 as Chat2Schema, ChatCreate


@app.get("/chats/", response_model=list[Chat2Schema], summary="Список чатов текущего пользователя", tags=['Chat'])
def get_user_chats(user: User = Depends(get_current_active_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Authorize first")
    return user.chats


@app.post("/chats/", response_model=Chat2Schema, summary="Создаем чат", tags=['Chat'])
def create_chat(chat: ChatCreate, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    db_chat = get_chat_by_name(db, chat.name)
    if db_chat:
        raise HTTPException(status_code=400, detail="Chat already registered")
    return crud_create_chat(db, user, chat)


@app.get("/chats/add_user/{user_id}", response_model=Chat2Schema, summary="Добавить участника", tags=['Chat'])
def add_user_to_chat(user_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=403, detail="Authorize first")
    if not user.active_chat_id:
        raise HTTPException(status_code=400, detail="Select chat first")
    new_member = get_user(db, user_id)
    if not new_member:
        raise HTTPException(status_code=404, detail="User not found")
    chat = add_group_member(db, user.active_chat_id, user.id, user_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Already in group")
    return chat
