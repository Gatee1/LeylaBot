import random
from aiogram import Bot
from bot.database.models import SessionLocal, User, DailyProgress
from bot.database.requests import get_or_create_daily_progress, get_user_stats
from sqlalchemy import select
from datetime import date, datetime

REMINDERS = {
    "shooting": [
        {
            "text": "✨ Пора творить шедевры! Не забудь сегодня записать свои ролики. Ты будешь сиять! ❤️",
            "media": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif",
            "type": "animation"
        }
    ],
    "upload": [
        {
            "text": "🚀 Время делиться контентом! Твои зрители уже ждут новые видео. Пора выкладывать! 🥰",
            "media": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l0Exd9XJm0H9H8LpG/giphy.gif",
            "type": "animation"
        }
    ]
}

async def check_and_send_reminders(bot: Bot):
    # Only Mon-Fri (0-4)
    if date.today().weekday() > 4:
        return

    now_time = datetime.now().strftime("%H:%M")

    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            progress = await get_or_create_daily_progress(user.id)
            
            # Check shooting reminder
            if user.shooting_time == now_time:
                if progress.shots_count < 3:
                    await send_user_reminder(bot, user.id, "shooting")
            
            # Check upload reminder
            if user.upload_time == now_time:
                if not all([progress.uploaded_yt, progress.uploaded_ig, progress.uploaded_tt, progress.uploaded_vk]):
                    await send_user_reminder(bot, user.id, "upload")

async def send_user_reminder(bot: Bot, user_id: int, reminder_type: str):
    reminder = random.choice(REMINDERS[reminder_type])
    try:
        if reminder["type"] == "animation":
            await bot.send_animation(
                chat_id=user_id,
                animation=reminder["media"],
                caption=reminder["text"]
            )
        else:
            await bot.send_message(chat_id=user_id, text=reminder["text"])
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")

async def send_weekly_report(bot: Bot):
    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            stats = await get_user_stats(user.id)
            last_week = stats[:7]
            total_week_shots = sum(s.shots_count for s in last_week)
            
            report = (
                "📈 <b>Твой еженедельный отчет:</b>\n\n"
                f"🎬 Снято за неделю: {total_week_shots} роликов\n"
                f"🔥 Текущий стрик: {user.streak} дней\n"
                f"🏆 Максимальный стрик: {user.max_streak} дней\n\n"
                "Ты супер! Давай на следующей неделе еще больше огня! 🚀"
            )
            
            try:
                await bot.send_message(user.id, report)
            except Exception as e:
                print(f"Failed to send report to {user.id}: {e}")
