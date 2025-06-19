"""
About dialog for AudKyɛfo
"""

import logging
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QFrame, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from utils.constants import APP_NAME, APP_DISPLAY_NAME, APP_VERSION, APP_AUTHOR
from utils.translation_loader import tr

# Set up logging
logger = logging.getLogger(__name__)

class AboutDialog(QDialog):
    """
    Dialog showing information about the application
    """

    def __init__(self, parent=None):
        """
        Initialize the about dialog

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Set window properties
        self.setWindowTitle(tr("ui.about_dialog.title", "About {app_name}").format(app_name=APP_NAME))
        self.setMinimumSize(400, 300)
        self.resize(450, 350)

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
        main_layout.setAlignment(Qt.AlignCenter)

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)

        # Create a layout for the dialog itself
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)

        # App icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)

        # Try to load the app icon from resources
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "app.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(64, 64))
        else:
            # Fallback to the resource path
            icon_label.setPixmap(QIcon(":/icons/app.png").pixmap(64, 64))

        main_layout.addWidget(icon_label)

        # App name
        app_display_name = tr("app.display_name", APP_DISPLAY_NAME)
        name_label = QLabel(app_display_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(name_label)

        # App version
        version_text = tr("ui.about_dialog.version", "Version {version}").format(version=APP_VERSION)
        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(version_label)

        # App author
        author_text = tr("ui.about_dialog.created_by", "Created by {author}").format(author=APP_AUTHOR)
        author_label = QLabel(author_text)
        author_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(author_label)

        # Description
        description_text = tr("ui.about_dialog.description",
            "AudKyɛfo is an offline desktop application for splitting audio files "
            "into segments based on custom preferences."
        )
        description_label = QLabel(description_text)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        # Close button
        close_button = QPushButton(tr("ui.about_dialog.close_button", "Close"))
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def update_translations(self):
        """Update all translated strings in the dialog"""
        self.setWindowTitle(tr("ui.about_dialog.title", "About {app_name}").format(app_name=APP_NAME))

        # Find and update all labels
        for widget in self.findChildren(QLabel):
            if widget.text() == APP_DISPLAY_NAME or widget.text() == tr("app.display_name", APP_DISPLAY_NAME):
                widget.setText(tr("app.display_name", APP_DISPLAY_NAME))
            elif "Version" in widget.text():
                widget.setText(tr("ui.about_dialog.version", "Version {version}").format(version=APP_VERSION))
            elif "Created by" in widget.text():
                widget.setText(tr("ui.about_dialog.created_by", "Created by {author}").format(author=APP_AUTHOR))
            elif "AudKyɛfo is" in widget.text():
                widget.setText(tr("ui.about_dialog.description",
                    "AudKyɛfo is an offline desktop application for splitting audio files "
                    "into segments based on custom preferences."
                ))

        # Update close button
        for widget in self.findChildren(QPushButton):
            if widget.text() == "Close" or widget.text() == tr("ui.about_dialog.close_button", "Close"):
                widget.setText(tr("ui.about_dialog.close_button", "Close"))