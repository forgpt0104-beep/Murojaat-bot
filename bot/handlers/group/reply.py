"""Detects employee replies inside the staff group and forwards them to the user."""

from __future__ import annotations

from aiogram import Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message
from loguru import logger

from bot.database.models.appeal import Appeal
from bot.database.uow import UnitOfWork
from bot.filters import IsReplyToAppealFilter, IsStaffGroupFilter
from bot.locales import i18n
from bot.services.appeal_service import AppealService

router = Router(name="group_reply")
router.message.filter(IsStaffGroupFilter())

GROUP_LANG = "en"


@router.message(IsReplyToAppealFilter())
async def on_employee_reply(message: Message, appeal: Appeal, uow: UnitOfWork) -> None:
    appeal_service = AppealService(uow, bot=message.bot)

    employee = message.from_user

    try:
        await appeal_service.handle_employee_reply(appeal, message, employee.id)
    except ValueError:
        await message.reply(i18n.get(GROUP_LANG, "new_appeal_unsupported_content"))
        return
    except TelegramForbiddenError:
        logger.warning(f"Could not deliver reply to user for appeal {appeal.formatted_number}")
        await message.reply(i18n.get(GROUP_LANG, "reply_failed"))
        return

    await message.reply(i18n.get(GROUP_LANG, "reply_sent_confirmation"))
