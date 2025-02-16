from datetime import datetime
import random
from typing import Optional
from pydantic import BaseModel, EmailStr

from .database import Base

# Pydantic Models
# Used for Request & Response validations

BASE62_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def generate_base62_id(length=6):
    return ''.join(random.choices(BASE62_ALPHABET, k=length))

class PostBase(BaseModel):
    id: str = None
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    createdAt: Optional[datetime] = None

# Generate New Unique ID
class PostCreate(PostBase):
    id: str = generate_base62_id()
    title: str
    content: str
    published: bool = True
    # createdAt auto created by database

class Post(PostBase):
    id: str
    title: str
    content: str
    createdAt: datetime
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    createdAt: Optional[datetime] = None

class UserGet(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
