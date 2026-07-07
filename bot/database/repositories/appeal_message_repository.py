"""Repository for AppealMessage model."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select

from bot.database.models.appeal_message import AppealMessage
from bot.database.repositories.base import BaseRepository


class AppealMessageRepository(BaseRepository[AppealMessage]):
    model = AppealMessage

    async def get_by_group_message(
        self, chat_id: int, message_id: int
    ) -> Optional[AppealMessage]:
        # See AppealRepository.get_by_group_message: (chat_id, message_id) is not
        # guaranteed unique in basic (non-super) groups, so pick the newest match.
        result = await self.session.execute(
            select(AppealMessage)
            .where(
                AppealMessage.group_chat_id == chat_id,
                AppealMessage.group_message_id == message_id,
            )
            .order_by(AppealMessage.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_user_message(
        self, chat_id: int, message_id: int
    ) -> Optional[AppealMessage]:
        result = await self.session.execute(
            select(AppealMessage)
            .where(
                AppealMessage.user_chat_id == chat_id,
                AppealMessage.user_message_id == message_id,
            )
            .order_by(AppealMessage.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def list_by_appeal(self, appeal_id: int) -> Sequence[AppealMessage]:
        result = await self.session.execute(
            select(AppealMessage)
            .where(AppealMessage.appeal_id == appeal_id)
            .order_by(AppealMessage.id)
        )
        return result.scalars().all()
