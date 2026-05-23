from datetime import date
from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.goal_repository import GoalRepository
from app.bot.keyboards.main import get_goals_keyboard, get_main_keyboard

router = Router()


@router.callback_query(F.data == "view_goals")
async def view_goals(callback: types.CallbackQuery, db: AsyncSession):
    repo = GoalRepository(db)
    goal = await repo.get_or_create_daily(callback.from_user.id, date.today())
    
    text = (
        "🎯 <b>Твои цели на сегодня:</b>\n\n"
        f"📹 Съемка: {goal.shoot_current}/{goal.shoot_goal}\n"
        f"✅ Публикация: {goal.publish_current}/{goal.publish_goal}\n\n"
        "<i>Продолжай в том же духе! Каждое видео приближает тебя к цели.</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_goals_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("goal_inc_"))
async def increment_goal(callback: types.CallbackQuery, db: AsyncSession):
    repo = GoalRepository(db)
    goal = await repo.get_or_create_daily(callback.from_user.id, date.today())
    
    field = callback.data.split("_")[-1] # "shoot" or "publish"
    
    if field == "shoot":
        goal.shoot_current += 1
    elif field == "publish":
        goal.publish_current += 1
        
    await db.commit()
    
    # Refresh the view
    text = (
        "🎯 <b>Твои цели на сегодня:</b>\n\n"
        f"📹 Съемка: {goal.shoot_current}/{goal.shoot_goal}\n"
        f"✅ Публикация: {goal.publish_current}/{goal.publish_goal}\n\n"
        "Отличная работа! 💪"
    )
    
    await callback.message.edit_text(text, reply_markup=get_goals_keyboard())
    await callback.answer(f"+1 к {'съемке' if field == 'shoot' else 'публикации'}!")
