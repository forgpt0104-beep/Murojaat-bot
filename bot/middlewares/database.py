"""Injects a per-update database session and UnitOfWork into handler data."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.database.engine import async_session_factory
from bot.database.uow import UnitOfWork


class DatabaseMiddleware(BaseMiddleware):
    """Opens one AsyncSession/UnitOfWork per incoming update and commits at the end."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            uow = UnitOfWork(session)
            data["session"] = session
            data["uow"] = uow
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
