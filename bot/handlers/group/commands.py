"""Convenience commands used directly inside the staff group."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.models.appeal import Appeal
from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter, IsReplyToAppealFilter, IsStaffGroupFilter
from bot.services.appeal_service import AppealService
from bot.services.statistics_service import StatisticsService
from bot.utils.formatting import status_label

router = Router(name="group_commands")
router.message.filter(IsStaffGroupFilter())

GROUP_LANG = "en"


@router.message(Command("status"), IsReplyToAppealFilter())
async def cmd_status(message: Message, appeal: Appeal) -> None:
    await message.reply(
        f"🆔 {appeal.formatted_number}\n📊 Status: {status_label(GROUP_LANG, appeal.status)}"
    )


@router.message(Command("close"), IsReplyToAppealFilter())
async def cmd_close(message: Message, appeal: Appeal, uow: UnitOfWork) -> None:
    appeal_service = AppealService(uow, bot=message.bot)
    await appeal_service.close_appeal(appeal)
    await message.reply(f"🔒 {appeal.formatted_number} closed.")


@router.message(Command("reopen"), IsReplyToAppealFilter())
async def cmd_reopen(message: Message, appeal: Appeal, uow: UnitOfWork) -> None:
    appeal_service = AppealService(uow, bot=message.bot)
    await appeal_service.reopen_appeal(appeal)
    await message.reply(f"🔄 {appeal.formatted_number} reopened (in process).")


@router.message(Command("stats"), IsAdminFilter())
async def cmd_group_stats(message: Message, uow: UnitOfWork) -> None:
    stats_service = StatisticsService(uow)
    snapshot = await stats_service.get_snapshot()
    await message.reply(
        "📊 Statistics\n"
        f"Today: {snapshot.today} | Week: {snapshot.week} | Month: {snapshot.month}\n"
        f"Users: {snapshot.total_users} | Appeals: {snapshot.total_appeals}\n"
        f"Answered: {snapshot.answered} | Pending: {snapshot.pending} | Closed: {snapshot.closed}"
    )
