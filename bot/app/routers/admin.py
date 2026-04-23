from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api.client import BackendClient
from app.filters.is_admin import IsAdmin
from app.keyboards.admin_kb import admin_menu_kb

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer("🔧 Admin paneli:", reply_markup=admin_menu_kb())


@router.message(Command("health"))
async def cmd_health(message: Message, backend: BackendClient):
    ok = await backend.health()
    status = "✅ Backend ishlayapti" if ok else "❌ Backend javob bermayapti"
    await message.answer(status)
