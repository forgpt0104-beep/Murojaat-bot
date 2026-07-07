"""Appeal model."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, Sequence, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin
from bot.database.models.enums import AppealStatus, LanguageEnum

if TYPE_CHECKING:
    from bot.database.models.appeal_message import AppealMessage
    from bot.database.models.user import User

appeal_number_seq = Sequence("appeal_number_seq", start=1, increment=1)


class Appeal(TimestampMixin, Base):
    """A support appeal submitted by a user."""

    __tablename__ = "appeals"
    __table_args__ = (
        Index("ix_appeals_appeal_number", "appeal_number", unique=True),
        Index("ix_appeals_user_id", "user_id"),
        Index("ix_appeals_status", "status"),
        Index("ix_appeals_group_message_id", "group_chat_id", "group_message_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appeal_number: Mapped[int] = mapped_column(
        appeal_number_seq,
        server_default=appeal_number_seq.next_value(),
        unique=True,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum, name="appeal_language_enum", native_enum=False),
        nullable=False,
    )
    status: Mapped[AppealStatus] = mapped_column(
        Enum(AppealStatus, name="appeal_status_enum", native_enum=False),
        default=AppealStatus.NEW,
        nullable=False,
    )
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location of the "card" posted in the staff group, needed to link replies back.
    group_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    closed_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship(back_populates="appeals")
    messages: Mapped[List["AppealMessage"]] = relationship(
        back_populates="appeal",
        cascade="all, delete-orphan",
        order_by="AppealMessage.id",
    )

    @property
    def formatted_number(self) -> str:
        return f"#{self.appeal_number:06d}"

    def __repr__(self) -> str:
        return f"<Appeal id={self.id} number={self.formatted_number} status={self.status}>"
