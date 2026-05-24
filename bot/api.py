import hashlib
import hmac
import json
import time
from typing import List, Optional
from urllib.parse import parse_qs
from datetime import date, datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from bot.config import config
from bot.database.requests import (
    get_user, add_user, get_or_create_daily_progress, update_shots, 
    update_upload_status, get_user_stats, get_user_streak,
    add_video, get_user_videos, update_video_status,
    get_weekly_analytics, get_top_videos
)
from bot.database.models import SessionLocal, init_db

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

class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

class AuthResponse(BaseModel):
    id: int
    username: Optional[str] = None
    full_name: str
    streak: int
    is_new: bool = False

class ProgressUpdate(BaseModel):
    shots_count: Optional[int] = None
    platform: Optional[str] = None # yt, ig, tt, vk
    status: Optional[bool] = None

class VideoCreate(BaseModel):
    title: str
    status: str = "recorded"
    platform: Optional[str] = None

class VideoResponse(BaseModel):
    id: int
    title: str
    status: str
    platform: Optional[str]
    created_at: datetime
    posted_at: Optional[datetime]

class StreakResponse(BaseModel):
    streak: int
    max_streak: int

class AnalyticsWeekly(BaseModel):
    total_shots: int
    total_posted: int
    daily_stats: List[dict]

# --- Auth Dependency ---

def verify_tma_data(x_telegram_init_data: str = Header(None, alias="X-Telegram-Init-Data")):
    if not x_telegram_init_data:
        # Dev fallback - enable only for local testing if needed
        # return {"id": 12345678, "first_name": "Dev", "username": "dev_user"}
        raise HTTPException(status_code=401, detail="X-Telegram-Init-Data header missing")
        
    init_data = x_telegram_init_data
    parsed_data = {k: v[0] for k, v in parse_qs(init_data).items()}
    
    if "hash" not in parsed_data:
        raise HTTPException(status_code=401, detail="Missing hash")
    
    received_hash = parsed_data.pop("hash")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
    
    secret_key = hmac.new(b"WebAppData", config.BOT_TOKEN.get_secret_value().encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(received_hash, expected_hash):
        raise HTTPException(status_code=401, detail="Invalid hash")
    
    # Check expiry (24h)
    if time.time() - int(parsed_data.get("auth_date", 0)) > 86400:
        raise HTTPException(status_code=401, detail="Data expired")
        
    user_data = json.loads(parsed_data["user"])
    return user_data

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

@app.post("/progress/daily")
async def update_daily_progress(
    update: ProgressUpdate, 
    tg_user: dict = Depends(verify_tma_data)
):
    try:
        user_id = tg_user["id"]
        if update.shots_count is not None:
            await update_shots(user_id, update.shots_count)
        
        if update.platform and update.status is not None:
            await update_upload_status(user_id, update.platform, update.status)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/daily")
async def get_daily_progress(tg_user: dict = Depends(verify_tma_data)):
    progress = await get_or_create_daily_progress(tg_user["id"])
    return {
        "date": progress.date.isoformat(),
        "shots_count": progress.shots_count,
        "platforms": {
            "yt": progress.uploaded_yt,
            "ig": progress.uploaded_ig,
            "tt": progress.uploaded_tt,
            "vk": progress.uploaded_vk
        }
    }

@app.get("/progress/streak", response_model=StreakResponse)
async def get_streak(tg_user: dict = Depends(verify_tma_data)):
    return await get_user_streak(tg_user["id"])

@app.post("/videos", response_model=VideoResponse)
async def create_video(video: VideoCreate, tg_user: dict = Depends(verify_tma_data)):
    try:
        return await add_video(tg_user["id"], video.title, video.status, video.platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos", response_model=List[VideoResponse])
async def get_videos(tg_user: dict = Depends(verify_tma_data)):
    return await get_user_videos(tg_user["id"])

@app.patch("/videos/{video_id}/status", response_model=VideoResponse)
async def patch_video_status(
    video_id: int, 
    status: str = Body(..., embed=True), 
    tg_user: dict = Depends(verify_tma_data)
):
    video = await update_video_status(video_id, status)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@app.get("/analytics/week", response_model=AnalyticsWeekly)
async def get_week_analytics(tg_user: dict = Depends(verify_tma_data)):
    return await get_weekly_analytics(tg_user["id"])

@app.get("/analytics/top", response_model=List[VideoResponse])
async def get_top(tg_user: dict = Depends(verify_tma_data)):
    return await get_top_videos(tg_user["id"])

# Legacy/Compatibility
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
