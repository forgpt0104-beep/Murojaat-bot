"""Aggregated statistics for the admin panel."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from bot.database.models.enums import AppealStatus
from bot.database.uow import UnitOfWork

LANGUAGE_NAMES = {"uz": "Uzbek", "ru": "Russian", "en": "English"}


@dataclass(slots=True)
class StatsSnapshot:
    today: int
    week: int
    month: int
    total_users: int
    total_appeals: int
    answered: int
    pending: int
    closed: int
    languages: Dict[str, int] = field(default_factory=dict)
    top_employees: List[tuple[str, int]] = field(default_factory=list)


class StatisticsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_snapshot(self) -> StatsSnapshot:
        now = datetime.now(timezone.utc)
        since_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since_week = now - timedelta(days=7)
        since_month = now - timedelta(days=30)

        today = await self.uow.appeals.count_created_since(since_today)
        week = await self.uow.appeals.count_created_since(since_week)
        month = await self.uow.appeals.count_created_since(since_month)

        total_users = await self.uow.users.count_total()
        total_appeals = await self.uow.appeals.count_total()

        answered = await self.uow.appeals.count_by_status(AppealStatus.ANSWERED)
        pending = await self.uow.appeals.count_by_status(
            AppealStatus.NEW
        ) + await self.uow.appeals.count_by_status(AppealStatus.IN_PROCESS)
        closed = await self.uow.appeals.count_by_status(AppealStatus.CLOSED)

        languages = await self.uow.appeals.count_by_language()

        top_employees_raw = await self.uow.admins.top_employees(limit=5)
        top_employees = [
            (admin.full_name or admin.username or str(admin.telegram_id), admin.replies_count)
            for admin in top_employees_raw
        ]

        return StatsSnapshot(
            today=today,
            week=week,
            month=month,
            total_users=total_users,
            total_appeals=total_appeals,
            answered=answered,
            pending=pending,
            closed=closed,
            languages=languages,
            top_employees=top_employees,
        )

    @staticmethod
    def format_languages(languages: Dict[str, int]) -> str:
        if not languages:
            return "—"
        lines = []
        for code, count in languages.items():
            name = LANGUAGE_NAMES.get(code, code)
            lines.append(f"  {name}: {count}")
        return "\n".join(lines)

    @staticmethod
    def format_top_employees(top_employees: List[tuple[str, int]]) -> str:
        if not top_employees:
            return "—"
        lines = []
        for i, (name, count) in enumerate(top_employees, start=1):
            lines.append(f"  {i}. {name} — {count} replies")
        return "\n".join(lines)
