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
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """
    Colored log formatter using ANSI escape codes.

    Colors are applied to log levels for better visibility in the terminal.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: bool = True,
    ):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._supports_color()

    def _supports_color(self) -> bool:
        """
        Check if the terminal supports color output.

        Returns:
            True if colors are supported, False otherwise
        """
        if not hasattr(sys.stderr, "isatty"):
            return False
        if not sys.stderr.isatty():
            return False

        try:
            import platform

            if platform.system() == "Windows":
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

        return True

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors.

        Args:
            record: The log record to format

        Returns:
            Formatted log string with ANSI color codes
        """
        if self.use_colors:
            levelname_original = record.levelname
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{self.BOLD}{record.levelname}{self.RESET}"
            formatted = super().format(record)
            record.levelname = levelname_original

            return formatted
        else:
            return super().format(record)


def setup_logger(
    name: str = "mezon",
    log_level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger for the Mezon SDK.

    Args:
        name: The logger name (default: "mezon")
        log_level: The logging level (default: logging.INFO)
        log_format: Custom log format string (optional)
        date_format: Custom date format string (optional)
        use_colors: Enable colored output (default: True)

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

        formatter = ColoredFormatter(
            log_format, datefmt=date_format, use_colors=use_colors
        )
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
