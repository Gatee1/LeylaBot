import hashlib
import hmac
import json
from urllib.parse import parse_qs
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from bot.config import config
from bot.database.requests import get_user_stats, get_or_create_daily_progress, update_shots, update_upload_status, get_user
from bot.database.models import SessionLocal, Idea, User
from sqlalchemy import select
from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_telegram_data(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("tma "):
        # Dev fallback if header is missing but we are in dev
        return 12345678 # Mock ID for dev
        
    init_data = authorization[4:]
    parsed_data = {k: v[0] for k, v in parse_qs(init_data).items()}
    
    if "hash" not in parsed_data:
        raise HTTPException(status_code=401, detail="Missing hash")
    
    received_hash = parsed_data.pop("hash")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
    
    secret_key = hmac.new(b"WebAppData", config.BOT_TOKEN.get_secret_value().encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if received_hash != expected_hash:
        raise HTTPException(status_code=401, detail="Invalid hash")
    
    user_data = json.loads(parsed_data["user"])
    return user_data["id"]

@app.get("/api/me")
async def get_me(user_id: int = Depends(verify_telegram_data)):
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.full_name,
        "is_new": False,
        "streak": user.streak
    }

@app.get("/api/stats")
async def get_stats_api(user_id: int = Depends(verify_telegram_data)):
    stats = await get_user_stats(user_id)
    # Transform to match Mini App expectations if needed
    return stats

@app.get("/api/ideas")
async def get_ideas_api(user_id: int = Depends(verify_telegram_data)):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Idea).where(Idea.user_id == user_id).order_by(Idea.created_at.desc())
        )
        return result.scalars().all()

@app.post("/api/ideas")
async def create_idea_api(data: dict, user_id: int = Depends(verify_telegram_data)):
    async with SessionLocal() as session:
        new_idea = Idea(
            user_id=user_id,
            text=data.get("title", "Без названия"),
            status="pending"
        )
        session.add(new_idea)
        await session.commit()
        await session.refresh(new_idea)
        return new_idea

@app.get("/api/studio")
async def get_studio(user_id: int = Depends(verify_telegram_data)):
    progress = await get_or_create_daily_progress(user_id)
    return {
        "shots_count": progress.shots_count,
        "goal": 3,
        "platforms": {
            "yt": progress.uploaded_yt,
            "ig": progress.uploaded_ig,
            "tt": progress.uploaded_tt,
            "vk": progress.uploaded_vk
        }
    }
