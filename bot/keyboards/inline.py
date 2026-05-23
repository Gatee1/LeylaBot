from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Note: Styles 'primary', 'success', 'danger' are available since Telegram Bot API 9.4
# If aiogram doesn't support them natively yet, we pass them as extra arguments

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

def upload_kb(progress: DailyProgress):
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
        [InlineKeyboardButton(text="👤 Выбор персонажа", callback_data="change_character", style="primary")],
        [InlineKeyboardButton(text="⏰ Настройка уведомлений", callback_data="setup_reminders", style="primary")],
        [InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])

def character_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Подружка", callback_data="char_Girlfriend", style="primary")],
        [InlineKeyboardButton(text="💪 Тренер", callback_data="char_Coach", style="danger")],
        [InlineKeyboardButton(text="🐱 Котик", callback_data="char_Cat", style="success")],
        [InlineKeyboardButton(text="« Назад", callback_data="settings")]
    ])
