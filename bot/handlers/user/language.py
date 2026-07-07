"""Language selection: initial choice and later changes via the main menu."""

from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models.enums import LanguageEnum
from bot.database.uow import UnitOfWork
from bot.filters import IsPrivateChatFilter, TextEqualsKey
from bot.keyboards.callback_data import LanguageCallback
from bot.keyboards.inline.language import language_keyboard
from bot.keyboards.reply import main_menu_keyboard
from bot.locales import i18n
from bot.services.user_service import UserService

router = Router(name="user_language")
router.message.filter(IsPrivateChatFilter())


@router.message(TextEqualsKey("btn_change_language"))
async def change_language(message: Message, lang: str) -> None:
    await message.answer(i18n.get(lang, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(LanguageCallback.filter())
async def on_language_selected(
    call: CallbackQuery,
    callback_data: LanguageCallback,
    uow: UnitOfWork,
    state: FSMContext,
) -> None:
    user_service = UserService(uow)
    telegram_user = call.from_user

    user, _ = await user_service.register(
        telegram_id=telegram_user.id,
        full_name=telegram_user.full_name,
        username=telegram_user.username,
    )
    language = LanguageEnum(callback_data.code)
    await user_service.set_language(user, language)
    await state.clear()

    await call.message.edit_text(i18n.get(language.value, "language_set"))
    await call.message.answer(
        i18n.get(language.value, "main_menu_text"),
        reply_markup=main_menu_keyboard(language.value),
    )
    await call.answer()
