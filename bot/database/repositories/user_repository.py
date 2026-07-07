"""Repository for User model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func, or_, select

from bot.database.models.enums import LanguageEnum
from bot.database.models.user import User
from bot.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        full_name: str,
        username: Optional[str] = None,
    ) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user is not None:
            changed = False
            if user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if user.username != username:
                user.username = username
                changed = True
            if changed:
                await self.session.flush()
            return user, False

        user = await self.create(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            language=LanguageEnum.UZ,
        )
        return user, True

    async def set_language(self, user: User, language: LanguageEnum) -> User:
        user.language = language
        await self.session.flush()
        return user

    async def set_phone_number(self, user: User, phone_number: str) -> User:
        user.phone_number = phone_number
        await self.session.flush()
        return user

    async def set_banned(self, user: User, is_banned: bool) -> User:
        user.is_banned = is_banned
        await self.session.flush()
        return user

    async def search(self, query: str, limit: int = 20) -> Sequence[User]:
        like = f"%{query}%"
        stmt = select(User).where(
            or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.phone_number.ilike(like),
            )
        )
        if query.lstrip("-").isdigit():
            stmt = select(User).where(
                or_(
                    User.telegram_id == int(query),
                    User.full_name.ilike(like),
                    User.username.ilike(like),
                    User.phone_number.ilike(like),
                )
            )
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return int(result.scalar_one())

    async def count_created_since(self, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(User.created_at >= since)
        )
        return int(result.scalar_one())

    async def list_all_active(self, batch_size: int = 500):
        """Yield all non-banned users in batches (used for broadcast)."""
        offset = 0
        while True:
            result = await self.session.execute(
                select(User)
                .where(User.is_banned.is_(False))
                .order_by(User.id)
                .offset(offset)
                .limit(batch_size)
            )
            batch = result.scalars().all()
            if not batch:
                break
            yield batch
            offset += batch_size

    async def count_by_language(self) -> dict[str, int]:
        result = await self.session.execute(
            select(User.language, func.count(User.id)).group_by(User.language)
        )
        return {str(lang.value if hasattr(lang, "value") else lang): count for lang, count in result.all()}
