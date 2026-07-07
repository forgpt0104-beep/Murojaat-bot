"""Admin panel: search appeals by ID, Telegram ID, username, name or phone."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter, IsPrivateChatFilter
from bot.keyboards.callback_data import AdminMenuCallback, PaginationCallback
from bot.keyboards.inline.pagination import search_results_keyboard
from bot.locales import i18n
from bot.states import SearchStates
from bot.utils.pagination import Page
from bot.utils.validators import sanitize_search_query

router = Router(name="admin_search")
router.message.filter(IsPrivateChatFilter(), IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

PER_PAGE = 10
SCOPE = "admin_search"


async def _render_results(uow: UnitOfWork, lang: str, query: str, page_number: int):
    total = await uow.appeals.count_search(query)
    page = Page(page=page_number, per_page=PER_PAGE, total_items=total)
    items = await uow.appeals.search(query, limit=PER_PAGE, offset=page.offset)
    keyboard = search_results_keyboard(lang, items, page_number, page.total_pages, scope=SCOPE)
    return items, keyboard


@router.callback_query(AdminMenuCallback.filter(F.action == "search"))
async def search_entry(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(SearchStates.waiting_query)
    await call.message.answer(i18n.get(lang, "search_prompt"))
    await call.answer()


@router.message(SearchStates.waiting_query)
async def search_execute(message: Message, state: FSMContext, uow: UnitOfWork, lang: str) -> None:
    query = sanitize_search_query(message.text or "")
    if not query:
        return

    await state.update_data(query=query)
    items, keyboard = await _render_results(uow, lang, query, 0)

    if not items:
        await message.answer(i18n.get(lang, "search_no_results"))
        return

    total = await uow.appeals.count_search(query)
    await message.answer(
        i18n.get(lang, "search_results_header", count=total), reply_markup=keyboard
    )


@router.callback_query(PaginationCallback.filter(F.scope == SCOPE))
async def search_paginate(
    call: CallbackQuery,
    callback_data: PaginationCallback,
    state: FSMContext,
    uow: UnitOfWork,
    lang: str,
) -> None:
    data = await state.get_data()
    query = data.get("query")
    if not query:
        await call.answer()
        return

    items, keyboard = await _render_results(uow, lang, query, callback_data.page)
    total = await uow.appeals.count_search(query)
    await call.message.edit_text(
        i18n.get(lang, "search_results_header", count=total), reply_markup=keyboard
    )
    await call.answer()
