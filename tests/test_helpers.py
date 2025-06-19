"""
Tests for the helper functions
"""

import os
import unittest
import tempfile
from utils.helpers import (
    format_time,
    parse_time,
    get_file_extension,
    human_readable_size,
    ensure_directory_exists,
    generate_output_filename
)

class TestHelpers(unittest.TestCase):
    """Test case for helper functions"""

    def test_format_time(self):
        """Test the format_time function"""
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(60), "01:00")
        self.assertEqual(format_time(90), "01:30")
        self.assertEqual(format_time(3600), "60:00")
        self.assertEqual(format_time(3661), "61:01")

    def test_parse_time(self):
        """Test the parse_time function"""
        self.assertEqual(parse_time("00:00"), 0)
        self.assertEqual(parse_time("01:00"), 60)
        self.assertEqual(parse_time("01:30"), 90)
        self.assertEqual(parse_time("60:00"), 3600)
        self.assertEqual(parse_time("61:01"), 3661)

        # Test invalid formats
        with self.assertRaises(ValueError):
            parse_time("invalid")
        with self.assertRaises(ValueError):
            parse_time("1:2")
        with self.assertRaises(ValueError):
            parse_time("01:60")

    def test_get_file_extension(self):
        """Test the get_file_extension function"""
        self.assertEqual(get_file_extension("file.mp3"), "mp3")
        self.assertEqual(get_file_extension("file.MP3"), "mp3")
        self.assertEqual(get_file_extension("file.wav"), "wav")
        self.assertEqual(get_file_extension("file"), "")
        self.assertEqual(get_file_extension("file."), "")
        self.assertEqual(get_file_extension("/path/to/file.mp3"), "mp3")

    def test_human_readable_size(self):
        """Test the human_readable_size function"""
        self.assertEqual(human_readable_size(0), "0 B")
        self.assertEqual(human_readable_size(1023), "1023.00 B")
        self.assertEqual(human_readable_size(1024), "1.00 KB")
        self.assertEqual(human_readable_size(1024 * 1024), "1.00 MB")
        self.assertEqual(human_readable_size(1024 * 1024 * 1024), "1.00 GB")

    def test_ensure_directory_exists(self):
        """Test the ensure_directory_exists function"""
        # Test with an existing directory
        self.assertTrue(ensure_directory_exists(os.getcwd()))

        # Test with a new directory
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_dir")
            self.assertTrue(ensure_directory_exists(new_dir))
            self.assertTrue(os.path.exists(new_dir))

            # Test with a nested directory
            nested_dir = os.path.join(new_dir, "nested", "dir")
            self.assertTrue(ensure_directory_exists(nested_dir))
            self.assertTrue(os.path.exists(nested_dir))

    def test_generate_output_filename(self):
        """Test the generate_output_filename function"""
        # Test with default pattern
        filename = generate_output_filename(
            "test", 1, 0, 60, "{original_name}_part_{number:03d}", "mp3"
        )
        self.assertEqual(filename, "test_part_001.mp3")

        # Test with custom pattern
        filename = generate_output_filename(
            "test", 1, 0, 60, "{original_name}_{start_time}-{end_time}", "wav"
        )
        self.assertEqual(filename, "test_00:00-01:00.wav")

        # Test with file extension in original name
        filename = generate_output_filename(
            "test.mp3", 1, 0, 60, "{original_name}_part_{number}", "wav"
        )
        self.assertEqual(filename, "test_part_1.wav")

if __name__ == "__main__":
    unittest.main()