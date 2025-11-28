"""
Centralized logging utilities for the Venice SDK.

This module provides a single helper that configures the package-level logger
so SDK consumers get consistent, structured output without duplicating boilerplate.
"""

from __future__ import annotations

import json
import logging
from logging import Logger
from typing import Optional, TextIO

DEFAULT_LOGGER_NAME = "venice_sdk"
DEFAULT_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class StructuredFormatter(logging.Formatter):
    """A simple JSON formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(
    level: int = logging.INFO,
    *,
    structured: bool = False,
    stream: Optional[TextIO] = None,
    force: bool = False,
) -> Logger:
    """
    Configure and return the root Venice SDK logger.

    Args:
        level: Logging level applied to the package logger and attached handlers.
        structured: When True, emit newline-delimited JSON payloads instead of the default format.
        stream: Optional stream to target (defaults to sys.stderr).
        force: When True, remove any previously attached handlers before configuring a new one.
    """

    logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    if force:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)

    if not logger.handlers:
        handler = logging.StreamHandler(stream)
        if structured:
            formatter: logging.Formatter = StructuredFormatter(datefmt=DEFAULT_DATE_FORMAT)
        else:
            formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)

        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            handler.setLevel(level)

    logger.setLevel(level)
    logger.propagate = False
    return logger
