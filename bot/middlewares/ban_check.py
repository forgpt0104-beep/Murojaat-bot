"""Blocks banned users from interacting with the bot in private chats."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.locales import i18n


class BanCheckMiddleware(BaseMiddleware):
    """Short-circuits handling for banned users (private chats only)."""

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

        if chat is None or chat.type != "private":
            return await handler(event, data)

        db_user = data.get("db_user")
        if db_user is not None and db_user.is_banned:
            lang = data.get("lang", "en")
            text = i18n.get(lang, "banned_message")
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            return None

        return await handler(event, data)
