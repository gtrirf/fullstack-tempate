from aiogram import Router

from app.routers.admin import router as admin_router
from app.routers.start import router as start_router


def setup_routers() -> Router:
    main = Router()
    main.include_router(admin_router)  # admin birinchi — filter prioriteti
    main.include_router(start_router)
    return main
