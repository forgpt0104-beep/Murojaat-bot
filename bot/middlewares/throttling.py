"""Simple per-user flood control (rate limiting) for private chats."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from cachetools import TTLCache
from loguru import logger

from bot.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    """Drops updates from a user that arrive faster than `THROTTLE_RATE_LIMIT` seconds apart."""

    def __init__(self) -> None:
        self._cache: TTLCache = TTLCache(maxsize=50_000, ttl=settings.THROTTLE_RATE_LIMIT)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat = None
        if isinstance(event, Message):
            chat = event.chat
        elif isinstance(event, CallbackQuery) and event.message is not None:
            chat = event.message.chat

        # Only throttle private chats; staff activity in the group must never be dropped.
        if chat is None or chat.type != "private":
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        if user.id in self._cache:
            logger.debug(f"Throttled update from user {user.id}")
            if isinstance(event, CallbackQuery):
                await event.answer()
            return None

        self._cache[user.id] = True
        return await handler(event, data)
