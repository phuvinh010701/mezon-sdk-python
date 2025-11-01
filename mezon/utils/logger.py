"""
Copyright 2020 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Optional


def setup_logger(
    name: str = "mezon",
    log_level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger for the Mezon SDK.

    Args:
        name: The logger name (default: "mezon")
        log_level: The logging level (default: logging.INFO)
        log_format: Custom log format string (optional)
        date_format: Custom date format string (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

        if log_format is None:
            log_format = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        if date_format is None:
            date_format = "%Y-%m-%d %H:%M:%S"

        formatter = logging.Formatter(log_format, datefmt=date_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: The logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def disable_logging(name: str = "mezon") -> None:
    """
    Disable logging for the specified logger.

    Args:
        name: The logger name (default: "mezon")
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL + 1)
    logger.disabled = True


def enable_logging(name: str = "mezon", log_level: int = logging.INFO) -> None:
    """
    Enable logging for the specified logger.

    Args:
        name: The logger name (default: "mezon")
        log_level: The logging level (default: logging.INFO)
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.disabled = False
