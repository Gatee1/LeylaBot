from aiogram import Router, types, F
from bot.keyboards.inline import main_menu_kb, time_settings_kb, settings_kb
from bot.database.models import SessionLocal, User

router = Router()

@router.callback_query(F.data == "setup_reminders")
async def setup_reminders(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption=(
            "⏰ <b>Настройка уведомлений:</b>\n\n"
            "Выбери, какое время ты хочешь изменить:"
        ),
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎥 Время съёмки", callback_data="time_shooting")],
            [types.InlineKeyboardButton(text="🚀 Время выкладки", callback_data="time_upload")],
            [types.InlineKeyboardButton(text="« Назад", callback_data="settings")]
        ])
    )

@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: types.CallbackQuery):
    reminder_type = callback.data.split("_")[1]
    label = "съёмки" if reminder_type == "shooting" else "выкладки"
    
    await callback.message.edit_caption(
        caption=f"⏰ <b>Выбери новое время для {label}:</b>",
        reply_markup=time_settings_kb(reminder_type)
    )

@router.callback_query(F.data.startswith("settime_"))
async def set_time(callback: types.CallbackQuery):
    _, reminder_type, target_time = callback.data.split("_")
    
    async with SessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        if reminder_type == "shooting":
            user.shooting_time = target_time
        else:
            user.upload_time = target_time
        await session.commit()
        
    await callback.answer(f"Время сохранено: {target_time}")
    await setup_reminders(callback)
