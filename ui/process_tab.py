"""
Processing and results tab for AudKyɛfo
"""

import os
import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QGroupBox, QFormLayout,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot

from core.audio_processor import AudioProcessor
from core.file_handler import open_directory
from utils.translation_loader import tr
from utils.ui_translator import update_ui_translations
from utils.helpers import generate_output_filename

# Set up logging
logger = logging.getLogger(__name__)

class ProcessingThread(QThread):
    """
    Thread for processing audio files
    """

    # Signals
    progress_updated = pyqtSignal(int, str)
    processing_finished = pyqtSignal(list)
    processing_error = pyqtSignal(str)

    def __init__(self, audio_processor: AudioProcessor, config: Dict[str, Any]):
        """
        Initialize the processing thread

        Args:
            audio_processor: Audio processor instance
            config: Processing configuration
        """
        super().__init__()

        self.audio_processor = audio_processor
        self.config = config

    def run(self):
        """Run the processing thread"""
        try:
            # Set the progress callback
            self.audio_processor.set_progress_callback(self.update_progress)

            # Split the audio
            output_files = self.audio_processor.split_audio(
                method=self.config.get("method"),
                output_dir=self.config.get("output_dir"),
                output_format=self.config.get("output_format"),
                naming_pattern=self.config.get("naming_pattern"),
                **self.config
            )

            # Emit the finished signal
            self.processing_finished.emit(output_files)
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            self.processing_error.emit(str(e))

    def update_progress(self, progress: int, message: str):
        """
        Update the progress

        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        self.progress_updated.emit(progress, message)


class ProcessTab(QWidget):
    """
    Tab for processing audio and displaying results
    """

    # Signals
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal(list)
    processing_error = pyqtSignal(str)

    def __init__(self, audio_processor: AudioProcessor):
        """
        Initialize the process tab

        Args:
            audio_processor: Audio processor instance
        """
        super().__init__()

        self.audio_processor = audio_processor
        self.config = {}
        self.output_files = []
        self.processing_thread = None

        # Set up the UI
        self.setup_ui()

        # Connect signals
        self.connect_signals()

        # Disable the tab initially
        self.setEnabled(False)

    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title label
        title_label = QLabel(tr("ui.process_tab.title", "Processing & Results"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Configuration summary group
        config_group = QGroupBox(tr("ui.process_tab.config_group", "Configuration Summary"))
        config_layout = QFormLayout(config_group)
        config_layout.setContentsMargins(20, 20, 20, 20)
        config_layout.setSpacing(10)
        main_layout.addWidget(config_group)

        # Configuration summary labels
        self.method_label = QLabel()
        self.output_dir_label = QLabel()
        self.output_format_label = QLabel()
        self.naming_pattern_label = QLabel()

        config_layout.addRow(tr("ui.process_tab.method_label", "Splitting Method:"), self.method_label)
        config_layout.addRow(tr("ui.process_tab.output_dir_label", "Output Directory:"), self.output_dir_label)
        config_layout.addRow(tr("ui.process_tab.output_format_label", "Output Format:"), self.output_format_label)
        config_layout.addRow(tr("ui.process_tab.naming_pattern_label", "Naming Pattern:"), self.naming_pattern_label)

        # Process button
        self.process_button = QPushButton(tr("ui.process_tab.process_button", "Start Processing"))
        self.process_button.setMinimumHeight(40)
        main_layout.addWidget(self.process_button)

        # Progress group
        progress_group = QGroupBox(tr("ui.process_tab.progress_group", "Processing Progress"))
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        progress_layout.setSpacing(10)
        main_layout.addWidget(progress_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        # Current operation label
        self.operation_label = QLabel(tr("ui.main_window.status_ready", "Ready"))
        self.operation_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.operation_label)

        # Processing log
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(100)
        progress_layout.addWidget(self.log_edit)

        # Results group
        results_group = QGroupBox(tr("ui.process_tab.results_group", "Results"))
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(10)
        main_layout.addWidget(results_group)

        # Results table
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels([
            tr("ui.process_tab.file_name_column", "File Name"),
            tr("ui.process_tab.duration_column", "Duration"),
            tr("ui.process_tab.size_column", "Size")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setMinimumHeight(150)
        results_layout.addWidget(self.results_table)

        # Action buttons
        action_layout = QHBoxLayout()

        self.open_folder_button = QPushButton(tr("ui.process_tab.open_folder_button", "Open Output Folder"))
        self.play_all_button = QPushButton(tr("ui.process_tab.play_all_button", "Play All"))
        self.reset_button = QPushButton(tr("ui.process_tab.reset_button", "Reset"))

        action_layout.addWidget(self.open_folder_button)
        action_layout.addWidget(self.play_all_button)
        action_layout.addWidget(self.reset_button)

        results_layout.addLayout(action_layout)

        # Add spacer at the bottom
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Initially hide the progress and results groups
        progress_group.setVisible(False)
        results_group.setVisible(False)

        # Store references to the groups
        self.progress_group = progress_group
        self.results_group = results_group

    def connect_signals(self):
        """Connect signals between components"""
        # Process button
        self.process_button.clicked.connect(self.start_processing)

        # Action buttons
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.play_all_button.clicked.connect(self.play_all)
        self.reset_button.clicked.connect(self.reset)

    def set_configuration(self, config: Dict[str, Any]):
        """
        Set the processing configuration

        Args:
            config: Processing configuration
        """
        self.config = config

        # Update the configuration summary
        self.update_config_summary()

        # Enable the tab
        self.setEnabled(True)

    def get_naming_pattern_example(self, pattern: str) -> str:
        """
        Generate a user-friendly example of the naming pattern

        Args:
            pattern: The naming pattern string

        Returns:
            User-friendly example string
        """
        try:
            # Generate an example filename using the pattern
            example = generate_output_filename(
                original_name="MyAudio",
                part_number=1,
                pattern=pattern,
                extension="mp3"
            )
            return f"Example: {example}"
        except Exception:
            # If the pattern is invalid, just show it as is with a note
            return f"Pattern: {pattern}"

    def update_config_summary(self):
        """Update the configuration summary labels"""
        # Method
        method = self.config.get("method", "")
        if method == "equal_parts":
            num_parts = self.config.get("num_parts", 2)
            self.method_label.setText(f"Equal Parts ({num_parts} parts)")
        elif method == "fixed_duration":
            duration = self.config.get("duration", 60)
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.method_label.setText(f"Fixed Duration ({minutes:02d}:{seconds:02d} per segment)")
        elif method == "custom_ranges":
            ranges = self.config.get("ranges", [])
            self.method_label.setText(f"Custom Ranges ({len(ranges)} segments)")
        else:
            self.method_label.setText("Unknown")

        # Output directory
        self.output_dir_label.setText(self.config.get("output_dir", ""))

        # Output format
        output_format = self.config.get("output_format", "")
        output_quality = self.config.get("output_quality", "medium")
        self.output_format_label.setText(f"{output_format.upper()} ({output_quality} quality)")

        # Naming pattern - show user-friendly example
        naming_pattern = self.config.get("naming_pattern", "")
        self.naming_pattern_label.setText(self.get_naming_pattern_example(naming_pattern))

    def start_processing(self):
        """Start the audio processing"""
        # Show the progress group
        self.progress_group.setVisible(True)

        # Hide the results group
        self.results_group.setVisible(False)

        # Reset the progress bar and log
        self.progress_bar.setValue(0)
        self.operation_label.setText("Starting...")
        self.log_edit.clear()

        # Log the configuration
        self.log(f"Starting processing with configuration:")
        self.log(f"Method: {self.method_label.text()}")
        self.log(f"Output Directory: {self.output_dir_label.text()}")
        self.log(f"Output Format: {self.output_format_label.text()}")
        self.log(f"Naming Pattern: {self.naming_pattern_label.text()}")

        # Disable the process button
        self.process_button.setEnabled(False)

        # Emit the processing started signal
        self.processing_started.emit()

        # Create and start the processing thread
        self.processing_thread = ProcessingThread(self.audio_processor, self.config)
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_finished.connect(self.on_processing_finished)
        self.processing_thread.processing_error.connect(self.on_processing_error)
        self.processing_thread.start()

    def update_progress(self, progress: int, message: str):
        """
        Update the progress display

        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        self.progress_bar.setValue(progress)
        self.operation_label.setText(message)
        self.log(message)

    def on_processing_finished(self, output_files: List[str]):
        """
        Handle processing finished event

        Args:
            output_files: List of output file paths
        """
        self.output_files = output_files

        # Log the results
        self.log(f"Processing complete. Created {len(output_files)} files.")

        # Update the results table
        self.update_results_table()

        # Show the results group
        self.results_group.setVisible(True)

        # Enable the process button
        self.process_button.setEnabled(True)

        # Emit the processing finished signal
        self.processing_finished.emit(output_files)

    def on_processing_error(self, error_message: str):
        """
        Handle processing error event

        Args:
            error_message: Error message
        """
        # Log the error
        self.log(f"Error: {error_message}")

        # Update the operation label
        self.operation_label.setText(f"Error: {error_message}")

        # Enable the process button
        self.process_button.setEnabled(True)

        # Emit the processing error signal
        self.processing_error.emit(error_message)

    def update_results_table(self):
        """Update the results table with the output files"""
        # Clear the table
        self.results_table.setRowCount(0)

        # Add the output files
        for i, file_path in enumerate(self.output_files):
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"

            # Add row to the table
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            # Add items to the row
            self.results_table.setItem(row, 0, QTableWidgetItem(file_name))
            self.results_table.setItem(row, 1, QTableWidgetItem("N/A"))  # Duration would require loading the file
            self.results_table.setItem(row, 2, QTableWidgetItem(size_str))

    def open_output_folder(self):
        """Open the output folder in the file explorer"""
        output_dir = self.config.get("output_dir", "")
        if output_dir and os.path.exists(output_dir):
            open_directory(output_dir)

    def play_all(self):
        """Play all the output files"""
        # This would normally use a media player to play the files
        self.log("Play all functionality not implemented yet")

    def reset(self):
        """Reset the processing tab"""
        # Clear the output files
        self.output_files = []

        # Clear the results table
        self.results_table.setRowCount(0)

        # Hide the progress and results groups
        self.progress_group.setVisible(False)
        self.results_group.setVisible(False)

        # Reset the progress bar and log
        self.progress_bar.setValue(0)
        self.operation_label.setText("Ready")
        self.log_edit.clear()

        # Enable the process button
        self.process_button.setEnabled(True)

    def log(self, message: str):
        """
        Add a message to the log

        Args:
            message: Message to add
        """
        self.log_edit.append(message)

        # Scroll to the bottom
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum()
        )

    def update_translations(self):
        """Update all translated strings in the tab"""
        # Create a translation map for common UI elements
        translation_map = {
            "Processing & Results": "ui.process_tab.title",
            "Configuration Summary": "ui.process_tab.config_summary_group",
            "Start Processing": "ui.process_tab.process_button",
            "Processing": "ui.process_tab.progress_group",
            "Operation:": "ui.process_tab.operation_label",
            "Progress:": "ui.process_tab.progress_label",
            "Log:": "ui.process_tab.log_label",
            "Results": "ui.process_tab.results_group",
            "Output Files": "ui.process_tab.results_table_title",
            "Filename": "ui.process_tab.filename_column",
            "Duration": "ui.process_tab.duration_column",
            "Size": "ui.process_tab.size_column",
            "Open Output Folder": "ui.process_tab.open_folder_button",
            "Clear Results": "ui.process_tab.clear_button"
        }

        # Update all widgets using the translation map
        update_ui_translations(self, translation_map)

        # Update table headers
        if hasattr(self, 'results_table'):
            if self.results_table.columnCount() >= 3:
                self.results_table.setHorizontalHeaderItem(0, QTableWidgetItem(tr("ui.process_tab.filename_column", "Filename")))
                self.results_table.setHorizontalHeaderItem(1, QTableWidgetItem(tr("ui.process_tab.duration_column", "Duration")))
                self.results_table.setHorizontalHeaderItem(2, QTableWidgetItem(tr("ui.process_tab.size_column", "Size")))