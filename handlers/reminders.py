from aiogram import Router, types, F
from bot.keyboards.inline import main_menu_kb

router = Router()

@router.callback_query(F.data == "setup_reminders")
async def setup_reminders(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption=(
            "⏰ <b>Настройка уведомлений:</b>\n\n"
            "По умолчанию я напоминаю о съёмке в <b>11:00</b> и о выкладке в <b>18:00</b>.\n\n"
            "<i>(Функция ручной настройки времени в разработке, пока используем стандартный график по будням)</i>"
        ),
        reply_markup=main_menu_kb()
    )
