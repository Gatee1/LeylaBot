from datetime import datetime, date
from sqlalchemy import BigInteger, String, Integer, Date, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from bot.config import config

engine = create_async_engine(config.DATABASE_URL.get_secret_value(), echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    character: Mapped[str] = mapped_column(String(32), default="Girlfriend")  # Girlfriend, Coach, Cat
    streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    progress: Mapped[list["DailyProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ideas: Mapped[list["Idea"]] = relationship(back_populates="user", cascade="all, delete-orphan")

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
    text: Mapped[str] = mapped_column(String)
    media_url: Mapped[str | None] = mapped_column(String)
    media_type: Mapped[str | None] = mapped_column(String)  # photo, video, gif
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, filming, done
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    user: Mapped["User"] = relationship(back_populates="ideas")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
