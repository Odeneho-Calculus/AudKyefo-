"""
Settings dialog for AudKyɛfo
"""

import os
import logging
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFormLayout, QComboBox, QCheckBox, QFileDialog, QGroupBox,
    QDialogButtonBox, QScrollArea, QFrame, QWidget, QLineEdit
)
from PyQt5.QtCore import Qt

from core.config_manager import ConfigManager
from utils.constants import (
    SUPPORTED_OUTPUT_FORMATS,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_NAMING_PATTERN
)
from utils.translation_loader import tr, translator

# Set up logging
logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """
    Dialog for application settings
    """

    def __init__(self, config_manager: ConfigManager, parent=None):
        """
        Initialize the settings dialog

        Args:
            config_manager: Configuration manager instance
            parent: Parent widget
        """
        super().__init__(parent)

        self.config_manager = config_manager

        # Set up the UI
        self.setup_ui()

        # Load settings
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface"""
        # Set window properties
        self.setWindowTitle(tr("ui.settings_dialog.title", "Preferences"))
        self.setMinimumWidth(400)
        self.resize(500, 450)

        # Create a scroll area for the content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Create a content widget for the scroll area
        content_widget = QWidget()

        # Main layout for the content widget
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)

        # Create a layout for the dialog itself
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)

        # Output settings group
        output_group = QGroupBox(tr("ui.settings_dialog.output_group", "Output Settings"))
        output_layout = QFormLayout(output_group)
        output_layout.setContentsMargins(20, 20, 20, 20)
        output_layout.setSpacing(10)
        main_layout.addWidget(output_group)

        # Default output format
        self.format_combo = QComboBox()
        for fmt in SUPPORTED_OUTPUT_FORMATS:
            self.format_combo.addItem(fmt.upper(), fmt)
        output_layout.addRow(tr("ui.settings_dialog.default_format_label", "Default Output Format:"), self.format_combo)

        # Default output location
        output_location_layout = QHBoxLayout()
        self.output_location_edit = QLabel()
        self.output_location_button = QPushButton(tr("ui.settings_dialog.browse_button", "Browse..."))
        output_location_layout.addWidget(self.output_location_edit)
        output_location_layout.addWidget(self.output_location_button)
        output_layout.addRow(tr("ui.settings_dialog.default_location_label", "Default Output Location:"), output_location_layout)

        # Connect the browse button
        self.output_location_button.clicked.connect(self.browse_output_location)

        # General settings group
        general_group = QGroupBox(tr("ui.settings_dialog.general_group", "General Settings"))
        general_layout = QFormLayout(general_group)
        general_layout.setContentsMargins(20, 20, 20, 20)
        general_layout.setSpacing(10)
        main_layout.addWidget(general_group)

        # Remember last settings
        self.remember_check = QCheckBox()
        general_layout.addRow(tr("ui.settings_dialog.remember_settings_label", "Remember Last Settings:"), self.remember_check)

        # Language
        self.language_combo = QComboBox()

        # Get available languages from the translation loader
        from utils.translation_loader import get_available_languages
        available_languages = get_available_languages()

        for lang_code, lang_name in available_languages:
            self.language_combo.addItem(lang_name, lang_code)

        general_layout.addRow(tr("ui.settings_dialog.language_label", "Language:"), self.language_combo)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr("ui.settings_dialog.theme_light", "Light"), "light")
        self.theme_combo.addItem(tr("ui.settings_dialog.theme_dark", "Dark"), "dark")
        general_layout.addRow(tr("ui.settings_dialog.theme_label", "Theme:"), self.theme_combo)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Translate standard buttons
        button_box.button(QDialogButtonBox.Ok).setText(tr("ui.common.ok", "OK"))
        button_box.button(QDialogButtonBox.Cancel).setText(tr("ui.common.cancel", "Cancel"))

    def load_settings(self):
        """Load settings from the configuration manager"""
        # Output format
        output_format = self.config_manager.get_setting("output_format", DEFAULT_OUTPUT_FORMAT)
        index = self.format_combo.findData(output_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)

        # Output location
        output_location = self.config_manager.get_setting("output_directory", "")
        self.output_location_edit.setText(output_location)

        # Remember last settings
        remember = self.config_manager.get_setting("remember_last_settings", True)
        self.remember_check.setChecked(remember)

        # Language
        language = self.config_manager.get_setting("language", "en")
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # Theme
        theme = self.config_manager.get_setting("theme", "light")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

    def browse_output_location(self):
        """Open a dialog to select the default output location"""
        folder = QFileDialog.getExistingDirectory(
            self, tr("ui.settings_dialog.select_output_location", "Select Default Output Location"),
            self.output_location_edit.text()
        )

        if folder:
            self.output_location_edit.setText(folder)

    def update_translations(self):
        """Update all translated strings in the dialog"""
        # Update window title
        self.setWindowTitle(tr("ui.settings_dialog.title", "Preferences"))

        # Update group boxes
        for group_box in self.findChildren(QGroupBox):
            if "Output Settings" in group_box.title():
                group_box.setTitle(tr("ui.settings_dialog.output_group", "Output Settings"))
            elif "General Settings" in group_box.title():
                group_box.setTitle(tr("ui.settings_dialog.general_group", "General Settings"))

        # Update form labels
        form_layouts = []
        for group_box in self.findChildren(QGroupBox):
            if group_box.layout() and isinstance(group_box.layout(), QFormLayout):
                form_layouts.append(group_box.layout())

        for form_layout in form_layouts:
            for row in range(form_layout.rowCount()):
                label_item = form_layout.itemAt(row, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label = label_item.widget()
                    if isinstance(label, QLabel):
                        if "Default Output Format" in label.text():
                            label.setText(tr("ui.settings_dialog.default_format_label", "Default Output Format:"))
                        elif "Default Output Location" in label.text():
                            label.setText(tr("ui.settings_dialog.default_location_label", "Default Output Location:"))
                        elif "Remember Last Settings" in label.text():
                            label.setText(tr("ui.settings_dialog.remember_settings_label", "Remember Last Settings:"))
                        elif "Language" in label.text():
                            label.setText(tr("ui.settings_dialog.language_label", "Language:"))
                        elif "Theme" in label.text():
                            label.setText(tr("ui.settings_dialog.theme_label", "Theme:"))

        # Update buttons
        for button in self.findChildren(QPushButton):
            if "Browse" in button.text():
                button.setText(tr("ui.settings_dialog.browse_button", "Browse..."))

        # Update theme combo box items
        theme_combo = self.theme_combo
        theme_combo.setItemText(0, tr("ui.settings_dialog.theme_light", "Light"))
        theme_combo.setItemText(1, tr("ui.settings_dialog.theme_dark", "Dark"))

        # Update dialog buttons
        button_box = self.findChild(QDialogButtonBox)
        if button_box:
            button_box.button(QDialogButtonBox.Ok).setText(tr("ui.common.ok", "OK"))
            button_box.button(QDialogButtonBox.Cancel).setText(tr("ui.common.cancel", "Cancel"))

    def accept(self):
        """Handle dialog acceptance"""
        # Get the new settings
        new_language = self.language_combo.currentData()
        new_theme = self.theme_combo.currentData()

        # Save settings
        self.config_manager.set_setting("output_format", self.format_combo.currentData())
        self.config_manager.set_setting("output_directory", self.output_location_edit.text())
        self.config_manager.set_setting("remember_last_settings", self.remember_check.isChecked())
        self.config_manager.set_setting("language", new_language)
        self.config_manager.set_setting("theme", new_theme)

        # Apply changes immediately
        from utils.translation_loader import translator
        from utils.style_loader import apply_stylesheet
        import logging

        logger = logging.getLogger(__name__)

        # Apply language change
        if translator.set_language(new_language):
            logger.info(f"Applied language change to: {new_language}")

            # Update the UI language in the main window
            if self.parent() and hasattr(self.parent(), 'update_ui_language'):
                self.parent().update_ui_language()

            # Inform the user that a restart is needed for full language change
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                tr("ui.settings_dialog.language_change_title", "Language Change"),
                tr("ui.settings_dialog.language_change_message",
                   "Language has been changed. Some UI elements have been updated, but a full restart is recommended for all changes to take effect.")
            )

        # Apply theme change
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if apply_stylesheet(app, new_theme):
            logger.info(f"Applied theme change to: {new_theme}")

        # Close the dialog
        super().accept()