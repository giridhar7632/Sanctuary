from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class EmotionalState(str, Enum):
    BURNOUT = "burnout"
    CREATIVE_BLOCK = "creative_block"
    ANXIETY = "anxiety"
    OVERWHELMED = "overwhelmed"
    DISCONNECTED = "disconnected"
    RESTLESS = "restless"

class MediaType(str, Enum):
    FILM = "film/movie"
    MUSIC_ARTIST = "music/artist"
    MUSIC_ALBUM = "music/album"
    BOOK = "book/book"
    TV_SHOW = "tv/show"
    PODCAST = "podcast"

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

class RitualRecord(BaseModel):
    user_id: str
    emotional_need: str
    comfort_media: List[str]
    ritual_content: str
    recommendations: Dict[str, Any]
    estimated_duration: str = "30min"
    rating: Optional[int] = None
    created_at: str

class EmotionRequest(BaseModel):
    text: str

class RitualRequest(BaseModel):
    text: str
    comfort_media: List[str]
    preferences: Optional[Dict[str, Any]]

class RitualResponse(BaseModel):
    success: bool
    ritual: RitualRecord

class FeedbackRequest(BaseModel):
    ritual_id: str
    rating: int
    comments: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_rituals: int
    average_rating: float
    popular_emotions: List[Dict[str, Any]]
    user_retention: float