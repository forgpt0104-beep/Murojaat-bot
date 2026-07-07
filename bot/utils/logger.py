"""Centralized loguru configuration."""

from __future__ import annotations

import sys

from loguru import logger

from bot.config import settings


def setup_logging() -> None:
    """Configure loguru sinks: colored console + rotating file sinks."""
    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        backtrace=False,
        diagnose=False,
    )

    logs_path = settings.logs_path

    logger.add(
        logs_path / "bot.log",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    logger.add(
        logs_path / "errors.log",
        level="ERROR",
        rotation="10 MB",
        retention="90 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    logger.info("Logging configured (level={})", settings.LOG_LEVEL)
