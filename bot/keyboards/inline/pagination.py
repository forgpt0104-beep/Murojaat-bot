"""Generic paginated list keyboard, used for admin search results."""

from __future__ import annotations

from typing import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.appeal import Appeal
from bot.keyboards.callback_data import AppealViewCallback, PaginationCallback
from bot.locales import i18n


def search_results_keyboard(
    lang: str,
    appeals: Sequence[Appeal],
    page: int,
    total_pages: int,
    scope: str = "search",
) -> InlineKeyboardMarkup:
    rows_builder = InlineKeyboardBuilder()
    for appeal in appeals:
        label = f"{appeal.formatted_number} | {appeal.user.full_name}"
        rows_builder.button(
            text=label,
            callback_data=AppealViewCallback(appeal_id=appeal.id, page=page),
        )
    rows_builder.adjust(1)

    nav_builder = InlineKeyboardBuilder()
    if page > 0:
        nav_builder.button(
            text=i18n.get(lang, "btn_prev"),
            callback_data=PaginationCallback(scope=scope, page=page - 1),
        )
    if page < total_pages - 1:
        nav_builder.button(
            text=i18n.get(lang, "btn_next"),
            callback_data=PaginationCallback(scope=scope, page=page + 1),
        )
    nav_builder.adjust(2)

    return rows_builder.attach(nav_builder).as_markup()
