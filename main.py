import asyncio
import logging
import sys
import os
import certifi
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncioScheduler

from bot.config import config
from bot.database.models import init_db
from bot.handlers import start, tracking, reminders, profile, ideas

# SSL fix for macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

async def main():
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    # Initialize DB
    await init_db()
    
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Initialize Scheduler
    scheduler = AsyncioScheduler(timezone=config.DEFAULT_TIMEZONE)
    
    from bot.utils.scheduler_tasks import send_reminder, send_weekly_report
    scheduler.add_job(send_reminder, "cron", hour=11, minute=0, args=[bot, "shooting"])
    scheduler.add_job(send_reminder, "cron", hour=18, minute=0, args=[bot, "upload"])
    scheduler.add_job(send_weekly_report, "cron", day_of_week="mon", hour=10, minute=0, args=[bot])
    
    scheduler.start()
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(tracking.router)
    dp.include_router(reminders.router)
    dp.include_router(profile.router)
    dp.include_router(ideas.router)
    
    # Robust polling loop
    while True:
        try:
            logging.info("Starting bot polling...")
            await dp.start_polling(bot, scheduler=scheduler)
        except Exception as e:
            logging.error(f"Polling error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
