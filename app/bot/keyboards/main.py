from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.core.config import settings


def get_main_keyboard() -> InlineKeyboardMarkup:
    # URL to the Vercel-deployed Mini App
    web_app_url = "https://lelya-studio.vercel.app" # This should be in settings/env
    
    keyboard = [
        [InlineKeyboardButton(text="🚀 Open Studio", web_app=WebAppInfo(url=web_app_url))],
        [
            InlineKeyboardButton(text="📈 Stats", callback_data="view_stats"),
            InlineKeyboardButton(text="🎯 Goals", callback_data="view_goals"),
        ],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="view_settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_goals_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="📹 Recorded +1", callback_data="goal_inc_shoot"),
            InlineKeyboardButton(text="✅ Published +1", callback_data="goal_inc_publish"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
