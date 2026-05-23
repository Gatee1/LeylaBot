from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.database.models import DailyProgress

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎥 Отметить съёмку", callback_data="track_shooting"),
            InlineKeyboardButton(text="🚀 Выкладка", callback_data="track_upload")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="view_stats"),
            InlineKeyboardButton(text="💡 Идеи", callback_data="view_ideas")
        ],
        [
            InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url="https://lelya-mini-app.vercel.app"))
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ]
    ])

def shooting_kb(current_count: int):
    buttons = []
    for i in range(1, 4):
        icon = "✅" if i <= current_count else "⚪️"
        buttons.append(InlineKeyboardButton(text=f"{icon} Ролик {i}", callback_data=f"shot_{i}"))
    
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def upload_kb(progress: DailyProgress):
    def get_icon(status): return "✅" if status else "❌"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_yt)} YouTube", callback_data="toggle_yt"),
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_ig)} Instagram", callback_data="toggle_ig")
        ],
        [
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_tt)} TikTok", callback_data="toggle_tt"),
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_vk)} VK", callback_data="toggle_vk")
        ],
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def settings_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Выбор персонажа", callback_data="change_character")],
        [InlineKeyboardButton(text="⏰ Настройка уведомлений", callback_data="setup_reminders")],
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def character_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Подружка", callback_data="char_Girlfriend")],
        [InlineKeyboardButton(text="💪 Тренер", callback_data="char_Coach")],
        [InlineKeyboardButton(text="🐱 Котик", callback_data="char_Cat")],
        [InlineKeyboardButton(text="« Назад", callback_data="settings")]
    ])
