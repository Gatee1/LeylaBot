import asyncio
import logging
import sys
import os
import certifi

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import config
from bot.database.models import init_db
from bot.handlers import start, tracking, reminders, profile, ideas, hashtags, reflection
from bot.api import app as api_app   # ← импортируем FastAPI app

# SSL fix
os.environ['SSL_CERT_FILE'] = certifi.where()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    await init_db()
    
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    scheduler = AsyncIOScheduler(timezone=config.DEFAULT_TIMEZONE)
    
    from bot.utils.scheduler_tasks import check_and_send_reminders, send_weekly_report
    scheduler.add_job(check_and_send_reminders, "interval", minutes=1, args=[bot])
    scheduler.add_job(send_weekly_report, "cron", day_of_week="mon", hour=10, minute=0, args=[bot])
    scheduler.start()
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(tracking.router)
    dp.include_router(reminders.router)
    dp.include_router(profile.router)
    dp.include_router(ideas.router)
    dp.include_router(hashtags.router)
    dp.include_router(reflection.router)
    
    logging.info("✅ Bot and API prepared. Starting polling...")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())