"""
Logging configuration for AudKyɛfo
"""

import os
import logging
import logging.handlers
from typing import Optional

def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Set up logging for the application

    Args:
        log_level: Logging level (default: INFO)
        log_file: Path to the log file (default: None)
    """
    # Create the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create a file handler if a log file is specified
    if log_file:
        # Ensure the directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create a rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1 MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set the logging level for third-party libraries
    logging.getLogger("pydub").setLevel(logging.WARNING)
    logging.getLogger("mutagen").setLevel(logging.WARNING)
    logging.getLogger("PyQt5").setLevel(logging.WARNING)