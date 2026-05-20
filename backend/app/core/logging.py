"""structlog configuration.

Dev (`APP_ENV=dev`): pretty colorized console output.
Prod (anything else): JSON lines for log aggregators.

Also routes stdlib `logging` (uvicorn, sqlalchemy, asyncpg) through structlog so
every line in the process shares one format.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Idempotently configure structlog + stdlib logging."""

    is_dev = settings.app_env == "dev"
    level = logging.DEBUG if settings.debug else logging.INFO

    # Shared pre-processors for both structlog-native and foreign (stdlib) logs.
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.add_logger_name,
    ]

    final_renderer: Any
    if is_dev:
        final_renderer = structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
    else:
        final_renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Route stdlib loggers (uvicorn, sqlalchemy, asyncpg, etc.) through structlog.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            final_renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    # Replace any pre-existing handlers so output is consistent.
    root.handlers = [handler]
    root.setLevel(level)

    # Quiet down noisy libraries unless we're explicitly debugging.
    for noisy in ("sqlalchemy.engine", "asyncpg", "httpx"):
        logging.getLogger(noisy).setLevel(logging.DEBUG if settings.debug else logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name) if name else structlog.get_logger()
