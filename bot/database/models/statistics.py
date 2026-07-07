"""Statistics model - daily aggregated counters for fast reporting."""

from __future__ import annotations

from datetime import date as date_type

from sqlalchemy import Date, Index
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base, TimestampMixin


class Statistics(TimestampMixin, Base):
    """One row per calendar day with aggregated counters."""

    __tablename__ = "statistics"
    __table_args__ = (Index("ix_statistics_date", "date", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, unique=True, nullable=False)

    new_appeals_count: Mapped[int] = mapped_column(default=0, nullable=False)
    answered_count: Mapped[int] = mapped_column(default=0, nullable=False)
    closed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    new_users_count: Mapped[int] = mapped_column(default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Statistics date={self.date} new_appeals={self.new_appeals_count}>"
