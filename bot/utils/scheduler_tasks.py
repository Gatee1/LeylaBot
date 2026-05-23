import random
from aiogram import Bot
from bot.database.models import SessionLocal, User, DailyProgress
from bot.database.requests import get_or_create_daily_progress, get_user_stats
from sqlalchemy import select
from datetime import date, datetime

from bot.utils.media_assets import ASSETS

async def check_and_send_reminders(bot: Bot):
    # Только с понедельника по пятницу
    if date.today().weekday() > 4:
        return

    now_time = datetime.now().strftime("%H:%M")
    # Вечерняя рефлексия всегда в 21:00 по умолчанию, если не задано иное
    is_reflection_time = now_time == "21:00"

    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Проверяем все три времени напоминаний
            if now_time in [user.morning_time, user.afternoon_time, user.evening_time]:
                is_morning = now_time == user.morning_time
                progress = await get_or_create_daily_progress(user.id)
                await send_unified_reminder(bot, user, progress, is_morning)
            
            if is_reflection_time:
                await send_evening_reflection(bot, user)

async def send_evening_reflection(bot: Bot, user: User):
    questions = [
        "Что сегодня было самым сложным в создании контента? ✍️",
        "За что ты сегодня собой гордишься? 🌟",
        "Какая идея сегодня пришла тебе в голову совершенно внезапно? 💡",
        "Что бы ты завтра сделала иначе, чтобы съемка прошла легче? 🎬",
        "Какой ролик сегодня доставил тебе больше всего удовольствия при монтаже? 🥰"
    ]
    question = random.choice(questions)
    
    text = (
        "🌙 <b>Время вечерней рефлексии</b>\n\n"
        f"{question}\n\n"
        "<i>Напиши ответ прямо сюда, это поможет тебе отслеживать свой рост!</i>"
    )
    
    try:
        from bot.handlers.reflection import ReflectionStates
        from aiogram.fsm.context import FSMContext
        # We can't easily set state from scheduler without a message, 
        # but we can send a message with a button to start reflection
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Ответить ✨", callback_data="start_reflection")]
        ])
        
        await bot.send_animation(
            chat_id=user.id,
            animation=ASSETS["welcome"],
            caption=text,
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Failed to send reflection to {user.id}: {e}")

async def send_unified_reminder(bot: Bot, user: User, progress: DailyProgress, is_morning: bool = False):
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
        if is_morning:
            # Утренний мудборд
            inspiration_url = random.choice(ASSETS["inspiration"])
            morning_text = f"✨ <b>Твой утренний мудборд для вдохновения:</b>\n\n{text}"
            await bot.send_photo(
                chat_id=user.id,
                photo=inspiration_url,
                caption=morning_text,
                parse_mode="HTML"
            )
        else:
            # Обычное напоминание с анимацией
            animation = ASSETS["shooting"]
            if shots >= goal_shots and uploaded >= goal_uploaded:
                animation = ASSETS["success"]

            await bot.send_animation(
                chat_id=user.id,
                animation=animation,
                caption=text,
                parse_mode="HTML"
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
