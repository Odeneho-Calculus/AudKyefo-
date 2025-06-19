"""
Style loader for AudKyɛfo
"""

import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream

# Set up logging
logger = logging.getLogger(__name__)

def load_stylesheet(theme: str = "light") -> str:
    """
    Load a stylesheet from the resources directory or generate a default one

    Args:
        theme: Theme name (light or dark)

    Returns:
        Stylesheet content as a string
    """
    # Determine the stylesheet path
    if theme not in ["light", "dark"]:
        theme = "light"  # Default to light theme

    stylesheet_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "resources", "styles", f"{theme}.qss"
    )

    # Check if the stylesheet exists
    if os.path.exists(stylesheet_path):
        # Load the stylesheet from file
        try:
            with open(stylesheet_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading stylesheet: {e}")
            # Fall back to generated stylesheet

    # Generate a default stylesheet if file doesn't exist or couldn't be loaded
    logger.info(f"Generating default {theme} stylesheet")
    return generate_default_stylesheet(theme)

def generate_default_stylesheet(theme: str = "light") -> str:
    """
    Generate a default stylesheet for the application

    Args:
        theme: Theme name (light or dark)

    Returns:
        Generated stylesheet as a string
    """
    # Get theme colors
    colors = get_theme_colors(theme)

    if theme == "dark":
        return f"""
        /* Global styles */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
            font-family: Arial, Helvetica, sans-serif;
        }}

        /* Main window */
        QMainWindow {{
            background-color: {colors['background']};
        }}

        /* Labels - ensure transparency */
        QLabel {{
            background-color: transparent;
            color: {colors['text']};
            border: none;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {colors['hover_bg']};
            border-color: {colors['highlight']};
        }}

        QPushButton:pressed {{
            background-color: {colors['highlight']};
            color: white;
        }}

        QPushButton:disabled {{
            background-color: {colors['background']};
            color: {colors['border']};
            border-color: {colors['border_light']};
        }}

        /* Tool buttons */
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 3px;
        }}

        QToolButton:hover {{
            background-color: {colors['hover_bg']};
            border-color: {colors['border']};
        }}

        QToolButton:pressed {{
            background-color: {colors['highlight']};
            border-color: {colors['highlight_light']};
        }}

        /* Input fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 4px;
            selection-background-color: {colors['highlight']};
            selection-color: white;
        }}

        /* Combo boxes */
        QComboBox {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 4px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            border-color: {colors['highlight']};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {colors['border']};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['highlight']};
            selection-color: white;
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid {colors['border']};
            height: 8px;
            background: {colors['background_secondary']};
            margin: 2px 0;
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {colors['highlight']};
            border: 1px solid {colors['highlight_light']};
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background: {colors['highlight_light']};
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-bottom-color: {colors['border']};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            min-width: 80px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['highlight']};
            color: white;
            border-bottom-color: {colors['highlight']};
        }}

        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {colors['hover_bg']};
        }}

        /* Group boxes */
        QGroupBox {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 24px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {colors['highlight']};
            background-color: transparent;
        }}

        /* Scroll bars */
        QScrollBar:vertical {{
            border: none;
            background: {colors['background_secondary']};
            width: 12px;
            margin: 12px 0 12px 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors['border']};
            min-height: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors['highlight']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 12px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: {colors['background_secondary']};
            height: 12px;
            margin: 0 12px 0 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors['border']};
            min-width: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors['highlight']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 12px;
        }}

        /* Progress bar */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
            background-color: {colors['background_secondary']};
            color: {colors['text']};
        }}

        QProgressBar::chunk {{
            background-color: {colors['highlight']};
            width: 1px;
        }}

        /* Menu */
        QMenuBar {{
            background-color: {colors['background']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['highlight']};
            color: white;
        }}

        QMenu {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QMenu::item {{
            padding: 6px 20px 6px 20px;
        }}

        QMenu::item:selected {{
            background-color: {colors['highlight']};
            color: white;
        }}

        /* Status bar */
        QStatusBar {{
            background-color: {colors['background']};
            color: {colors['text']};
            border-top: 1px solid {colors['border']};
        }}

        /* Custom drop zone */
        DropZone {{
            background-color: {colors['drop_zone_bg']};
            border: 2px dashed {colors['drop_zone_border']};
            border-radius: 8px;
            padding: 15px;
            color: {colors['text']};
        }}

        DropZone:hover {{
            background-color: {colors['drop_zone_hover_bg']};
            border-color: {colors['drop_zone_hover_border']};
            border-width: 3px;
        }}

        DropZone QLabel {{
            background-color: transparent;
            border: none;
        }}
        """
    else:  # Light theme
        return f"""
        /* Global styles */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
            font-family: Arial, Helvetica, sans-serif;
        }}

        /* Main window */
        QMainWindow {{
            background-color: {colors['background']};
        }}

        /* Labels - ensure transparency */
        QLabel {{
            background-color: transparent;
            color: {colors['text']};
            border: none;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {colors['hover_bg']};
            border-color: {colors['highlight']};
        }}

        QPushButton:pressed {{
            background-color: {colors['highlight']};
            color: white;
        }}

        QPushButton:disabled {{
            background-color: {colors['background']};
            color: {colors['border']};
            border-color: {colors['border_light']};
        }}

        /* Tool buttons */
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 3px;
        }}

        QToolButton:hover {{
            background-color: {colors['hover_bg']};
            border-color: {colors['border']};
        }}

        QToolButton:pressed {{
            background-color: {colors['highlight']};
            border-color: {colors['highlight_light']};
        }}

        /* Input fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 4px;
            selection-background-color: {colors['highlight']};
            selection-color: white;
        }}

        /* Combo boxes */
        QComboBox {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 4px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            border-color: {colors['highlight']};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {colors['border']};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors['form_field_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['highlight']};
            selection-color: white;
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid {colors['border']};
            height: 8px;
            background: {colors['background_secondary']};
            margin: 2px 0;
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {colors['highlight']};
            border: 1px solid {colors['highlight_light']};
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background: {colors['highlight_light']};
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-bottom-color: {colors['border']};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            min-width: 80px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['highlight']};
            color: white;
            border-bottom-color: {colors['highlight']};
        }}

        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {colors['hover_bg']};
        }}

        /* Group boxes */
        QGroupBox {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 24px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {colors['highlight']};
            background-color: transparent;
        }}

        /* Scroll bars */
        QScrollBar:vertical {{
            border: none;
            background: {colors['background_secondary']};
            width: 12px;
            margin: 12px 0 12px 0;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors['border']};
            min-height: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors['highlight']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 12px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: {colors['background_secondary']};
            height: 12px;
            margin: 0 12px 0 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors['border']};
            min-width: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors['highlight']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 12px;
        }}

        /* Progress bar */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
            background-color: {colors['background_secondary']};
            color: {colors['text']};
        }}

        QProgressBar::chunk {{
            background-color: {colors['highlight']};
            width: 1px;
        }}

        /* Menu */
        QMenuBar {{
            background-color: {colors['background']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['highlight']};
            color: white;
        }}

        QMenu {{
            background-color: {colors['background_secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QMenu::item {{
            padding: 6px 20px 6px 20px;
        }}

        QMenu::item:selected {{
            background-color: {colors['highlight']};
            color: white;
        }}

        /* Status bar */
        QStatusBar {{
            background-color: {colors['background']};
            color: {colors['text']};
            border-top: 1px solid {colors['border']};
        }}

        /* Custom drop zone */
        DropZone {{
            background-color: {colors['drop_zone_bg']};
            border: 2px dashed {colors['drop_zone_border']};
            border-radius: 8px;
            padding: 15px;
            color: {colors['text']};
        }}

        DropZone:hover {{
            background-color: {colors['drop_zone_hover_bg']};
            border-color: {colors['drop_zone_hover_border']};
            border-width: 3px;
        }}

        DropZone QLabel {{
            background-color: transparent;
            border: none;
        }}
        """

def get_theme_colors(theme: str = None) -> dict:
    """
    Get the colors for the specified theme

    Args:
        theme: Theme name (light or dark). If None, gets from config.

    Returns:
        Dictionary of theme colors
    """
    if theme is None:
        # Get theme from config
        from core.config_manager import ConfigManager
        config = ConfigManager()
        theme = config.get_setting("theme", "light")

    if theme == "dark":
        return {
            "background": "#212121",
            "background_secondary": "#2D2D2D",
            "text": "#E0E0E0",
            "border": "#616161",
            "border_light": "#424242",
            "highlight": "#43A047",
            "highlight_light": "#4CAF50",
            "highlight_secondary": "#1E88E5",
            "drop_zone_bg": "#2D2D2D",
            "drop_zone_border": "#616161",
            "drop_zone_hover_bg": "#1B5E20",
            "drop_zone_hover_border": "#4CAF50",
            "valid_drop_bg": "rgba(46, 125, 50, 0.2)",
            "invalid_drop_bg": "rgba(244, 67, 54, 0.2)",
            "invalid_drop_border": "#F44336",
            "form_field_bg": "#424242",
            "hover_bg": "#505050"
        }
    else:  # light theme
        return {
            "background": "#FAFAFA",
            "background_secondary": "#FFFFFF",
            "text": "#212121",
            "border": "#BDBDBD",
            "border_light": "#E0E0E0",
            "highlight": "#2E7D32",
            "highlight_light": "#388E3C",
            "highlight_secondary": "#1976D2",
            "drop_zone_bg": "#F5F5F5",
            "drop_zone_border": "#BDBDBD",
            "drop_zone_hover_bg": "#E8F5E9",
            "drop_zone_hover_border": "#2E7D32",
            "valid_drop_bg": "rgba(46, 125, 50, 0.1)",
            "invalid_drop_bg": "rgba(244, 67, 54, 0.1)",
            "invalid_drop_border": "#F44336",
            "form_field_bg": "#FFFFFF",
            "hover_bg": "#EEEEEE"
        }

def apply_stylesheet(app: QApplication, theme: str = "light") -> bool:
    """
    Apply a stylesheet to the application

    Args:
        app: QApplication instance
        theme: Theme name (light or dark)

    Returns:
        True if the stylesheet was applied successfully, False otherwise
    """
    stylesheet = load_stylesheet(theme)

    if not stylesheet:
        return False

    app.setStyleSheet(stylesheet)
    return True