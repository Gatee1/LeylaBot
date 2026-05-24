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

async def get_user_ideas(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(Idea.user_id == user_id).order_by(Idea.created_at.desc())
        )
        return result.scalars().all()

async def add_idea(user_id: int, title: str, description: str = None, platform: str = None, status: str = "backlog", scheduled_for: datetime = None):
    async with SessionLocal() as session:
        idea = Idea(user_id=user_id, title=title, description=description, platform=platform, status=status, scheduled_for=scheduled_for)
        session.add(idea)
        await session.commit()
        await session.refresh(idea)
        return idea

async def update_idea(idea_id: int, user_id: int, **kwargs):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(and_(Idea.id == idea_id, Idea.user_id == user_id))
        )
        idea = result.scalar_one_or_none()
        if idea:
            for key, value in kwargs.items():
                if hasattr(idea, key):
                    setattr(idea, key, value)
            await session.commit()
            await session.refresh(idea)
        return idea

async def delete_idea(idea_id: int, user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(and_(Idea.id == idea_id, Idea.user_id == user_id))
        )
        idea = result.scalar_one_or_none()
        if idea:
            await session.delete(idea)
            await session.commit()
            return True
        return False

async def get_studio_today(user_id: int):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        user = await session.get(User, user_id)
        
        # Get activity for last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        result = await session.execute(
            select(DailyProgress.shots_count)
            .where(and_(DailyProgress.user_id == user_id, DailyProgress.date >= thirty_days_ago))
            .order_by(DailyProgress.date.asc())
        )
        activity = result.scalars().all()
        
        # Calculate posted count from platform statuses
        posted = 0
        if progress.uploaded_yt: posted += 1
        if progress.uploaded_ig: posted += 1
        if progress.uploaded_tt: posted += 1
        if progress.uploaded_vk: posted += 1
        
        return {
            "recorded": progress.shots_count,
            "posted": posted,
            "goal": 3,
            "streak": user.streak if user else 0,
            "activity": activity
        }

async def record_studio_action(user_id: int, kind: str):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        if kind == "recorded":
            await update_shots(user_id, progress.shots_count + 1)
        elif kind == "posted":
            # For simplicity, we just mark platforms in order or add a generic posted counter if needed
            # But let's just use update_upload_status for one of the platforms that is not yet posted
            if not progress.uploaded_yt: await update_upload_status(user_id, "yt", True)
            elif not progress.uploaded_ig: await update_upload_status(user_id, "ig", True)
            elif not progress.uploaded_tt: await update_upload_status(user_id, "tt", True)
            elif not progress.uploaded_vk: await update_upload_status(user_id, "vk", True)
            
        return await get_studio_today(user_id)

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
