"""User-facing handlers (private chat). Router order matters: specific menu handlers
must be registered before the appeal flow's broad content catch-all so that pressing
a main-menu button always overrides an in-progress appeal composition.
"""

from aiogram import Router

from bot.handlers.user import appeal, help, language, my_appeals, start

router = Router(name="user")
router.include_router(start.router)
router.include_router(language.router)
router.include_router(my_appeals.router)
router.include_router(help.router)
router.include_router(appeal.router)

__all__ = ["router"]
