"""
Main audio processing logic for AudKyɛfo
"""

import os
import logging
from typing import List, Dict, Tuple, Callable, Optional, Union
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.aac import AAC
from mutagen.mp4 import MP4

from utils.constants import (
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    SPLIT_METHOD_EQUAL,
    SPLIT_METHOD_DURATION,
    SPLIT_METHOD_CUSTOM
)
from utils.helpers import get_file_extension, human_readable_size, ensure_directory_exists
from core.splitter import split_audio

# Set up logging
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Main class for audio processing operations
    """

    def __init__(self):
        """Initialize the audio processor"""
        self.audio_file = None
        self.audio_segment = None
        self.metadata = {}
        self.progress_callback = None

    def set_progress_callback(self, callback: Callable[[int, str], None]) -> None:
        """
        Set a callback function for progress updates

        Args:
            callback: Function that takes progress percentage and status message
        """
        self.progress_callback = callback

    def _update_progress(self, progress: int, message: str) -> None:
        """
        Update progress using the callback if available

        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        if self.progress_callback:
            self.progress_callback(progress, message)

    def load_file(self, file_path: str) -> bool:
        """
        Load an audio file and extract its metadata

        Args:
            file_path: Path to the audio file

        Returns:
            True if the file was loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        self.audio_file = file_path
        extension = get_file_extension(file_path)

        if extension not in SUPPORTED_INPUT_FORMATS:
            logger.error(f"Unsupported file format: {extension}")
            return False

        try:
            self._update_progress(0, f"Loading {os.path.basename(file_path)}...")

            # Load audio file using pydub
            self.audio_segment = AudioSegment.from_file(file_path)

            # Extract metadata
            self._extract_metadata(file_path)

            self._update_progress(10, "File loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")
            self.audio_file = None
            self.audio_segment = None
            self.metadata = {}
            return False

    def _extract_metadata(self, file_path: str) -> None:
        """
        Extract metadata from the audio file

        Args:
            file_path: Path to the audio file
        """
        extension = get_file_extension(file_path)

        # Basic metadata from pydub
        self.metadata = {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "format": extension,
            "channels": self.audio_segment.channels,
            "sample_width": self.audio_segment.sample_width,
            "frame_rate": self.audio_segment.frame_rate,
            "duration_seconds": len(self.audio_segment) / 1000,
            "size_bytes": os.path.getsize(file_path),
            "size_human": human_readable_size(os.path.getsize(file_path))
        }

        # Try to extract additional metadata using mutagen
        try:
            if extension == "mp3":
                audio = MP3(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate,
                    "title": audio.get("TIT2", ["Unknown"])[0],
                    "artist": audio.get("TPE1", ["Unknown"])[0],
                    "album": audio.get("TALB", ["Unknown"])[0]
                })
            elif extension == "wav":
                audio = WAVE(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate
                })
            elif extension == "flac":
                audio = FLAC(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate,
                    "title": audio.get("title", ["Unknown"])[0],
                    "artist": audio.get("artist", ["Unknown"])[0],
                    "album": audio.get("album", ["Unknown"])[0]
                })
            elif extension == "ogg":
                audio = OggVorbis(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate,
                    "title": audio.get("title", ["Unknown"])[0],
                    "artist": audio.get("artist", ["Unknown"])[0],
                    "album": audio.get("album", ["Unknown"])[0]
                })
            elif extension == "aac":
                audio = AAC(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate
                })
            elif extension == "m4a":
                audio = MP4(file_path)
                self.metadata.update({
                    "bitrate": audio.info.bitrate,
                    "title": audio.get("\xa9nam", ["Unknown"])[0],
                    "artist": audio.get("\xa9ART", ["Unknown"])[0],
                    "album": audio.get("\xa9alb", ["Unknown"])[0]
                })
        except Exception as e:
            logger.warning(f"Error extracting additional metadata: {e}")

    def get_metadata(self) -> Dict:
        """
        Get the metadata of the loaded audio file

        Returns:
            Dictionary containing the metadata
        """
        return self.metadata

    def split_audio(
        self,
        method: str,
        output_dir: str,
        output_format: str,
        naming_pattern: str,
        **kwargs
    ) -> List[str]:
        """
        Split the audio file based on the specified method

        Args:
            method: Splitting method (equal_parts, fixed_duration, custom_ranges)
            output_dir: Output directory
            output_format: Output format
            naming_pattern: Naming pattern for output files
            **kwargs: Additional parameters for the splitting method
                - num_parts: Number of equal parts (for equal_parts method)
                - duration: Duration in seconds (for fixed_duration method)
                - ranges: List of (start, end) tuples in seconds (for custom_ranges method)
                - overlap: Overlap duration in seconds

        Returns:
            List of paths to the created audio files
        """
        if not self.audio_segment:
            logger.error("No audio file loaded")
            return []

        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            logger.error(f"Unsupported output format: {output_format}")
            return []

        # Ensure output directory exists
        if not ensure_directory_exists(output_dir):
            logger.error(f"Could not create output directory: {output_dir}")
            return []

        self._update_progress(20, "Analyzing audio...")

        # Get the original filename without extension
        original_name = os.path.splitext(os.path.basename(self.audio_file))[0]

        # Get the overlap duration
        overlap = kwargs.get("overlap", 0)

        # Call the appropriate splitting function
        try:
            self._update_progress(30, f"Splitting audio using {method} method...")

            output_files = split_audio(
                self.audio_segment,
                method,
                output_dir,
                original_name,
                output_format,
                naming_pattern,
                overlap=overlap,
                progress_callback=self._update_progress,
                **kwargs
            )

            self._update_progress(100, f"Splitting complete. Created {len(output_files)} files.")
            return output_files
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            self._update_progress(0, f"Error: {str(e)}")
            return []