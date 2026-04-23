from .queries import get_bot_user, upsert_bot_user


async def get_or_create_user(telegram_id: int, username: str | None, language_code: str = "uz") -> dict:
    user = await get_bot_user(telegram_id)
    if not user:
        await upsert_bot_user(telegram_id, username, language_code)
        user = await get_bot_user(telegram_id)
    return user
