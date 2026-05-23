import asyncio
import logging
import sys
import os
import certifi

# Fix imports for BotHost/Production
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

try:
    from apscheduler.schedulers.asyncio import AsyncioScheduler
except ImportError:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler as AsyncioScheduler

from bot.config import config
from bot.database.models import init_db
from bot.handlers import start, tracking, reminders, profile, ideas, hashtags, reflection

# SSL fix for macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

async def main():
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Initialize Scheduler
    scheduler = AsyncioScheduler(timezone=config.DEFAULT_TIMEZONE)
    
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
    
    # Start API server in background
    import uvicorn
    from bot.api import app as api_app
    from threading import Thread
    
    def run_api():
        uvicorn.run(api_app, host="0.0.0.0", port=3000)
    
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Robust polling loop
    while True:
        try:
            logging.info("Connecting to database...")
            await init_db()
            
            logging.info("Starting bot polling...")
            await dp.start_polling(bot, scheduler=scheduler)
        except Exception as e:
            logging.error(f"Critical error: {e}")
            logging.info("Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
