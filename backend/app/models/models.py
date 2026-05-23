from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer, String, Text, DateTime, JSON, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import uuid
import enum

class IdeaStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    PUBLISHED = "published"

class Platform(str, enum.Enum):
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    VK = "vk"

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    manager_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    social_accounts: Mapped[List["SocialAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ideas: Mapped[List["Idea"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    daily_goals: Mapped[List["DailyGoal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    daily_stats: Mapped[List["DailyStat"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    streaks: Mapped[List["Streak"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), index=True)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform), nullable=False)
    external_user_id: Mapped[str] = mapped_column(String, nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="social_accounts")

class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform), nullable=False)
    status: Mapped[IdeaStatus] = mapped_column(SQLEnum(IdeaStatus), default=IdeaStatus.DRAFT)
    
    user: Mapped["User"] = relationship(back_populates="ideas")

class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), index=True)
    shoot_goal: Mapped[int] = mapped_column(Integer, default=3)
    shoot_current: Mapped[int] = mapped_column(Integer, default=0)
    publish_goal: Mapped[int] = mapped_column(Integer, default=3)
    publish_current: Mapped[int] = mapped_column(Integer, default=0)
    
    user: Mapped["User"] = relationship(back_populates="daily_goals")

class DailyStat(Base):
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    reach: Mapped[int] = mapped_column(BigInteger, default=0)
    views: Mapped[int] = mapped_column(BigInteger, default=0)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform), index=True)
    
    user: Mapped["User"] = relationship(back_populates="daily_stats")

class Streak(Base):
    __tablename__ = "streaks"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), unique=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="streaks")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", on_delete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
