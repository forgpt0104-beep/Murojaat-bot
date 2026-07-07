"""Input validation and parsing helpers for admin search/ban commands."""

from __future__ import annotations

import re
from typing import Optional

USERNAME_RE = re.compile(r"^@?[A-Za-z0-9_]{5,32}$")


def parse_telegram_id(raw: str) -> Optional[int]:
    """Parse a raw string into a Telegram user id, or None if not a valid id."""
    raw = raw.strip()
    if raw.lstrip("-").isdigit():
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def parse_username(raw: str) -> Optional[str]:
    """Parse a raw string into a bare username (without '@'), or None."""
    raw = raw.strip()
    if USERNAME_RE.match(raw):
        return raw.lstrip("@")
    return None


def sanitize_search_query(raw: str, max_length: int = 128) -> str:
    """Trim and cap the length of a free-text search query to avoid abuse."""
    return raw.strip()[:max_length]


def is_valid_phone(raw: str) -> bool:
    digits = re.sub(r"\D", "", raw)
    return 7 <= len(digits) <= 15
