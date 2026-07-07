"""Persistent main-menu reply keyboard."""

from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.locales import i18n


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.get(lang, "btn_new_appeal"))
    builder.button(text=i18n.get(lang, "btn_my_appeals"))
    builder.button(text=i18n.get(lang, "btn_change_language"))
    builder.button(text=i18n.get(lang, "btn_help"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)
