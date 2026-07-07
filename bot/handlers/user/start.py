"""/start command: registers the user and shows language selection or main menu."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database.uow import UnitOfWork
from bot.filters import IsPrivateChatFilter
from bot.keyboards.inline.language import language_keyboard
from bot.keyboards.reply import main_menu_keyboard
from bot.locales import i18n
from bot.services.user_service import UserService

router = Router(name="user_start")
router.message.filter(IsPrivateChatFilter())


@router.message(CommandStart())
async def cmd_start(message: Message, uow: UnitOfWork, state: FSMContext, lang: str) -> None:
    await state.clear()

    user_service = UserService(uow)
    telegram_user = message.from_user
    user, is_new = await user_service.register(
        telegram_id=telegram_user.id,
        full_name=telegram_user.full_name,
        username=telegram_user.username,
    )

    if is_new:
        await message.answer(i18n.get("en", "choose_language"), reply_markup=language_keyboard())
        return

    await message.answer(
        i18n.get(user.language.value, "main_menu_text"),
        reply_markup=main_menu_keyboard(user.language.value),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, lang: str) -> None:
    await message.answer(
        i18n.get(lang, "main_menu_text"), reply_markup=main_menu_keyboard(lang)
    )
