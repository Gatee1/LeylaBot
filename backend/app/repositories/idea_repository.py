from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Idea
from app.repositories.base import BaseRepository
import uuid


class IdeaRepository(BaseRepository[Idea]):
    def __init__(self, db: AsyncSession):
        super().__init__(Idea, db)

    async def get_by_user(self, telegram_id: int) -> List[Idea]:
        query = select(Idea).where(Idea.telegram_id == telegram_id).order_by(Idea.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, idea_id: uuid.UUID, telegram_id: int) -> Optional[Idea]:
        query = select(Idea).where(Idea.id == idea_id, Idea.telegram_id == telegram_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
