"""Filter detecting that a group message is an employee reply to an appeal card."""

from __future__ import annotations

from typing import Any, Dict, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import settings
from bot.database.models.appeal import Appeal
from bot.database.uow import UnitOfWork


class IsReplyToAppealFilter(BaseFilter):
    """Passes if `message` is a reply (in the staff group) to a known appeal message.

    On success, injects `appeal` into the handler's data so the handler doesn't
    need to re-fetch it.
    """

    async def __call__(
        self, message: Message, uow: UnitOfWork
    ) -> Union[bool, Dict[str, Any]]:
        if message.chat.id != settings.GROUP_ID:
            return False

        if message.reply_to_message is None:
            return False

        replied_message_id = message.reply_to_message.message_id

        appeal = await uow.appeals.get_by_group_message(message.chat.id, replied_message_id)
        if appeal is not None:
            return {"appeal": appeal}

        appeal_message = await uow.appeal_messages.get_by_group_message(
            message.chat.id, replied_message_id
        )
        if appeal_message is not None:
            appeal = await uow.appeals.get_by_id(appeal_message.appeal_id)
            if appeal is not None:
                return {"appeal": appeal}

        return False
