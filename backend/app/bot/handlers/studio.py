from aiogram import Router, types, F
from app.bot.keyboards.main import get_main_keyboard

router = Router()


@router.callback_query(F.data == "view_stats")
async def view_stats(callback: types.CallbackQuery):
    # This is a simplified view, detailed stats are in the Mini App
    text = (
        "📈 <b>Твоя аналитика:</b>\n\n"
        "Общий охват: 1.2M\n"
        "Новых подписчиков: +4.2K\n\n"
        "Подробную статистику по каждой платформе (TikTok, YT, IG, VK) смотри в приложении Studio!"
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "view_settings")
async def view_settings(callback: types.CallbackQuery):
    text = (
        "⚙️ <b>Настройки:</b>\n\n"
        "🔔 Уведомления: Включены\n"
        "🌍 Таймзона: UTC\n"
        "👤 Аккаунты: TikTok, Instagram\n\n"
        "<i>Изменить настройки можно в профиле внутри Mini App.</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()
