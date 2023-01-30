from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app import app, get_db
from crud.user import get_current_active_user
from crud.message import create_message as crud_create_message
from models import User
from schemas import Message as MessageSchema, MessageCreate


@app.get("/messages/", response_model=list[MessageSchema], summary="Список сообщений текущего чата", tags=['Message'])
def get_chat_messages(user: User = Depends(get_current_active_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Authorize first")
    if not user.active_chat_id:
        raise HTTPException(status_code=400, detail="Select chat first")
    return user.active_chat.messages


@app.post("/messages/", response_model=MessageSchema, summary="Новое сообщение", tags=['Message'])
def create_message(message: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    if not user:
        raise HTTPException(status_code=403, detail="Authorize first")
    if not user.active_chat_id:
        raise HTTPException(status_code=400, detail="Select chat first")
    return crud_create_message(db, user.active_chat_id, message)
