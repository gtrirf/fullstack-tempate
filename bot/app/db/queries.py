from .database import get_db


async def upsert_bot_user(telegram_id: int, username: str | None, language_code: str = "uz"):
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO bot_users (telegram_id, username, language_code)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username
            """,
            (telegram_id, username, language_code),
        )
        await db.commit()


async def get_bot_user(telegram_id: int) -> dict | None:
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM bot_users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def set_language(telegram_id: int, lang: str):
    async with get_db() as db:
        await db.execute(
            "UPDATE bot_users SET language_code = ? WHERE telegram_id = ?",
            (lang, telegram_id),
        )
        await db.commit()


async def set_blocked(telegram_id: int, blocked: bool):
    async with get_db() as db:
        await db.execute(
            "UPDATE bot_users SET is_blocked = ? WHERE telegram_id = ?",
            (int(blocked), telegram_id),
        )
        await db.commit()
