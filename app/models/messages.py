import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    """
    creator - автор сообщения
    companion - собеседник, если речь идет об ответе на сообщение конкретного участника группового чата
    citation - часть оригинального сообщения, использованного как цитата при ответе
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    destination_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    citation = Column(String, nullable=True, default=None)
    body = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())

    creator = relationship("User", foreign_keys=[creator_id])
    companion = relationship("User", foreign_keys=[destination_id])
