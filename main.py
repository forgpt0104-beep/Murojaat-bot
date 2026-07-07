"""Entry point for the Telegram Support Request Bot."""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from loguru import logger

from bot.config import settings
from bot.database.engine import async_session_factory, dispose_engine
from bot.database.models.enums import AdminRole
from bot.database.uow import UnitOfWork
from bot.handlers import router as root_router
from bot.middlewares import (
    BanCheckMiddleware,
    DatabaseMiddleware,
    I18nMiddleware,
    LoggingMiddleware,
    ThrottlingMiddleware,
)
from bot.utils.logger import setup_logging

BOT_COMMANDS = [
    BotCommand(command="start", description="Start / restart the bot"),
    BotCommand(command="menu", description="Show the main menu"),
    BotCommand(command="help", description="Get help"),
]

ADMIN_COMMANDS = BOT_COMMANDS + [
    BotCommand(command="admin", description="Open the admin panel"),
]


async def ensure_super_admin() -> None:
    """Guarantee the SUPER_ADMIN_ID always has an active super_admin Admin row."""
    async with async_session_factory() as session:
        uow = UnitOfWork(session)
        await uow.admins.add_admin(settings.SUPER_ADMIN_ID, role=AdminRole.SUPER_ADMIN)
        await session.commit()


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(BOT_COMMANDS)
    try:
        await bot.set_my_commands(
            ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=settings.SUPER_ADMIN_ID)
        )
    except Exception:
        logger.warning("Could not set admin command scope (super admin may not have started the bot yet)")


def register_middlewares(dp: Dispatcher) -> None:
    # All registered as outer middlewares so they run once per update, before any
    # router/filter resolution, and so downstream filters (e.g. IsAdminFilter) can
    # rely on `uow`, `lang` and `db_user` already being present in handler data.
    for observer in (dp.message, dp.callback_query):
        observer.outer_middleware(DatabaseMiddleware())
        observer.outer_middleware(I18nMiddleware())
        observer.outer_middleware(LoggingMiddleware())
        observer.outer_middleware(BanCheckMiddleware())
        observer.outer_middleware(ThrottlingMiddleware())


async def main() -> None:
    setup_logging()
    logger.info("Starting Telegram Support Request Bot...")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    register_middlewares(dp)
    dp.include_router(root_router)

    await ensure_super_admin()
    await setup_bot_commands(bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot polling started")
        await dp.start_polling(bot)
    finally:
        await dispose_engine()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
