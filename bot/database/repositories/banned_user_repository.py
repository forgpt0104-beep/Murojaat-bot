"""Repository for BannedUser model."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select

from bot.database.models.banned_user import BannedUser
from bot.database.repositories.base import BaseRepository


class BannedUserRepository(BaseRepository[BannedUser]):
    model = BannedUser

    async def ban(
        self, user_id: int, banned_by_telegram_id: int, reason: Optional[str] = None
    ) -> BannedUser:
        record = BannedUser(
            user_id=user_id,
            banned_by_telegram_id=banned_by_telegram_id,
            reason=reason,
            is_active=True,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def unban(self, user_id: int) -> None:
        result = await self.session.execute(
            select(BannedUser).where(
                BannedUser.user_id == user_id, BannedUser.is_active.is_(True)
            )
        )
        for record in result.scalars().all():
            record.is_active = False
        await self.session.flush()

    async def get_active_for_user(self, user_id: int) -> Optional[BannedUser]:
        result = await self.session.execute(
            select(BannedUser)
            .where(BannedUser.user_id == user_id, BannedUser.is_active.is_(True))
            .order_by(BannedUser.created_at.desc())
        )
        return result.scalars().first()

    async def list_active(self) -> Sequence[BannedUser]:
        result = await self.session.execute(
            select(BannedUser).where(BannedUser.is_active.is_(True))
        )
        return result.scalars().all()
