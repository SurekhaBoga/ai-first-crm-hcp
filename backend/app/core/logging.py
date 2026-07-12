"""Process-wide logging configuration, applied once at app startup."""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )

    # Quiet noisy third-party loggers down to warnings unless the app itself
    # is running at DEBUG.
    if settings.LOG_LEVEL.upper() != "DEBUG":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
