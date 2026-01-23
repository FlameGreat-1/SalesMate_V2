"""Logging utilities for SalesMate"""

import logging
import sys
from typing import Optional

from src.config import settings


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only add handler if logger doesn't have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set log level
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    else:
        # Use log level from settings
        logger.setLevel(getattr(logging, settings.app.log_level.upper()))
    
    return logger
