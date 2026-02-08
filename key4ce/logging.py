"""Logging system for Key4ce."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from key4ce.config.manager import get_config_dir


# Global logger instance
_logger: Optional[logging.Logger] = None


def get_log_path() -> Path:
    """Get the path for log files."""
    config_dir = get_config_dir()
    log_dir = config_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """Set up logging for Key4ce.
    
    Args:
        level: Logging level (default DEBUG)
        
    Returns:
        Configured logger
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Create logger
    _logger = logging.getLogger("key4ce")
    _logger.setLevel(level)
    _logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter(
        "%(levelname)-8s | %(message)s"
    )
    
    # File handler - rotating daily
    log_path = get_log_path()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"key4ce_{today}.log"
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)
    
    # Also log errors to a separate file
    error_file = log_path / "errors.log"
    error_handler = logging.FileHandler(error_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    _logger.addHandler(error_handler)
    
    # Console handler (only for warnings and above in production)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    _logger.addHandler(console_handler)
    
    _logger.info("=" * 60)
    _logger.info("Key4ce logging initialized")
    _logger.info(f"Log file: {log_file}")
    _logger.info("=" * 60)
    
    return _logger


def get_logger(name: str = "key4ce") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (will be prefixed with 'key4ce.')
        
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        setup_logging()
    
    if name == "key4ce":
        return _logger
    
    return logging.getLogger(f"key4ce.{name}")


def log_exception(exc: Exception, context: str = "") -> None:
    """Log an exception with full traceback.
    
    Args:
        exc: Exception to log
        context: Additional context about where the error occurred
    """
    logger = get_logger()
    if context:
        logger.exception(f"{context}: {exc}")
    else:
        logger.exception(f"Unhandled exception: {exc}")


# Convenience functions
def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a warning message."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a critical message."""
    get_logger().critical(msg, *args, **kwargs)
