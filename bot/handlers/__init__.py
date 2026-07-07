"""Root handlers package: aggregates the user, group and admin routers."""

from aiogram import Router

from bot.handlers import admin, errors, group, user

router = Router(name="root")
router.include_router(errors.router)
router.include_router(admin.router)
router.include_router(group.router)
router.include_router(user.router)

__all__ = ["router"]
