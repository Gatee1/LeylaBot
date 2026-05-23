from sqlalchemy import select, update, and_
from bot.database.models import SessionLocal, User, DailyProgress, Idea
from datetime import date

async def get_user(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def add_user(user_id: int, username: str, full_name: str):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
        return user

async def get_or_create_daily_progress(user_id: int, target_date: date = None):
    if target_date is None:
        target_date = date.today()
        
    async with SessionLocal() as session:
        result = await session.execute(
            select(DailyProgress).where(
                and_(DailyProgress.user_id == user_id, DailyProgress.date == target_date)
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            progress = DailyProgress(user_id=user_id, date=target_date)
            session.add(progress)
            await session.commit()
            await session.refresh(progress)
            
        return progress

async def update_shots(user_id: int, count: int):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id)
        old_count = progress.shots_count
        progress.shots_count = count
        session.add(progress)
        
        # Streak logic
        if count >= 3 and old_count < 3:
            user = await session.get(User, user_id)
            user.streak += 1
            if user.streak > user.max_streak:
                user.max_streak = user.streak
        
        await session.commit()

async def update_upload_status(user_id: int, platform: str, status: bool):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id)
        if platform == "yt": progress.uploaded_yt = status
        elif platform == "ig": progress.uploaded_ig = status
        elif platform == "tt": progress.uploaded_tt = status
        elif platform == "vk": progress.uploaded_vk = status
        session.add(progress)
        await session.commit()

async def get_user_stats(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(DailyProgress).where(DailyProgress.user_id == user_id).order_by(DailyProgress.date.desc())
        )
        return result.scalars().all()
