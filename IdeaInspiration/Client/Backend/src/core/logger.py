"""Logging configuration for PrismQ Web Client Backend."""

import logging
import sys
from pathlib import Path

from .config import settings


def setup_logging() -> logging.Logger:
    """
    Set up application logging.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = settings.get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(
        log_dir / "backend.log",
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Get application logger
    logger = logging.getLogger("prismq.client.backend")
    logger.setLevel(log_level)
    
    return logger
