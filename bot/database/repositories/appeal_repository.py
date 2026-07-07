"""Repository for Appeal model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from bot.database.models.appeal import Appeal
from bot.database.models.enums import AppealStatus, LanguageEnum
from bot.database.models.user import User
from bot.database.repositories.base import BaseRepository


class AppealRepository(BaseRepository[Appeal]):
    model = Appeal

    async def create_appeal(self, user_id: int, language: LanguageEnum) -> Appeal:
        appeal = Appeal(user_id=user_id, language=language, status=AppealStatus.NEW)
        self.session.add(appeal)
        await self.session.flush()
        await self.session.refresh(appeal)
        return appeal

    async def get_by_id(self, obj_id: int) -> Optional[Appeal]:
        result = await self.session.execute(
            select(Appeal).options(joinedload(Appeal.user)).where(Appeal.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_by_appeal_number(self, appeal_number: int) -> Optional[Appeal]:
        result = await self.session.execute(
            select(Appeal)
            .options(joinedload(Appeal.user))
            .where(Appeal.appeal_number == appeal_number)
        )
        return result.scalar_one_or_none()

    async def get_by_group_message(
        self, chat_id: int, message_id: int
    ) -> Optional[Appeal]:
        # In basic (non-super) Telegram groups, message_id is not guaranteed to be
        # globally unique across bot identities, so more than one Appeal can end up
        # with the same (group_chat_id, group_message_id) pair. Prefer the most
        # recently created match instead of raising on ambiguity.
        result = await self.session.execute(
            select(Appeal)
            .options(joinedload(Appeal.user))
            .where(
                Appeal.group_chat_id == chat_id,
                Appeal.group_message_id == message_id,
            )
            .order_by(Appeal.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def set_group_message(
        self, appeal: Appeal, chat_id: int, message_id: int
    ) -> Appeal:
        appeal.group_chat_id = chat_id
        appeal.group_message_id = message_id
        await self.session.flush()
        return appeal

    async def set_status(self, appeal: Appeal, status: AppealStatus) -> Appeal:
        appeal.status = status
        await self.session.flush()
        return appeal

    async def set_summary_text(self, appeal: Appeal, text: str) -> Appeal:
        appeal.summary_text = text
        await self.session.flush()
        return appeal

    async def get_user_appeals(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> Sequence[Appeal]:
        result = await self.session.execute(
            select(Appeal)
            .where(Appeal.user_id == user_id)
            .order_by(Appeal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def count_user_appeals(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Appeal.id)).where(Appeal.user_id == user_id)
        )
        return int(result.scalar_one())

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(Appeal.id)))
        return int(result.scalar_one())

    async def count_by_status(self, status: AppealStatus) -> int:
        result = await self.session.execute(
            select(func.count(Appeal.id)).where(Appeal.status == status)
        )
        return int(result.scalar_one())

    async def count_created_since(self, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count(Appeal.id)).where(Appeal.created_at >= since)
        )
        return int(result.scalar_one())

    async def count_by_language(self) -> dict[str, int]:
        result = await self.session.execute(
            select(Appeal.language, func.count(Appeal.id)).group_by(Appeal.language)
        )
        return {
            str(lang.value if hasattr(lang, "value") else lang): count
            for lang, count in result.all()
        }

    @staticmethod
    def _search_conditions(query: str):
        conditions = [
            User.full_name.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%"),
            User.phone_number.ilike(f"%{query}%"),
        ]
        cleaned = query.lstrip("#")
        if cleaned.isdigit():
            conditions.append(Appeal.appeal_number == int(cleaned))
        if query.lstrip("-").isdigit():
            conditions.append(User.telegram_id == int(query))
        return conditions

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> Sequence[Appeal]:
        stmt = (
            select(Appeal)
            .join(User, Appeal.user_id == User.id)
            .options(joinedload(Appeal.user))
            .where(or_(*self._search_conditions(query)))
            .order_by(Appeal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def count_search(self, query: str) -> int:
        stmt = (
            select(func.count(Appeal.id))
            .select_from(Appeal)
            .join(User, Appeal.user_id == User.id)
            .where(or_(*self._search_conditions(query)))
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_recent(self, limit: int = 20, offset: int = 0) -> Sequence[Appeal]:
        result = await self.session.execute(
            select(Appeal)
            .options(joinedload(Appeal.user))
            .order_by(Appeal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    async def list_all_for_export(self) -> Sequence[Appeal]:
        result = await self.session.execute(
            select(Appeal).options(joinedload(Appeal.user)).order_by(Appeal.id)
        )
        return result.unique().scalars().all()
