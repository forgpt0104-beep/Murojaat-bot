"""AppealMessage model - represents every individual message/attachment exchanged."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base, TimestampMixin
from bot.database.models.enums import ContentType, SenderType

if TYPE_CHECKING:
    from bot.database.models.appeal import Appeal


class AppealMessage(TimestampMixin, Base):
    """A single message (text or media) belonging to an appeal thread."""

    __tablename__ = "appeal_messages"
    __table_args__ = (
        Index("ix_appeal_messages_appeal_id", "appeal_id"),
        Index(
            "ix_appeal_messages_group_message",
            "group_chat_id",
            "group_message_id",
        ),
        Index(
            "ix_appeal_messages_user_message",
            "user_chat_id",
            "user_message_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appeal_id: Mapped[int] = mapped_column(
        ForeignKey("appeals.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: Mapped[SenderType] = mapped_column(
        Enum(SenderType, name="sender_type_enum", native_enum=False), nullable=False
    )
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, name="content_type_enum", native_enum=False), nullable=False
    )

    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_unique_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    media_group_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Message identifiers in the bot chat with the user.
    user_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    user_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Message identifiers in the staff group (used to link replies back).
    group_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Telegram user id of the employee who authored this message (if sender is employee).
    employee_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    appeal: Mapped["Appeal"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return (
            f"<AppealMessage id={self.id} appeal_id={self.appeal_id} "
            f"sender={self.sender_type} type={self.content_type}>"
        )
