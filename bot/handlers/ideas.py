import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database.models import SessionLocal, Idea
from bot.keyboards.inline import main_menu_kb
from bot.utils.media_assets import ASSETS
from sqlalchemy import select

router = Router()

class IdeaStates(StatesGroup):
    waiting_for_content = State()

# Regex for social media links
SOCIAL_LINK_PATTERN = re.compile(
    r'(https?://)?(www\.)?(instagram\.com/(reels|p|reel)/|tiktok\.com/|youtube\.com/(shorts/|watch\?v=)|vk\.com/clip-|v\.vk\.com/c/|youtube\.be/)'
)

@router.callback_query(F.data == "view_ideas")
async def view_ideas(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(Idea.user_id == callback.from_user.id).order_by(Idea.created_at.desc())
        )
        ideas = result.scalars().all()
    
    if not ideas:
        text = "💡 <b>Твой банк идей пуст.</b>\nХочешь добавить что-то новое? Можно прислать текст, фото, видео или ссылку на Reels/TikTok!"
    else:
        text = "💡 <b>Твои идеи:</b>\n\n"
        for i, idea in enumerate(ideas[:10], 1):
            icon = "📝" if not idea.media_type else "🖼" if idea.media_type == "photo" else "🎬"
            if idea.text and SOCIAL_LINK_PATTERN.search(idea.text):
                icon = "🔗"
            content = idea.text if idea.text else "Без текста"
            # Truncate long links or text
            display_text = (content[:40] + '...') if len(content) > 40 else content
            text += f"<b>{i}.</b> {icon} {display_text}\n"
        
        if len(ideas) > 10:
            text += f"\n<i>...и еще {len(ideas)-10} идей</i>"
            
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ Добавить идею", callback_data="add_idea", style="success")],
        [types.InlineKeyboardButton(text="🗑 Очистить банк", callback_data="clear_ideas", style="danger")],
        [types.InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])
    
    try:
        await callback.message.edit_media(
            media=types.InputMediaAnimation(media=ASSETS["ideas"], caption=text),
            reply_markup=kb
        )
    except Exception:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=kb
        )

@router.callback_query(F.data == "add_idea")
async def add_idea_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(IdeaStates.waiting_for_content)
    await callback.message.answer("Пришли свою идею! Это может быть текст, фото или короткое видео-референс:")
    await callback.answer()

@router.message(IdeaStates.waiting_for_content)
async def process_idea(message: types.Message, state: FSMContext):
    media_id = None
    media_type = None
    text = message.text or message.caption

    if message.photo:
        media_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        media_id = message.video.file_id
        media_type = "video"
    elif message.animation:
        media_id = message.animation.file_id
        media_type = "animation"
    elif message.document:
        # Handle case where image is sent as document
        if message.document.mime_type and message.document.mime_type.startswith("image/"):
            media_id = message.document.file_id
            media_type = "photo"
        elif message.document.mime_type and message.document.mime_type.startswith("video/"):
            media_id = message.document.file_id
            media_type = "video"

    async with SessionLocal() as session:
        new_idea = Idea(
            user_id=message.from_user.id,
            text=text,
            media_id=media_id,
            media_type=media_type
        )
        session.add(new_idea)
        await session.commit()
        
    await state.clear()
    
    # Use answer_animation for better UX
    try:
        await message.answer_animation(
            animation=ASSETS["success"],
            caption="✅ <b>Идея сохранена в твой банк!</b>\nЯ напомню о ней, когда ты пойдешь снимать контент.",
            reply_markup=main_menu_kb()
        )
    except Exception:
        await message.answer(
            text="✅ <b>Идея сохранена в твой банк!</b>\nЯ напомню о ней, когда ты пойдешь снимать контент.",
            reply_markup=main_menu_kb()
        )

# Auto-save links sent to bot
@router.message(F.text, lambda message: SOCIAL_LINK_PATTERN.search(message.text))
async def auto_save_link(message: types.Message, state: FSMContext):
    # Check if we are currently in some state
    current_state = await state.get_state()
    if current_state:
        return

    async with SessionLocal() as session:
        new_idea = Idea(
            user_id=message.from_user.id,
            text=message.text,
            media_type="link"
        )
        session.add(new_idea)
        await session.commit()

    await message.reply(
        "🔗 <b>Ссылка распознана!</b>\nЯ сохранил этот референс в твой банк идей. 💡",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "clear_ideas")
async def clear_ideas(callback: types.CallbackQuery):
    from sqlalchemy import delete
    async with SessionLocal() as session:
        await session.execute(delete(Idea).where(Idea.user_id == callback.from_user.id))
        await session.commit()
    
    await callback.answer("Банк идей очищен!")
    await view_ideas(callback)
