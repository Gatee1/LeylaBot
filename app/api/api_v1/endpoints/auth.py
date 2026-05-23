from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import TelegramAuthRequest, Token
from app.services.user_service import UserService
from app.core.security import verify_init_data, create_access_token, create_refresh_token
from app.core.logging import logger

router = APIRouter()


@router.post("/telegram", response_model=Token)
async def auth_telegram(
    request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user via Telegram WebApp initData.
    """
    try:
        user_data = verify_init_data(request.init_data)
        user_service = UserService(db)
        user, is_new = await user_service.get_or_create_user(user_data)
        
        access_token = create_access_token(user.telegram_id)
        refresh_token = create_refresh_token(user.telegram_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Auth failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )
