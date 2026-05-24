from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database.models import SessionLocal, Reflection
from bot.keyboards.inline import main_menu_kb
from bot.utils.media_assets import ASSETS

router = Router()

class ReflectionStates(StatesGroup):
    waiting_for_answer = State()

@router.callback_query(F.data == "start_reflection")
async def start_reflection(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ReflectionStates.waiting_for_answer)
    await callback.message.answer("Я внимательно слушаю... Поделись своими мыслями за сегодня:")
    await callback.answer()

@router.message(ReflectionStates.waiting_for_answer)
async def process_reflection_answer(message: types.Message, state: FSMContext):
    async with SessionLocal() as session:
        new_reflection = Reflection(
            user_id=message.from_user.id,
            answer=message.text
        )
        session.add(new_reflection)
        await session.commit()
        
    await state.clear()
    try:
        await message.answer_animation(
            animation=ASSETS["success"],
            caption="✅ Твоя рефлексия сохранена. Ты молодец, что находишь время на анализ! Спокойной ночи! ✨",
            reply_markup=main_menu_kb()
        )
    except Exception:
        await message.answer(
            text="✅ Твоя рефлексия сохранена. Ты молодец, что находишь время на анализ! Спокойной ночи! ✨",
            reply_markup=main_menu_kb()
        )

@router.callback_query(F.data == "view_reflections")
async def view_reflections(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Reflection).where(Reflection.user_id == callback.from_user.id).order_by(Reflection.created_at.desc())
        )
        reflections = result.scalars().all()
    
    if not reflections:
        text = "🌙 <b>Твой дневник рефлексии пуст.</b>\nБот будет спрашивать тебя каждый вечер в 21:00!"
    else:
        text = "🌙 <b>Твои последние записи:</b>\n\n"
        for r in reflections[:5]:
            date_str = r.date.strftime("%d.%m")
            text += f"📅 <b>{date_str}:</b> {r.answer}\n\n"
            
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])
    
    try:
        await callback.message.edit_media(
            media=types.InputMediaAnimation(media=ASSETS["welcome"], caption=text),
            reply_markup=kb
        )
    except Exception:
        await callback.message.answer_animation(
            animation=ASSETS["welcome"],
            caption=text,
            reply_markup=kb
        )
        await callback.message.delete()
