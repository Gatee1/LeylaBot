from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.models import User as UserModel, Platform
from app.schemas.studio import IdeaSchema, IdeaCreateRequest, IdeaUpdateRequest
from app.services.idea_service import IdeaService

router = APIRouter()


@router.get("", response_model=List[IdeaSchema])
async def get_ideas(
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = IdeaService(db)
    return await service.get_user_ideas(current_user.telegram_id)


@router.post("", response_model=IdeaSchema)
async def create_idea(
    request: IdeaCreateRequest,
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = IdeaService(db)
    return await service.create_idea(
        current_user.telegram_id, 
        request.title, 
        Platform(request.platform.lower())
    )


@router.patch("/{idea_id}", response_model=IdeaSchema)
async def update_idea(
    idea_id: uuid.UUID,
    request: IdeaUpdateRequest,
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = IdeaService(db)
    idea = await service.update_idea(
        current_user.telegram_id, 
        idea_id, 
        request.model_dump(exclude_unset=True)
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: uuid.UUID,
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = IdeaService(db)
    success = await service.delete_idea(current_user.telegram_id, idea_id)
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"status": "success"}
