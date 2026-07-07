"""Admin panel: ban / unban users."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter, IsPrivateChatFilter
from bot.keyboards.callback_data import AdminMenuCallback
from bot.locales import i18n
from bot.services.user_service import UserNotFoundError, UserService
from bot.states import BanStates, UnbanStates

router = Router(name="admin_ban")
router.message.filter(IsPrivateChatFilter(), IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


def _display_name(user) -> str:
    return f"@{user.username}" if user.username else user.full_name


@router.callback_query(AdminMenuCallback.filter(F.action == "ban"))
async def ban_entry(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(BanStates.waiting_target)
    await call.message.answer(i18n.get(lang, "ban_prompt"))
    await call.answer()


@router.message(BanStates.waiting_target)
async def ban_receive_target(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(target=(message.text or "").strip())
    await state.set_state(BanStates.waiting_reason)
    await message.answer(i18n.get(lang, "ban_reason_prompt"))


@router.message(BanStates.waiting_reason)
async def ban_receive_reason(
    message: Message, state: FSMContext, uow: UnitOfWork, lang: str
) -> None:
    reason = None if (message.text or "").strip() == "/skip" else message.text
    data = await state.get_data()
    target = data.get("target", "")
    await state.clear()

    user_service = UserService(uow)
    try:
        user = await user_service.ban_user(target, message.from_user.id, reason)
    except UserNotFoundError:
        await message.answer(i18n.get(lang, "ban_user_not_found"))
        return

    await message.answer(i18n.get(lang, "ban_success", user=_display_name(user)))


@router.callback_query(AdminMenuCallback.filter(F.action == "unban"))
async def unban_entry(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(UnbanStates.waiting_target)
    await call.message.answer(i18n.get(lang, "unban_prompt"))
    await call.answer()


@router.message(UnbanStates.waiting_target)
async def unban_receive_target(
    message: Message, state: FSMContext, uow: UnitOfWork, lang: str
) -> None:
    target = (message.text or "").strip()
    await state.clear()

    user_service = UserService(uow)
    try:
        user = await user_service.unban_user(target)
    except UserNotFoundError:
        await message.answer(i18n.get(lang, "ban_user_not_found"))
        return

    await message.answer(i18n.get(lang, "unban_success", user=_display_name(user)))
