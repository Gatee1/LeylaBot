from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.database.models import DailyProgress

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎥 Отметить съёмку", callback_data="track_shooting", style="primary"),
            InlineKeyboardButton(text="🚀 Выкладка", callback_data="track_upload", style="success")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="view_stats"),
            InlineKeyboardButton(text="💡 Идеи", callback_data="view_ideas")
        ],
        [
            InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url="https://mini-app-leyla.vercel.app"))
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ]
    ])

def shooting_kb(current_count: int):
    buttons = []
    for i in range(1, 4):
        icon = "✅" if i <= current_count else "⚪️"
        style = "success" if i <= current_count else None
        buttons.append(InlineKeyboardButton(text=f"{icon} Ролик {i}", callback_data=f"shot_{i}", style=style))
    
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def upload_kb(progress):
    def get_icon(status): return "✅" if status else "❌"
    def get_style(status): return "success" if status else "danger"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_yt)} YouTube", callback_data="toggle_yt", style=get_style(progress.uploaded_yt)),
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_ig)} Instagram", callback_data="toggle_ig", style=get_style(progress.uploaded_ig))
        ],
        [
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_tt)} TikTok", callback_data="toggle_tt", style=get_style(progress.uploaded_tt)),
            InlineKeyboardButton(text=f"{get_icon(progress.uploaded_vk)} VK", callback_data="toggle_vk", style=get_style(progress.uploaded_vk))
        ],
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def settings_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Настройка времени", callback_data="setup_reminders", style="primary")],
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def time_settings_kb(reminder_type: str):
    # type can be 'shooting' or 'upload'
    times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    keyboard = []
    row = []
    for t in times:
        row.append(InlineKeyboardButton(text=t, callback_data=f"settime_{reminder_type}_{t}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton(text="« Назад", callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
