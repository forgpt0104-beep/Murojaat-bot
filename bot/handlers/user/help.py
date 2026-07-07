"""Help menu."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.filters import IsPrivateChatFilter, TextEqualsKey
from bot.locales import i18n

router = Router(name="user_help")
router.message.filter(IsPrivateChatFilter())


@router.message(TextEqualsKey("btn_help"))
@router.message(Command("help"))
async def show_help(message: Message, lang: str) -> None:
    await message.answer(i18n.get(lang, "help_text"))
