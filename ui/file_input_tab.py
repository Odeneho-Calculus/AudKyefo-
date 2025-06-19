"""
File input tab for AudKyɛfo
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Add the project root to the Python path when running this file directly
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QGroupBox, QFormLayout, QSizePolicy,
    QSpacerItem, QFrame, QSlider, QStyle, QToolButton,
    QApplication, QScrollArea
)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QSize, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from core.audio_processor import AudioProcessor
from core.config_manager import ConfigManager
from utils.helpers import format_time
from utils.constants import (
    SUPPORTED_INPUT_FORMATS, PRIMARY_COLOR, SECONDARY_COLOR,
    BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR
)
from utils.translation_loader import tr
from utils.style_loader import get_theme_colors
from utils.ui_translator import update_ui_translations

# Set up logging
logger = logging.getLogger(__name__)

class FileInputTab(QWidget):
    """
    Tab for selecting and previewing audio files
    """

    # Signals
    file_loaded = pyqtSignal(bool, dict)  # success, metadata

    def __init__(self, audio_processor: AudioProcessor):
        """
        Initialize the file input tab

        Args:
            audio_processor: Audio processor instance
        """
        super().__init__()

        self.audio_processor = audio_processor
        self.current_file = None
        self.is_playing = False
        self.previous_volume = 70  # Default volume level

        # Get theme colors
        self.config_manager = ConfigManager()
        self.theme_colors = get_theme_colors()

        # Set up the UI
        self.setup_ui()

        # Initialize audio player
        self.initialize_audio_player()

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Create media player
        self.media_player = QMediaPlayer()
        self.media_player.setVolume(self.previous_volume)

        # Connect media player signals
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.stateChanged.connect(self.media_state_changed)

        # Timer for updating the position slider
        self.position_timer = QTimer(self)
        self.position_timer.setInterval(1000)  # Update every second
        self.position_timer.timeout.connect(self.update_position_timer)

        # We'll update the theme when the tab is shown
        # Add a showEvent handler to update the theme

    def initialize_audio_player(self):
        """Initialize the audio player controls and connections"""
        # This would normally initialize a media player component
        # For now, we'll just set up the UI connections

        # Connect time slider
        self.time_slider.sliderMoved.connect(self.seek_audio)

        # Initialize time display
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")

        # Set initial volume
        self.volume_slider.setValue(self.previous_volume)

        # Log initialization
        logger.info("Audio player controls initialized")

    def setup_ui(self):
        """Set up the user interface"""
        # Create a content widget for the scroll area
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Create scroll area for better navigation
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove frame border

        # Set scroll area as the main widget
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)

        # Title label with enhanced styling
        title_label = QLabel(tr("ui.file_input_tab.title", "Select Audio File"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {self.theme_colors['highlight']};
            margin-bottom: 10px;
            background-color: transparent;
        """)
        main_layout.addWidget(title_label)

        # Add a separator line under the title
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {self.theme_colors['highlight']}; max-height: 2px;")
        main_layout.addWidget(separator)

        # File selection section
        file_selection_group = QGroupBox()
        file_selection_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {self.theme_colors['border']};
                border-radius: 8px;
                background-color: {self.theme_colors['background_secondary']};
                margin-top: 15px;
            }}
            QGroupBox QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        file_selection_layout = QVBoxLayout(file_selection_group)
        file_selection_layout.setContentsMargins(15, 15, 15, 15)
        file_selection_layout.setSpacing(15)
        main_layout.addWidget(file_selection_group)

        # Section title
        section_title = QLabel(tr("ui.file_input_tab.section_title", "Audio File Selection"))
        section_title.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {self.theme_colors['text']};
            background-color: transparent;
            border: none;
        """)
        file_selection_layout.addWidget(section_title)

        # Drop zone with enhanced visual cues
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.load_file)
        file_selection_layout.addWidget(self.drop_zone)

        # Browse button with icon and better sizing
        browse_button = QPushButton(tr("ui.file_input_tab.browse_button", "Browse for Audio File"))
        # Get system folder icon
        browse_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        browse_button.setIconSize(QSize(20, 20))
        browse_button.setFixedHeight(40)
        browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors['highlight_secondary']};
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors['highlight_secondary']};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self.theme_colors['highlight_secondary']};
                opacity: 1.0;
            }}
        """)
        browse_button.clicked.connect(self.browse_file)
        file_selection_layout.addWidget(browse_button)

        # File info group box with enhanced styling
        self.file_info_group = QGroupBox(tr("ui.file_input_tab.file_info_group", "File Information"))
        self.file_info_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {self.theme_colors['border']};
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
                background-color: {self.theme_colors['background_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {self.theme_colors['highlight']};
                background-color: transparent;
            }}
            QGroupBox QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        self.file_info_group.setVisible(False)
        main_layout.addWidget(self.file_info_group)

        # File info layout with better organization
        file_info_layout = QFormLayout(self.file_info_group)
        file_info_layout.setContentsMargins(20, 25, 20, 20)
        file_info_layout.setSpacing(12)
        file_info_layout.setLabelAlignment(Qt.AlignRight)
        file_info_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # File info labels with better styling
        self.filename_label = QLabel()
        self.format_label = QLabel()
        self.duration_label = QLabel()
        self.channels_label = QLabel()
        self.sample_rate_label = QLabel()
        self.size_label = QLabel()

        # Apply consistent styling to all value labels
        for label in [self.filename_label, self.format_label, self.duration_label,
                     self.channels_label, self.sample_rate_label, self.size_label]:
            label.setStyleSheet("""
                font-weight: normal;
                padding: 2px;
                background-color: transparent;
                border: none;
            """)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Add rows with styled field labels
        field_style = """
            font-weight: bold;
            color: #555555;
            background-color: transparent;
            border: none;
        """
        file_name_field = QLabel(tr("ui.file_input_tab.filename_label", "File Name:"))
        file_name_field.setStyleSheet(field_style)
        file_info_layout.addRow(file_name_field, self.filename_label)

        format_field = QLabel(tr("ui.file_input_tab.format_label", "Format:"))
        format_field.setStyleSheet(field_style)
        file_info_layout.addRow(format_field, self.format_label)

        duration_field = QLabel(tr("ui.file_input_tab.duration_label", "Duration:"))
        duration_field.setStyleSheet(field_style)
        file_info_layout.addRow(duration_field, self.duration_label)

        channels_field = QLabel(tr("ui.file_input_tab.channels_label", "Channels:"))
        channels_field.setStyleSheet(field_style)
        file_info_layout.addRow(channels_field, self.channels_label)

        sample_rate_field = QLabel(tr("ui.file_input_tab.sample_rate_label", "Sample Rate:"))
        sample_rate_field.setStyleSheet(field_style)
        file_info_layout.addRow(sample_rate_field, self.sample_rate_label)

        size_field = QLabel(tr("ui.file_input_tab.size_label", "File Size:"))
        size_field.setStyleSheet(field_style)
        file_info_layout.addRow(size_field, self.size_label)

        # Enhanced audio preview group
        self.preview_group = QGroupBox(tr("ui.file_input_tab.preview_group", "Audio Preview"))
        self.preview_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {PRIMARY_COLOR};
            }}
        """)
        self.preview_group.setVisible(False)
        main_layout.addWidget(self.preview_group)

        # Preview layout with more controls
        preview_layout = QVBoxLayout(self.preview_group)
        preview_layout.setContentsMargins(20, 25, 20, 20)
        preview_layout.setSpacing(15)

        # Time display
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        preview_layout.addLayout(time_layout)

        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        self.time_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #999999;
                height: 8px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {SECONDARY_COLOR};
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {SECONDARY_COLOR};
                border-radius: 4px;
            }}
        """)
        preview_layout.addWidget(self.time_slider)

        # Control buttons layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Rewind button
        self.rewind_button = QToolButton()
        self.rewind_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.rewind_button.setIconSize(QSize(24, 24))
        self.rewind_button.setToolTip("Rewind")
        self.rewind_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border-radius: 12px;
            }
        """)
        controls_layout.addWidget(self.rewind_button)

        # Play/pause button
        self.play_button = QToolButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setIconSize(QSize(32, 32))
        self.play_button.setToolTip("Play")
        self.play_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border-radius: 16px;
            }
        """)
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)

        # Forward button
        self.forward_button = QToolButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.forward_button.setIconSize(QSize(24, 24))
        self.forward_button.setToolTip("Forward")
        self.forward_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border-radius: 12px;
            }
        """)
        controls_layout.addWidget(self.forward_button)

        # Volume button
        self.volume_button = QToolButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.volume_button.setIconSize(QSize(24, 24))
        self.volume_button.setToolTip("Volume")
        self.volume_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border-radius: 12px;
            }
        """)
        controls_layout.addWidget(self.volume_button)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #999999;
                height: 4px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {SECONDARY_COLOR};
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {SECONDARY_COLOR};
                border-radius: 2px;
            }}
        """)
        controls_layout.addWidget(self.volume_slider)

        # Add controls to preview layout
        preview_layout.addLayout(controls_layout)

        # Add spacer at the bottom
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def browse_file(self):
        """Open a file dialog to select an audio file"""
        file_filter = "Audio Files ("
        for fmt in SUPPORTED_INPUT_FORMATS:
            file_filter += f"*.{fmt} "
        file_filter = file_filter.strip() + ");;All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", file_filter
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """
        Load an audio file

        Args:
            file_path: Path to the audio file
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            self.file_loaded.emit(False, {})
            return

        # Load the file using the audio processor
        success = self.audio_processor.load_file(file_path)

        if success:
            self.current_file = file_path
            metadata = self.audio_processor.get_metadata()
            self.update_file_info(metadata)

            # Load the file into the media player
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

            # Reset playback state
            self.is_playing = False
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_button.setToolTip("Play")

            self.file_loaded.emit(True, metadata)
        else:
            self.current_file = None
            self.file_info_group.setVisible(False)
            self.preview_group.setVisible(False)
            self.file_loaded.emit(False, {})

    def update_file_info(self, metadata: Dict[str, Any]):
        """
        Update the file information display

        Args:
            metadata: File metadata
        """
        # Update file information labels with enhanced formatting
        self.filename_label.setText(metadata.get("filename", "Unknown"))
        self.format_label.setText(metadata.get("format", "Unknown").upper())

        duration = metadata.get("duration_seconds", 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_text = f"{minutes:02d}:{seconds:02d}"
        self.duration_label.setText(duration_text)

        self.channels_label.setText(str(metadata.get("channels", "Unknown")))
        self.sample_rate_label.setText(f"{metadata.get('frame_rate', 0):,} Hz")
        self.size_label.setText(metadata.get("size_human", "Unknown"))

        # Show the file info group with a smooth transition
        self.file_info_group.setVisible(True)

        # Update audio preview elements
        self.current_time_label.setText("00:00")
        self.total_time_label.setText(duration_text)
        self.time_slider.setValue(0)

        # Reset playback controls
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("Play")

        # Show the preview group with a smooth transition
        self.preview_group.setVisible(True)

        # Log the loaded file information
        logger.info(f"Loaded audio file: {metadata.get('filename', 'Unknown')}")
        logger.info(f"Format: {metadata.get('format', 'Unknown').upper()}, "
                   f"Duration: {duration_text}, "
                   f"Channels: {metadata.get('channels', 'Unknown')}, "
                   f"Sample Rate: {metadata.get('frame_rate', 0)} Hz")

    def toggle_playback(self):
        """Toggle audio playback"""
        if not self.current_file:
            logger.warning("No file loaded to play")
            return

        if self.play_button.toolTip() == "Play":
            # Change to pause icon
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_button.setToolTip("Pause")

            # Start audio playback
            self.media_player.play()
            self.is_playing = True

            # Start the position update timer
            self.position_timer.start()

            # Connect the control buttons if not already connected
            if not self.rewind_button.receivers(self.rewind_button.clicked):
                self.rewind_button.clicked.connect(self.rewind_audio)
                self.forward_button.clicked.connect(self.forward_audio)
                self.volume_button.clicked.connect(self.toggle_mute)
                self.volume_slider.valueChanged.connect(self.set_volume)

            # Log the action
            logger.info(f"Started playback of {self.current_file}")
        else:
            # Change to play icon
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_button.setToolTip("Play")

            # Pause audio playback
            self.media_player.pause()
            self.is_playing = False

            # Stop the position update timer
            self.position_timer.stop()

            # Log the action
            logger.info(f"Paused playback of {self.current_file}")

    def rewind_audio(self):
        """Rewind the audio by 5 seconds"""
        if not self.current_file:
            return

        # Rewind the audio by 5 seconds
        current_position = self.media_player.position()
        new_position = max(0, current_position - 5000)  # 5000 ms = 5 seconds
        self.media_player.setPosition(new_position)
        logger.info(f"Rewind audio to {new_position} ms")

    def forward_audio(self):
        """Forward the audio by 5 seconds"""
        if not self.current_file:
            return

        # Forward the audio by 5 seconds
        current_position = self.media_player.position()
        duration = self.media_player.duration()
        new_position = min(duration, current_position + 5000)  # 5000 ms = 5 seconds
        self.media_player.setPosition(new_position)
        logger.info(f"Forward audio to {new_position} ms")

    def toggle_mute(self):
        """Toggle audio mute"""
        if not self.current_file:
            return

        # Toggle audio mute
        if self.media_player.volume() > 0:
            self.previous_volume = self.media_player.volume()
            self.media_player.setVolume(0)
            self.volume_slider.setValue(0)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            volume_to_set = self.previous_volume if hasattr(self, 'previous_volume') and self.previous_volume > 0 else 70
            self.media_player.setVolume(volume_to_set)
            self.volume_slider.setValue(volume_to_set)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        logger.info(f"Toggle mute: {'Muted' if self.media_player.volume() == 0 else 'Unmuted'}")

    def set_volume(self, value):
        """Set the audio volume"""
        if not self.current_file:
            return

        # Set the audio volume
        self.media_player.setVolume(value)

        # Update the volume button icon based on the volume level
        if value == 0:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        elif value < 30:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        else:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        logger.info(f"Set volume to {value}%")

    def seek_audio(self, position):
        """
        Seek to a position in the audio file

        Args:
            position: Position in the slider (0-100)
        """
        if not self.current_file:
            return

        # Calculate the position in milliseconds
        duration = self.media_player.duration()
        if duration > 0:
            # Convert slider position (0-100) to milliseconds
            position_ms = int((position / 100.0) * duration)

            # Set the position in the media player
            self.media_player.setPosition(position_ms)

            # Update the current time label
            minutes = int(position_ms / 60000)
            seconds = int((position_ms % 60000) / 1000)
            self.current_time_label.setText(f"{minutes:02d}:{seconds:02d}")

            logger.info(f"Seek to position {position}% ({minutes:02d}:{seconds:02d})")

    def update_position(self, position):
        """
        Update the position slider and time label when the media position changes

        Args:
            position: Current position in milliseconds
        """
        if self.time_slider.isSliderDown():
            return  # Don't update if user is dragging the slider

        # Update the time slider
        duration = self.media_player.duration()
        if duration > 0:
            # Convert position to slider value (0-100)
            slider_value = int((position / duration) * 100)
            self.time_slider.setValue(slider_value)

        # Update the current time label
        minutes = int(position / 60000)
        seconds = int((position % 60000) / 1000)
        self.current_time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_position_timer(self):
        """Update position from timer for smoother updates"""
        if self.is_playing and not self.time_slider.isSliderDown():
            self.update_position(self.media_player.position())

    def update_duration(self, duration):
        """
        Update the total time label when the media duration is available

        Args:
            duration: Total duration in milliseconds
        """
        # Update the total time label
        minutes = int(duration / 60000)
        seconds = int((duration % 60000) / 1000)
        self.total_time_label.setText(f"{minutes:02d}:{seconds:02d}")

        # Reset the time slider
        self.time_slider.setValue(0)

    def media_state_changed(self, state):
        """
        Handle media state changes

        Args:
            state: New media state
        """
        from PyQt5.QtMultimedia import QMediaPlayer

        if state == QMediaPlayer.StoppedState:
            # Media playback has stopped (reached the end or stopped manually)
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_button.setToolTip("Play")
            self.is_playing = False
            self.position_timer.stop()

            # Reset position to beginning
            self.time_slider.setValue(0)
            self.current_time_label.setText("00:00")

            logger.info("Media playback stopped")

    def showEvent(self, event):
        """Handle show event to update theme"""
        # Update theme colors when the tab is shown
        self.theme_colors = get_theme_colors()

        # Update UI with new theme colors
        self.update_theme()

        # Call the parent class's showEvent
        super().showEvent(event)

    def update_translations(self):
        """Update all translated strings in the tab"""
        # Create a translation map for common UI elements
        translation_map = {
            "Select Audio File": "ui.file_input_tab.title",
            "Audio File Selection": "ui.file_input_tab.section_title",
            "Browse for Audio File": "ui.file_input_tab.browse_button",
            "File Information": "ui.file_input_tab.file_info_group",
            "File Name:": "ui.file_input_tab.filename_label",
            "Format:": "ui.file_input_tab.format_label",
            "Duration:": "ui.file_input_tab.duration_label",
            "Channels:": "ui.file_input_tab.channels_label",
            "Sample Rate:": "ui.file_input_tab.sample_rate_label",
            "File Size:": "ui.file_input_tab.size_label",
            "Audio Preview": "ui.file_input_tab.preview_group",
            "Play": "ui.file_input_tab.play_button",
            "Pause": "ui.file_input_tab.pause_button",
            "Rewind": "ui.file_input_tab.rewind_button",
            "Forward": "ui.file_input_tab.forward_button",
            "Volume": "ui.file_input_tab.volume_label"
        }

        # Update all widgets using the translation map
        update_ui_translations(self, translation_map)

        # Update drop zone translations
        if hasattr(self, 'drop_zone') and hasattr(self.drop_zone, 'update_translations'):
            self.drop_zone.update_translations()

    def update_theme(self):
        """Update the UI with the current theme colors"""
        # Update the drop zone
        self.drop_zone.update_theme(self.theme_colors)

        # Update file info group
        self.file_info_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {self.theme_colors['border']};
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
                background-color: {self.theme_colors['background_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {self.theme_colors['highlight']};
            }}
        """)

        # Update preview group
        self.preview_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {self.theme_colors['border']};
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
                background-color: {self.theme_colors['background_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {self.theme_colors['highlight']};
            }}
        """)

        # Update sliders
        self.time_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.theme_colors['border']};
                height: 8px;
                background: {self.theme_colors['form_field_bg']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.theme_colors['highlight_secondary']};
                border: 1px solid {self.theme_colors['border']};
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {self.theme_colors['highlight_secondary']};
                border-radius: 4px;
            }}
        """)

        self.volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.theme_colors['border']};
                height: 4px;
                background: {self.theme_colors['form_field_bg']};
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {self.theme_colors['highlight_secondary']};
                border: 1px solid {self.theme_colors['border']};
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {self.theme_colors['highlight_secondary']};
                border-radius: 2px;
            }}
        """)

        # Update control buttons
        button_style = f"""
            QToolButton {{
                border: none;
                padding: 5px;
                background-color: transparent;
                color: {self.theme_colors['text']};
            }}
            QToolButton:hover {{
                background-color: {self.theme_colors['hover_bg']};
                border-radius: 12px;
            }}
        """

        self.rewind_button.setStyleSheet(button_style)
        self.forward_button.setStyleSheet(button_style)
        self.volume_button.setStyleSheet(button_style)

        # Play button is slightly larger
        self.play_button.setStyleSheet(f"""
            QToolButton {{
                border: none;
                padding: 5px;
                background-color: transparent;
                color: {self.theme_colors['text']};
            }}
            QToolButton:hover {{
                background-color: {self.theme_colors['hover_bg']};
                border-radius: 16px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter event

        Args:
            event: Drag enter event
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        Handle drop event

        Args:
            event: Drop event
        """
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.load_file(file_path)
            event.acceptProposedAction()


class DropZone(QFrame):
    """
    Enhanced drop zone widget for dragging and dropping files
    """

    # Signals
    file_dropped = pyqtSignal(str)

    def __init__(self):
        """Initialize the drop zone"""
        super().__init__()

        # Get theme colors
        self.theme_colors = get_theme_colors()

        # Set up the UI
        self.setup_ui()

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Track hover state
        self.is_hovering = False

    def update_theme(self, theme_colors):
        """Update the UI with the current theme colors"""
        self.theme_colors = theme_colors

        # Update the styling with improved drop zone visuals
        self.setStyleSheet(f"""
            DropZone {{
                background-color: {self.theme_colors['drop_zone_bg']};
                border: 2px dashed {self.theme_colors['drop_zone_border']};
                border-radius: 8px;
                padding: 10px;
                color: {self.theme_colors['text']};
            }}
            DropZone:hover {{
                background-color: {self.theme_colors['drop_zone_hover_bg']};
                border-color: {self.theme_colors['drop_zone_hover_border']};
                border-width: 3px;
            }}
            DropZone QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        # Update text colors with explicit transparency for all labels
        for child in self.findChildren(QLabel):
            if "Drop audio file here" in child.text():
                child.setStyleSheet(f"""
                    font-size: 18px;
                    font-weight: bold;
                    color: {self.theme_colors['highlight']};
                    margin-top: 5px;
                    background-color: transparent;
                    border: none;
                """)
            elif "Or click" in child.text():
                child.setStyleSheet(f"""
                    font-size: 14px;
                    color: {self.theme_colors['text']};
                    background-color: transparent;
                    border: none;
                """)
            elif "Supported formats" in child.text():
                child.setStyleSheet(f"""
                    font-size: 12px;
                    color: {self.theme_colors['text']};
                    margin-top: 5px;
                    background-color: transparent;
                    padding: 5px 10px;
                    border: none;
                """)

    def setup_ui(self):
        """Set up the user interface with enhanced visual cues"""
        # Set frame style with dashed border as requested in the UI critique
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        # Use sizePolicy to allow the widget to expand vertically as needed
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setSizePolicy(size_policy)

        # Apply advanced styling with proper transparency for all child elements
        self.setStyleSheet(f"""
            DropZone {{
                background-color: {self.theme_colors['drop_zone_bg']};
                border: 2px dashed {self.theme_colors['drop_zone_border']};
                border-radius: 8px;
                padding: 15px;
                color: {self.theme_colors['text']};
            }}
            DropZone:hover {{
                background-color: {self.theme_colors['drop_zone_hover_bg']};
                border-color: {self.theme_colors['drop_zone_hover_border']};
                border-width: 3px;
            }}
            DropZone QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        # Layout with better spacing and alignment
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 30, 25, 30)  # More generous margins
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Icon label with system icon and proper transparency
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")

        # Use system icon for audio files
        audio_icon = self.style().standardIcon(QStyle.SP_FileIcon)
        icon_pixmap = audio_icon.pixmap(64, 64)
        icon_label.setPixmap(icon_pixmap)

        layout.addWidget(icon_label)
        self.icon_label = icon_label  # Store reference for hover effects

        # Main instruction with emoji and proper styling
        text_label = QLabel(tr("ui.file_input_tab.drop_zone_text", "🎵 Drag and drop an audio file here"))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {self.theme_colors['highlight']};
            margin-top: 5px;
            background-color: transparent;
            border: none;
        """)
        layout.addWidget(text_label)
        self.text_label = text_label  # Store reference for translation updates

        # Secondary instruction with proper transparency
        secondary_label = QLabel(tr("ui.file_input_tab.drop_zone_secondary", "Or click <b>Browse for Audio File</b>"))
        secondary_label.setAlignment(Qt.AlignCenter)
        secondary_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self.theme_colors['text']};
            background-color: transparent;
            border: none;
        """)
        layout.addWidget(secondary_label)
        self.secondary_label = secondary_label  # Store reference for translation updates

        # Supported formats with improved styling and proper transparency
        formats_text = ", ".join(SUPPORTED_INPUT_FORMATS).upper()
        formats_label = QLabel(tr("ui.file_input_tab.supported_formats", "Supported formats: {formats}").format(formats=formats_text))
        formats_label.setAlignment(Qt.AlignCenter)
        formats_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.theme_colors['text']};
            margin-top: 8px;
            background-color: transparent;
            padding: 6px 12px;
            border: none;
        """)
        layout.addWidget(formats_label)
        self.formats_label = formats_label  # Store reference for translation updates

    def enterEvent(self, event):
        """Handle mouse enter event for hover effects"""
        self.is_hovering = True

        # Change the icon to a highlighted version with proper transparency
        audio_icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.icon_label.setPixmap(audio_icon.pixmap(72, 72))  # Slightly larger on hover
        self.icon_label.setStyleSheet("background-color: transparent;")

        # Apply hover styling with proper transparency for all elements
        self.setStyleSheet(f"""
            DropZone {{
                background-color: {self.theme_colors['drop_zone_hover_bg']};
                border: 3px dashed {self.theme_colors['drop_zone_hover_border']};
                border-radius: 8px;
                padding: 15px;
                color: {self.theme_colors['text']};
            }}
            DropZone QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event for hover effects"""
        self.is_hovering = False

        # Restore the original icon with proper transparency
        audio_icon = self.style().standardIcon(QStyle.SP_FileIcon)
        self.icon_label.setPixmap(audio_icon.pixmap(64, 64))
        self.icon_label.setStyleSheet("background-color: transparent;")

        # Reset to normal styling with proper transparency for all elements
        self.setStyleSheet(f"""
            DropZone {{
                background-color: {self.theme_colors['drop_zone_bg']};
                border: 2px dashed {self.theme_colors['drop_zone_border']};
                border-radius: 8px;
                padding: 15px;
                color: {self.theme_colors['text']};
            }}
            DropZone:hover {{
                background-color: {self.theme_colors['drop_zone_hover_bg']};
                border-color: {self.theme_colors['drop_zone_hover_border']};
                border-width: 3px;
            }}
            DropZone QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        super().leaveEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter event with enhanced visual feedback

        Args:
            event: Drag enter event
        """
        if event.mimeData().hasUrls():
            # Check if it's an audio file
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')

            if file_ext in SUPPORTED_INPUT_FORMATS:
                # Change styling to indicate valid drop target with proper transparency for labels
                self.setStyleSheet(f"""
                    DropZone {{
                        background-color: {self.theme_colors['valid_drop_bg']};
                        border: 3px dashed {self.theme_colors['highlight']};
                        border-radius: 8px;
                        padding: 15px;
                        color: {self.theme_colors['text']};
                    }}
                    DropZone QLabel {{
                        background-color: transparent;
                        border: none;
                    }}
                """)

                # Change icon to indicate valid file
                audio_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
                self.icon_label.setPixmap(audio_icon.pixmap(72, 72))
                self.icon_label.setStyleSheet("background-color: transparent;")

                event.acceptProposedAction()
            else:
                # Change styling to indicate invalid file type with proper transparency for labels
                self.setStyleSheet(f"""
                    DropZone {{
                        background-color: {self.theme_colors['invalid_drop_bg']};
                        border: 3px dashed {self.theme_colors['invalid_drop_border']};
                        border-radius: 8px;
                        padding: 15px;
                        color: {self.theme_colors['text']};
                    }}
                    DropZone QLabel {{
                        background-color: transparent;
                        border: none;
                    }}
                """)

                # Change icon to indicate invalid file
                audio_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                self.icon_label.setPixmap(audio_icon.pixmap(72, 72))
                self.icon_label.setStyleSheet("background-color: transparent;")

                # Don't accept the action for invalid files
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        Handle drop event with enhanced visual feedback

        Args:
            event: Drop event
        """
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()

            # Reset the styling with proper transparency for all elements
            self.setStyleSheet(f"""
                DropZone {{
                    background-color: {self.theme_colors['drop_zone_bg']};
                    border: 2px dashed {self.theme_colors['drop_zone_border']};
                    border-radius: 8px;
                    padding: 15px;
                    color: {self.theme_colors['text']};
                }}
                DropZone:hover {{
                    background-color: {self.theme_colors['drop_zone_hover_bg']};
                    border-color: {self.theme_colors['drop_zone_hover_border']};
                    border-width: 3px;
                }}
                DropZone QLabel {{
                    background-color: transparent;
                    border: none;
                }}
            """)

            # Reset the icon with proper transparency
            audio_icon = self.style().standardIcon(QStyle.SP_FileIcon)
            self.icon_label.setPixmap(audio_icon.pixmap(64, 64))
            self.icon_label.setStyleSheet("background-color: transparent;")

            # Emit the signal with the file path
            self.file_dropped.emit(file_path)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """
        Handle drag leave event to reset styling

        Args:
            event: Drag leave event
        """
        # Reset the styling with proper transparency for all elements
        self.setStyleSheet(f"""
            DropZone {{
                background-color: {self.theme_colors['drop_zone_bg']};
                border: 2px dashed {self.theme_colors['drop_zone_border']};
                border-radius: 8px;
                padding: 15px;
                color: {self.theme_colors['text']};
            }}
            DropZone:hover {{
                background-color: {self.theme_colors['drop_zone_hover_bg']};
                border-color: {self.theme_colors['drop_zone_hover_border']};
                border-width: 3px;
            }}
            DropZone QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        # Reset the icon with proper transparency
        audio_icon = self.style().standardIcon(QStyle.SP_FileIcon)
        self.icon_label.setPixmap(audio_icon.pixmap(64, 64))
        self.icon_label.setStyleSheet("background-color: transparent;")

        super().dragLeaveEvent(event)

    def update_translations(self):
        """Update all translated strings in the drop zone"""
        if hasattr(self, 'text_label'):
            self.text_label.setText(tr("ui.file_input_tab.drop_zone_text", "🎵 Drag and drop an audio file here"))

        if hasattr(self, 'secondary_label'):
            self.secondary_label.setText(tr("ui.file_input_tab.drop_zone_secondary", "Or click <b>Browse for Audio File</b>"))

        if hasattr(self, 'formats_label'):
            formats_text = ", ".join(SUPPORTED_INPUT_FORMATS).upper()
            self.formats_label.setText(tr("ui.file_input_tab.supported_formats", "Supported formats: {formats}").format(formats=formats_text))


# Add a main function to allow running this file directly for testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from utils.logger import setup_logging
    from utils.style_loader import apply_stylesheet

    # Set up logging
    setup_logging(log_level=logging.INFO)

    # Create the application
    app = QApplication(sys.argv)

    # Create an audio processor instance
    audio_processor = AudioProcessor()

    # Create the file input tab
    file_input_tab = FileInputTab(audio_processor)

    # Apply a stylesheet
    apply_stylesheet(app, "dark")

    # Show the widget
    file_input_tab.setWindowTitle("AudKyɛfo - File Input Test")
    file_input_tab.setGeometry(100, 100, 800, 600)
    file_input_tab.show()

    # Start the event loop
    sys.exit(app.exec_())