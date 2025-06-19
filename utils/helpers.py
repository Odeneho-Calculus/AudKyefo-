"""
Helper functions for the AudKyɛfo application
"""

import os
import re
from typing import List, Tuple, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string in MM:SS format
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def parse_time(time_str: str) -> float:
    """
    Parse time string in MM:SS format to seconds

    Args:
        time_str: Time string in MM:SS format

    Returns:
        Time in seconds

    Raises:
        ValueError: If the time string is not in the correct format
    """
    if not time_str:
        return 0.0

    # Check if the format is MM:SS
    pattern = r"^(\d+):([0-5]\d)$"
    match = re.match(pattern, time_str)

    if not match:
        raise ValueError(f"Invalid time format: {time_str}. Expected format: MM:SS")

    minutes, seconds = match.groups()
    return int(minutes) * 60 + int(seconds)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path

    Args:
        file_path: Path to the file

    Returns:
        File extension without the dot
    """
    return os.path.splitext(file_path)[1][1:].lower()

def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"

def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure that a directory exists, create it if it doesn't

    Args:
        directory: Path to the directory

    Returns:
        True if the directory exists or was created, False otherwise
    """
    if not directory:
        return False

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def generate_output_filename(
    original_name: str,
    part_number: int,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    pattern: str = "{original_name}_part_{number:03d}",
    extension: str = "mp3"
) -> str:
    """
    Generate an output filename based on the pattern

    Args:
        original_name: Original file name without extension
        part_number: Part number
        start_time: Start time in seconds (optional)
        end_time: End time in seconds (optional)
        pattern: Naming pattern
        extension: Output file extension

    Returns:
        Generated filename
    """
    # Remove extension from original name if present
    original_name = os.path.splitext(original_name)[0]

    # Replace variables in the pattern
    filename = pattern.format(
        original_name=original_name,
        number=part_number,
        start_time=format_time(start_time) if start_time is not None else "",
        end_time=format_time(end_time) if end_time is not None else ""
    )

    # Add extension
    return f"{filename}.{extension}"

def check_disk_space(directory: str, required_space: int) -> bool:
    """
    Check if there's enough disk space in the specified directory

    Args:
        directory: Path to the directory
        required_space: Required space in bytes

    Returns:
        True if there's enough space, False otherwise
    """
    try:
        if not os.path.exists(directory):
            # Check the parent directory if it doesn't exist
            parent_dir = os.path.dirname(directory)
            if not parent_dir:
                parent_dir = os.getcwd()
            directory = parent_dir

        # Get free space
        free_space = os.statvfs(directory).f_frsize * os.statvfs(directory).f_bavail
        return free_space >= required_space
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        # Return True to avoid blocking the operation if we can't check
        return True