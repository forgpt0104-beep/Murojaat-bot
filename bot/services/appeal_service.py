"""Business logic for appeal creation, group publishing and reply routing."""

from __future__ import annotations

from typing import Optional, Sequence

from aiogram import Bot
from aiogram.types import Message
from loguru import logger

from bot.config import settings
from bot.database.models.appeal import Appeal
from bot.database.models.appeal_message import AppealMessage
from bot.database.models.enums import AppealStatus, ContentType, LanguageEnum, SenderType
from bot.database.models.user import User
from bot.database.uow import UnitOfWork
from bot.utils.content import ContentPayload, extract_content, send_payload
from bot.utils.formatting import build_group_appeal_card, build_response_header
from bot.utils.pagination import Page

MAX_PREVIEW_LENGTH = 500


class AppealService:
    def __init__(self, uow: UnitOfWork, bot: Bot) -> None:
        self.uow = uow
        self.bot = bot

    async def create_appeal(self, user: User, language: LanguageEnum) -> Appeal:
        appeal = await self.uow.appeals.create_appeal(user.id, language)
        logger.info(f"Created appeal {appeal.formatted_number} for user {user.telegram_id}")
        return appeal

    async def add_user_message(
        self, appeal: Appeal, message: Message
    ) -> Optional[AppealMessage]:
        payload = extract_content(message)
        if payload is None:
            return None

        return await self.uow.appeal_messages.create(
            appeal_id=appeal.id,
            sender_type=SenderType.USER,
            content_type=payload.content_type,
            text=payload.text or payload.caption,
            file_id=payload.file_id,
            file_unique_id=payload.file_unique_id,
            media_group_id=payload.media_group_id,
            user_chat_id=message.chat.id,
            user_message_id=message.message_id,
        )

    async def publish_to_group(self, appeal: Appeal, user: User) -> None:
        """Post the appeal card + all attachments into the staff group."""
        messages: Sequence[AppealMessage] = await self.uow.appeal_messages.list_by_appeal(
            appeal.id
        )

        text_parts = [m.text for m in messages if m.content_type == ContentType.TEXT and m.text]
        preview = "\n".join(text_parts)[:MAX_PREVIEW_LENGTH]
        if preview:
            await self.uow.appeals.set_summary_text(appeal, preview)

        card_text = build_group_appeal_card(appeal, user, preview)
        card_message = await self.bot.send_message(settings.GROUP_ID, card_text)
        await self.uow.appeals.set_group_message(
            appeal, card_message.chat.id, card_message.message_id
        )

        for m in messages:
            if m.content_type == ContentType.TEXT:
                continue

            payload = ContentPayload(
                content_type=m.content_type,
                text=m.text,
                file_id=m.file_id,
                file_unique_id=m.file_unique_id,
                media_group_id=m.media_group_id,
            )
            sent = await send_payload(
                self.bot,
                settings.GROUP_ID,
                payload,
                reply_to_message_id=card_message.message_id,
            )
            m.group_chat_id = sent.chat.id
            m.group_message_id = sent.message_id

        await self.uow.session.flush()
        logger.info(f"Published appeal {appeal.formatted_number} to group {settings.GROUP_ID}")

    async def handle_employee_reply(
        self, appeal: Appeal, employee_message: Message, employee_telegram_id: int
    ) -> AppealMessage:
        """Forward an employee's reply (any content type) back to the original user."""
        payload = extract_content(employee_message)
        if payload is None:
            raise ValueError("Unsupported content type in employee reply")

        user = await self.uow.users.get_by_id(appeal.user_id)
        if user is None:
            raise ValueError(f"User for appeal {appeal.id} not found")

        header = build_response_header(user.language.value, appeal)
        await self.bot.send_message(user.telegram_id, header)

        sent = await send_payload(
            self.bot,
            user.telegram_id,
            payload,
            caption=payload.caption,
        )

        appeal_message = await self.uow.appeal_messages.create(
            appeal_id=appeal.id,
            sender_type=SenderType.EMPLOYEE,
            content_type=payload.content_type,
            text=payload.text or payload.caption,
            file_id=payload.file_id,
            file_unique_id=payload.file_unique_id,
            media_group_id=payload.media_group_id,
            user_chat_id=sent.chat.id,
            user_message_id=sent.message_id,
            group_chat_id=employee_message.chat.id,
            group_message_id=employee_message.message_id,
            employee_telegram_id=employee_telegram_id,
        )

        await self.uow.appeals.set_status(appeal, AppealStatus.ANSWERED)
        employee = employee_message.from_user
        await self.uow.admins.increment_replies_count(
            employee_telegram_id,
            full_name=employee.full_name if employee else None,
            username=employee.username if employee else None,
        )

        logger.info(
            f"Employee {employee_telegram_id} replied to appeal {appeal.formatted_number}"
        )
        return appeal_message

    async def get_user_appeals_page(
        self, user_id: int, page: Page
    ) -> tuple[Sequence[Appeal], int]:
        total = await self.uow.appeals.count_user_appeals(user_id)
        items = await self.uow.appeals.get_user_appeals(
            user_id, limit=page.per_page, offset=page.offset
        )
        return items, total

    async def get_appeal_detail(self, appeal_id: int) -> Optional[Appeal]:
        return await self.uow.appeals.get_by_id(appeal_id)

    async def reopen_appeal(self, appeal: Appeal) -> Appeal:
        return await self.uow.appeals.set_status(appeal, AppealStatus.IN_PROCESS)

    async def close_appeal(self, appeal: Appeal) -> Appeal:
        return await self.uow.appeals.set_status(appeal, AppealStatus.CLOSED)
