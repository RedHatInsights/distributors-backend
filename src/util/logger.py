"""Logging configuration for the distributor API."""

import logging
import sys

from util.settings import constants


def get_logger(name: str = "distributor-api") -> logging.Logger:
    """Set up and configure a logger with console output."""
    format_string = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(format_string))
    logging.basicConfig(level=constants.LOG_LEVEL.upper(), handlers=[handler])
    return logging.getLogger(name)
