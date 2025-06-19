#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AudKyɛfo - Audio Splitter
Main entry point for the application
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from core.config_manager import ConfigManager
from utils.style_loader import apply_stylesheet
from utils.logger import setup_logging
from utils.translation_loader import translator

# Set up logging
setup_logging(
    log_level=logging.INFO,
    log_file=os.path.expanduser("~/.audkyefo/logs/app.log")
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the application"""
    # Create the application
    app = QApplication(sys.argv)

    # Load configuration
    config_manager = ConfigManager()

    # Set language
    language = config_manager.get_setting("language", "en")
    if translator.set_language(language):
        logger.info(f"Set language to: {language}")
    else:
        logger.warning(f"Failed to set language to: {language}")

    # Set application name and display name
    app_name = translator.get_translation("app.name", "AudKyɛfo")
    app_display_name = translator.get_translation("app.display_name", "AudKyɛfo - Audio Splitter")
    app.setApplicationName(app_name)
    app.setApplicationDisplayName(app_display_name)

    # Set application icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        logger.warning(f"Application icon not found at {icon_path}")

    # Apply stylesheet
    theme = config_manager.get_setting("theme", "light")
    if apply_stylesheet(app, theme):
        logger.info(f"Applied {theme} theme stylesheet")
    else:
        logger.warning(f"Failed to apply {theme} theme stylesheet")

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()