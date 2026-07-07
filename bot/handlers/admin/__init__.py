"""Admin panel handlers (private chat only, IsAdminFilter enforced per-router)."""

from aiogram import Router

from bot.handlers.admin import ban, broadcast, export, panel, search, settings, statistics

router = Router(name="admin")
router.include_router(panel.router)
router.include_router(statistics.router)
router.include_router(broadcast.router)
router.include_router(search.router)
router.include_router(ban.router)
router.include_router(export.router)
router.include_router(settings.router)

__all__ = ["router"]
