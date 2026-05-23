from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.models import User as UserModel
from app.schemas.user import User, OnboardingRequest, ProfileResponse, Achievement
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=User)
async def get_me(
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Get current user profile.
    """
    # Calculate streak and total reels (simplified for now)
    is_new = current_user.onboarded_at is None
    
    return {
        "telegram_id": current_user.telegram_id,
        "first_name": current_user.first_name,
        "username": current_user.username,
        "photo_url": current_user.photo_url,
        "is_new": is_new,
        "streak_days": 0,
        "total_reels": 0,
        "timezone": current_user.timezone,
        "manager_username": current_user.manager_username,
        "notifications_enabled": current_user.notifications_enabled
    }


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Get full profile with achievements.
    """
    # 1. Get user data (same as /me)
    is_new = current_user.onboarded_at is None
    me_data = {
        "telegram_id": current_user.telegram_id,
        "first_name": current_user.first_name,
        "username": current_user.username,
        "photo_url": current_user.photo_url,
        "is_new": is_new,
        "streak_days": 0,
        "total_reels": 0,
        "timezone": current_user.timezone,
        "manager_username": current_user.manager_username,
        "notifications_enabled": current_user.notifications_enabled
    }

    # 2. Mock achievements for now
    achievements = [
        Achievement(
            key="hot_streak",
            label="Hot Streak",
            earned_at=date.today(),
            earned_at_label=date.today().strftime("%b %d, %Y"),
            icon="flame"
        )
    ]

    return ProfileResponse(me=me_data, achievements=achievements)


@router.post("/onboarding", response_model=User)
async def onboard_me(
    request: OnboardingRequest,
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete user onboarding.
    """
    user_service = UserService(db)
    user = await user_service.onboard_user(current_user.telegram_id, request.model_dump())
    
    return {
        "telegram_id": user.telegram_id,
        "first_name": user.first_name,
        "username": user.username,
        "photo_url": user.photo_url,
        "is_new": False,
        "streak_days": 0,
        "total_reels": 0,
        "timezone": user.timezone,
        "manager_username": user.manager_username,
        "notifications_enabled": user.notifications_enabled
    }
