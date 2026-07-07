"""Staff-group handlers. `commands` must be registered before `reply` so that
/status, /close, /reopen are treated as commands and not accidentally forwarded
to the user as a literal reply.
"""

from aiogram import Router

from bot.handlers.group import commands, reply

router = Router(name="group")
router.include_router(commands.router)
router.include_router(reply.router)

__all__ = ["router"]
