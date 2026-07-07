"""Global error handler: logs every unhandled exception and replies with a friendly message."""

from __future__ import annotations

from aiogram import Bot, Router
from aiogram.types import ErrorEvent
from loguru import logger

from bot.locales import DEFAULT_LANGUAGE, i18n

router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent, bot: Bot, lang: str = DEFAULT_LANGUAGE) -> bool:
    """Catch-all handler so a single bad update never crashes the bot process.

    `lang` is populated from the same middleware chain (I18nMiddleware) that
    handlers use, so the failure message is shown in the user's own language
    instead of always falling back to English.
    """
    logger.opt(exception=event.exception).error(
        f"Unhandled exception while processing update {event.update.update_id}"
    )

    update = event.update
    chat_id = None
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None and update.callback_query.message is not None:
        chat_id = update.callback_query.message.chat.id

    if chat_id is not None:
        try:
            await bot.send_message(chat_id, i18n.get(lang, "error_generic"))
        except Exception:
            logger.exception("Failed to notify user about an unhandled error")

    return True
