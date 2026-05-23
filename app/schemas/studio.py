from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class GoalSchema(BaseModel):
    key: str
    label: str
    value: int
    total: int


class IdeaSchema(BaseModel):
    id: uuid.UUID
    title: str
    platform: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudioResponse(BaseModel):
    goals: List[GoalSchema]
    activity: List[int]
    ideas: List[IdeaSchema]


class IdeaCreateRequest(BaseModel):
    title: str
    platform: str


class IdeaUpdateRequest(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None


class PlatformStat(BaseModel):
    platform: str
    label: str
    reach: int
    reach_label: str


class MetricStat(BaseModel):
    key: str
    label: str
    value: str
    delta_pct: float


class TopVideoStat(BaseModel):
    id: str
    platform: str
    title: str
    views: int
    views_label: str
    thumbnail_url: str
    published_at: datetime


class StatsResponse(BaseModel):
    total_reach: int
    total_reach_label: str
    reach_by_day: List[int]
    reach_by_platform: List[PlatformStat]
    metrics: List[MetricStat]
    top_videos: List[TopVideoStat]
