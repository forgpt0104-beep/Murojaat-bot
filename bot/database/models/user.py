"""User model."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin
from bot.database.models.enums import LanguageEnum

if TYPE_CHECKING:
    from bot.database.models.appeal import Appeal
    from bot.database.models.banned_user import BannedUser


class User(TimestampMixin, Base):
    """A Telegram end-user who can submit appeals."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_telegram_id", "telegram_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, name="language_enum", native_enum=False),
        default=LanguageEnum.UZ,
        nullable=False,
    )
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    appeals: Mapped[List["Appeal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    ban_records: Mapped[List["BannedUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} lang={self.language}>"
