from sqlalchemy import select, update, and_, desc, func
from bot.database.models import SessionLocal, User, DailyProgress, Idea, Video, Account
from datetime import date, datetime, timedelta

async def get_user(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def add_user(user_id: int, username: str, full_name: str, **kwargs):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=username, full_name=full_name, **kwargs)
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                user = await session.get(User, user_id)
        return user

async def update_user(user_id: int, **kwargs):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await session.commit()
            await session.refresh(user)
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
        ).order_by(DailyProgress.id.desc())
    )
    progresses = result.scalars().all()
    
    if not progresses:
        progress = DailyProgress(user_id=user_id, date=target_date)
        session.add(progress)
        if commit:
            try:
                await session.commit()
                await session.refresh(progress)
            except Exception:
                await session.rollback()
                # If commit fails, it might be a race condition, try fetching again
                result = await session.execute(
                    select(DailyProgress).where(
                        and_(DailyProgress.user_id == user_id, DailyProgress.date == target_date)
                    )
                )
                progress = result.scalars().first()
        return progress
    
    # If multiple found, return the most recent one (highest ID)
    return progresses[0]

async def update_shots(user_id: int, count: int):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        old_count = progress.shots_count or 0
        progress.shots_count = count
        
        # Streak logic
        if count >= 3 and old_count < 3:
            user = await session.get(User, user_id)
            if user:
                user.streak += 1
                if user.streak > user.max_streak:
                    user.max_streak = user.streak
        
        await session.commit()

async def update_posts(user_id: int, count: int):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        progress.posts_count = count
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
        
        return {
            "recorded": progress.shots_count or 0,
            "posted": progress.posts_count or 0,
            "goal": user.daily_goal if user else 3,
            "streak": user.streak if user else 0,
            "activity": [v or 0 for v in activity]
        }

async def record_studio_action(user_id: int, kind: str):
    async with SessionLocal() as session:
        progress = await get_or_create_daily_progress(user_id, session=session)
        
        if kind == "recorded":
            current = progress.shots_count or 0
            await update_shots(user_id, current + 1)
        elif kind == "posted":
            current = progress.posts_count or 0
            await update_posts(user_id, current + 1)
            
            # Legacy platform logic (optional but keeping for now)
            target_platform = None
            if not progress.uploaded_yt: 
                progress.uploaded_yt = True
                target_platform = "youtube"
            elif not progress.uploaded_ig: 
                progress.uploaded_ig = True
                target_platform = "instagram"
            elif not progress.uploaded_tt: 
                progress.uploaded_tt = True
                target_platform = "tiktok"
            elif not progress.uploaded_vk: 
                progress.uploaded_vk = True
                target_platform = "vk"
            
            if target_platform:
                video = Video(
                    user_id=user_id, 
                    title=f"Post on {target_platform.capitalize()} ({date.today().isoformat()})",
                    status="posted",
                    platform=target_platform,
                    posted_at=datetime.now()
                )
                session.add(video)
                await session.commit()
            
        # Refresh progress to get updated values
        return await get_studio_today(user_id)

async def get_detailed_analytics(user_id: int):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return {"platforms": []}
            
        platforms = user.platforms or []
        result_platforms = []
        
        for p in platforms:
            # Count posted videos for this platform
            v_result = await session.execute(
                select(func.count(Video.id))
                .where(and_(Video.user_id == user_id, Video.platform == p, Video.status == "posted"))
            )
            count = v_result.scalar() or 0
            
            # Get latest video as top post
            tp_result = await session.execute(
                select(Video)
                .where(and_(Video.user_id == user_id, Video.platform == p, Video.status == "posted"))
                .order_by(Video.posted_at.desc())
                .limit(1)
            )
            top_video = tp_result.scalar_one_or_none()
            
            # Growth calculation (simplistic: compared to last week)
            seven_days_ago = datetime.now() - timedelta(days=7)
            prev_v_result = await session.execute(
                select(func.count(Video.id))
                .where(and_(
                    Video.user_id == user_id, 
                    Video.platform == p, 
                    Video.status == "posted",
                    Video.posted_at < seven_days_ago
                ))
            )
            prev_count = prev_v_result.scalar() or 0
            
            growth = 0
            if prev_count > 0:
                growth = ((count - prev_count) / prev_count) * 100
            elif count > 0:
                growth = 100.0 # First week growth
                
            # Reach (simulated as count * 150 for now, as we don't have real API)
            # In a real app, this would come from an external service
            reach = count * 150 
            
            result_platforms.append({
                "platform": p.upper(),
                "reach": reach,
                "growth": growth,
                "top_post": {
                    "title": top_video.title,
                    "views": reach # Use reach as views for mock
                } if top_video else None
            })
            
        return {"platforms": result_platforms}

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

async def get_user_accounts(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Account).where(Account.user_id == user_id).order_by(Account.connected_at.desc())
        )
        return result.scalars().all()

async def save_account(user_id: int, platform: str, tokens: dict, profile_data: dict = None):
    async with SessionLocal() as session:
        # Check if account already exists
        result = await session.execute(
            select(Account).where(and_(Account.user_id == user_id, Account.platform == platform))
        )
        account = result.scalar_one_or_none()
        
        if not account:
            account = Account(user_id=user_id, platform=platform)
            session.add(account)
            
        account.access_token = tokens.get("access_token")
        account.refresh_token = tokens.get("refresh_token")
        if tokens.get("expires_in"):
            account.token_expires_at = datetime.now() + timedelta(seconds=tokens["expires_in"])
            
        if profile_data:
            account.handle = profile_data.get("handle")
            account.display_name = profile_data.get("display_name")
            account.avatar_url = profile_data.get("avatar_url")
            account.followers = profile_data.get("followers", 0)
            
        account.status = "active"
        account.connected_at = datetime.now()
        
        await session.commit()
        return account

async def delete_account(user_id: int, account_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Account).where(and_(Account.id == account_id, Account.user_id == user_id))
        )
        account = result.scalar_one_or_none()
        if account:
            await session.delete(account)
            await session.commit()
            return True
        return False

async def fetch_account_analytics(user_id: int, account_id: int, range_str: str = "30d"):
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        if not account or account.user_id != user_id:
            return None
            
        # Mock analytics based on account data
        # In a real app, this would fetch from social platform APIs
        days = 30
        if range_str == "7d": days = 7
        elif range_str == "90d": days = 90
        
        return {
            "account_id": account.id,
            "platform": account.platform,
            "handle": account.handle or "creator",
            "summary": {
                "followers": account.followers,
                "followers_delta": int(account.followers * 0.05),
                "reach": account.followers * 10,
                "reach_delta": 12.5,
                "posts": 12,
                "engagement_rate": 4.2
            },
            "top_posts": [
                {
                    "id": f"p{i}",
                    "title": f"Viral {account.platform.capitalize()} Content {i}",
                    "url": "#",
                    "thumbnail_url": account.avatar_url,
                    "views": account.followers * (5 - i),
                    "likes": int(account.followers * (5 - i) * 0.1),
                    "comments": int(account.followers * (5 - i) * 0.01),
                    "published_at": (datetime.now() - timedelta(days=i*2)).isoformat()
                } for i in range(1, 6)
            ],
            "timeseries": [
                {
                    "date": (date.today() - timedelta(days=i)).isoformat(),
                    "followers": account.followers - (days - i) * 10,
                    "reach": (account.followers * 10) - (days - i) * 100
                } for i in range(days, -1, -1)
            ]
        }
