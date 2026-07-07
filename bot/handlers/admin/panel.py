"""/admin entry point: shows the admin panel inline menu."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.filters import IsAdminFilter, IsPrivateChatFilter
from bot.keyboards.inline.admin import admin_panel_keyboard
from bot.locales import i18n

router = Router(name="admin_panel")
router.message.filter(IsPrivateChatFilter(), IsAdminFilter())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(i18n.get(lang, "admin_panel_title"), reply_markup=admin_panel_keyboard(lang))
