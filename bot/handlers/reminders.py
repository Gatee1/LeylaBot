import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.inline import main_menu_kb, settings_kb
from bot.database.models import SessionLocal, User
from bot.utils.media_assets import ASSETS

router = Router()

class TimeSettings(StatesGroup):
    waiting_for_morning = State()
    waiting_for_afternoon = State()
    waiting_for_evening = State()

@router.callback_query(F.data == "setup_reminders")
async def setup_reminders(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
    
    await callback.message.edit_media(
        media=types.InputMediaAnimation(
            media=ASSETS["settings"],
            caption=(
                "⏰ <b>Настройка времени напоминаний</b>\n\n"
                f"🌅 Утро: <b>{user.morning_time}</b>\n"
                f"☀️ День: <b>{user.afternoon_time}</b>\n"
                f"🌙 Вечер: <b>{user.evening_time}</b>\n\n"
                "Выбери, какое время хочешь изменить, и напиши новое в чат (например, 12:30):"
            )
        ),
        reply_markup=settings_kb()
    )

@router.callback_query(F.data.startswith("set_"))
async def start_set_time(callback: types.CallbackQuery, state: FSMContext):
    time_type = callback.data.split("_")[1]
    labels = {"morning": "утреннего", "afternoon": "дневного", "evening": "вечернего"}
    
    await state.update_data(time_type=time_type)
    if time_type == "morning": await state.set_state(TimeSettings.waiting_for_morning)
    elif time_type == "afternoon": await state.set_state(TimeSettings.waiting_for_afternoon)
    else: await state.set_state(TimeSettings.waiting_for_evening)
    
    await callback.message.answer(f"Напиши время для <b>{labels[time_type]}</b> напоминания в формате HH:MM (например, 09:15):")
    await callback.answer()

@router.message(TimeSettings.waiting_for_morning)
@router.message(TimeSettings.waiting_for_afternoon)
@router.message(TimeSettings.waiting_for_evening)
async def process_time_input(message: types.Message, state: FSMContext):
    time_str = message.text.strip()
    
    # Регулярка для проверки формата HH:MM
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_str):
        await message.answer("❌ Неверный формат! Напиши время в формате ЧЧ:ММ (например, 08:30 или 20:00):")
        return

    data = await state.get_data()
    time_type = data.get("time_type")
    
    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if time_type == "morning": user.morning_time = time_str
        elif time_type == "afternoon": user.afternoon_time = time_str
        elif time_type == "evening": user.evening_time = time_str
        await session.commit()
        
    await state.clear()
    try:
        await message.answer_animation(
            animation=ASSETS["success"],
            caption=f"✅ Время успешно сохранено: <b>{time_str}</b>",
            reply_markup=main_menu_kb()
        )
    except Exception:
        await message.answer(
            text=f"✅ Время успешно сохранено: <b>{time_str}</b>",
            reply_markup=main_menu_kb()
        )
