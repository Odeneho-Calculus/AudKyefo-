"""
Validation functions for the AudKyɛfo application
"""

import os
import re
from typing import Tuple, List, Optional
import logging
from utils.constants import SUPPORTED_INPUT_FORMATS, SUPPORTED_OUTPUT_FORMATS

# Set up logging
logger = logging.getLogger(__name__)

def is_valid_audio_file(file_path: str) -> bool:
    """
    Check if a file is a valid audio file based on its extension

    Args:
        file_path: Path to the file

    Returns:
        True if the file has a supported audio extension, False otherwise
    """
    if not os.path.isfile(file_path):
        return False

    extension = os.path.splitext(file_path)[1][1:].lower()
    return extension in SUPPORTED_INPUT_FORMATS

def is_valid_output_format(format_str: str) -> bool:
    """
    Check if a format string is a valid output format

    Args:
        format_str: Format string

    Returns:
        True if the format is supported, False otherwise
    """
    return format_str.lower() in SUPPORTED_OUTPUT_FORMATS

def is_valid_time_format(time_str: str) -> bool:
    """
    Check if a time string is in valid MM:SS format

    Args:
        time_str: Time string

    Returns:
        True if the time string is valid, False otherwise
    """
    if not time_str:
        return False

    pattern = r"^(\d+):([0-5]\d)$"
    return bool(re.match(pattern, time_str))

def is_valid_time_range(start_time: str, end_time: str, total_duration: float) -> Tuple[bool, Optional[str]]:
    """
    Check if a time range is valid

    Args:
        start_time: Start time in MM:SS format
        end_time: End time in MM:SS format
        total_duration: Total duration of the audio in seconds

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not is_valid_time_format(start_time):
        return False, f"Invalid start time format: {start_time}. Expected format: MM:SS"

    if not is_valid_time_format(end_time):
        return False, f"Invalid end time format: {end_time}. Expected format: MM:SS"

    # Convert to seconds
    start_seconds = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
    end_seconds = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])

    if start_seconds >= end_seconds:
        return False, "Start time must be less than end time"

    if start_seconds < 0:
        return False, "Start time cannot be negative"

    if end_seconds > total_duration:
        return False, f"End time exceeds audio duration ({int(total_duration // 60):02d}:{int(total_duration % 60):02d})"

    return True, None

def is_valid_output_directory(directory: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a directory is a valid output directory

    Args:
        directory: Path to the directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not directory:
        return False, "Output directory cannot be empty"

    # Check if directory exists
    if not os.path.exists(directory):
        try:
            # Try to create it
            os.makedirs(directory)
        except Exception as e:
            return False, f"Cannot create output directory: {e}"

    # Check if it's a directory
    if not os.path.isdir(directory):
        return False, "Output path is not a directory"

    # Check if it's writable
    if not os.access(directory, os.W_OK):
        return False, "Output directory is not writable"

    return True, None

def is_valid_naming_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a naming pattern is valid

    Args:
        pattern: Naming pattern

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "Naming pattern cannot be empty"

    # Check for required variables
    if "{original_name}" not in pattern:
        return False, "Naming pattern must include {original_name}"

    if "{number" not in pattern and "{start_time}" not in pattern and "{end_time}" not in pattern:
        return False, "Naming pattern must include at least one of: {number}, {start_time}, {end_time}"

    # Check for invalid characters in file names
    invalid_chars = r'[<>:"/\\|?*]'
    # Remove the variables from the pattern before checking
    test_pattern = pattern
    for var in ["{original_name}", "{number}", "{number:03d}", "{start_time}", "{end_time}"]:
        test_pattern = test_pattern.replace(var, "")

    if re.search(invalid_chars, test_pattern):
        return False, "Naming pattern contains invalid characters for file names"

    return True, None