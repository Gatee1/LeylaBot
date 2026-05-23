import random
from aiogram import Bot
from bot.database.models import SessionLocal, User, DailyProgress
from bot.database.requests import get_or_create_daily_progress
from bot.utils.reminders_data import CHARACTERS
from sqlalchemy import select
from datetime import date

async def send_reminder(bot: Bot, reminder_type: str):
    # Only Mon-Fri (0-4)
    if date.today().weekday() > 4:
        return

    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            progress = await get_or_create_daily_progress(user.id)
            
            # Check if already done
            if reminder_type == "shooting" and progress.shots_count >= 3:
                continue
            if reminder_type == "upload" and all([progress.uploaded_yt, progress.uploaded_ig, progress.uploaded_tt, progress.uploaded_vk]):
                continue
                
            char_data = CHARACTERS.get(user.character, CHARACTERS["Girlfriend"])
            reminder = random.choice(char_data[reminder_type])
            
            try:
                if reminder["type"] == "animation":
                    await bot.send_animation(
                        chat_id=user.id,
                        animation=reminder["media"],
                        caption=reminder["text"]
                    )
                elif reminder["type"] == "photo":
                    await bot.send_photo(
                        chat_id=user.id,
                        photo=reminder["media"],
                        caption=reminder["text"]
                    )
                else:
                    await bot.send_message(chat_id=user.id, text=reminder["text"])
            except Exception as e:
                print(f"Failed to send reminder to {user.id}: {e}")

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
