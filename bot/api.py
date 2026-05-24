import hashlib
import hmac
import json
import time
import logging
from typing import List, Optional
from urllib.parse import parse_qs
from datetime import date, datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from bot.config import config
from bot.database.requests import (
    get_user, add_user, get_or_create_daily_progress, update_shots, 
    update_upload_status, get_user_streak,
    add_video, get_user_videos, update_video_status,
    get_weekly_analytics, get_top_videos,
    get_user_ideas, add_idea, update_idea, delete_idea,
    get_studio_today, record_studio_action
)
from bot.database.models import SessionLocal, init_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Creator OS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ Database initialized successfully")

# --- Schemas ---

class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    platform: Optional[str] = None
    status: str = "backlog"
    scheduled_for: Optional[datetime] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class IdeaResponse(IdeaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StudioToday(BaseModel):
    recorded: int
    posted: int
    goal: int
    streak: int
    activity: List[int]

class AnalyticsPlatform(BaseModel):
    platform: str = "All"
    reach: int = 0
    growth: int = 0
    top_post: Optional[dict] = None

class AnalyticsResponse(BaseModel):
    platforms: List[AnalyticsPlatform]

class AuthResponse(BaseModel):
    id: int
    username: Optional[str] = None
    full_name: str
    streak: int
    is_new: bool = False

# --- Auth Dependency ---

def verify_tma_data(x_telegram_init_data: str = Header(None, alias="X-Telegram-Init-Data")):
    if not x_telegram_init_data:
        logger.warning("X-Telegram-Init-Data header missing")
        raise HTTPException(status_code=401, detail="X-Telegram-Init-Data header missing")
        
    init_data = x_telegram_init_data
    try:
        parsed_data = {k: v[0] for k, v in parse_qs(init_data).items()}
        
        if "hash" not in parsed_data:
            logger.warning("Missing hash in initData")
            raise HTTPException(status_code=401, detail="Missing hash")
        
        received_hash = parsed_data.pop("hash")
        # Build check string from ALL remaining parameters
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        secret_key = hmac.new(b"WebAppData", config.BOT_TOKEN.get_secret_value().encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(received_hash, expected_hash):
            logger.warning(f"Invalid hash. Check string: {data_check_string}")
            # If hash fails, it's definitely unauthorized
            raise HTTPException(status_code=401, detail="Invalid hash")
        
        # Check expiry (relaxed to 30 days for testing)
        auth_date = int(parsed_data.get("auth_date", 0))
        if auth_date > 0 and time.time() - auth_date > 86400 * 30:
            logger.warning(f"Data expired. auth_date: {auth_date}")
            raise HTTPException(status_code=401, detail="Data expired")
            
        user_data = json.loads(parsed_data["user"])
        return user_data
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Data parsing error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid data format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# --- Endpoints ---

@app.post("/auth/register", response_model=AuthResponse)
async def register(tg_user: dict = Depends(verify_tma_data)):
    try:
        user_id = tg_user["id"]
        username = tg_user.get("username")
        full_name = tg_user.get("first_name", "")
        if tg_user.get("last_name"):
            full_name += f" {tg_user['last_name']}"
            
        user = await get_user(user_id)
        is_new = False
        if not user:
            user = await add_user(user_id, username, full_name)
            is_new = True
            
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "streak": user.streak,
            "is_new": is_new
        }
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/me", response_model=AuthResponse)
async def auth_me(tg_user: dict = Depends(verify_tma_data)):
    user = await get_user(tg_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "streak": user.streak
    }

@app.get("/users/me", response_model=AuthResponse)
async def get_me(tg_user: dict = Depends(verify_tma_data)):
    user = await get_user(tg_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "streak": user.streak
    }

# --- Studio Endpoints (TanStack Start Expected) ---

@app.get("/studio/today", response_model=StudioToday)
async def studio_today(tg_user: dict = Depends(verify_tma_data)):
    return await get_studio_today(tg_user["id"])

@app.post("/studio/{kind}", response_model=StudioToday)
async def studio_action(kind: str, tg_user: dict = Depends(verify_tma_data)):
    if kind not in ["recorded", "posted"]:
        raise HTTPException(status_code=400, detail="Invalid action kind")
    return await record_studio_action(tg_user["id"], kind)

# --- Ideas Endpoints (TanStack Start Expected) ---

@app.get("/ideas", response_model=List[IdeaResponse])
async def list_ideas(tg_user: dict = Depends(verify_tma_data)):
    return await get_user_ideas(tg_user["id"])

@app.post("/ideas", response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, tg_user: dict = Depends(verify_tma_data)):
    return await add_idea(
        user_id=tg_user["id"],
        title=idea.title,
        description=idea.description,
        platform=idea.platform,
        status=idea.status,
        scheduled_for=idea.scheduled_for
    )

@app.patch("/ideas/{idea_id}", response_model=IdeaResponse)
async def patch_idea(idea_id: int, payload: IdeaUpdate, tg_user: dict = Depends(verify_tma_data)):
    idea = await update_idea(idea_id, tg_user["id"], **payload.dict(exclude_unset=True))
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@app.delete("/ideas/{idea_id}")
async def remove_idea(idea_id: int, tg_user: dict = Depends(verify_tma_data)):
    success = await delete_idea(idea_id, tg_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"ok": True}

# --- Analytics Endpoints ---

@app.get("/analytics", response_model=AnalyticsResponse)
async def analytics_overview(tg_user: dict = Depends(verify_tma_data)):
    # Mocking some data for the frontend to display something pretty
    return {
        "platforms": [
            {"platform": "YouTube", "reach": 1250, "growth": 12, "top_post": {"title": "Viral Shot 1", "views": 5000}},
            {"platform": "Instagram", "reach": 850, "growth": -5, "top_post": {"title": "Aesthetic Reel", "views": 2000}},
            {"platform": "TikTok", "reach": 3200, "growth": 45, "top_post": {"title": "Funny Trend", "views": 15000}},
        ]
    }

# Legacy support
@app.get("/api/me")
async def legacy_me(tg_user: dict = Depends(verify_tma_data)):
    user = await get_user(tg_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "telegram_id": user.id,
        "first_name": user.full_name,
        "username": user.username,
        "streak_days": user.streak
    }
