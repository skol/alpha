from typing import Optional

from sqlalchemy.orm import Session

from app.crud.chat import get_chat
from app.models import Message, Chat
from app.schemas import MessageCreate


def create_message(db: Session, chat_id: int, msg: MessageCreate) -> Optional[Message]:
    chat = get_chat(db, chat_id)
    if chat is None or not(msg.creator_id in [x.id for x in chat.members]):
        return None
    db_message = Message(citation=msg.citation, body=msg.body, creator_id=msg.creator_id, destination_id=msg.destination_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    chat.messages.append(db_message)
    db.commit()
    return db_message


def get_messages(db: Session, chat_id: int):
    """
    Получить сообщения для заданного чата.
    :param db:
    :param chat_id:
    :return:
    """
    return db.query(Message).filter(Chat.messages.any(Chat.id == chat_id)).all()
