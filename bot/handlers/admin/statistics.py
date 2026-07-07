"""Admin panel: statistics dashboard."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter
from bot.keyboards.callback_data import AdminMenuCallback
from bot.locales import i18n
from bot.services.statistics_service import StatisticsService

router = Router(name="admin_statistics")
router.callback_query.filter(IsAdminFilter())


@router.callback_query(AdminMenuCallback.filter(F.action == "stats"))
async def show_statistics(call: CallbackQuery, uow: UnitOfWork, lang: str) -> None:
    stats_service = StatisticsService(uow)
    snapshot = await stats_service.get_snapshot()

    text = i18n.get(
        lang,
        "stats_title",
        today=snapshot.today,
        week=snapshot.week,
        month=snapshot.month,
        total_users=snapshot.total_users,
        total_appeals=snapshot.total_appeals,
        answered=snapshot.answered,
        pending=snapshot.pending,
        closed=snapshot.closed,
        languages=StatisticsService.format_languages(snapshot.languages),
        top_employees=StatisticsService.format_top_employees(snapshot.top_employees),
    )
    await call.message.answer(text)
    await call.answer()
