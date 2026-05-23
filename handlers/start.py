from aiogram import Router, types
from aiogram.filters import CommandStart
from bot.database.requests import add_user
from bot.keyboards.inline import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    welcome_text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я твой личный помощник по контенту. Помогу не забыть про ролики, "
        "отследить прогресс и держать дисциплину. 🔥\n\n"
        "Выбирай действие в меню ниже:"
    )
    
    # Можно отправить красивую картинку/гифку
    await message.answer_photo(
        photo="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif",
        caption=welcome_text,
        reply_markup=main_menu_kb()
    )
