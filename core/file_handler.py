"""
File I/O operations for AudKyɛfo
"""

import os
import shutil
import logging
from typing import List, Dict, Optional, Tuple
from utils.constants import SUPPORTED_INPUT_FORMATS
from utils.helpers import get_file_extension, ensure_directory_exists

# Set up logging
logger = logging.getLogger(__name__)

def get_recent_files(max_count: int = 10) -> List[str]:
    """
    Get the list of recently used files from the settings

    Args:
        max_count: Maximum number of files to return

    Returns:
        List of file paths
    """
    # This would normally read from a settings file
    # For now, return an empty list
    return []

def add_recent_file(file_path: str, max_count: int = 10) -> None:
    """
    Add a file to the list of recently used files

    Args:
        file_path: Path to the file
        max_count: Maximum number of files to keep
    """
    # This would normally update a settings file
    pass

def clear_recent_files() -> None:
    """Clear the list of recently used files"""
    # This would normally update a settings file
    pass

def get_default_output_directory() -> str:
    """
    Get the default output directory

    Returns:
        Path to the default output directory
    """
    # Use the user's music directory if available, otherwise use the home directory
    if os.path.exists(os.path.expanduser("~/Music")):
        return os.path.expanduser("~/Music/AudKyefo")
    else:
        return os.path.expanduser("~/AudKyefo")

def copy_file(source: str, destination: str) -> bool:
    """
    Copy a file from source to destination

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        True if the file was copied successfully, False otherwise
    """
    try:
        # Ensure the destination directory exists
        dest_dir = os.path.dirname(destination)
        if not ensure_directory_exists(dest_dir):
            return False

        # Copy the file
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return False

def delete_file(file_path: str) -> bool:
    """
    Delete a file

    Args:
        file_path: Path to the file

    Returns:
        True if the file was deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

def get_files_in_directory(directory: str, filter_audio: bool = True) -> List[str]:
    """
    Get the list of files in a directory

    Args:
        directory: Path to the directory
        filter_audio: If True, only return audio files

    Returns:
        List of file paths
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return []

    files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if not os.path.isfile(file_path):
            continue

        if filter_audio:
            extension = get_file_extension(file_path)
            if extension not in SUPPORTED_INPUT_FORMATS:
                continue

        files.append(file_path)

    return files

def open_directory(directory: str) -> bool:
    """
    Open a directory in the file explorer

    Args:
        directory: Path to the directory

    Returns:
        True if the directory was opened successfully, False otherwise
    """
    try:
        if not os.path.exists(directory):
            return False

        # Use the appropriate command based on the platform
        if os.name == 'nt':  # Windows
            os.startfile(directory)
        elif os.name == 'posix':  # macOS and Linux
            import subprocess
            if os.path.exists('/usr/bin/open'):  # macOS
                subprocess.Popen(['open', directory])
            elif os.path.exists('/usr/bin/xdg-open'):  # Linux
                subprocess.Popen(['xdg-open', directory])
            else:
                return False
        else:
            return False

        return True
    except Exception as e:
        logger.error(f"Error opening directory: {e}")
        return False