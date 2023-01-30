import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, PrimaryKeyConstraint, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

chat_messages_table = Table(
    "chat_messages",
    Base.metadata,
    Column("chat_id", ForeignKey("chats.id")),
    Column("message_id", ForeignKey("messages.id")),
    PrimaryKeyConstraint("chat_id", "message_id", name="chat_messages_pk"),
)


chat_members_table = Table(
    "chat_members",
    Base.metadata,
    Column("chat_id", ForeignKey("chats.id")),
    Column("user_id", ForeignKey("users.id")),
    Column("created_at", DateTime(), default=datetime.datetime.now()),
    PrimaryKeyConstraint("chat_id", "user_id", name="chat_members_pk"),
)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_group_chat = Column(Boolean, default=False, nullable=False)

    creator = relationship("User", foreign_keys=[creator_id])
    members = relationship("User", secondary=chat_members_table, backref="chats")
    messages = relationship("Message", secondary=chat_messages_table)
