import json
import logging

import redis
from django.conf import settings

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL)
    return _redis_client


def notify_user(telegram_id: str | int, message: str, parse_mode: str = "HTML") -> bool:
    """Bot orqali Telegram foydalanuvchisiga xabar yuborish (Redis pub/sub)."""
    payload = json.dumps({
        "telegram_id": str(telegram_id),
        "message": message,
        "parse_mode": parse_mode,
    })
    try:
        _get_redis().publish("bot:notify", payload)
        logger.info("Notification published to telegram_id=%s", telegram_id)
        return True
    except Exception as exc:
        logger.error("Failed to publish notification to telegram_id=%s: %s", telegram_id, exc)
        return False
