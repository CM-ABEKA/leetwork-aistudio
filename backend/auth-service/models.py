"""
Data models for authentication service
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """
    Base user model
    """
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Model for creating a new user
    """
    password: str


class UserInDB(UserBase):
    """
    User model as stored in database
    """
    id: UUID
    password_hash: str
    role: str = "user"  # user, admin, enterprise
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    User model for API responses (without sensitive data)
    """
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """
    Data extracted from JWT token
    """
    email: Optional[str] = None
    role: Optional[str] = None
