"""Business logic around Users: registration, language, ban/unban."""

from __future__ import annotations

from typing import Optional, Sequence

from bot.database.models.enums import LanguageEnum
from bot.database.models.user import User
from bot.database.uow import UnitOfWork
from bot.utils.validators import parse_telegram_id, parse_username


class UserNotFoundError(Exception):
    """Raised when a user lookup by id/username fails."""


class UserService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def register(
        self, telegram_id: int, full_name: str, username: Optional[str]
    ) -> tuple[User, bool]:
        return await self.uow.users.get_or_create(telegram_id, full_name, username)

    async def set_language(self, user: User, language: LanguageEnum) -> User:
        return await self.uow.users.set_language(user, language)

    async def set_phone_number(self, user: User, phone_number: str) -> User:
        return await self.uow.users.set_phone_number(user, phone_number)

    async def find_user(self, query: str) -> Optional[User]:
        """Resolve a user from a Telegram ID, @username, or free-text search term."""
        telegram_id = parse_telegram_id(query)
        if telegram_id is not None:
            return await self.uow.users.get_by_telegram_id(telegram_id)

        username = parse_username(query)
        if username is not None:
            results = await self.uow.users.search(username, limit=1)
            return results[0] if results else None

        results = await self.uow.users.search(query, limit=1)
        return results[0] if results else None

    async def search_users(self, query: str, limit: int = 20) -> Sequence[User]:
        return await self.uow.users.search(query, limit=limit)

    async def ban_user(
        self, target_query: str, banned_by_telegram_id: int, reason: Optional[str]
    ) -> User:
        user = await self.find_user(target_query)
        if user is None:
            raise UserNotFoundError(target_query)

        await self.uow.banned_users.ban(user.id, banned_by_telegram_id, reason)
        await self.uow.users.set_banned(user, True)
        return user

    async def unban_user(self, target_query: str) -> User:
        user = await self.find_user(target_query)
        if user is None:
            raise UserNotFoundError(target_query)

        await self.uow.banned_users.unban(user.id)
        await self.uow.users.set_banned(user, False)
        return user
