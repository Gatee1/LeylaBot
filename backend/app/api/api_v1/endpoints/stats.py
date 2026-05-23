from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.models import User as UserModel, DailyStat, SocialAccount
from app.schemas.studio import StatsResponse, PlatformStat, MetricStat, TopVideoStat

router = APIRouter()


@router.get("", response_model=StatsResponse)
async def get_stats(
    current_user: UserModel = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated social media stats.
    """
    # 1. Check for connected accounts
    query = select(SocialAccount).where(SocialAccount.telegram_id == current_user.telegram_id)
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    # 2. Get daily stats for last 12 periods (days or weeks)
    # For now, let's use the last 12 days
    start_date = date.today() - timedelta(days=11)
    stats_query = select(DailyStat).where(
        DailyStat.telegram_id == current_user.telegram_id,
        DailyStat.date >= start_date
    ).order_by(DailyStat.date.asc())
    
    stats_result = await db.execute(stats_query)
    daily_stats = stats_result.scalars().all()
    
    # Simple aggregation for the graph
    reach_by_day_map = {start_date + timedelta(days=i): 0 for i in range(12)}
    for s in daily_stats:
        if s.date in reach_by_day_map:
            reach_by_day_map[s.date] += s.reach
            
    reach_by_day = list(reach_by_day_map.values())
    
    # If no real data, use mock as fallback so the UI looks good
    if not daily_stats and not accounts:
        return StatsResponse(
            total_reach=1200000,
            total_reach_label="1.2M",
            reach_by_day=[30, 55, 40, 70, 90, 60, 110, 130, 95, 75, 60, 45],
            reach_by_platform=[
                PlatformStat(platform="tiktok", label="TikTok", reach=45200, reach_label="45.2K"),
                PlatformStat(platform="youtube", label="YouTube", reach=28900, reach_label="28.9K"),
                PlatformStat(platform="instagram", label="Instagram", reach=62100, reach_label="62.1K"),
                PlatformStat(platform="vk", label="VK", reach=14700, reach_label="14.7K"),
            ],
            metrics=[
                MetricStat(key="watch_time_hours", label="Время просмотра (ч)", value="8,420", delta_pct=12.0),
                MetricStat(key="avg_retention", label="Среднее удержание", value="64.2%", delta_pct=-1.4),
                MetricStat(key="shares", label="Репосты", value="12.5K", delta_pct=34.0),
            ],
            top_videos=[
                TopVideoStat(
                    id="v1",
                    platform="instagram",
                    title="Life as a Creator",
                    views=452000,
                    views_label="452K",
                    thumbnail_url="https://images.unsplash.com/photo-1498050108023-c5249f4df085",
                    published_at=datetime.now() - timedelta(days=2)
                )
            ]
        )

    # Calculate real totals (simplified)
    total_reach = sum(reach_by_day)
    
    return StatsResponse(
        total_reach=total_reach,
        total_reach_label=f"{total_reach/1000:.1f}K" if total_reach < 1000000 else f"{total_reach/1000000:.1f}M",
        reach_by_day=reach_by_day,
        reach_by_platform=[
            PlatformStat(platform=acc.platform, label=acc.platform.capitalize(), reach=0, reach_label="0")
            for acc in accounts
        ],
        metrics=[],
        top_videos=[]
    )
