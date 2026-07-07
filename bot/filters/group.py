"""Filters restricting handlers to the configured staff group or private chats."""

from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import settings


class IsStaffGroupFilter(BaseFilter):
    """Passes only if the message was sent in the configured staff group."""

    async def __call__(self, message: Message) -> bool:
        return message.chat.id == settings.GROUP_ID


class IsPrivateChatFilter(BaseFilter):
    """Passes only for private (1-to-1) chats with the bot."""

    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"
