"""
Split configuration tab for AudKyɛfo
"""

import os
import logging
from typing import Dict, Any, List, Tuple, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QLabel, QSpinBox, QTimeEdit, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSpacerItem,
    QSizePolicy, QSlider, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime

from utils.constants import (
    SUPPORTED_OUTPUT_FORMATS,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_NAMING_PATTERN,
    SPLIT_METHOD_EQUAL,
    SPLIT_METHOD_DURATION,
    SPLIT_METHOD_CUSTOM
)
from utils.translation_loader import tr
from utils.helpers import format_time, parse_time
from utils.validators import is_valid_time_format, is_valid_output_directory, is_valid_naming_pattern
from utils.ui_translator import update_ui_translations

# Set up logging
logger = logging.getLogger(__name__)

class ConfigTab(QWidget):
    """
    Tab for configuring audio splitting options
    """

    # Signals
    config_changed = pyqtSignal(dict)

    def __init__(self):
        """Initialize the configuration tab"""
        super().__init__()

        self.audio_metadata = {}
        self.total_duration = 0

        # Set up the UI
        self.setup_ui()

        # Connect signals
        self.connect_signals()

        # Disable the tab initially
        self.setEnabled(False)

    def setup_ui(self):
        """Set up the user interface"""
        # Main layout with scroll area to handle overflow
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)

        # Set scroll area as the main widget
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)

        # Title label
        title_label = QLabel(tr("ui.config_tab.title", "Split Configuration"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Splitting method group with improved styling
        method_group = QGroupBox(tr("ui.config_tab.method_group", "Splitting Method"))
        method_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        method_layout = QVBoxLayout(method_group)
        method_layout.setContentsMargins(20, 30, 20, 20)
        method_layout.setSpacing(20)
        main_layout.addWidget(method_group)

        # Radio buttons for splitting methods
        self.method_group = QButtonGroup(self)

        # Equal parts method with improved layout
        method_option_layout = QHBoxLayout()
        method_option_layout.setContentsMargins(0, 0, 0, 0)
        method_option_layout.setSpacing(10)

        self.equal_parts_radio = QRadioButton(tr("ui.config_tab.equal_parts_radio", "Equal Parts"))
        self.equal_parts_radio.setStyleSheet("font-weight: bold;")
        self.method_group.addButton(self.equal_parts_radio, 0)
        method_option_layout.addWidget(self.equal_parts_radio)
        method_option_layout.addStretch(1)
        method_layout.addLayout(method_option_layout)

        # Equal parts settings with improved spacing
        equal_parts_widget = QWidget()
        equal_parts_layout = QFormLayout(equal_parts_widget)
        equal_parts_layout.setContentsMargins(30, 5, 10, 15)
        equal_parts_layout.setSpacing(10)
        equal_parts_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.num_parts_spin = QSpinBox()
        self.num_parts_spin.setMinimum(2)
        self.num_parts_spin.setMaximum(100)
        self.num_parts_spin.setValue(2)
        self.num_parts_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        equal_parts_layout.addRow(tr("ui.config_tab.num_parts_label", "Number of parts:"), self.num_parts_spin)

        self.part_duration_label = QLabel("00:00 per part")
        self.part_duration_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        equal_parts_layout.addRow(tr("ui.config_tab.part_duration_label", "Duration per part:"), self.part_duration_label)

        method_layout.addWidget(equal_parts_widget)

        # Add a separator between methods
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        method_layout.addWidget(separator1)

        # Fixed duration method with improved layout
        method_option_layout2 = QHBoxLayout()
        method_option_layout2.setContentsMargins(0, 0, 0, 0)
        method_option_layout2.setSpacing(10)

        self.fixed_duration_radio = QRadioButton(tr("ui.config_tab.fixed_duration_radio", "Fixed Duration"))
        self.fixed_duration_radio.setStyleSheet("font-weight: bold;")
        self.method_group.addButton(self.fixed_duration_radio, 1)
        method_option_layout2.addWidget(self.fixed_duration_radio)
        method_option_layout2.addStretch(1)
        method_layout.addLayout(method_option_layout2)

        # Fixed duration settings with improved spacing
        fixed_duration_widget = QWidget()
        fixed_duration_layout = QFormLayout(fixed_duration_widget)
        fixed_duration_layout.setContentsMargins(30, 5, 10, 15)
        fixed_duration_layout.setSpacing(10)
        fixed_duration_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.duration_edit = QLineEdit()
        self.duration_edit.setPlaceholderText("MM:SS")
        self.duration_edit.setText("01:00")  # Default to 1 minute
        self.duration_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fixed_duration_layout.addRow(tr("ui.config_tab.duration_format_label", "Duration (MM:SS):"), self.duration_edit)

        self.num_segments_label = QLabel("0 segments")
        self.num_segments_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fixed_duration_layout.addRow(tr("ui.config_tab.estimated_segments_label", "Estimated segments:"), self.num_segments_label)

        method_layout.addWidget(fixed_duration_widget)

        # Add a separator between methods
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        method_layout.addWidget(separator2)

        # Custom ranges method with improved layout
        method_option_layout3 = QHBoxLayout()
        method_option_layout3.setContentsMargins(0, 0, 0, 0)
        method_option_layout3.setSpacing(10)

        self.custom_ranges_radio = QRadioButton(tr("ui.config_tab.custom_ranges_radio", "Custom Ranges (Advanced)"))
        self.custom_ranges_radio.setStyleSheet("font-weight: bold;")
        self.method_group.addButton(self.custom_ranges_radio, 2)
        method_option_layout3.addWidget(self.custom_ranges_radio)
        method_option_layout3.addStretch(1)
        method_layout.addLayout(method_option_layout3)

        # Custom ranges settings with improved spacing
        custom_ranges_widget = QWidget()
        custom_ranges_layout = QVBoxLayout(custom_ranges_widget)
        custom_ranges_layout.setContentsMargins(30, 5, 10, 15)
        custom_ranges_layout.setSpacing(15)

        # Table for time ranges
        self.ranges_table = QTableWidget(0, 2)
        self.ranges_table.setHorizontalHeaderLabels([
            tr("ui.config_tab.start_time_format_column", "Start Time (MM:SS)"),
            tr("ui.config_tab.end_time_format_column", "End Time (MM:SS)")
        ])
        self.ranges_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ranges_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ranges_table.setMinimumHeight(150)
        self.ranges_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        custom_ranges_layout.addWidget(self.ranges_table)

        # Buttons for managing ranges
        ranges_buttons_layout = QHBoxLayout()
        ranges_buttons_layout.setSpacing(10)

        self.add_range_button = QPushButton(tr("ui.config_tab.add_range_button", "Add Range"))
        self.add_range_button.setToolTip(tr("ui.config_tab.add_range_tooltip", "Add a new time range to the list"))
        self.remove_range_button = QPushButton(tr("ui.config_tab.remove_range_button", "Remove Range"))
        self.remove_range_button.setToolTip(tr("ui.config_tab.remove_range_tooltip", "Remove the selected time range"))

        ranges_buttons_layout.addWidget(self.add_range_button)
        ranges_buttons_layout.addWidget(self.remove_range_button)
        ranges_buttons_layout.addStretch(1)

        custom_ranges_layout.addLayout(ranges_buttons_layout)
        method_layout.addWidget(custom_ranges_widget)

        # Add spacing between sections
        main_layout.addSpacing(15)

        # Additional settings group with improved styling
        settings_group = QGroupBox(tr("ui.config_tab.additional_settings_group", "Additional Settings"))
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        settings_layout = QFormLayout(settings_group)
        settings_layout.setContentsMargins(20, 30, 20, 20)
        settings_layout.setSpacing(15)
        settings_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        main_layout.addWidget(settings_group)

        # Overlap duration with improved layout
        overlap_layout = QHBoxLayout()
        overlap_layout.setSpacing(10)
        self.overlap_check = QCheckBox(tr("ui.config_tab.overlap_duration_label", "Overlap Duration:"))
        self.overlap_check.setToolTip(tr("ui.config_tab.overlap_tooltip", "Enable overlapping between segments"))
        self.overlap_edit = QLineEdit()
        self.overlap_edit.setPlaceholderText("MM:SS")
        self.overlap_edit.setEnabled(False)
        self.overlap_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        overlap_layout.addWidget(self.overlap_check)
        overlap_layout.addWidget(self.overlap_edit)
        settings_layout.addRow("", overlap_layout)

        # Output format with improved layout
        self.format_combo = QComboBox()
        self.format_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.format_combo.setToolTip(tr("ui.config_tab.format_tooltip", "Select the output file format"))
        for fmt in SUPPORTED_OUTPUT_FORMATS:
            self.format_combo.addItem(fmt.upper(), fmt)
        self.format_combo.setCurrentText(DEFAULT_OUTPUT_FORMAT.upper())
        settings_layout.addRow(tr("ui.config_tab.output_format_label", "Output Format:"), self.format_combo)

        # Output quality with improved layout
        quality_layout = QHBoxLayout()
        quality_layout.setSpacing(10)
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(0)
        self.quality_slider.setMaximum(2)
        self.quality_slider.setValue(1)  # Medium quality by default
        self.quality_slider.setToolTip(tr("ui.config_tab.quality_tooltip", "Adjust the output quality"))
        self.quality_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.quality_label = QLabel(tr("ui.config_tab.quality_medium", "Medium"))
        self.quality_label.setMinimumWidth(60)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        settings_layout.addRow(tr("ui.config_tab.output_quality_label", "Output Quality:"), quality_layout)

        # Output folder with improved layout
        output_folder_layout = QHBoxLayout()
        output_folder_layout.setSpacing(10)
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_folder_edit.setToolTip(tr("ui.config_tab.output_folder_tooltip", "Location where output files will be saved"))
        self.output_folder_button = QPushButton(tr("ui.config_tab.browse_button", "Browse..."))
        self.output_folder_button.setToolTip(tr("ui.config_tab.browse_folder_tooltip", "Select output folder"))
        output_folder_layout.addWidget(self.output_folder_edit)
        output_folder_layout.addWidget(self.output_folder_button)
        settings_layout.addRow(tr("ui.config_tab.output_folder_label", "Output Folder:"), output_folder_layout)

        # Naming pattern with improved layout and help icon
        naming_layout = QHBoxLayout()
        naming_layout.setSpacing(10)
        self.naming_pattern_edit = QLineEdit()
        self.naming_pattern_edit.setText(DEFAULT_NAMING_PATTERN)
        self.naming_pattern_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.naming_pattern_edit.setToolTip(tr("ui.config_tab.naming_pattern_tooltip",
                                           "Pattern used to name output files\n"
                                           "Available variables:\n"
                                           "{original_name} - Original file name\n"
                                           "{number} - Segment number\n"
                                           "{start_time} - Start time of segment\n"
                                           "{end_time} - End time of segment"))
        naming_layout.addWidget(self.naming_pattern_edit)
        settings_layout.addRow(tr("ui.config_tab.naming_pattern_label", "Naming Pattern:"), naming_layout)

        # Naming pattern help with improved styling
        naming_help = QLabel(
            tr("ui.config_tab.naming_pattern_help",
               "Available variables: {original_name}, {number}, {start_time}, {end_time}")
        )
        naming_help.setStyleSheet("font-size: 10px; color: #666666; padding-left: 10px;")
        naming_help.setWordWrap(True)
        settings_layout.addRow("", naming_help)

        # Add spacing before apply button
        main_layout.addSpacing(20)

        # Apply button with improved styling
        apply_button_layout = QHBoxLayout()
        apply_button_layout.setContentsMargins(0, 10, 0, 10)
        self.apply_button = QPushButton("Apply Configuration")
        self.apply_button.setMinimumHeight(40)
        self.apply_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.apply_button.setToolTip("Apply the current configuration")
        apply_button_layout.addStretch(1)
        apply_button_layout.addWidget(self.apply_button)
        apply_button_layout.addStretch(1)
        main_layout.addLayout(apply_button_layout)

        # Add spacer at the bottom
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set default method
        self.equal_parts_radio.setChecked(True)

    def connect_signals(self):
        """Connect signals between components"""
        # Method selection
        self.method_group.buttonClicked.connect(self.update_method_settings)

        # Equal parts settings
        self.num_parts_spin.valueChanged.connect(self.update_part_duration)

        # Fixed duration settings
        self.duration_edit.textChanged.connect(self.update_num_segments)

        # Custom ranges settings
        self.add_range_button.clicked.connect(self.add_range)
        self.remove_range_button.clicked.connect(self.remove_range)

        # Overlap settings
        self.overlap_check.stateChanged.connect(self.toggle_overlap)

        # Output quality
        self.quality_slider.valueChanged.connect(self.update_quality_label)

        # Output folder
        self.output_folder_button.clicked.connect(self.browse_output_folder)

        # Apply button
        self.apply_button.clicked.connect(self.apply_configuration)

    def set_audio_metadata(self, metadata: Dict[str, Any]):
        """
        Set the audio metadata

        Args:
            metadata: Audio metadata
        """
        self.audio_metadata = metadata
        self.total_duration = metadata.get("duration_seconds", 0)

        # Set default output folder
        default_output_dir = os.path.dirname(metadata.get("path", ""))
        self.output_folder_edit.setText(default_output_dir)

        # Update UI based on the new metadata
        self.update_part_duration()
        self.update_num_segments()

        # Enable the tab
        self.setEnabled(True)

    def update_method_settings(self):
        """Update the settings based on the selected method"""
        # Get the selected method
        selected_id = self.method_group.checkedId()

        # Update UI based on the selected method
        if selected_id == 0:  # Equal parts
            self.update_part_duration()
        elif selected_id == 1:  # Fixed duration
            self.update_num_segments()

    def update_part_duration(self):
        """Update the part duration label"""
        if not self.total_duration:
            return

        num_parts = self.num_parts_spin.value()
        part_duration = self.total_duration / num_parts

        self.part_duration_label.setText(format_time(part_duration))

    def update_num_segments(self):
        """Update the number of segments label"""
        if not self.total_duration:
            return

        duration_str = self.duration_edit.text()
        if not is_valid_time_format(duration_str):
            self.num_segments_label.setText("Invalid format")
            return

        try:
            duration = parse_time(duration_str)
            if duration <= 0:
                self.num_segments_label.setText("Invalid duration")
                return

            num_segments = int(self.total_duration / duration) + (1 if self.total_duration % duration > 0 else 0)
            self.num_segments_label.setText(f"{num_segments} segments")
        except ValueError:
            self.num_segments_label.setText("Invalid format")

    def add_range(self):
        """Add a new time range to the table"""
        row = self.ranges_table.rowCount()
        self.ranges_table.insertRow(row)

        # Set default values
        if row == 0:
            start_time = "00:00"
            end_time = format_time(min(60, self.total_duration))
        else:
            # Get the end time of the previous range
            prev_end = self.ranges_table.item(row - 1, 1).text()
            try:
                prev_end_seconds = parse_time(prev_end)
                start_time = prev_end
                end_time = format_time(min(prev_end_seconds + 60, self.total_duration))
            except ValueError:
                start_time = "00:00"
                end_time = format_time(min(60, self.total_duration))

        self.ranges_table.setItem(row, 0, QTableWidgetItem(start_time))
        self.ranges_table.setItem(row, 1, QTableWidgetItem(end_time))

    def remove_range(self):
        """Remove the selected time range from the table"""
        selected_rows = self.ranges_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Remove rows in reverse order to avoid index issues
        for row in sorted([index.row() for index in selected_rows], reverse=True):
            self.ranges_table.removeRow(row)

    def toggle_overlap(self, state: int):
        """
        Toggle the overlap duration field

        Args:
            state: Checkbox state
        """
        self.overlap_edit.setEnabled(state == Qt.Checked)
        if state == Qt.Checked:
            self.overlap_edit.setText("00:05")  # Default to 5 seconds
        else:
            self.overlap_edit.clear()

    def update_quality_label(self, value: int):
        """
        Update the quality label based on the slider value

        Args:
            value: Slider value
        """
        if value == 0:
            self.quality_label.setText("Low")
        elif value == 1:
            self.quality_label.setText("Medium")
        else:
            self.quality_label.setText("High")

    def browse_output_folder(self):
        """Open a dialog to select the output folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.output_folder_edit.text()
        )

        if folder:
            self.output_folder_edit.setText(folder)

    def apply_configuration(self):
        """Apply the current configuration"""
        # Validate the configuration
        if not self.validate_configuration():
            return

        # Get the configuration
        config = self.get_configuration()

        # Emit the configuration changed signal
        self.config_changed.emit(config)

    def validate_configuration(self) -> bool:
        """
        Validate the current configuration

        Returns:
            True if the configuration is valid, False otherwise
        """
        # Validate output directory
        output_dir = self.output_folder_edit.text()
        valid, error_message = is_valid_output_directory(output_dir)
        if not valid:
            logger.error(f"Invalid output directory: {error_message}")
            return False

        # Validate naming pattern
        naming_pattern = self.naming_pattern_edit.text()
        valid, error_message = is_valid_naming_pattern(naming_pattern)
        if not valid:
            logger.error(f"Invalid naming pattern: {error_message}")
            return False

        # Validate method-specific settings
        selected_id = self.method_group.checkedId()

        if selected_id == 1:  # Fixed duration
            duration_str = self.duration_edit.text()
            if not is_valid_time_format(duration_str):
                logger.error("Invalid duration format")
                return False

            try:
                duration = parse_time(duration_str)
                if duration <= 0:
                    logger.error("Duration must be greater than 0")
                    return False
            except ValueError:
                logger.error("Invalid duration format")
                return False

        elif selected_id == 2:  # Custom ranges
            if self.ranges_table.rowCount() == 0:
                logger.error("No time ranges specified")
                return False

            for row in range(self.ranges_table.rowCount()):
                start_item = self.ranges_table.item(row, 0)
                end_item = self.ranges_table.item(row, 1)

                if not start_item or not end_item:
                    logger.error(f"Missing time value in row {row + 1}")
                    return False

                start_time = start_item.text()
                end_time = end_item.text()

                if not is_valid_time_format(start_time):
                    logger.error(f"Invalid start time format in row {row + 1}")
                    return False

                if not is_valid_time_format(end_time):
                    logger.error(f"Invalid end time format in row {row + 1}")
                    return False

                try:
                    start_seconds = parse_time(start_time)
                    end_seconds = parse_time(end_time)

                    if start_seconds >= end_seconds:
                        logger.error(f"Start time must be less than end time in row {row + 1}")
                        return False

                    if end_seconds > self.total_duration:
                        logger.error(f"End time exceeds audio duration in row {row + 1}")
                        return False
                except ValueError:
                    logger.error(f"Invalid time format in row {row + 1}")
                    return False

        # Validate overlap
        if self.overlap_check.isChecked():
            overlap_str = self.overlap_edit.text()
            if not is_valid_time_format(overlap_str):
                logger.error("Invalid overlap format")
                return False

            try:
                overlap = parse_time(overlap_str)
                if overlap < 0:
                    logger.error("Overlap must be non-negative")
                    return False
            except ValueError:
                logger.error("Invalid overlap format")
                return False

        return True

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get the current configuration

        Returns:
            Dictionary containing the configuration
        """
        # Get the selected method
        selected_id = self.method_group.checkedId()
        if selected_id == 0:
            method = SPLIT_METHOD_EQUAL
        elif selected_id == 1:
            method = SPLIT_METHOD_DURATION
        else:
            method = SPLIT_METHOD_CUSTOM

        # Get method-specific settings
        method_settings = {}

        if method == SPLIT_METHOD_EQUAL:
            method_settings["num_parts"] = self.num_parts_spin.value()

        elif method == SPLIT_METHOD_DURATION:
            try:
                duration = parse_time(self.duration_edit.text())
                method_settings["duration"] = duration
            except ValueError:
                method_settings["duration"] = 60  # Default to 60 seconds

        elif method == SPLIT_METHOD_CUSTOM:
            ranges = []
            for row in range(self.ranges_table.rowCount()):
                start_item = self.ranges_table.item(row, 0)
                end_item = self.ranges_table.item(row, 1)

                if start_item and end_item:
                    try:
                        start_seconds = parse_time(start_item.text())
                        end_seconds = parse_time(end_item.text())
                        ranges.append((start_seconds, end_seconds))
                    except ValueError:
                        pass

            method_settings["ranges"] = ranges

        # Get overlap
        overlap = 0
        if self.overlap_check.isChecked():
            try:
                overlap = parse_time(self.overlap_edit.text())
            except ValueError:
                pass

        # Get output format
        output_format = self.format_combo.currentData()

        # Get output quality
        quality_value = self.quality_slider.value()
        if quality_value == 0:
            quality = "low"
        elif quality_value == 1:
            quality = "medium"
        else:
            quality = "high"

        # Build the configuration
        config = {
            "method": method,
            "output_dir": self.output_folder_edit.text(),
            "output_format": output_format,
            "output_quality": quality,
            "naming_pattern": self.naming_pattern_edit.text(),
            "overlap": overlap,
            **method_settings
        }

        return config

    def load_configuration(self, config: Dict[str, Any]):
        """
        Load a configuration

        Args:
            config: Configuration dictionary
        """
        # Set method
        method = config.get("method", SPLIT_METHOD_EQUAL)
        if method == SPLIT_METHOD_EQUAL:
            self.equal_parts_radio.setChecked(True)
            self.num_parts_spin.setValue(config.get("num_parts", 2))
        elif method == SPLIT_METHOD_DURATION:
            self.fixed_duration_radio.setChecked(True)
            duration = config.get("duration", 60)
            self.duration_edit.setText(format_time(duration))
        elif method == SPLIT_METHOD_CUSTOM:
            self.custom_ranges_radio.setChecked(True)
            ranges = config.get("ranges", [])

            # Clear existing ranges
            self.ranges_table.setRowCount(0)

            # Add new ranges
            for start, end in ranges:
                row = self.ranges_table.rowCount()
                self.ranges_table.insertRow(row)
                self.ranges_table.setItem(row, 0, QTableWidgetItem(format_time(start)))
                self.ranges_table.setItem(row, 1, QTableWidgetItem(format_time(end)))

        # Set overlap
        overlap = config.get("overlap", 0)
        if overlap > 0:
            self.overlap_check.setChecked(True)
            self.overlap_edit.setText(format_time(overlap))
        else:
            self.overlap_check.setChecked(False)

        # Set output format
        output_format = config.get("output_format", DEFAULT_OUTPUT_FORMAT)
        index = self.format_combo.findData(output_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)

        # Set output quality
        quality = config.get("output_quality", "medium")
        if quality == "low":
            self.quality_slider.setValue(0)
        elif quality == "medium":
            self.quality_slider.setValue(1)
        else:
            self.quality_slider.setValue(2)

        # Set output directory
        output_dir = config.get("output_dir", "")
        if output_dir:
            self.output_folder_edit.setText(output_dir)

        # Set naming pattern
        naming_pattern = config.get("naming_pattern", DEFAULT_NAMING_PATTERN)
        self.naming_pattern_edit.setText(naming_pattern)

        # Update UI
        self.update_method_settings()

    def update_translations(self):
        """Update all translated strings in the tab"""
        # Create a translation map for common UI elements
        translation_map = {
            "Split Configuration": "ui.config_tab.title",
            "Splitting Method": "ui.config_tab.method_group",
            "Equal Parts": "ui.config_tab.method_equal",
            "Fixed Duration": "ui.config_tab.method_duration",
            "Custom Points": "ui.config_tab.method_custom",
            "Number of parts:": "ui.config_tab.equal_parts_label",
            "Duration per part:": "ui.config_tab.duration_label",
            "Add": "ui.config_tab.add_button",
            "Remove": "ui.config_tab.remove_button",
            "Clear All": "ui.config_tab.clear_button",
            "Split Points": "ui.config_tab.split_points_group",
            "Time": "ui.config_tab.time_column",
            "Label": "ui.config_tab.label_column",
            "Output Settings": "ui.config_tab.output_group",
            "Output Format:": "ui.config_tab.format_label",
            "Output Quality:": "ui.config_tab.quality_label",
            "Low": "ui.config_tab.quality_low",
            "Medium": "ui.config_tab.quality_medium",
            "High": "ui.config_tab.quality_high",
            "Output Folder:": "ui.config_tab.output_folder_label",
            "Browse...": "ui.config_tab.browse_button",
            "Naming Pattern:": "ui.config_tab.naming_pattern_label",
            "Advanced Options": "ui.config_tab.advanced_group",
            "Add overlap between segments:": "ui.config_tab.overlap_label",
            "Preserve original metadata": "ui.config_tab.preserve_metadata",
            "Normalize audio levels": "ui.config_tab.normalize_audio"
        }

        # Update all widgets using the translation map
        update_ui_translations(self, translation_map)

        # Update table headers
        if hasattr(self, 'split_points_table'):
            if self.split_points_table.columnCount() >= 2:
                self.split_points_table.setHorizontalHeaderItem(0, QTableWidgetItem(tr("ui.config_tab.time_column", "Time")))
                self.split_points_table.setHorizontalHeaderItem(1, QTableWidgetItem(tr("ui.config_tab.label_column", "Label")))