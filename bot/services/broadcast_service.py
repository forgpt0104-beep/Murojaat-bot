"""Business logic for sending admin broadcasts to all bot users."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from loguru import logger

from bot.database.uow import UnitOfWork
from bot.utils.content import ContentPayload, send_payload

BROADCAST_DELAY_SECONDS = 0.05


@dataclass(slots=True)
class BroadcastResult:
    sent: int
    failed: int


class BroadcastService:
    def __init__(self, uow: UnitOfWork, bot: Bot) -> None:
        self.uow = uow
        self.bot = bot

    async def count_recipients(self) -> int:
        total = 0
        async for batch in self.uow.users.list_all_active():
            total += len(batch)
        return total

    async def broadcast(self, payload: ContentPayload) -> BroadcastResult:
        sent = 0
        failed = 0

        async for batch in self.uow.users.list_all_active():
            for user in batch:
                try:
                    await send_payload(self.bot, user.telegram_id, payload)
                    sent += 1
                except TelegramRetryAfter as exc:
                    await asyncio.sleep(exc.retry_after)
                    try:
                        await send_payload(self.bot, user.telegram_id, payload)
                        sent += 1
                    except Exception:
                        failed += 1
                except TelegramForbiddenError:
                    failed += 1
                except Exception:
                    logger.exception(f"Broadcast failed for user {user.telegram_id}")
                    failed += 1

                await asyncio.sleep(BROADCAST_DELAY_SECONDS)

        logger.info(f"Broadcast finished: sent={sent} failed={failed}")
        return BroadcastResult(sent=sent, failed=failed)
