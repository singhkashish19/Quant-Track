"""Structured logging setup for QuantTrack."""

import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings


def _ensure_log_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def configure_logger() -> logging.Logger:
    _ensure_log_directory(settings.log_file)

    logger = logging.getLogger("quanttrack")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = configure_logger()
