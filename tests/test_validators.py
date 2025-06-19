"""
Tests for the validator functions
"""

import os
import unittest
import tempfile
from utils.validators import (
    is_valid_audio_file,
    is_valid_output_format,
    is_valid_time_format,
    is_valid_time_range,
    is_valid_output_directory,
    is_valid_naming_pattern
)

class TestValidators(unittest.TestCase):
    """Test case for validator functions"""

    def test_is_valid_audio_file(self):
        """Test the is_valid_audio_file function"""
        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(suffix=".mp3") as mp3_file, \
             tempfile.NamedTemporaryFile(suffix=".txt") as txt_file:

            # Test valid audio file
            self.assertTrue(is_valid_audio_file(mp3_file.name))

            # Test invalid audio file
            self.assertFalse(is_valid_audio_file(txt_file.name))

            # Test non-existent file
            self.assertFalse(is_valid_audio_file("non_existent_file.mp3"))

    def test_is_valid_output_format(self):
        """Test the is_valid_output_format function"""
        # Test valid formats
        self.assertTrue(is_valid_output_format("mp3"))
        self.assertTrue(is_valid_output_format("wav"))
        self.assertTrue(is_valid_output_format("MP3"))  # Case insensitive

        # Test invalid formats
        self.assertFalse(is_valid_output_format("txt"))
        self.assertFalse(is_valid_output_format(""))

    def test_is_valid_time_format(self):
        """Test the is_valid_time_format function"""
        # Test valid formats
        self.assertTrue(is_valid_time_format("00:00"))
        self.assertTrue(is_valid_time_format("01:30"))
        self.assertTrue(is_valid_time_format("99:59"))

        # Test invalid formats
        self.assertFalse(is_valid_time_format(""))
        self.assertFalse(is_valid_time_format("1:30"))  # Missing leading zero
        self.assertFalse(is_valid_time_format("01:60"))  # Seconds > 59
        self.assertFalse(is_valid_time_format("01:5"))   # Missing trailing zero
        self.assertFalse(is_valid_time_format("01-30"))  # Wrong separator

    def test_is_valid_time_range(self):
        """Test the is_valid_time_range function"""
        # Test valid ranges
        valid, _ = is_valid_time_range("00:00", "01:00", 120)
        self.assertTrue(valid)

        valid, _ = is_valid_time_range("01:00", "02:00", 120)
        self.assertTrue(valid)

        # Test invalid ranges
        valid, error = is_valid_time_range("01:00", "00:30", 120)
        self.assertFalse(valid)
        self.assertIn("Start time must be less than end time", error)

        valid, error = is_valid_time_range("00:00", "03:00", 120)
        self.assertFalse(valid)
        self.assertIn("End time exceeds audio duration", error)

        valid, error = is_valid_time_range("invalid", "01:00", 120)
        self.assertFalse(valid)
        self.assertIn("Invalid start time format", error)

        valid, error = is_valid_time_range("00:00", "invalid", 120)
        self.assertFalse(valid)
        self.assertIn("Invalid end time format", error)

    def test_is_valid_output_directory(self):
        """Test the is_valid_output_directory function"""
        # Test with an existing directory
        valid, _ = is_valid_output_directory(os.getcwd())
        self.assertTrue(valid)

        # Test with a new directory
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_dir")
            valid, _ = is_valid_output_directory(new_dir)
            self.assertTrue(valid)
            self.assertTrue(os.path.exists(new_dir))

        # Test with an empty path
        valid, error = is_valid_output_directory("")
        self.assertFalse(valid)
        self.assertIn("Output directory cannot be empty", error)

    def test_is_valid_naming_pattern(self):
        """Test the is_valid_naming_pattern function"""
        # Test valid patterns
        valid, _ = is_valid_naming_pattern("{original_name}_part_{number}")
        self.assertTrue(valid)

        valid, _ = is_valid_naming_pattern("{original_name}_{start_time}-{end_time}")
        self.assertTrue(valid)

        # Test invalid patterns
        valid, error = is_valid_naming_pattern("")
        self.assertFalse(valid)
        self.assertIn("Naming pattern cannot be empty", error)

        valid, error = is_valid_naming_pattern("part_{number}")
        self.assertFalse(valid)
        self.assertIn("must include {original_name}", error)

        valid, error = is_valid_naming_pattern("{original_name}_part")
        self.assertFalse(valid)
        self.assertIn("must include at least one of", error)

        valid, error = is_valid_naming_pattern("{original_name}_part_{number}?")
        self.assertFalse(valid)
        self.assertIn("contains invalid characters", error)

if __name__ == "__main__":
    unittest.main()