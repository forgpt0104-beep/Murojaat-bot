"""Inline keyboards package."""

from bot.keyboards.inline.admin import admin_panel_keyboard, export_format_keyboard
from bot.keyboards.inline.appeal import (
    appeal_detail_keyboard,
    attach_more_keyboard,
    my_appeals_keyboard,
)
from bot.keyboards.inline.confirm import confirm_keyboard
from bot.keyboards.inline.language import language_keyboard
from bot.keyboards.inline.pagination import search_results_keyboard

__all__ = [
    "language_keyboard",
    "attach_more_keyboard",
    "my_appeals_keyboard",
    "appeal_detail_keyboard",
    "confirm_keyboard",
    "admin_panel_keyboard",
    "export_format_keyboard",
    "search_results_keyboard",
]
