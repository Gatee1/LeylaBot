from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token, create_refresh_token


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_or_create_user(self, telegram_data: Dict[str, Any]) -> tuple[User, bool]:
        telegram_id = telegram_data.get("id")
        if not telegram_id:
            raise ValueError("Telegram ID missing in data")

        user = await self.repo.get_by_telegram_id(telegram_id)
        is_new = False
        
        if not user:
            user_in = {
                "telegram_id": telegram_id,
                "first_name": telegram_data.get("first_name", "User"),
                "username": telegram_data.get("username"),
                "photo_url": telegram_data.get("photo_url"),
                "timezone": "UTC",
            }
            user = await self.repo.create(user_in)
            is_new = True
        
        return user, is_new

    async def onboard_user(self, telegram_id: int, data: Dict[str, Any]) -> User:
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")
        
        update_data = {
            "first_name": data.get("first_name", user.first_name),
            "timezone": data.get("timezone", user.timezone),
            "onboarded_at": datetime.now(timezone.utc)
        }
        return await self.repo.update(user, update_data)
