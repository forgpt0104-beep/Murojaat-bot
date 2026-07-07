"""Typed callback_data factories shared across inline keyboards."""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class LanguageCallback(CallbackData, prefix="lang"):
    code: str


class AttachMoreCallback(CallbackData, prefix="attach"):
    answer: str  # "yes" | "no"


class ConfirmCallback(CallbackData, prefix="confirm"):
    action: str
    answer: str  # "yes" | "no"


class PaginationCallback(CallbackData, prefix="page"):
    scope: str  # e.g. "my_appeals", "search", "export"
    page: int


class AppealViewCallback(CallbackData, prefix="appeal_view"):
    appeal_id: int
    page: int = 0


class AppealActionCallback(CallbackData, prefix="appeal_act"):
    action: str  # "reopen" | "close"
    appeal_id: int


class AdminMenuCallback(CallbackData, prefix="admin_menu"):
    action: str


class ExportFormatCallback(CallbackData, prefix="export"):
    fmt: str  # "csv" | "excel" | "pdf"


class SettingsCallback(CallbackData, prefix="settings"):
    key: str
