"""Admin panel: broadcast a message to all bot users."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models.enums import ContentType
from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter, IsPrivateChatFilter
from bot.keyboards.callback_data import AdminMenuCallback, ConfirmCallback
from bot.keyboards.inline.confirm import confirm_keyboard
from bot.locales import i18n
from bot.services.broadcast_service import BroadcastService
from bot.states import BroadcastStates
from bot.utils.content import ContentPayload, extract_content

router = Router(name="admin_broadcast")
router.message.filter(IsPrivateChatFilter(), IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

BROADCAST_ACTION = "broadcast"


@router.callback_query(AdminMenuCallback.filter(F.action == "broadcast"))
async def broadcast_entry(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(BroadcastStates.waiting_content)
    await call.message.answer(i18n.get(lang, "broadcast_prompt"))
    await call.answer()


@router.message(BroadcastStates.waiting_content)
async def broadcast_receive_content(
    message: Message, state: FSMContext, uow: UnitOfWork, lang: str
) -> None:
    payload = extract_content(message)
    if payload is None:
        await message.answer(i18n.get(lang, "new_appeal_unsupported_content"))
        return

    item: Dict[str, Any] = asdict(payload)
    item["content_type"] = payload.content_type.value
    await state.update_data(payload=item)
    await state.set_state(BroadcastStates.waiting_confirmation)

    broadcast_service = BroadcastService(uow, bot=message.bot)
    count = await broadcast_service.count_recipients()

    await message.answer(
        i18n.get(lang, "broadcast_confirm", count=count),
        reply_markup=confirm_keyboard(lang, BROADCAST_ACTION),
    )


@router.callback_query(
    BroadcastStates.waiting_confirmation, ConfirmCallback.filter(F.action == BROADCAST_ACTION)
)
async def broadcast_confirm(
    call: CallbackQuery,
    callback_data: ConfirmCallback,
    state: FSMContext,
    uow: UnitOfWork,
    lang: str,
) -> None:
    await call.message.edit_reply_markup(reply_markup=None)

    if callback_data.answer != "yes":
        await state.clear()
        await call.message.answer(i18n.get(lang, "broadcast_cancelled"))
        await call.answer()
        return

    data = await state.get_data()
    item = data.get("payload")
    await state.clear()

    if not item:
        await call.answer()
        return

    payload = ContentPayload(
        content_type=ContentType(item["content_type"]),
        text=item.get("text"),
        file_id=item.get("file_id"),
        file_unique_id=item.get("file_unique_id"),
        media_group_id=item.get("media_group_id"),
        caption=item.get("caption"),
    )

    await call.message.answer(i18n.get(lang, "broadcast_started"))
    broadcast_service = BroadcastService(uow, bot=call.bot)
    result = await broadcast_service.broadcast(payload)

    await call.message.answer(
        i18n.get(lang, "broadcast_finished", sent=result.sent, failed=result.failed)
    )
    await call.answer()
