"""Filter matching a message's text against a localized string for the current user."""

from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.locales import i18n


class TextEqualsKey(BaseFilter):
    """Passes if `message.text` equals the translation of `key` in the current language."""

    def __init__(self, key: str) -> None:
        self.key = key

    async def __call__(self, message: Message, lang: str) -> bool:
        if message.text is None:
            return False
        return message.text == i18n.get(lang, self.key)
