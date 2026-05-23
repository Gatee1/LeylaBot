from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.database.models import SessionLocal, Idea
from bot.keyboards.inline import main_menu_kb
from sqlalchemy import select

router = Router()

class IdeaStates(StatesGroup):
    waiting_for_idea = State()

@router.callback_query(F.data == "view_ideas")
async def view_ideas(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(Idea.user_id == callback.from_user.id).order_by(Idea.created_at.desc())
        )
        ideas = result.scalars().all()
    
    if not ideas:
        text = "💡 <b>Твой банк идей пуст.</b>\nХочешь добавить что-то новое?"
    else:
        text = "💡 <b>Твои идеи:</b>\n\n"
        for i, idea in enumerate(ideas[:10], 1):
            text += f"{i}. {idea.text}\n"
        
        if len(ideas) > 10:
            text += f"\n<i>...и еще {len(ideas)-10} идей</i>"
            
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ Добавить идею", callback_data="add_idea")],
        [types.InlineKeyboardButton(text="« Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_caption(caption=text, reply_markup=kb)

@router.callback_query(F.data == "add_idea")
async def add_idea_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(IdeaStates.waiting_for_idea)
    await callback.message.answer("Напиши свою идею или сценарий одним сообщением:")
    await callback.answer()

@router.message(IdeaStates.waiting_for_idea)
async def process_idea(message: types.Message, state: FSMContext):
    async with SessionLocal() as session:
        new_idea = Idea(
            user_id=message.from_user.id,
            text=message.text
        )
        session.add(new_idea)
        await session.commit()
        
    await state.clear()
    await message.answer(
        "✅ Идея сохранена в банк!",
        reply_markup=main_menu_kb()
    )
