"""Shared enum types used across ORM models."""

from __future__ import annotations

import enum


class LanguageEnum(str, enum.Enum):
    """Supported interface languages."""

    UZ = "uz"
    RU = "ru"
    EN = "en"


class AppealStatus(str, enum.Enum):
    """Lifecycle status of an appeal."""

    NEW = "new"
    IN_PROCESS = "in_process"
    ANSWERED = "answered"
    CLOSED = "closed"


class SenderType(str, enum.Enum):
    """Who authored a given appeal message."""

    USER = "user"
    EMPLOYEE = "employee"
    SYSTEM = "system"


class ContentType(str, enum.Enum):
    """Type of content carried by an appeal message / attachment."""

    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    DOCUMENT = "document"
    AUDIO = "audio"
    ANIMATION = "animation"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    VIDEO_NOTE = "video_note"


class AdminRole(str, enum.Enum):
    """Role of an administrator/employee."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EMPLOYEE = "employee"
