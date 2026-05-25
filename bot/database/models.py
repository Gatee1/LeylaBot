from datetime import datetime, date
from sqlalchemy import BigInteger, String, Integer, Date, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint, select, delete, func
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
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    morning_time: Mapped[str] = mapped_column(String(5), default="10:00")
    afternoon_time: Mapped[str] = mapped_column(String(5), default="14:00")
    evening_time: Mapped[str] = mapped_column(String(5), default="19:00")
    
    # New fields for Mini App
    platforms: Mapped[list[str]] = mapped_column(JSON, default=list) # yt, ig, tt, vk
    daily_goal: Mapped[int] = mapped_column(Integer, default=3)
    
    # Notifications
    notif_daily_reminder: Mapped[bool] = mapped_column(Boolean, default=True)
    notif_streak_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    notif_ideas_digest: Mapped[bool] = mapped_column(Boolean, default=True)
    
    streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    progress: Mapped[list["DailyProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ideas: Mapped[list["Idea"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    videos: Mapped[list["Video"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hashtags: Mapped[list["Hashtag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reflections: Mapped[list["Reflection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class DailyProgress(Base):
    __tablename__ = "daily_progress"
    __table_args__ = (UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    
    shots_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    posts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    
    # Platform upload status
    uploaded_yt: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_ig: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_tt: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_vk: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user: Mapped["User"] = relationship(back_populates="progress")

class Account(Base):
    __tablename__ = "accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(32)) # youtube, instagram, tiktok
    handle: Mapped[str | None] = mapped_column(String(128))
    display_name: Mapped[str | None] = mapped_column(String(128))
    avatar_url: Mapped[str | None] = mapped_column(String)
    followers: Mapped[int] = mapped_column(Integer, default=0)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String(32), default="active") # active, expired
    
    # Tokens (in a real app, these should be encrypted)
    access_token: Mapped[str | None] = mapped_column(String)
    refresh_token: Mapped[str | None] = mapped_column(String)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    user: Mapped["User"] = relationship(back_populates="accounts")

class Idea(Base):
    __tablename__ = "ideas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True)
    media_id: Mapped[str | None] = mapped_column(String, nullable=True) # Telegram file_id
    media_type: Mapped[str | None] = mapped_column(String(32), nullable=True) # photo, video, animation
    status: Mapped[str] = mapped_column(String(32), default="backlog")  # backlog, scheduled, recorded, posted
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    user: Mapped["User"] = relationship(back_populates="ideas")

class Video(Base):
    __tablename__ = "videos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="recorded")  # recorded, edited, posted
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True) # yt, ig, tt, vk
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="videos")

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
        
    # Manual migrations and cleanup
    async with engine.connect() as conn:
        # 1. Add columns to users table
        for column, type_ in [
            ("avatar_url", "TEXT"),
            ("platforms", "JSON"),
            ("daily_goal", "INTEGER DEFAULT 3"),
            ("notif_daily_reminder", "BOOLEAN DEFAULT 1"),
            ("notif_streak_alerts", "BOOLEAN DEFAULT 1"),
            ("notif_ideas_digest", "BOOLEAN DEFAULT 1"),
            ("onboarded_at", "DATETIME")
        ]:
            try:
                await conn.execute(f"ALTER TABLE users ADD COLUMN {column} {type_}")
                await conn.commit()
            except Exception:
                pass

        # 2. Add columns to ideas table
        for column, type_ in [
            ("title", "VARCHAR(255)"),
            ("description", "TEXT"),
            ("platform", "VARCHAR(32)"),
            ("media_id", "TEXT"),
            ("media_type", "VARCHAR(32)"),
            ("scheduled_for", "DATETIME")
        ]:
            try:
                await conn.execute(f"ALTER TABLE ideas ADD COLUMN {column} {type_}")
                await conn.commit()
            except Exception:
                pass

        # 3. Add columns to daily_progress
        try:
            await conn.execute("ALTER TABLE daily_progress ADD COLUMN posts_count INTEGER DEFAULT 0")
            await conn.commit()
        except Exception:
            pass
        
        # 4. Data cleanup: Ensure shots_count and posts_count are not NULL
        try:
            await conn.execute("UPDATE daily_progress SET shots_count = 0 WHERE shots_count IS NULL")
            await conn.execute("UPDATE daily_progress SET posts_count = 0 WHERE posts_count IS NULL")
            await conn.commit()
        except Exception:
            pass

        # 5. Create missing tables
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id BIGINT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    status VARCHAR(32) NOT NULL DEFAULT 'recorded',
                    platform VARCHAR(32),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    posted_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            await conn.commit()
        except Exception:
            pass

    # 6. Duplicates cleanup (using SessionLocal)
    async with SessionLocal() as session:
        result = await session.execute(
            select(DailyProgress.user_id, DailyProgress.date)
            .group_by(DailyProgress.user_id, DailyProgress.date)
            .having(func.count(DailyProgress.id) > 1)
        )
        duplicates = result.all()
        
        if duplicates:
            print(f"🔍 Found {len(duplicates)} pairs with duplicates. Cleaning up...")
            for user_id, target_date in duplicates:
                result = await session.execute(
                    select(DailyProgress.id)
                    .where(DailyProgress.user_id == user_id, DailyProgress.date == target_date)
                    .order_by(DailyProgress.id.desc())
                )
                ids = result.scalars().all()
                await session.execute(
                    delete(DailyProgress).where(DailyProgress.id.in_(ids[1:]))
                )
            await session.commit()
            print("✅ Duplicates cleanup complete.")
