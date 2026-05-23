import random
from aiogram import Bot
from bot.database.models import SessionLocal, User, DailyProgress
from bot.database.requests import get_or_create_daily_progress, get_user_stats
from sqlalchemy import select
from datetime import date, datetime

async def check_and_send_reminders(bot: Bot):
    # Только с понедельника по пятницу
    if date.today().weekday() > 4:
        return

    now_time = datetime.now().strftime("%H:%M")

    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Проверяем все три времени напоминаний
            if now_time in [user.morning_time, user.afternoon_time, user.evening_time]:
                progress = await get_or_create_daily_progress(user.id)
                await send_unified_reminder(bot, user, progress)

async def send_unified_reminder(bot: Bot, user: User, progress: DailyProgress):
    shots = progress.shots_count
    goal_shots = 3
    
    platforms = [progress.uploaded_yt, progress.uploaded_ig, progress.uploaded_tt, progress.uploaded_vk]
    uploaded = sum(platforms)
    goal_uploaded = 4
    
    # Тексты для разных ситуаций
    if shots >= goal_shots and uploaded >= goal_uploaded:
        texts = [
            f"🌟 Сегодня ты выложила {uploaded}/{goal_uploaded} роликов и записала {shots}/{goal_shots} роликов. Ты молодец!",
            f"💎 План выполнен на 100%! Записано: {shots}/{goal_shots}, Выложено: {uploaded}/{goal_uploaded}. Ты большая умница! ✨",
            f"🌈 Идеальный день! {shots} снято, {uploaded} выложено. Ты просто супер! ❤️"
        ]
    else:
        left_shots = max(0, goal_shots - shots)
        left_uploaded = max(0, goal_uploaded - uploaded)
        
        status_line = f"Сегодня ты выложила {uploaded}/{goal_uploaded} роликов и записала {shots}/{goal_shots} роликов."
        todo_line = f"осталось {left_uploaded} выложить и {left_shots} снять, продолжаем!"
        
        texts = [
            f"⚡️ {status_line} {todo_line}",
            f"💪 {status_line} Давай поднажмем, {todo_line}",
            f"🎬 {status_line} Еще чуть-чуть: {todo_line} 🥰"
        ]

    text = random.choice(texts)
    
    try:
        # Красивая анимация для поддержки
        animation = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif"
        if shots >= goal_shots and uploaded >= goal_uploaded:
            animation = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l0Exd9XJm0H9H8LpG/giphy.gif"

        await bot.send_animation(
            chat_id=user.id,
            animation=animation,
            caption=text
        )
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
