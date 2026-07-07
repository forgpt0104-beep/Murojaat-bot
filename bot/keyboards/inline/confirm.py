"""Generic Yes/No confirmation inline keyboard."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import ConfirmCallback
from bot.locales import i18n


def confirm_keyboard(lang: str, action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get(lang, "btn_yes"),
        callback_data=ConfirmCallback(action=action, answer="yes"),
    )
    builder.button(
        text=i18n.get(lang, "btn_no"),
        callback_data=ConfirmCallback(action=action, answer="no"),
    )
    builder.adjust(2)
    return builder.as_markup()
