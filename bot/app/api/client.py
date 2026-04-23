import logging

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class BackendClient:
    """Backend REST API bilan ishlash uchun client."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self._base = settings.backend_url.rstrip("/")
        self._bot_headers = {"X-Bot-Secret": settings.bot_secret}

    async def get_user(self, telegram_id: int) -> dict | None:
        """Telegram ID orqali backend'dan user ma'lumotlarini olish."""
        try:
            async with self.session.get(
                f"{self._base}/api/users/by-telegram/{telegram_id}/",
                headers=self._bot_headers,
            ) as r:
                if r.status == 200:
                    return await r.json()
                return None
        except Exception as exc:
            logger.error("get_user failed for telegram_id=%s: %s", telegram_id, exc)
            return None

    async def health(self) -> bool:
        """Backend health check."""
        try:
            async with self.session.get(f"{self._base}/api/health/") as r:
                return r.status == 200
        except Exception:
            return False
