from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    timezone: str = "UTC"
    notifications_enabled: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    manager_username: Optional[str] = None


class User(UserBase):
    is_new: bool = False
    streak_days: int = 0
    total_reels: int = 0
    manager_username: Optional[str] = None

    class Config:
        from_attributes = True


class OnboardingRequest(BaseModel):
    first_name: str
    timezone: str


class TelegramAuthRequest(BaseModel):
    init_data: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Achievement(BaseModel):
    key: str
    label: str
    earned_at: date
    earned_at_label: str
    icon: str


class ProfileResponse(BaseModel):
    me: User
    achievements: List[Achievement]
