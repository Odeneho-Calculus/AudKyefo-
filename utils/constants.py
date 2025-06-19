"""
Constants used throughout the AudKyɛfo application
"""

# Application information
APP_NAME = "AudKyɛfo"
APP_DISPLAY_NAME = "AudKyɛfo - Audio Splitter"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AudKyɛfo Team"

# UI Constants
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400
WINDOW_DEFAULT_WIDTH = 800
WINDOW_DEFAULT_HEIGHT = 600

# Audio formats
SUPPORTED_INPUT_FORMATS = ["mp3", "wav", "aac", "ogg", "m4a", "flac"]
SUPPORTED_OUTPUT_FORMATS = ["mp3", "wav", "aac", "ogg", "m4a", "flac"]

# Default values
DEFAULT_OUTPUT_FORMAT = "mp3"
DEFAULT_NAMING_PATTERN = "{original_name}_part_{number:03d}"
DEFAULT_OVERLAP_DURATION = 0  # in seconds

# Splitting methods
SPLIT_METHOD_EQUAL = "equal_parts"
SPLIT_METHOD_DURATION = "fixed_duration"
SPLIT_METHOD_CUSTOM = "custom_ranges"

# Color scheme
PRIMARY_COLOR = "#2E7D32"  # Green
SECONDARY_COLOR = "#1976D2"  # Blue
BACKGROUND_COLOR = "#FAFAFA"  # Light Gray
TEXT_COLOR = "#212121"  # Dark Gray
ACCENT_COLOR = "#FF5722"  # Orange for warnings

# Progress stages
PROGRESS_FILE_LOADING = 10
PROGRESS_AUDIO_ANALYSIS = 20
PROGRESS_SPLITTING_START = 30
PROGRESS_SPLITTING_END = 90
PROGRESS_FILE_EXPORT = 100