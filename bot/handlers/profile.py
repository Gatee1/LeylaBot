from aiogram import Router, types, F
from bot.database.requests import get_user_stats, get_user
from bot.keyboards.inline import settings_kb, main_menu_kb
from bot.database.models import SessionLocal, User

router = Router()

@router.callback_query(F.data == "view_stats")
async def view_stats(callback: types.CallbackQuery):
    stats = await get_user_stats(callback.from_user.id)
    
    if not stats:
        await callback.answer("Статистики пока нет. Начни отмечать прогресс!")
        return
        
    total_shots = sum(s.shots_count for s in stats)
    days_count = len(stats)
    
    text = (
        "📊 <b>Твоя статистика:</b>\n\n"
        f"🎬 Всего снято: {total_shots} ролика(ов)\n"
        f"📅 Дней в деле: {days_count}\n\n"
        "Последние 5 дней:\n"
    )
    
    for s in stats[:5]:
        platforms = []
        if s.uploaded_yt: platforms.append("YT")
        if s.uploaded_ig: platforms.append("IG")
        if s.uploaded_tt: platforms.append("TT")
        if s.uploaded_vk: platforms.append("VK")
        
        plat_str = ", ".join(platforms) if platforms else "не выложено"
        text += f"• {s.date.strftime('%d.%m')}: {s.shots_count}/3 🎥 ({plat_str})\n"
        
    await callback.message.edit_caption(
        caption=text,
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "settings")
async def settings_menu(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption="⚙️ <b>Настройки:</b>\nЗдесь можно изменить время уведомлений.",
        reply_markup=settings_kb()
    )

async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption=f"👋 С возвращением!\n\nВыбирай действие в меню ниже:",
        reply_markup=main_menu_kb()
    )
