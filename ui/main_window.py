"""
Main application window for AudKyɛfo
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QMenu, QMessageBox,
    QFileDialog, QStatusBar, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import Qt, QSize

from ui.file_input_tab import FileInputTab
from ui.config_tab import ConfigTab
from ui.process_tab import ProcessTab
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog

from core.audio_processor import AudioProcessor
from core.config_manager import ConfigManager
from core.file_handler import add_recent_file, get_recent_files, clear_recent_files

from utils.constants import (
    APP_NAME, APP_DISPLAY_NAME, APP_VERSION,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT
)
from utils.translation_loader import translator, tr

# Set up logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window
    """

    def __init__(self):
        """Initialize the main window"""
        super().__init__()

        # Initialize components
        self.audio_processor = AudioProcessor()
        self.config_manager = ConfigManager()

        # Set up the UI
        self.setup_ui()

        # Connect signals
        self.connect_signals()

        # Load settings
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface"""
        # Set window properties
        self.setWindowTitle(tr("app.display_name", APP_DISPLAY_NAME))
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.file_input_tab = FileInputTab(self.audio_processor)
        self.config_tab = ConfigTab()
        self.process_tab = ProcessTab(self.audio_processor)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.file_input_tab, tr("ui.file_input_tab.title", "File Input"))
        self.tab_widget.addTab(self.config_tab, tr("ui.config_tab.title", "Split Configuration"))
        self.tab_widget.addTab(self.process_tab, tr("ui.process_tab.title", "Processing & Results"))

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("ui.main_window.status_ready", "Ready"))

    def create_menu_bar(self):
        """Create the menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu(tr("ui.main_window.file_menu", "&File"))

        # Open action
        open_action = QAction(QIcon(), tr("ui.main_window.open_action", "&Open Audio File..."), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        # Recent files submenu
        self.recent_files_menu = QMenu(tr("ui.main_window.recent_files", "&Recent Files"), self)
        file_menu.addMenu(self.recent_files_menu)
        self.update_recent_files_menu()

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction(QIcon(), tr("ui.main_window.exit_action", "E&xit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = self.menuBar().addMenu(tr("ui.main_window.edit_menu", "&Edit"))

        # Settings action
        settings_action = QAction(QIcon(), tr("ui.main_window.preferences_action", "&Preferences..."), self)
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)

        # Clear recent files action
        clear_recent_action = QAction(QIcon(), tr("ui.main_window.clear_recent_action", "&Clear Recent Files"), self)
        clear_recent_action.triggered.connect(self.clear_recent_files)
        edit_menu.addAction(clear_recent_action)

        # Help menu
        help_menu = self.menuBar().addMenu(tr("ui.main_window.help_menu", "&Help"))

        # How to use action
        how_to_action = QAction(QIcon(), tr("ui.main_window.how_to_action", "&How to Use"), self)
        how_to_action.triggered.connect(self.show_help)
        help_menu.addAction(how_to_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction(QIcon(), tr("ui.main_window.about_action", "&About AudKyɛfo"), self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Connect signals between components"""
        # Connect file input tab signals
        self.file_input_tab.file_loaded.connect(self.on_file_loaded)

        # Connect config tab signals
        self.config_tab.config_changed.connect(self.on_config_changed)

        # Connect process tab signals
        self.process_tab.processing_started.connect(self.on_processing_started)
        self.process_tab.processing_finished.connect(self.on_processing_finished)
        self.process_tab.processing_error.connect(self.on_processing_error)

        # Connect audio processor signals
        self.audio_processor.set_progress_callback(self.update_progress)

    def load_settings(self):
        """Load application settings"""
        # Load recent files
        self.update_recent_files_menu()

        # Load last configuration if enabled
        if self.config_manager.get_setting("remember_last_settings", True):
            last_config = self.config_manager.get_last_configuration()
            if last_config:
                self.config_tab.load_configuration(last_config)

    def update_recent_files_menu(self):
        """Update the recent files menu"""
        self.recent_files_menu.clear()

        recent_files = self.config_manager.get_recent_files()

        if not recent_files:
            no_recent_action = QAction(tr("ui.main_window.no_recent_files", "No Recent Files"), self)
            no_recent_action.setEnabled(False)
            self.recent_files_menu.addAction(no_recent_action)
            return

        for file_path in recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_file_dialog(self):
        """Open a file dialog to select an audio file"""
        file_filter = "Audio Files (*.mp3 *.wav *.aac *.ogg *.m4a *.flac);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", file_filter
        )

        if file_path:
            self.load_file(file_path)

    def open_recent_file(self):
        """Open a recently used file"""
        action = self.sender()
        if action:
            file_path = action.data()
            if file_path and os.path.exists(file_path):
                self.load_file(file_path)
            else:
                QMessageBox.warning(
                    self,
                    tr("ui.main_window.file_not_found", "File Not Found"),
                    tr("ui.main_window.file_no_longer_exists", "The file {file_path} no longer exists.").format(file_path=file_path)
                )
                self.update_recent_files_menu()

    def load_file(self, file_path: str):
        """
        Load an audio file

        Args:
            file_path: Path to the audio file
        """
        # Switch to the file input tab
        self.tab_widget.setCurrentWidget(self.file_input_tab)

        # Load the file
        self.file_input_tab.load_file(file_path)

        # Add to recent files
        self.config_manager.add_recent_file(file_path)
        self.update_recent_files_menu()

    def clear_recent_files(self):
        """Clear the list of recently used files"""
        self.config_manager.clear_recent_files()
        self.update_recent_files_menu()

    def show_settings_dialog(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec_():
            # Reload settings if the dialog was accepted
            self.load_settings()

    def show_help(self):
        """Show the help dialog"""
        QMessageBox.information(
            self,
            tr("ui.main_window.how_to_use_title", "How to Use AudKyɛfo"),
            tr("ui.main_window.how_to_use_text",
               "AudKyɛfo is an audio splitting application.\n\n"
               "1. Select an audio file in the 'File Input' tab\n"
               "2. Configure splitting options in the 'Split Configuration' tab\n"
               "3. Process the file in the 'Processing & Results' tab\n\n"
               "For more information, please refer to the documentation."
            )
        )

    def show_about_dialog(self):
        """Show the about dialog"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def on_file_loaded(self, success: bool, metadata: Dict[str, Any]):
        """
        Handle file loaded event

        Args:
            success: Whether the file was loaded successfully
            metadata: File metadata
        """
        if success:
            self.status_bar.showMessage(f"Loaded: {metadata.get('filename', '')}")

            # Enable the config tab
            self.tab_widget.setTabEnabled(1, True)

            # Switch to the config tab
            self.tab_widget.setCurrentIndex(1)

            # Update the config tab with the file metadata
            self.config_tab.set_audio_metadata(metadata)
        else:
            self.status_bar.showMessage("Error loading file")

    def on_config_changed(self, config: Dict[str, Any]):
        """
        Handle configuration changed event

        Args:
            config: New configuration
        """
        # Update the process tab with the new configuration
        self.process_tab.set_configuration(config)

        # Enable the process tab
        self.tab_widget.setTabEnabled(2, True)

    def on_processing_started(self):
        """Handle processing started event"""
        self.status_bar.showMessage("Processing...")

        # Disable the file input and config tabs
        self.tab_widget.setTabEnabled(0, False)
        self.tab_widget.setTabEnabled(1, False)

    def on_processing_finished(self, output_files: List[str]):
        """
        Handle processing finished event

        Args:
            output_files: List of output file paths
        """
        self.status_bar.showMessage(f"Processing complete. Created {len(output_files)} files.")

        # Enable the file input and config tabs
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setTabEnabled(1, True)

        # Save the last configuration
        self.config_manager.save_last_configuration(self.config_tab.get_configuration())

    def on_processing_error(self, error_message: str):
        """
        Handle processing error event

        Args:
            error_message: Error message
        """
        self.status_bar.showMessage(f"Error: {error_message}")

        # Enable the file input and config tabs
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setTabEnabled(1, True)

    def update_progress(self, progress: int, message: str):
        """
        Update the progress status

        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        self.status_bar.showMessage(f"{message} ({progress}%)")

        # Update the process tab
        self.process_tab.update_progress(progress, message)

    def update_ui_language(self):
        """Update the UI with the current language"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Updating UI language")

        # Update window title
        self.setWindowTitle(tr("app.display_name", APP_DISPLAY_NAME))
        logger.debug(f"Updated window title to: {self.windowTitle()}")

        # Update tab titles
        self.tab_widget.setTabText(0, tr("ui.file_input_tab.title", "Select Audio File"))
        self.tab_widget.setTabText(1, tr("ui.config_tab.title", "Split Configuration"))
        self.tab_widget.setTabText(2, tr("ui.process_tab.title", "Processing & Results"))
        logger.debug("Updated tab titles")

        # Update menu bar (recreate it)
        self.menuBar().clear()
        self.create_menu_bar()
        logger.debug("Recreated menu bar")

        # Update status bar
        if self.status_bar.currentMessage() == "Ready" or self.status_bar.currentMessage() == tr("ui.main_window.status_ready", "Ready"):
            self.status_bar.showMessage(tr("ui.main_window.status_ready", "Ready"))
            logger.debug(f"Updated status bar message to: {self.status_bar.currentMessage()}")

        # Update all tabs
        if hasattr(self.file_input_tab, 'update_translations'):
            logger.debug("Updating FileInputTab translations")
            self.file_input_tab.update_translations()

        if hasattr(self.config_tab, 'update_translations'):
            logger.debug("Updating ConfigTab translations")
            self.config_tab.update_translations()

        if hasattr(self.process_tab, 'update_translations'):
            logger.debug("Updating ProcessTab translations")
            self.process_tab.update_translations()

        # Force a repaint of the UI
        self.repaint()
        logger.info("UI language update complete")

    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event

        Args:
            event: Close event
        """
        # Save settings before closing
        self.config_manager.save_last_configuration(self.config_tab.get_configuration())

        event.accept()