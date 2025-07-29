from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserSignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    created_at: datetime

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str

class User(BaseModel):
    id: str
    name: str
    email: str
    password_hash: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime