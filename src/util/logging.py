"""
Logging configuration for the NYC Landmarks Research Agent.
Provides a centralized logging setup for the application.
"""
import logging
import sys
from typing import Optional

from src.config import settings


def configure_logging(level: Optional[str] = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level. If not provided, uses the level from settings.
    """
    log_level = level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_library_loggers()
    
    # Log configuration complete
    root_logger.debug(f"Logging configured with level: {log_level}")


def configure_library_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    # Set higher log level for some chatty libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
