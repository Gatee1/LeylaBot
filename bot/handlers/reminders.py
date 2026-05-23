from aiogram import Router, types, F
from bot.keyboards.inline import main_menu_kb, time_settings_kb, settings_kb
from bot.database.models import SessionLocal, User

router = Router()

@router.callback_query(F.data == "setup_reminders")
async def setup_reminders(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption=(
            "⏰ <b>Настройка времени напоминаний:</b>\n\n"
            "Выбери удобное время, в которое я буду присылать тебе отчет о прогрессе за день:"
        ),
        reply_markup=time_settings_kb()
    )

@router.callback_query(F.data.startswith("settime_"))
async def set_time(callback: types.CallbackQuery):
    target_time = callback.data.split("_")[1]
    
    async with SessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        user.shooting_time = target_time
        await session.commit()
        
    await callback.answer(f"Время напоминания установлено на: {target_time}")
    await callback.message.edit_caption(
        caption=f"✅ Время успешно сохранено! Буду ждать тебя в <b>{target_time}</b> каждый будний день.",
        reply_markup=main_menu_kb()
    )
