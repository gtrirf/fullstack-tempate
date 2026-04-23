import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path

DB_PATH = Path("data/bot.db")


@asynccontextmanager
async def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    async with get_db() as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS bot_users (
                telegram_id   INTEGER PRIMARY KEY,
                username      TEXT,
                language_code TEXT    DEFAULT 'uz',
                is_blocked    BOOLEAN DEFAULT 0,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()
