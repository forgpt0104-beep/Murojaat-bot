"""Simple JSON-based i18n loader with fallback to English."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger

LOCALES_DIR = Path(__file__).resolve().parent
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("uz", "ru", "en")


class I18n:
    """Loads locale JSON files once and exposes a `.get()` translation helper."""

    def __init__(self) -> None:
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_all()

    def _load_all(self) -> None:
        for lang in SUPPORTED_LANGUAGES:
            path = LOCALES_DIR / f"{lang}.json"
            with path.open("r", encoding="utf-8") as f:
                self._translations[lang] = json.load(f)

    def get(self, lang: str, key: str, **kwargs: Any) -> str:
        """Return the translated, formatted string for `key` in `lang`."""
        lang = lang if lang in self._translations else DEFAULT_LANGUAGE
        translations = self._translations.get(lang, {})
        template = translations.get(key)

        if template is None:
            template = self._translations[DEFAULT_LANGUAGE].get(key)

        if template is None:
            logger.warning(f"Missing translation key '{key}' for language '{lang}'")
            return key

        if kwargs:
            try:
                return template.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                logger.exception(f"Failed to format translation key '{key}'")
                return template

        return template


i18n = I18n()


def _(lang: str, key: str, **kwargs: Any) -> str:
    """Shorthand translation function."""
    return i18n.get(lang, key, **kwargs)
