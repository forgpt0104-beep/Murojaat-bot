"""New Appeal creation flow: collects one or more messages, then submits to the group."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models.enums import ContentType, SenderType
from bot.database.models.user import User
from bot.database.uow import UnitOfWork
from bot.filters import IsPrivateChatFilter, TextEqualsKey
from bot.keyboards.callback_data import AttachMoreCallback
from bot.keyboards.inline.appeal import attach_more_keyboard
from bot.keyboards.reply import main_menu_keyboard
from bot.locales import i18n
from bot.services.appeal_service import AppealService
from bot.states import AppealStates
from bot.utils.content import extract_content

router = Router(name="user_appeal")
router.message.filter(IsPrivateChatFilter())


@router.message(TextEqualsKey("btn_new_appeal"))
async def new_appeal_entry(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(AppealStates.waiting_content)
    await state.update_data(items=[])
    await message.answer(i18n.get(lang, "new_appeal_prompt"))


@router.message(AppealStates.waiting_content)
async def receive_appeal_content(message: Message, state: FSMContext, lang: str) -> None:
    payload = extract_content(message)
    if payload is None:
        await message.answer(i18n.get(lang, "new_appeal_unsupported_content"))
        return

    data = await state.get_data()
    items: List[Dict[str, Any]] = data.get("items", [])

    item = asdict(payload)
    item["content_type"] = payload.content_type.value
    item["user_chat_id"] = message.chat.id
    item["user_message_id"] = message.message_id
    items.append(item)

    await state.update_data(items=items)
    await state.set_state(AppealStates.waiting_attach_more)

    await message.answer(
        i18n.get(lang, "new_appeal_received_item"), reply_markup=attach_more_keyboard(lang)
    )


@router.callback_query(AppealStates.waiting_attach_more, AttachMoreCallback.filter())
async def on_attach_more_answer(
    call: CallbackQuery,
    callback_data: AttachMoreCallback,
    state: FSMContext,
    uow: UnitOfWork,
    db_user: User,
    lang: str,
) -> None:
    await call.message.edit_reply_markup(reply_markup=None)

    if callback_data.answer == "yes":
        await state.set_state(AppealStates.waiting_content)
        await call.message.answer(i18n.get(lang, "new_appeal_prompt"))
        await call.answer()
        return

    data = await state.get_data()
    items: List[Dict[str, Any]] = data.get("items", [])

    if not items or db_user is None:
        await call.message.answer(i18n.get(lang, "new_appeal_empty"))
        await call.answer()
        return

    appeal_service = AppealService(uow, bot=call.bot)
    appeal = await appeal_service.create_appeal(db_user, db_user.language)

    for item in items:
        await uow.appeal_messages.create(
            appeal_id=appeal.id,
            sender_type=SenderType.USER,
            content_type=ContentType(item["content_type"]),
            text=item.get("text") or item.get("caption"),
            file_id=item.get("file_id"),
            file_unique_id=item.get("file_unique_id"),
            media_group_id=item.get("media_group_id"),
            user_chat_id=item.get("user_chat_id"),
            user_message_id=item.get("user_message_id"),
        )

    await appeal_service.publish_to_group(appeal, db_user)

    await state.clear()
    await call.message.answer(
        i18n.get(lang, "new_appeal_created", appeal_number=appeal.appeal_number),
        reply_markup=main_menu_keyboard(lang),
    )
    await call.answer()
