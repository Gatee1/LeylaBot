from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import DailyGoal
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[DailyGoal]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyGoal, db)

    async def get_by_user_and_date(self, telegram_id: int, target_date: date) -> Optional[DailyGoal]:
        query = select(DailyGoal).where(
            DailyGoal.telegram_id == telegram_id,
            DailyGoal.date == target_date
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_daily(self, telegram_id: int, target_date: date) -> DailyGoal:
        goal = await self.get_by_user_and_date(telegram_id, target_date)
        if not goal:
            goal = await self.create({
                "telegram_id": telegram_id,
                "date": target_date,
                "shoot_goal": 3,
                "shoot_current": 0,
                "publish_goal": 3,
                "publish_current": 0
            })
        return goal
