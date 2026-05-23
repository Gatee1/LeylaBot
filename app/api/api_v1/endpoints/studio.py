from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.models import User as UserModel, DailyGoal
from app.schemas.studio import StudioResponse, GoalSchema
from app.services.idea_service import IdeaService
from app.repositories.goal_repository import GoalRepository

router = APIRouter()


@router.get("", response_model=StudioResponse)
async def get_studio_data(
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Get daily goals
    goal_repo = GoalRepository(db)
    daily_goal = await goal_repo.get_or_create_daily(current_user.telegram_id, date.today())
    
    goals = [
        GoalSchema(key="shoot", label="Съемка", value=daily_goal.shoot_current, total=daily_goal.shoot_goal),
        GoalSchema(key="publish", label="Публикация", value=daily_goal.publish_current, total=daily_goal.publish_goal),
    ]
    
    # 2. Get activity for last 30 days
    # Intensity = (shoot_current + publish_current) / (shoot_goal + publish_goal) scaled to 0..3
    start_date = date.today() - timedelta(days=29)
    query = select(DailyGoal).where(
        DailyGoal.telegram_id == current_user.telegram_id,
        DailyGoal.date >= start_date
    ).order_by(DailyGoal.date.asc())
    
    result = await db.execute(query)
    daily_goals = {g.date: g for g in result.scalars().all()}
    
    activity = []
    for i in range(30):
        target_date = start_date + timedelta(days=i)
        goal = daily_goals.get(target_date)
        if not goal:
            activity.append(0)
        else:
            total_current = goal.shoot_current + goal.publish_current
            if total_current == 0:
                activity.append(0)
            elif total_current >= (goal.shoot_goal + goal.publish_goal):
                activity.append(3)
            elif total_current >= (goal.shoot_goal + goal.publish_goal) // 2:
                activity.append(2)
            else:
                activity.append(1)
    
    # 3. Get recent ideas
    idea_service = IdeaService(db)
    ideas = await idea_service.get_user_ideas(current_user.telegram_id)
    
    return StudioResponse(
        goals=goals,
        activity=activity,
        ideas=ideas[:5]
    )
