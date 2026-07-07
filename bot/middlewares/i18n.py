"""Resolves the current user's language and injects it (and the User row) into handler data."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from bot.database.uow import UnitOfWork
from bot.locales import DEFAULT_LANGUAGE


class I18nMiddleware(BaseMiddleware):
    """Sets `data["lang"]` and `data["db_user"]` based on the stored User, if any."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        telegram_user = data.get("event_from_user")
        uow: Optional[UnitOfWork] = data.get("uow")

        lang = DEFAULT_LANGUAGE
        db_user = None

        if uow is not None and telegram_user is not None:
            db_user = await uow.users.get_by_telegram_id(telegram_user.id)
            if db_user is not None:
                lang = db_user.language.value

        data["lang"] = lang
        data["db_user"] = db_user

        return await handler(event, data)
