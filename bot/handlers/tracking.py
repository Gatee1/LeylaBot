from aiogram import Router, types, F
from bot.database.requests import get_or_create_daily_progress, update_shots, update_upload_status
from bot.keyboards.inline import shooting_kb, upload_kb, main_menu_kb
from bot.utils.media_assets import ASSETS

router = Router()

@router.callback_query(F.data == "track_shooting")
async def track_shooting(callback: types.CallbackQuery):
    progress = await get_or_create_daily_progress(callback.from_user.id)
    await callback.message.edit_media(
        media=types.InputMediaAnimation(
            media=ASSETS["shooting"],
            caption=f"🎥 <b>Отметь снятые сегодня ролики:</b>\nТвоя цель на сегодня: 3 шт."
        ),
        reply_markup=shooting_kb(progress.shots_count)
    )

@router.callback_query(F.data.startswith("shot_"))
async def handle_shot(callback: types.CallbackQuery):
    count = int(callback.data.split("_")[1])
    await update_shots(callback.from_user.id, count)
    
    progress = await get_or_create_daily_progress(callback.from_user.id)
    
    text = f"✅ Отлично! Роликов снято: {count}/3"
    if count == 3:
        text += "\n\n🚀 План по съёмке выполнен! Пора выкладывать?"
        
    await callback.answer(f"Записано: {count}")
    await callback.message.edit_caption(
        caption=text,
        reply_markup=shooting_kb(progress.shots_count)
    )

@router.callback_query(F.data == "track_upload")
async def track_upload(callback: types.CallbackQuery):
    progress = await get_or_create_daily_progress(callback.from_user.id)
    await callback.message.edit_media(
        media=types.InputMediaAnimation(
            media=ASSETS["upload"],
            caption="🚀 <b>Отметь площадки, на которые уже выложен контент:</b>"
        ),
        reply_markup=upload_kb(progress)
    )

@router.callback_query(F.data.startswith("toggle_"))
async def handle_toggle(callback: types.CallbackQuery):
    platform = callback.data.split("_")[1]
    progress = await get_or_create_daily_progress(callback.from_user.id)
    
    current_status = getattr(progress, f"uploaded_{platform}")
    await update_upload_status(callback.from_user.id, platform, not current_status)
    
    new_progress = await get_or_create_daily_progress(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=upload_kb(new_progress))
    await callback.answer("Статус обновлен!")

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    try:
        await callback.message.edit_media(
            media=types.InputMediaAnimation(
                media=ASSETS["welcome"],
                caption=f"✨ С возвращением!\n\nВыбирай действие в меню ниже:"
            ),
            reply_markup=main_menu_kb()
        )
    except Exception:
        await callback.message.answer_animation(
            animation=ASSETS["welcome"],
            caption=f"✨ С возвращением!\n\nВыбирай действие в меню ниже:",
            reply_markup=main_menu_kb()
        )
        await callback.message.delete()
