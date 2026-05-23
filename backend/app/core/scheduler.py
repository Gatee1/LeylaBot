import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from aiogram import Bot
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import logger
from app.db.session import async_session_factory
from app.models.models import User, DailyGoal


async def send_morning_reminder(bot: Bot):
    """Sends morning reminders to all users."""
    async with async_session_factory() as db:
        query = select(User).where(User.notifications_enabled == True)
        result = await db.execute(query)
        users = result.scalars().all()
        
        for user in users:
            try:
                # In a real app, check user's timezone here
                await bot.send_message(
                    user.telegram_id,
                    f"Доброе утро, {user.first_name}! ☀️\n\n"
                    "Готова покорять новые вершины сегодня?\n"
                    "Твоя цель на сегодня: 3 новых ролика. Давай сделаем это! 💪"
                )
            except Exception as e:
                logger.error("Failed to send morning reminder", user_id=user.telegram_id, error=str(e))


async def send_evening_reminder(bot: Bot):
    """Sends evening reminders to check progress."""
    async with async_session_factory() as db:
        query = select(User).where(User.notifications_enabled == True)
        result = await db.execute(query)
        users = result.scalars().all()
        
        for user in users:
            try:
                # Get today's goals
                # repo = GoalRepository(db) # or manual query
                await bot.send_message(
                    user.telegram_id,
                    "Вечерний чек-ин! 🌙\n\n"
                    "Как успехи с контентом сегодня?\n"
                    "Не забудь отметить записанные и выложенные ролики в Studio!"
                )
            except Exception as e:
                logger.error("Failed to send evening reminder", user_id=user.telegram_id, error=str(e))


def setup_scheduler(bot: Bot):
    jobstores = {
        'default': RedisJobStore(url=settings.REDIS_URL)
    }
    
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    
    # Morning reminder at 10:00
    scheduler.add_job(
        send_morning_reminder,
        'cron',
        hour=10,
        minute=0,
        args=[bot],
        id='morning_reminder',
        replace_existing=True
    )
    
    # Evening reminder at 20:00
    scheduler.add_job(
        send_evening_reminder,
        'cron',
        hour=20,
        minute=0,
        args=[bot],
        id='evening_reminder',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
