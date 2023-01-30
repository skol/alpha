from typing import Optional

from sqlalchemy.orm import Session

from app.models import Chat, User
from app.schemas import ChatCreate


def create_chat(db: Session, user: User, chat: ChatCreate) -> Optional[Chat]:
    db_chat = Chat(name=chat.name, is_group_chat=chat.is_group_chat, creator_id=user.id)
    db_chat.members.append(user)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chat(db: Session, chat_id: int) -> Optional[Chat]:
    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_chat_by_name(db: Session, chat_name: str) -> Optional[Chat]:
    return db.query(Chat).filter(Chat.name == chat_name).first()


def update_chat(db: Session, chat_id: int, name: str) -> Optional[Chat]:
    instance: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if instance.is_group_chat:
        instance.name = name
        db.commit()
        db.refresh(instance)
    return instance


def set_chat_as_group(db: Session, chat_id: int) -> Chat:
    instance: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not instance.is_group_chat:
        instance.is_group_chat = True
        db.commit()
        db.refresh(instance)
    return instance


def add_group_member(db: Session, chat_id: int, initiator_id: int, new_member_id: int) -> Optional[Chat]:
    """
    Добавляем участника в группу
    :param db:
    :param chat_id:
    :param initiator_id:
    :param new_member_id:
    :return: None если уже там или обновленную запись чата
    """
    instance: Chat = db.query(Chat).filter(Chat.id == chat_id).first()
    members = set()
    for member in instance.members:
        members.add(member.id)
    # members = list(members)
    if initiator_id in members and new_member_id not in members:
        user = db.query(User).filter(User.id == new_member_id).first()
        instance.members.append(user)
        instance.is_group_chat = instance.is_group_chat or (len(members) + 1 > 2)
        db.commit()
        db.refresh(instance)
        return instance
    return None
