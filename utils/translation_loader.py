"""
Translation loader for AudKyɛfo
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class TranslationLoader:
    """
    Class for loading and managing translations
    """

    def __init__(self):
        """Initialize the translation loader"""
        self.translations = {}
        self.current_language = "en"
        self.available_languages = []
        self.load_translations()

    def load_translations(self) -> None:
        """Load all available translations"""
        translations_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "resources", "translations"
        )

        if not os.path.exists(translations_dir):
            logger.warning(f"Translations directory not found: {translations_dir}")
            return

        # Load all JSON files in the translations directory
        for filename in os.listdir(translations_dir):
            if filename.endswith(".json"):
                language_code = os.path.splitext(filename)[0]
                file_path = os.path.join(translations_dir, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.translations[language_code] = json.load(f)
                    logger.info(f"Loaded translation: {language_code}")

                    # Add to available languages
                    if language_code not in self.available_languages:
                        self.available_languages.append(language_code)

                except Exception as e:
                    logger.error(f"Error loading translation {language_code}: {e}")

    def set_language(self, language_code: str) -> bool:
        """
        Set the current language

        Args:
            language_code: Language code (e.g., "en", "tw")

        Returns:
            True if the language was set successfully, False otherwise
        """
        if language_code in self.translations:
            # Only reload if the language is actually changing
            if self.current_language != language_code:
                self.current_language = language_code
                logger.info(f"Set language to: {language_code}")

                # Reload translations to ensure we have the latest
                self.reload_translations()
                logger.info(f"Reloaded translations after language change to: {language_code}")
            else:
                logger.info(f"Language already set to: {language_code}")
            return True
        else:
            logger.warning(f"Language not found: {language_code}")
            return False

    def get_translation(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a translation for a key

        Args:
            key: Translation key (e.g., "ui.main_window.file_menu")
            default: Default value if the key doesn't exist

        Returns:
            Translated string
        """
        # Try to get the translation in the current language
        translation = self._get_nested_value(self.translations.get(self.current_language, {}), key)

        # If not found, try to get the English translation
        if translation is None and self.current_language != "en":
            translation = self._get_nested_value(self.translations.get("en", {}), key)
            if translation is not None:
                logger.debug(f"Using English fallback for key: {key}")

        # If still not found, return the default value or the key itself
        if translation is None:
            if default is not None:
                logger.debug(f"Using default value for key: {key} in language: {self.current_language}")
                return default
            else:
                # Log missing translation key for developers
                logger.warning(f"Missing translation key: {key} in language: {self.current_language}")
                return key

        logger.debug(f"Translated '{key}' to '{translation}' in {self.current_language}")
        return translation

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """
        Get a nested value from a dictionary using a dot-separated key

        Args:
            data: Dictionary to search
            key: Dot-separated key (e.g., "ui.main_window.file_menu")

        Returns:
            Value if found, None otherwise
        """
        keys = key.split(".")
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value if isinstance(value, str) else None

    def get_available_languages(self) -> List[Tuple[str, str]]:
        """
        Get a list of available languages

        Returns:
            List of tuples containing language code and language name
        """
        languages = []

        for lang_code in self.available_languages:
            # Get the language name from the translation file if available
            lang_name = self._get_nested_value(self.translations.get(lang_code, {}), "language.name")

            # If not found, use default names
            if lang_name is None:
                if lang_code == "en":
                    lang_name = "English"
                elif lang_code == "tw":
                    lang_name = "Twi"
                else:
                    lang_name = lang_code.upper()

            languages.append((lang_code, lang_name))

        return languages

    def get_current_language(self) -> str:
        """
        Get the current language code

        Returns:
            Current language code
        """
        return self.current_language

    def reload_translations(self) -> None:
        """
        Reload all translation files
        Useful when translations have been modified
        """
        current_lang = self.current_language
        self.translations = {}
        self.available_languages = []
        self.load_translations()

        # Restore the current language if it's still available
        if current_lang in self.translations:
            self.current_language = current_lang
        else:
            self.current_language = "en"

# Create a singleton instance
translator = TranslationLoader()

def tr(key: str, default: Optional[str] = None) -> str:
    """
    Get a translation for a key

    Args:
        key: Translation key (e.g., "ui.main_window.file_menu")
        default: Default value if the key doesn't exist

    Returns:
        Translated string
    """
    return translator.get_translation(key, default)

def get_available_languages() -> List[Tuple[str, str]]:
    """
    Get a list of available languages

    Returns:
        List of tuples containing language code and language name
    """
    return translator.get_available_languages()

def get_current_language() -> str:
    """
    Get the current language code

    Returns:
        Current language code
    """
    return translator.get_current_language()

def set_language(language_code: str) -> bool:
    """
    Set the current language

    Args:
        language_code: Language code (e.g., "en", "tw")

    Returns:
        True if the language was set successfully, False otherwise
    """
    return translator.set_language(language_code)