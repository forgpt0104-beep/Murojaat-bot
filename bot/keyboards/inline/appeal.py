"""Inline keyboards for the appeal creation and viewing flows."""

from __future__ import annotations

from typing import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.appeal import Appeal
from bot.database.models.enums import AppealStatus
from bot.keyboards.callback_data import (
    AppealActionCallback,
    AppealViewCallback,
    AttachMoreCallback,
    PaginationCallback,
)
from bot.locales import i18n


def attach_more_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get(lang, "btn_yes"), callback_data=AttachMoreCallback(answer="yes")
    )
    builder.button(
        text=i18n.get(lang, "btn_no"), callback_data=AttachMoreCallback(answer="no")
    )
    builder.adjust(2)
    return builder.as_markup()


def my_appeals_keyboard(
    lang: str,
    appeals: Sequence[Appeal],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    status_key_map = {
        AppealStatus.NEW: "status_new",
        AppealStatus.IN_PROCESS: "status_in_process",
        AppealStatus.ANSWERED: "status_answered",
        AppealStatus.CLOSED: "status_closed",
    }

    rows_builder = InlineKeyboardBuilder()
    for appeal in appeals:
        status_label = i18n.get(lang, status_key_map[appeal.status])
        rows_builder.button(
            text=f"{appeal.formatted_number} | {status_label}",
            callback_data=AppealViewCallback(appeal_id=appeal.id, page=page),
        )
    rows_builder.adjust(1)

    nav_builder = InlineKeyboardBuilder()
    if page > 0:
        nav_builder.button(
            text=i18n.get(lang, "btn_prev"),
            callback_data=PaginationCallback(scope="my_appeals", page=page - 1),
        )
    if page < total_pages - 1:
        nav_builder.button(
            text=i18n.get(lang, "btn_next"),
            callback_data=PaginationCallback(scope="my_appeals", page=page + 1),
        )
    nav_builder.adjust(2)

    return rows_builder.attach(nav_builder).as_markup()


def appeal_detail_keyboard(lang: str, appeal: Appeal, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if appeal.status == AppealStatus.CLOSED:
        builder.button(
            text=i18n.get(lang, "btn_reopen"),
            callback_data=AppealActionCallback(action="reopen", appeal_id=appeal.id),
        )
    builder.button(
        text=i18n.get(lang, "btn_back"),
        callback_data=PaginationCallback(scope="my_appeals", page=page),
    )
    builder.adjust(1)
    return builder.as_markup()
