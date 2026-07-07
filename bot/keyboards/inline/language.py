"""Language selection inline keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import LanguageCallback

LANGUAGE_LABELS = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in LANGUAGE_LABELS.items():
        builder.button(text=label, callback_data=LanguageCallback(code=code))
    builder.adjust(1)
    return builder.as_markup()
