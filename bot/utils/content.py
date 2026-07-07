"""Helpers to extract and re-send arbitrary Telegram message content.

Centralizes the mapping between a `types.Message` and our internal
`ContentType` so the same logic can be reused when:
  * saving an incoming user appeal message,
  * forwarding that message into the staff group,
  * saving/forwarding an employee's reply back to the user.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from aiogram.types import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

from bot.database.models.enums import ContentType


@dataclass(slots=True)
class ContentPayload:
    """Normalized representation of a single message's content."""

    content_type: ContentType
    text: Optional[str] = None
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None
    media_group_id: Optional[str] = None
    caption: Optional[str] = None


def extract_content(message: Message) -> Optional[ContentPayload]:
    """Extract a normalized ContentPayload from an incoming message, or None if unsupported."""
    media_group_id = message.media_group_id

    if message.text is not None:
        return ContentPayload(content_type=ContentType.TEXT, text=message.text)

    if message.photo:
        largest = message.photo[-1]
        return ContentPayload(
            content_type=ContentType.PHOTO,
            file_id=largest.file_id,
            file_unique_id=largest.file_unique_id,
            media_group_id=media_group_id,
            caption=message.caption,
        )

    if message.video:
        return ContentPayload(
            content_type=ContentType.VIDEO,
            file_id=message.video.file_id,
            file_unique_id=message.video.file_unique_id,
            media_group_id=media_group_id,
            caption=message.caption,
        )

    if message.voice:
        return ContentPayload(
            content_type=ContentType.VOICE,
            file_id=message.voice.file_id,
            file_unique_id=message.voice.file_unique_id,
            caption=message.caption,
        )

    if message.document:
        return ContentPayload(
            content_type=ContentType.DOCUMENT,
            file_id=message.document.file_id,
            file_unique_id=message.document.file_unique_id,
            media_group_id=media_group_id,
            caption=message.caption,
        )

    if message.audio:
        return ContentPayload(
            content_type=ContentType.AUDIO,
            file_id=message.audio.file_id,
            file_unique_id=message.audio.file_unique_id,
            media_group_id=media_group_id,
            caption=message.caption,
        )

    if message.animation:
        return ContentPayload(
            content_type=ContentType.ANIMATION,
            file_id=message.animation.file_id,
            file_unique_id=message.animation.file_unique_id,
            caption=message.caption,
        )

    if message.sticker:
        return ContentPayload(
            content_type=ContentType.STICKER,
            file_id=message.sticker.file_id,
            file_unique_id=message.sticker.file_unique_id,
        )

    if message.video_note:
        return ContentPayload(
            content_type=ContentType.VIDEO_NOTE,
            file_id=message.video_note.file_id,
            file_unique_id=message.video_note.file_unique_id,
        )

    if message.location:
        text = f"{message.location.latitude},{message.location.longitude}"
        return ContentPayload(content_type=ContentType.LOCATION, text=text)

    if message.contact:
        parts = [
            message.contact.phone_number or "",
            message.contact.first_name or "",
            message.contact.last_name or "",
        ]
        return ContentPayload(content_type=ContentType.CONTACT, text="|".join(parts))

    return None


async def send_payload(
    bot: Bot,
    chat_id: int,
    payload: ContentPayload,
    caption: Optional[str] = None,
    reply_markup=None,
    reply_to_message_id: Optional[int] = None,
) -> Message:
    """Send a ContentPayload to `chat_id`, choosing the appropriate Bot API method."""
    kwargs = {}
    if reply_to_message_id is not None:
        kwargs["reply_to_message_id"] = reply_to_message_id

    text_or_caption = caption if caption is not None else payload.caption

    if payload.content_type == ContentType.TEXT:
        return await bot.send_message(
            chat_id, payload.text or "", reply_markup=reply_markup, **kwargs
        )

    if payload.content_type == ContentType.PHOTO:
        return await bot.send_photo(
            chat_id,
            photo=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.VIDEO:
        return await bot.send_video(
            chat_id,
            video=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.VOICE:
        return await bot.send_voice(
            chat_id,
            voice=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.DOCUMENT:
        return await bot.send_document(
            chat_id,
            document=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.AUDIO:
        return await bot.send_audio(
            chat_id,
            audio=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.ANIMATION:
        return await bot.send_animation(
            chat_id,
            animation=payload.file_id,
            caption=text_or_caption,
            reply_markup=reply_markup,
            **kwargs,
        )

    if payload.content_type == ContentType.STICKER:
        return await bot.send_sticker(chat_id, sticker=payload.file_id, **kwargs)

    if payload.content_type == ContentType.VIDEO_NOTE:
        return await bot.send_video_note(chat_id, video_note=payload.file_id, **kwargs)

    if payload.content_type == ContentType.LOCATION:
        lat_str, lon_str = (payload.text or "0,0").split(",")
        return await bot.send_location(
            chat_id, latitude=float(lat_str), longitude=float(lon_str), **kwargs
        )

    if payload.content_type == ContentType.CONTACT:
        phone, first_name, last_name = ((payload.text or "").split("|") + ["", "", ""])[:3]
        return await bot.send_contact(
            chat_id,
            phone_number=phone,
            first_name=first_name or "Contact",
            last_name=last_name or None,
            **kwargs,
        )

    raise ValueError(f"Unsupported content type: {payload.content_type}")


MEDIA_GROUP_INPUT_TYPES = {
    ContentType.PHOTO: InputMediaPhoto,
    ContentType.VIDEO: InputMediaVideo,
    ContentType.DOCUMENT: InputMediaDocument,
    ContentType.AUDIO: InputMediaAudio,
}
