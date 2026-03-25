"""
Production-ready logging configuration
Uses structlog for structured JSON logging in production
"""

import logging
import sys
import structlog
from typing import Any


def configure_logging(environment: str = "development", log_level: str = "INFO"):
    """
    Configure logging based on environment

    Args:
        environment: "development" or "production"
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    is_production = environment.lower() == "production"

    # Set log level
    log_level_num = getattr(logging, log_level.upper(), logging.INFO)

    if is_production:
        # Production: Structured JSON logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure root logger for JSON output
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
            )
        )

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level_num)

        # Suppress verbose third-party logs in production
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

    else:
        # Development: Human-readable colored output
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure root logger for console output
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level_num)


def get_logger(name: str) -> Any:
    """
    Get a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance (structlog or stdlib logging)
    """
    return structlog.get_logger(name)
