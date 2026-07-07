"""Root handlers package: aggregates the user, group and admin routers.

`user` is included before `admin` so that a main-menu button press (e.g.
"My Appeals") always takes priority over a leftover admin FSM state (e.g. the
admin tapped "Search" but never finished typing a query) - otherwise the next
free-text handler still "waiting" in the admin router would swallow it first.
"""

from aiogram import Router

from bot.handlers import admin, errors, group, user

router = Router(name="root")
router.include_router(errors.router)
router.include_router(group.router)
router.include_router(user.router)
router.include_router(admin.router)

__all__ = ["router"]
