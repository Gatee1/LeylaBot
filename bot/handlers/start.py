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
        f"✨ Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я твой премиальный ассистент по контенту. Моя миссия — сделать твой путь креатора легким и дисциплинированным. 💎\n\n"
        "📈 <b>Твой план:</b> 3 ролика в день (Пн-Пт).\n"
        "🚀 <b>Твой успех:</b> Все площадки (YT, IG, TT, VK).\n\n"
        "Выбирай действие в меню ниже:"
    )
    
    await message.answer_animation(
        animation="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqZndqJmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif",
        caption=welcome_text,
        reply_markup=main_menu_kb()
    )
