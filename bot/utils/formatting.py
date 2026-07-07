"""Text formatting helpers: group appeal cards, user-facing messages, dates."""

from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from bot.config import settings
from bot.database.models.appeal import Appeal
from bot.database.models.enums import AppealStatus, LanguageEnum
from bot.database.models.user import User
from bot.locales import i18n

LANGUAGE_DISPLAY_NAMES = {
    LanguageEnum.UZ: "Uzbek 🇺🇿",
    LanguageEnum.RU: "Russian 🇷🇺",
    LanguageEnum.EN: "English 🇬🇧",
}

STATUS_KEY_MAP = {
    AppealStatus.NEW: "status_new",
    AppealStatus.IN_PROCESS: "status_in_process",
    AppealStatus.ANSWERED: "status_answered",
    AppealStatus.CLOSED: "status_closed",
}


def local_now() -> datetime:
    return datetime.now(ZoneInfo(settings.TIMEZONE))


def format_datetime(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    local_dt = dt.astimezone(ZoneInfo(settings.TIMEZONE))
    return local_dt.strftime("%Y-%m-%d %H:%M")


def status_label(lang: str, status: AppealStatus) -> str:
    return i18n.get(lang, STATUS_KEY_MAP[status])


def build_group_appeal_card(appeal: Appeal, user: User, text_preview: str) -> str:
    """Build the beautiful staff-group card shown for a new appeal."""
    username_display = f"@{user.username}" if user.username else "—"
    language_display = LANGUAGE_DISPLAY_NAMES.get(appeal.language, appeal.language.value)

    lines = [
        "━━━━━━━━━━━━━━━━━━",
        "📨 <b>NEW APPEAL</b>",
        "",
        "🆔 <b>ID:</b>",
        appeal.formatted_number,
        "",
        "🌐 <b>Language:</b>",
        language_display,
        "",
        "📅 <b>Date:</b>",
        format_datetime(appeal.created_at),
        "",
        "👤 <b>User:</b>",
        f"Full Name: {escape(user.full_name)}",
        f"Username: {escape(username_display)}",
        f"Telegram ID: <code>{user.telegram_id}</code>",
        "",
        "💬 <b>Appeal:</b>",
        escape(text_preview) if text_preview else "(no text, see attachments below)",
        "━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)


def build_response_header(lang: str, appeal: Appeal) -> str:
    return i18n.get(lang, "response_header", appeal_number=appeal.appeal_number)


def build_my_appeals_item(lang: str, appeal: Appeal) -> str:
    return i18n.get(
        lang,
        "my_appeals_item",
        appeal_number=appeal.appeal_number,
        status=status_label(lang, appeal.status),
        date=format_datetime(appeal.created_at),
    )


def build_appeal_detail_header(lang: str, appeal: Appeal) -> str:
    return i18n.get(
        lang,
        "appeal_detail_header",
        appeal_number=appeal.appeal_number,
        date=format_datetime(appeal.created_at),
        status=status_label(lang, appeal.status),
    )
