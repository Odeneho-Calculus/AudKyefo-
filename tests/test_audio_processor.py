"""
Tests for the audio processor
"""

import os
import unittest
import tempfile
from unittest.mock import MagicMock, patch
from core.audio_processor import AudioProcessor

class TestAudioProcessor(unittest.TestCase):
    """Test case for the AudioProcessor class"""

    def setUp(self):
        """Set up the test case"""
        self.processor = AudioProcessor()

        # Create a mock progress callback
        self.progress_callback = MagicMock()
        self.processor.set_progress_callback(self.progress_callback)

    @patch('core.audio_processor.AudioSegment')
    @patch('core.audio_processor.os.path.exists')
    @patch('core.audio_processor.os.path.getsize')
    def test_load_file(self, mock_getsize, mock_exists, mock_audio_segment):
        """Test the load_file method"""
        # Mock the dependencies
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_audio = MagicMock()
        mock_audio.channels = 2
        mock_audio.sample_width = 2
        mock_audio.frame_rate = 44100
        mock_audio_segment.from_file.return_value = mock_audio

        # Test with a valid file
        result = self.processor.load_file("test.mp3")
        self.assertTrue(result)
        self.assertEqual(self.processor.audio_file, "test.mp3")
        self.assertEqual(self.processor.audio_segment, mock_audio)

        # Check that the progress callback was called
        self.progress_callback.assert_called()

        # Test with a non-existent file
        mock_exists.return_value = False
        result = self.processor.load_file("non_existent.mp3")
        self.assertFalse(result)

        # Test with an exception
        mock_exists.return_value = True
        mock_audio_segment.from_file.side_effect = Exception("Test error")
        result = self.processor.load_file("test.mp3")
        self.assertFalse(result)

    def test_get_metadata(self):
        """Test the get_metadata method"""
        # Set up test metadata
        test_metadata = {"filename": "test.mp3", "duration_seconds": 60}
        self.processor.metadata = test_metadata

        # Test getting the metadata
        metadata = self.processor.get_metadata()
        self.assertEqual(metadata, test_metadata)

    @patch('core.audio_processor.split_audio')
    @patch('core.audio_processor.ensure_directory_exists')
    def test_split_audio(self, mock_ensure_dir, mock_split_audio):
        """Test the split_audio method"""
        # Mock the dependencies
        mock_ensure_dir.return_value = True
        mock_split_audio.return_value = ["output1.mp3", "output2.mp3"]

        # Set up test audio segment
        self.processor.audio_segment = MagicMock()
        self.processor.audio_file = "test.mp3"

        # Test with valid parameters
        output_files = self.processor.split_audio(
            method="equal_parts",
            output_dir="/output",
            output_format="mp3",
            naming_pattern="{original_name}_part_{number}",
            num_parts=2
        )

        self.assertEqual(output_files, ["output1.mp3", "output2.mp3"])

        # Check that the progress callback was called
        self.progress_callback.assert_called()

        # Test with no audio loaded
        self.processor.audio_segment = None
        output_files = self.processor.split_audio(
            method="equal_parts",
            output_dir="/output",
            output_format="mp3",
            naming_pattern="{original_name}_part_{number}",
            num_parts=2
        )

        self.assertEqual(output_files, [])

        # Test with invalid output format
        self.processor.audio_segment = MagicMock()
        output_files = self.processor.split_audio(
            method="equal_parts",
            output_dir="/output",
            output_format="invalid",
            naming_pattern="{original_name}_part_{number}",
            num_parts=2
        )

        self.assertEqual(output_files, [])

        # Test with directory creation failure
        mock_ensure_dir.return_value = False
        output_files = self.processor.split_audio(
            method="equal_parts",
            output_dir="/output",
            output_format="mp3",
            naming_pattern="{original_name}_part_{number}",
            num_parts=2
        )

        self.assertEqual(output_files, [])

        # Test with an exception
        mock_ensure_dir.return_value = True
        mock_split_audio.side_effect = Exception("Test error")
        output_files = self.processor.split_audio(
            method="equal_parts",
            output_dir="/output",
            output_format="mp3",
            naming_pattern="{original_name}_part_{number}",
            num_parts=2
        )

        self.assertEqual(output_files, [])

if __name__ == "__main__":
    unittest.main()