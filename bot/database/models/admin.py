"""Admin model."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base, TimestampMixin
from bot.database.models.enums import AdminRole


class Admin(TimestampMixin, Base):
    """An administrator or employee with elevated privileges."""

    __tablename__ = "admins"
    __table_args__ = (
        Index("ix_admins_telegram_id", "telegram_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole, name="admin_role_enum", native_enum=False),
        default=AdminRole.ADMIN,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    replies_count: Mapped[int] = mapped_column(default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Admin id={self.id} telegram_id={self.telegram_id} role={self.role}>"
