from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database.models import SessionLocal, Hashtag
from bot.keyboards.inline import main_menu_kb
from bot.utils.media_assets import ASSETS
from sqlalchemy import select, delete

router = Router()

class HashtagStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_content = State()

@router.callback_query(F.data == "view_hashtags")
async def view_hashtags(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Hashtag).where(Hashtag.user_id == callback.from_user.id)
        )
        hashtags = result.scalars().all()
    
    if not hashtags:
        text = "☁️ <b>Твое облако хэштегов пусто.</b>\nСоздавай наборы тегов для разных типов роликов, чтобы копировать их в один клик!"
    else:
        text = "☁️ <b>Твои наборы хэштегов:</b>\n\n"
        for i, h in enumerate(hashtags, 1):
            text += f"<b>{i}. {h.name}</b>\n<code>{h.content}</code>\n\n"
            
    kb_list = []
    for h in hashtags:
        kb_list.append([types.InlineKeyboardButton(text=f"❌ Удалить {h.name}", callback_data=f"del_hashtag_{h.id}")])
    
    kb_list.append([types.InlineKeyboardButton(text="➕ Создать набор", callback_data="add_hashtag")])
    kb_list.append([types.InlineKeyboardButton(text="« Назад", callback_data="main_menu")])
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    try:
        await callback.message.edit_media(
            media=types.InputMediaAnimation(media=ASSETS["stats"], caption=text),
            reply_markup=kb
        )
    except Exception:
        await callback.message.answer_animation(
            animation=ASSETS["stats"],
            caption=text,
            reply_markup=kb
        )
        await callback.message.delete()

@router.callback_query(F.data == "add_hashtag")
async def add_hashtag_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(HashtagStates.waiting_for_name)
    await callback.message.answer("Введите название для набора (например, 'Beauty' или 'Vlog'):")
    await callback.answer()

@router.message(HashtagStates.waiting_for_name)
async def process_hashtag_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(HashtagStates.waiting_for_content)
    await message.answer("Теперь пришли сам список хэштегов через пробел:")

@router.message(HashtagStates.waiting_for_content)
async def process_hashtag_content(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with SessionLocal() as session:
        new_hashtag = Hashtag(
            user_id=message.from_user.id,
            name=data['name'],
            content=message.text
        )
        session.add(new_hashtag)
        await session.commit()
        
    await state.clear()
    await message.answer_animation(
        animation=ASSETS["success"],
        caption=f"✅ Набор '{data['name']}' сохранен!",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data.startswith("del_hashtag_"))
async def delete_hashtag(callback: types.CallbackQuery):
    hashtag_id = int(callback.data.split("_")[-1])
    async with SessionLocal() as session:
        await session.execute(delete(Hashtag).where(Hashtag.id == hashtag_id))
        await session.commit()
    
    await callback.answer("Набор удален!")
    await view_hashtags(callback)
