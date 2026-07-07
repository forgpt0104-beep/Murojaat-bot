"""Generic base repository providing common CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common async CRUD helpers for a single model."""

    model: Type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, obj_id)

    async def get_all(self) -> Sequence[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def save(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
