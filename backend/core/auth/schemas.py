"""
Pydantic models for authentication and user management.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserRole:
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class User(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
