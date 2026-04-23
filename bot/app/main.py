import asyncio
import json
import logging

import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.db.database import init_db
from app.logging import setup_logging
from app.middlewares.api_session import ApiSessionMiddleware
from app.routers import setup_routers


async def on_startup(bot: Bot):
    await init_db()
    for admin_id in settings.admins:
        try:
            await bot.send_message(admin_id, "✅ Bot ishga tushdi")
        except Exception as e:
            logging.error("Startup message failed for %s: %s", admin_id, e)


async def on_shutdown(bot: Bot):
    for admin_id in settings.admins:
        try:
            await bot.send_message(admin_id, "⛔️ Bot to'xtatildi")
        except Exception as e:
            logging.error("Shutdown message failed for %s: %s", admin_id, e)


async def redis_subscriber(bot: Bot):
    """Backend'dan Redis pub/sub orqali xabarlarni qabul qilib Telegram'ga yuboradi."""
    r = aioredis.from_url(settings.redis_url)
    pubsub = r.pubsub()
    await pubsub.subscribe("bot:notify")
    logging.info("Redis subscriber ready on channel: bot:notify")

    async for raw in pubsub.listen():
        if raw["type"] != "message":
            continue
        try:
            data = json.loads(raw["data"])
            await bot.send_message(
                chat_id=int(data["telegram_id"]),
                text=data["message"],
                parse_mode=data.get("parse_mode", "HTML"),
            )
            logging.info("Notification sent to telegram_id=%s", data["telegram_id"])
        except Exception as e:
            logging.error("Notification error: %s", e)


async def main():
    setup_logging(logging.INFO)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(setup_routers())

    api_middleware = ApiSessionMiddleware()
    dp.message.middleware(api_middleware)
    dp.callback_query.middleware(api_middleware)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
        redis_subscriber(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())
