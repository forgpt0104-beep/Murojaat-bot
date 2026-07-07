"""My Appeals: paginated list + detail view for the current user."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.database.models.appeal import Appeal
from bot.database.models.user import User
from bot.database.uow import UnitOfWork
from bot.filters import IsPrivateChatFilter, TextEqualsKey
from bot.keyboards.callback_data import (
    AppealActionCallback,
    AppealViewCallback,
    PaginationCallback,
)
from bot.keyboards.inline.appeal import appeal_detail_keyboard, my_appeals_keyboard
from bot.locales import i18n
from bot.services.appeal_service import AppealService
from bot.utils.formatting import build_appeal_detail_header
from bot.utils.pagination import Page

router = Router(name="user_my_appeals")
router.message.filter(IsPrivateChatFilter())

PER_PAGE = 5


async def _render_page(uow: UnitOfWork, user: User, lang: str, page_number: int):
    appeal_service = AppealService(uow, bot=None)  # bot not needed for read-only listing
    page = Page(page=page_number, per_page=PER_PAGE, total_items=0)
    items, total = await appeal_service.get_user_appeals_page(user.id, page)
    page.total_items = total

    header = i18n.get(lang, "my_appeals_header", page=page_number + 1, total_pages=page.total_pages)
    keyboard = my_appeals_keyboard(lang, items, page_number, page.total_pages)
    return header, keyboard, items


@router.message(TextEqualsKey("btn_my_appeals"))
async def my_appeals_entry(message: Message, uow: UnitOfWork, db_user: User, lang: str) -> None:
    if db_user is None:
        return

    total = await uow.appeals.count_user_appeals(db_user.id)
    if total == 0:
        await message.answer(i18n.get(lang, "my_appeals_empty"))
        return

    header, keyboard, _ = await _render_page(uow, db_user, lang, 0)
    await message.answer(header, reply_markup=keyboard)


@router.callback_query(PaginationCallback.filter(F.scope == "my_appeals"))
async def my_appeals_paginate(
    call: CallbackQuery,
    callback_data: PaginationCallback,
    uow: UnitOfWork,
    db_user: User,
    lang: str,
) -> None:
    if db_user is None:
        await call.answer()
        return

    header, keyboard, _ = await _render_page(uow, db_user, lang, callback_data.page)
    await call.message.edit_text(header, reply_markup=keyboard)
    await call.answer()


async def _can_view(uow: UnitOfWork, call: CallbackQuery, appeal: Appeal, db_user: User) -> bool:
    """Owners can always view their own appeal; admins may view any appeal (e.g. from search)."""
    if db_user is not None and appeal.user_id == db_user.id:
        return True

    if call.from_user.id == settings.SUPER_ADMIN_ID:
        return True

    admin = await uow.admins.get_by_telegram_id(call.from_user.id)
    return bool(admin and admin.is_active)


@router.callback_query(AppealViewCallback.filter())
async def my_appeal_detail(
    call: CallbackQuery,
    callback_data: AppealViewCallback,
    uow: UnitOfWork,
    db_user: User,
    lang: str,
) -> None:
    appeal_service = AppealService(uow, bot=call.bot)
    appeal = await appeal_service.get_appeal_detail(callback_data.appeal_id)

    if appeal is None or not await _can_view(uow, call, appeal, db_user):
        await call.answer(i18n.get(lang, "error_generic"), show_alert=True)
        return

    header = build_appeal_detail_header(lang, appeal)
    messages = await uow.appeal_messages.list_by_appeal(appeal.id)

    lines = [header]
    if not messages:
        lines.append(i18n.get(lang, "appeal_detail_no_messages"))
    else:
        for m in messages:
            sender_label = "You" if m.sender_type.value == "user" else "Support"
            content_label = m.text if m.content_type.value == "text" else f"[{m.content_type.value}]"
            lines.append(f"<b>{sender_label}:</b> {content_label}")

    await call.message.edit_text(
        "\n".join(lines), reply_markup=appeal_detail_keyboard(lang, appeal, callback_data.page)
    )
    await call.answer()


@router.callback_query(AppealActionCallback.filter())
async def my_appeal_reopen(
    call: CallbackQuery,
    callback_data: AppealActionCallback,
    uow: UnitOfWork,
    db_user: User,
    lang: str,
) -> None:
    if callback_data.action != "reopen":
        await call.answer()
        return

    appeal_service = AppealService(uow, bot=call.bot)
    appeal = await appeal_service.get_appeal_detail(callback_data.appeal_id)

    if appeal is None or not await _can_view(uow, call, appeal, db_user):
        await call.answer(i18n.get(lang, "error_generic"), show_alert=True)
        return

    await appeal_service.reopen_appeal(appeal)

    header = build_appeal_detail_header(lang, appeal)
    await call.message.edit_text(header, reply_markup=appeal_detail_keyboard(lang, appeal))
    await call.answer()
