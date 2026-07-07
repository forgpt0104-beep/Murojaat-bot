"""Inline keyboards for the admin panel."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callback_data import AdminMenuCallback, ExportFormatCallback
from bot.locales import i18n


def admin_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get(lang, "btn_admin_stats"),
        callback_data=AdminMenuCallback(action="stats"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_broadcast"),
        callback_data=AdminMenuCallback(action="broadcast"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_search"),
        callback_data=AdminMenuCallback(action="search"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_ban"),
        callback_data=AdminMenuCallback(action="ban"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_unban"),
        callback_data=AdminMenuCallback(action="unban"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_export"),
        callback_data=AdminMenuCallback(action="export"),
    )
    builder.button(
        text=i18n.get(lang, "btn_admin_settings"),
        callback_data=AdminMenuCallback(action="settings"),
    )
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def export_format_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="CSV", callback_data=ExportFormatCallback(fmt="csv"))
    builder.button(text="Excel", callback_data=ExportFormatCallback(fmt="excel"))
    builder.button(text="PDF", callback_data=ExportFormatCallback(fmt="pdf"))
    builder.adjust(3)
    return builder.as_markup()
