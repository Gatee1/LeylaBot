from abc import ABC, abstractmethod
from typing import Any, Dict, List
import httpx
from app.core.logging import logger


class BaseSocialService(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.client = httpx.AsyncClient(timeout=10.0)

    @abstractmethod
    async def get_user_stats(self, access_token: str) -> Dict[str, Any]:
        """Fetch user stats from platform API."""
        pass

    @abstractmethod
    async def get_top_videos(self, access_token: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch top videos from platform API."""
        pass

    async def close(self):
        await self.client.aclose()
