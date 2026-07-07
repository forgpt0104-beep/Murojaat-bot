"""Unit of Work: bundles a single AsyncSession with all repositories."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repositories import (
    AdminRepository,
    AppealMessageRepository,
    AppealRepository,
    BannedUserRepository,
    SettingsRepository,
    UserRepository,
)


class UnitOfWork:
    """Groups repositories that share a single database session/transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.appeals = AppealRepository(session)
        self.appeal_messages = AppealMessageRepository(session)
        self.admins = AdminRepository(session)
        self.settings = SettingsRepository(session)
        self.banned_users = BannedUserRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
