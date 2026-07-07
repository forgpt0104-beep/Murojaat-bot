"""Settings model - simple key/value store for runtime-configurable options."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base, TimestampMixin


class Setting(TimestampMixin, Base):
    """A single runtime setting, editable from the admin panel."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Setting key={self.key!r} value={self.value!r}>"
