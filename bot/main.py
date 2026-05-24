import asyncio
import logging
import sys
import os
import threading
import uvicorn
from fastapi import FastAPI

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ====================== FASTAPI ======================
from bot.api import app as fastapi_app

# ====================== AIogram ======================
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import config
from bot.database.models import init_db
from bot.handlers import start, tracking, reminders, profile, ideas, hashtags, reflection
from bot.utils.scheduler_tasks import check_and_send_reminders, send_weekly_report

# ====================== CONFIG ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

# ====================== RUN API IN BACKGROUND ======================
def run_api():
    print("🚀 Starting FastAPI server on http://0.0.0.0:7328")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=7328,
        log_level="info",
        reload=False
    )

# ====================== MAIN ======================
async def main():
    await init_db()
    
    # Запускаем FastAPI в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("✅ FastAPI started in background thread")
    
    # Инициализация бота
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Scheduler
    scheduler = AsyncIOScheduler(timezone=config.DEFAULT_TIMEZONE)
    scheduler.add_job(check_and_send_reminders, "interval", minutes=1, args=[bot])
    scheduler.add_job(send_weekly_report, "cron", day_of_week="mon", hour=10, minute=0, args=[bot])
    scheduler.start()
    
    # Роутеры
    dp.include_router(start.router)
    dp.include_router(tracking.router)
    dp.include_router(reminders.router)
    dp.include_router(profile.router)
    dp.include_router(ideas.router)
    dp.include_router(hashtags.router)
    dp.include_router(reflection.router)
    
    print("✅ Bot started successfully. Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
    except Exception as e:
        print(f"Critical error: {e}")