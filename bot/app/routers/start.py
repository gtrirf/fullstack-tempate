from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api.client import BackendClient
from app.db.helper import get_or_create_user
from app.keyboards.user_kb import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, backend: BackendClient):
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        language_code=message.from_user.language_code or "uz",
    )

    backend_user = await backend.get_user(message.from_user.id)

    if backend_user:
        name = backend_user.get("username") or message.from_user.first_name
        text = (
            f"Xush kelibsiz, <b>{name}</b>!\n\n"
            "Akkauntingiz muvaffaqiyatli bog'langan. ✅"
        )
    else:
        text = (
            f"Salom, <b>{message.from_user.first_name}</b>! 👋\n\n"
            "Akkauntingizni bog'lash uchun saytda profilingizga kiring va "
            "<b>Telegram</b> bo'limidan ulang."
        )

    await message.answer(text, reply_markup=main_menu_kb())
