import sys
import os
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "database"
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    title: str

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    content: str
    role: str
    image: str = ""
    timestamp: datetime

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    session_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None