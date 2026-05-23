from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Idea, IdeaStatus, Platform
from app.repositories.idea_repository import IdeaRepository


class IdeaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IdeaRepository(db)

    async def get_user_ideas(self, telegram_id: int) -> List[Idea]:
        return await self.repo.get_by_user(telegram_id)

    async def create_idea(self, telegram_id: int, title: str, platform: Platform) -> Idea:
        return await self.repo.create({
            "telegram_id": telegram_id,
            "title": title,
            "platform": platform,
            "status": IdeaStatus.DRAFT
        })

    async def update_idea(self, telegram_id: int, idea_id: uuid.UUID, data: dict) -> Optional[Idea]:
        idea = await self.repo.get_by_id_and_user(idea_id, telegram_id)
        if not idea:
            return None
        return await self.repo.update(idea, data)

    async def delete_idea(self, telegram_id: int, idea_id: uuid.UUID) -> bool:
        idea = await self.repo.get_by_id_and_user(idea_id, telegram_id)
        if not idea:
            return False
        await self.repo.delete(idea.id)
        return True
