import aiohttp
from aiogram import BaseMiddleware

from app.api.client import BackendClient


class ApiSessionMiddleware(BaseMiddleware):
    """Har bir handler uchun aiohttp session va BackendClient inject qiladi."""

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def __call__(self, handler, event, data):
        session = self._get_session()
        data["backend"] = BackendClient(session)
        return await handler(event, data)
