from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)

    active_chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)
    active_chat = relationship("Chat", foreign_keys=[active_chat_id])

    avatar = Column(String(), nullable=True, default=None)
    ava050 = Column(String(), nullable=True, default=None)
    ava100 = Column(String(), nullable=True, default=None)
    ava400 = Column(String(), nullable=True, default=None)
