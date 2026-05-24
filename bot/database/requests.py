from sqlalchemy import select, update, and_, desc, func
from bot.database.models import SessionLocal, User, DailyProgress, Idea, Video
from datetime import date, datetime, timedelta

async def get_user(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def add_user(user_id: int, username: str, full_name: str):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                # If user was created by another concurrent request, just return existing
                user = await session.get(User, user_id)
        return user

async def get_or_create_daily_progress(user_id: int, target_date: date = None, session=None):
    if target_date is None:
        target_date = date.today()
        
    if session is None:
        async with SessionLocal() as session:
            return await _get_or_create_progress_logic(user_id, target_date, session, commit=True)
    else:
        return await _get_or_create_progress_logic(user_id, target_date, session, commit=False)

async def _get_or_create_progress_logic(user_id, target_date, session, commit=False):
    result = await session.execute(
        select(DailyProgress).where(
            and_(DailyProgress.user_id == user_id, DailyProgress.date == target_date)
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = DailyProgress(user_id=user_id, date=target_date)
        session.add(progress)
        if commit:
            await session.commit()
            await session.refresh(progress)
            
    return progress

async def update_shots(user_id: int, count: int):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        old_count = progress.shots_count
        progress.shots_count = count
        
        # Streak logic
        if count >= 3 and old_count < 3:
            user = await session.get(User, user_id)
            if user:
                user.streak += 1
                if user.streak > user.max_streak:
                    user.max_streak = user.streak
        
        await session.commit()

async def update_upload_status(user_id: int, platform: str, status: bool):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        if platform == "yt": progress.uploaded_yt = status
        elif platform == "ig": progress.uploaded_ig = status
        elif platform == "tt": progress.uploaded_tt = status
        elif platform == "vk": progress.uploaded_vk = status
        await session.commit()

async def get_user_stats(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(DailyProgress).where(DailyProgress.user_id == user_id).order_by(DailyProgress.date.desc())
        )
        return result.scalars().all()

async def get_user_streak(user_id: int):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        return {"streak": user.streak if user else 0, "max_streak": user.max_streak if user else 0}

async def add_video(user_id: int, title: str, status: str = "recorded", platform: str = None):
    async with SessionLocal() as session:
        video = Video(user_id=user_id, title=title, status=status, platform=platform)
        session.add(video)
        await session.commit()
        await session.refresh(video)
        return video

async def get_user_videos(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(Video.user_id == user_id).order_by(Video.created_at.desc())
        )
        return result.scalars().all()

async def update_video_status(video_id: int, status: str):
    async with SessionLocal() as session:
        video = await session.get(Video, video_id)
        if video:
            video.status = status
            if status == "posted":
                video.posted_at = datetime.now()
            await session.commit()
            await session.refresh(video)
        return video

async def get_weekly_analytics(user_id: int):
    async with SessionLocal() as session:
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        result = await session.execute(
            select(DailyProgress).where(
                and_(DailyProgress.user_id == user_id, DailyProgress.date >= start_of_week)
            )
        )
        progresses = result.scalars().all()
        
        total_shots = sum(p.shots_count for p in progresses)
        total_posted = sum(1 for p in progresses if p.uploaded_yt or p.uploaded_ig or p.uploaded_tt or p.uploaded_vk)
        
        return {
            "total_shots": total_shots,
            "total_posted": total_posted,
            "daily_stats": [
                {
                    "date": p.date.isoformat(),
                    "shots": p.shots_count,
                    "platforms": {
                        "yt": p.uploaded_yt,
                        "ig": p.uploaded_ig,
                        "tt": p.uploaded_tt,
                        "vk": p.uploaded_vk
                    }
                } for p in progresses
            ]
        }

async def get_top_videos(user_id: int, limit: int = 5):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Video).where(
                and_(Video.user_id == user_id, Video.status == "posted")
            ).order_by(Video.posted_at.desc()).limit(limit)
        )
        return result.scalars().all()
