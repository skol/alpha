from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class MessageCreate(BaseModel):
    creator_id: int
    destination_id: Union[int | None] = None
    citation: Union[str | None] = None
    body: str


class Message(BaseModel):
    id: int
    citation: Union[str | None] = None
    body: str
    created_at: datetime

    creator: 'User'
    companion: Optional['User'] = None

    class Config:
        orm_mode = True


class ChatCreate(BaseModel):
    creator_id: int
    name: str
    is_group_chat: bool = False


class Chat(BaseModel):
    id: int
    creator_id: int
    name: str
    is_group_chat: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


class Chat2(BaseModel):
    id: int
    creator_id: int
    name: str
    is_group_chat: bool = False
    created_at: datetime

    creator: 'User'
    members: list['User'] = []
    messages: list[Message] = []

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    phone: str
    name: str
    password: str
    avatar: Union[str | None] = None


class User(BaseModel):
    """
    Модель пользователя
    """
    id: int
    phone: str
    name: str
    is_active: bool
    avatar: Union[str | None] = None

    class Config:
        orm_mode = True


class User2(BaseModel):
    """
    Модель пользователя
    """
    id: int
    phone: str
    name: str
    is_active: bool
    active_chat: Union[Chat | None] = None
    chats: list[Chat] = []
    avatar: Union[str | None] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    phone: str | None = None


Chat.update_forward_refs(User=User)
Chat2.update_forward_refs(User=User)
Message.update_forward_refs(User=User)
