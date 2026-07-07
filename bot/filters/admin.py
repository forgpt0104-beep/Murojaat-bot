"""Filter that only allows administrators (super admin or DB-registered admins)."""

from __future__ import annotations

from typing import Any, Dict, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.database.uow import UnitOfWork


class IsAdminFilter(BaseFilter):
    """Passes only if the sender is the super admin or an active Admin row."""

    async def __call__(
        self, event: Union[Message, CallbackQuery], uow: UnitOfWork
    ) -> Union[bool, Dict[str, Any]]:
        user = event.from_user
        if user is None:
            return False

        if user.id == settings.SUPER_ADMIN_ID:
            return True

        admin = await uow.admins.get_by_telegram_id(user.id)
        return bool(admin and admin.is_active)
