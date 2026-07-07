"""BannedUser model - audit trail of ban/unban actions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.database.models.user import User


class BannedUser(TimestampMixin, Base):
    """Records that a user was banned, by whom, and why."""

    __tablename__ = "banned_users"
    __table_args__ = (Index("ix_banned_users_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    banned_by_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="ban_records")

    def __repr__(self) -> str:
        return f"<BannedUser user_id={self.user_id} active={self.is_active}>"
