import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import logger
from app.bot.handlers import base, goals, studio
from app.bot.middlewares import DbSessionMiddleware
from app.core.scheduler import setup_scheduler


async def start_bot():
    # Initialize bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    # Storage
    redis = Redis.from_url(settings.REDIS_URL)
    storage = RedisStorage(redis)
    
    dp = Dispatcher(storage=storage)

    # Middlewares
    dp.update.middleware(DbSessionMiddleware())

    # Handlers
    dp.include_router(base.router)
    dp.include_router(goals.router)
    dp.include_router(studio.router)

    # Scheduler
    scheduler = setup_scheduler(bot)

    logger.info("Bot starting...")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Bot polling error", error=str(e))
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot())
