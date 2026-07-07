"""Logs every incoming update for auditing purposes."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Emits a structured log line for every processed Message/CallbackQuery."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        user_id = user.id if user else "unknown"

        if isinstance(event, Message):
            logger.bind(user_id=user_id).info(
                f"Message from {user_id} in chat {event.chat.id} ({event.chat.type}): "
                f"content_type={event.content_type}"
            )
        elif isinstance(event, CallbackQuery):
            logger.bind(user_id=user_id).info(
                f"CallbackQuery from {user_id}: data={event.data}"
            )

        return await handler(event, data)
