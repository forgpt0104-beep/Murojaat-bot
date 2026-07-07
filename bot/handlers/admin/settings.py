"""Admin panel: view and edit runtime key/value settings."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.uow import UnitOfWork
from bot.filters import IsAdminFilter, IsPrivateChatFilter
from bot.keyboards.callback_data import AdminMenuCallback
from bot.locales import i18n
from bot.states import SettingsStates

router = Router(name="admin_settings")
router.message.filter(IsPrivateChatFilter(), IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(AdminMenuCallback.filter(F.action == "settings"))
async def settings_entry(call: CallbackQuery, uow: UnitOfWork, state: FSMContext, lang: str) -> None:
    settings_rows = await uow.settings.get_all()

    lines = [i18n.get(lang, "settings_title"), ""]
    if not settings_rows:
        lines.append("—")
    else:
        for row in settings_rows:
            lines.append(f"<code>{row.key}</code> = {row.value}")

    lines.append("")
    lines.append("Send <code>key=value</code> to create or update a setting.")

    await state.set_state(SettingsStates.waiting_value)
    await call.message.answer("\n".join(lines))
    await call.answer()


@router.message(SettingsStates.waiting_value)
async def settings_receive_kv(
    message: Message, state: FSMContext, uow: UnitOfWork, lang: str
) -> None:
    text = (message.text or "").strip()
    if "=" not in text:
        await message.answer("Format: <code>key=value</code>")
        return

    key, _, value = text.partition("=")
    key = key.strip()
    value = value.strip()

    if not key:
        await message.answer("Format: <code>key=value</code>")
        return

    await uow.settings.set_value(key, value)
    await state.clear()
    await message.answer(f"✅ <code>{key}</code> = {value}")
