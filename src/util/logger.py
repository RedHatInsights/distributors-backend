"""Logging configuration for the distributor API."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from util.settings import constants


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with structured fields.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted log string.
        """
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add any extra fields that were passed to the logger
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str = "distributor-api") -> logging.Logger:
    """Set up and configure a logger with console output.

    Args:
        name: Name of the logger.

    Returns:
        Configured logger instance.
    """
    from util.settings import constants

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger(name)

    # Set log level based on DEBUG_MODE
    # INFO for production (security/compliance logs)
    # DEBUG when DEBUG_MODE is enabled
    log_level = logging.DEBUG if constants.DEBUG_MODE else logging.INFO
    logger.setLevel(log_level)

    # Avoid duplicate handlers if logger already configured
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
    """Log a message with additional context fields.

    Args:
        logger: The logger instance to use.
        level: Log level (info, warning, error, etc.).
        message: The log message.
        **kwargs: Additional fields to include in the structured log.
    """
    record = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper()),
        "(unknown file)",
        0,
        message,
        (),
        None,
    )
    record.extra_fields = kwargs
    logger.handle(record)


def log_debug(logger: logging.Logger, message: str, **kwargs) -> None:
    """Log a debug message with context (only when DEBUG_MODE is enabled).

    Args:
        logger: The logger instance to use.
        message: The debug message.
        **kwargs: Additional fields to include in the structured log.
    """
    if constants.DEBUG_MODE:
        log_with_context(logger, "debug", message, **kwargs)
