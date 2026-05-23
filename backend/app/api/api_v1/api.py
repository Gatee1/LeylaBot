from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, studio, ideas, stats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/me", tags=["users"])
api_router.include_router(studio.router, prefix="/studio", tags=["studio"])
api_router.include_router(ideas.router, prefix="/ideas", tags=["ideas"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
