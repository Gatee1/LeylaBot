from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from app.bot.keyboards.main import get_main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, db: AsyncSession):
    user_service = UserService(db)
    user_data = {
        "id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "username": message.from_user.username,
        "photo_url": None, # Telegram bot API doesn't provide photo URL directly in message
    }
    user, is_new = await user_service.get_or_create_user(user_data)
    
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я твой ассистент Lelya Creator Studio.\n"
        "Помогаю отслеживать прогресс, ставить цели и расти в соцсетях.\n\n"
        "Нажми кнопку ниже, чтобы открыть Studio или начни записывать свои успехи прямо здесь!"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню Lelya Creator Studio:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()
