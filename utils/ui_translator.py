"""
UI translation utilities for AudKyɛfo
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QAction, QMenu, QTabWidget,
    QGroupBox, QCheckBox, QRadioButton, QComboBox, QLineEdit,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QObject

from utils.translation_loader import tr

# Set up logging
logger = logging.getLogger(__name__)

class UITranslator:
    """
    Utility class for translating UI components
    """

    @staticmethod
    def translate_widget(widget: QWidget, translation_map: Dict[str, str]) -> None:
        """
        Translate a widget using a translation map

        Args:
            widget: Widget to translate
            translation_map: Dictionary mapping widget text to translation keys
        """
        # Helper function to translate text if it's in the map
        def translate_text(text, default_text=None):
            if not text:
                return text

            if text in translation_map:
                translated = tr(translation_map[text], default_text or text)
                logger.debug(f"Translated '{text}' to '{translated}' using key '{translation_map[text]}'")
                return translated
            return text

        try:
            if isinstance(widget, QLabel):
                text = widget.text()
                widget.setText(translate_text(text))

            elif isinstance(widget, QPushButton):
                text = widget.text()
                widget.setText(translate_text(text))
                # Also translate tooltip
                if widget.toolTip() and widget.toolTip() in translation_map:
                    widget.setToolTip(translate_text(widget.toolTip()))

            elif isinstance(widget, QAction):
                text = widget.text()
                widget.setText(translate_text(text))
                # Also translate tooltip
                if widget.toolTip() and widget.toolTip() in translation_map:
                    widget.setToolTip(translate_text(widget.toolTip()))

            elif isinstance(widget, QMenu):
                text = widget.title()
                widget.setTitle(translate_text(text))

            elif isinstance(widget, QGroupBox):
                text = widget.title()
                widget.setTitle(translate_text(text))

            elif isinstance(widget, QCheckBox) or isinstance(widget, QRadioButton):
                text = widget.text()
                widget.setText(translate_text(text))

            elif isinstance(widget, QComboBox):
                for i in range(widget.count()):
                    text = widget.itemText(i)
                    translated = translate_text(text)
                    if translated != text:
                        widget.setItemText(i, translated)

            elif isinstance(widget, QTabWidget):
                for i in range(widget.count()):
                    text = widget.tabText(i)
                    translated = translate_text(text)
                    if translated != text:
                        widget.setTabText(i, translated)

            elif isinstance(widget, QTableWidget):
                # Translate horizontal header
                for i in range(widget.columnCount()):
                    if widget.horizontalHeaderItem(i):
                        text = widget.horizontalHeaderItem(i).text()
                        translated = translate_text(text)
                        if translated != text:
                            widget.horizontalHeaderItem(i).setText(translated)

                # Translate vertical header
                for i in range(widget.rowCount()):
                    if widget.verticalHeaderItem(i):
                        text = widget.verticalHeaderItem(i).text()
                        translated = translate_text(text)
                        if translated != text:
                            widget.verticalHeaderItem(i).setText(translated)
        except Exception as e:
            logger.error(f"Error translating widget {widget.__class__.__name__}: {e}")

    @staticmethod
    def translate_widgets(parent: QWidget, translation_map: Dict[str, str]) -> None:
        """
        Recursively translate all widgets in a parent widget

        Args:
            parent: Parent widget
            translation_map: Dictionary mapping widget text to translation keys
        """
        # Translate the parent widget itself
        UITranslator.translate_widget(parent, translation_map)

        # Translate all child widgets
        for child in parent.findChildren(QWidget):
            UITranslator.translate_widget(child, translation_map)

        # Log translation activity
        logger.debug(f"Translated {len(parent.findChildren(QWidget))} widgets in {parent.__class__.__name__}")

    @staticmethod
    def create_translation_map(widgets: List[QWidget], prefix: str = "") -> Dict[str, str]:
        """
        Create a translation map from a list of widgets

        Args:
            widgets: List of widgets
            prefix: Prefix for translation keys

        Returns:
            Dictionary mapping widget text to translation keys
        """
        translation_map = {}

        for widget in widgets:
            if isinstance(widget, QLabel):
                text = widget.text()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}"
                    translation_map[text] = key

            elif isinstance(widget, QPushButton):
                text = widget.text()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_button"
                    translation_map[text] = key

            elif isinstance(widget, QAction):
                text = widget.text()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_action"
                    translation_map[text] = key

            elif isinstance(widget, QMenu):
                text = widget.title()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_menu"
                    translation_map[text] = key

            elif isinstance(widget, QGroupBox):
                text = widget.title()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_group"
                    translation_map[text] = key

            elif isinstance(widget, QCheckBox):
                text = widget.text()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_check"
                    translation_map[text] = key

            elif isinstance(widget, QRadioButton):
                text = widget.text()
                if text:
                    key = f"{prefix}.{text.lower().replace(' ', '_')}_radio"
                    translation_map[text] = key

            elif isinstance(widget, QComboBox):
                for i in range(widget.count()):
                    text = widget.itemText(i)
                    if text:
                        key = f"{prefix}.{text.lower().replace(' ', '_')}_item"
                        translation_map[text] = key

            elif isinstance(widget, QTabWidget):
                for i in range(widget.count()):
                    text = widget.tabText(i)
                    if text:
                        key = f"{prefix}.{text.lower().replace(' ', '_')}_tab"
                        translation_map[text] = key

            elif isinstance(widget, QTableWidget):
                # Horizontal header
                for i in range(widget.columnCount()):
                    text = widget.horizontalHeaderItem(i).text() if widget.horizontalHeaderItem(i) else ""
                    if text:
                        key = f"{prefix}.{text.lower().replace(' ', '_')}_column"
                        translation_map[text] = key

                # Vertical header
                for i in range(widget.rowCount()):
                    text = widget.verticalHeaderItem(i).text() if widget.verticalHeaderItem(i) else ""
                    if text:
                        key = f"{prefix}.{text.lower().replace(' ', '_')}_row"
                        translation_map[text] = key

        return translation_map

def update_ui_translations(parent: QWidget, translation_map: Dict[str, str]) -> None:
    """
    Update translations for all widgets in a parent widget

    Args:
        parent: Parent widget
        translation_map: Dictionary mapping widget text to translation keys
    """
    # Log the translation map for debugging
    logger.debug(f"Translation map for {parent.__class__.__name__}: {list(translation_map.keys())}")

    # Create a more flexible translation map that ignores case and whitespace
    flexible_map = {}
    for text, key in translation_map.items():
        # Add the original mapping
        flexible_map[text] = key

        # Add a version with normalized whitespace
        normalized = ' '.join(text.split())
        if normalized != text:
            flexible_map[normalized] = key

        # Add a version without trailing colon
        if text.endswith(':'):
            flexible_map[text[:-1]] = key

        # Add a version with trailing colon
        if not text.endswith(':'):
            flexible_map[text + ':'] = key

    UITranslator.translate_widgets(parent, flexible_map)