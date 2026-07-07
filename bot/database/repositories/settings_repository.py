"""Repository for Setting model (key/value store)."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select

from bot.database.models.settings import Setting
from bot.database.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[Setting]):
    model = Setting

    async def get_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        result = await self.session.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting is not None else default

    async def set_value(
        self, key: str, value: str, description: Optional[str] = None
    ) -> Setting:
        result = await self.session.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting is None:
            setting = Setting(key=key, value=value, description=description)
            self.session.add(setting)
        else:
            setting.value = value
            if description is not None:
                setting.description = description
        await self.session.flush()
        return setting

    async def get_all(self) -> Sequence[Setting]:
        result = await self.session.execute(select(Setting).order_by(Setting.key))
        return result.scalars().all()
