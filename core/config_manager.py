"""
Settings management for AudKyɛfo
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from utils.constants import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_NAMING_PATTERN,
    DEFAULT_OVERLAP_DURATION
)
from utils.helpers import ensure_directory_exists

# Set up logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Class for managing application settings
    """

    def __init__(self):
        """Initialize the config manager"""
        self.config_dir = os.path.expanduser("~/.audkyefo")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the config file

        Returns:
            Dictionary containing the settings
        """
        default_settings = {
            "output_format": DEFAULT_OUTPUT_FORMAT,
            "output_directory": os.path.expanduser("~/Music/AudKyefo"),
            "naming_pattern": DEFAULT_NAMING_PATTERN,
            "overlap_duration": DEFAULT_OVERLAP_DURATION,
            "remember_last_settings": True,
            "theme": "dark",
            "language": "en",
            "recent_files": []
        }

        if not os.path.exists(self.config_file):
            # Create default settings file
            ensure_directory_exists(self.config_dir)
            self._save_settings(default_settings)
            return default_settings

        try:
            with open(self.config_file, 'r') as f:
                settings = json.load(f)

            # Update with any missing default settings
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value

            return settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return default_settings

    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to the config file

        Args:
            settings: Dictionary containing the settings

        Returns:
            True if the settings were saved successfully, False otherwise
        """
        try:
            ensure_directory_exists(self.config_dir)
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value

        Args:
            key: Setting key
            default: Default value if the setting doesn't exist

        Returns:
            Setting value
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a setting value

        Args:
            key: Setting key
            value: Setting value

        Returns:
            True if the setting was saved successfully, False otherwise
        """
        self.settings[key] = value
        return self._save_settings(self.settings)

    def add_recent_file(self, file_path: str, max_count: int = 10) -> bool:
        """
        Add a file to the list of recently used files

        Args:
            file_path: Path to the file
            max_count: Maximum number of files to keep

        Returns:
            True if the list was updated successfully, False otherwise
        """
        recent_files = self.settings.get("recent_files", [])

        # Remove the file if it already exists in the list
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add the file to the beginning of the list
        recent_files.insert(0, file_path)

        # Limit the number of files
        recent_files = recent_files[:max_count]

        self.settings["recent_files"] = recent_files
        return self._save_settings(self.settings)

    def get_recent_files(self, max_count: int = 10) -> list:
        """
        Get the list of recently used files

        Args:
            max_count: Maximum number of files to return

        Returns:
            List of file paths
        """
        recent_files = self.settings.get("recent_files", [])

        # Filter out files that no longer exist
        recent_files = [f for f in recent_files if os.path.exists(f)]

        # Update the settings if files were removed
        if len(recent_files) != len(self.settings.get("recent_files", [])):
            self.settings["recent_files"] = recent_files
            self._save_settings(self.settings)

        return recent_files[:max_count]

    def clear_recent_files(self) -> bool:
        """
        Clear the list of recently used files

        Returns:
            True if the list was cleared successfully, False otherwise
        """
        self.settings["recent_files"] = []
        return self._save_settings(self.settings)

    def save_last_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Save the last used configuration

        Args:
            config: Dictionary containing the configuration

        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        if not self.settings.get("remember_last_settings", True):
            return True

        for key, value in config.items():
            self.settings[f"last_{key}"] = value

        return self._save_settings(self.settings)

    def get_last_configuration(self) -> Dict[str, Any]:
        """
        Get the last used configuration

        Returns:
            Dictionary containing the configuration
        """
        if not self.settings.get("remember_last_settings", True):
            return {}

        config = {}
        for key in self.settings:
            if key.startswith("last_"):
                config[key[5:]] = self.settings[key]

        return config