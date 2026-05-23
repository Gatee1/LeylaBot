from datetime import datetime, date
from sqlalchemy import BigInteger, String, Integer, Date, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from bot.config import config

# Using SQLite for local storage on BotHost
engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    morning_time: Mapped[str] = mapped_column(String(5), default="10:00")
    afternoon_time: Mapped[str] = mapped_column(String(5), default="14:00")
    evening_time: Mapped[str] = mapped_column(String(5), default="19:00")
    streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    progress: Mapped[list["DailyProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ideas: Mapped[list["Idea"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hashtags: Mapped[list["Hashtag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reflections: Mapped[list["Reflection"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class DailyProgress(Base):
    __tablename__ = "daily_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    
    shots_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Platform upload status
    uploaded_yt: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_ig: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_tt: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_vk: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user: Mapped["User"] = relationship(back_populates="progress")

class Idea(Base):
    __tablename__ = "ideas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str | None] = mapped_column(String, nullable=True)
    media_id: Mapped[str | None] = mapped_column(String, nullable=True) # Telegram file_id
    media_type: Mapped[str | None] = mapped_column(String(32), nullable=True) # photo, video, animation
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, filming, done
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    user: Mapped["User"] = relationship(back_populates="ideas")

class Hashtag(Base):
    __tablename__ = "hashtags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(String)
    
    user: Mapped["User"] = relationship(back_populates="hashtags")

class Reflection(Base):
    __tablename__ = "reflections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    answer: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    user: Mapped["User"] = relationship(back_populates="reflections")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Manual migration for existing SQLite database
    async with engine.connect() as conn:
        # Add columns to ideas table if they don't exist
        for column, type_ in [("media_id", "TEXT"), ("media_type", "VARCHAR(32)")]:
            try:
                await conn.execute(f"ALTER TABLE ideas ADD COLUMN {column} {type_}")
                await conn.commit()
            except Exception:
                pass # Column already exists
