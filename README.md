# AudKyɛfo - Audio Splitter

AudKyɛfo (meaning "Audio Splitter" in Twi) is a fully offline desktop application built with Python and PyQt5 that allows users to upload audio files and split them into segments based on custom preferences.

## Features

- **Offline-first**: No internet connection required, all processing is done locally
- **Multi-format support**: Input/output for MP3, WAV, AAC, OGG, M4A, FLAC
- **Flexible splitting options**:
  - Split by number of equal chunks
  - Split by fixed duration
  - Split by custom time ranges
- **Cross-platform**: Works on Windows, macOS, and Linux
- **User-friendly interface**: Clean, modern PyQt5 UI with progress indicators

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)

### Install from Source

1. Clone the repository:
   ```
   git clone https://github.com/Odeneho-Calculus/AudKyefo-.git
   cd audkyefo
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run.py
   ```

   The `run.py` script will check for required dependencies and install them if needed.

### Standalone Executable

For Windows users, a standalone executable is available in the releases section. This executable includes all dependencies and does not require Python to be installed.

To build the executable yourself:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build_exe.py
   ```

3. The executable will be created in the `dist` directory.

## Usage

1. **Select an audio file**:
   - Use the "File Input" tab to select an audio file
   - Drag and drop an audio file onto the application
   - Use the "Open Audio File" option in the File menu

2. **Configure splitting options**:
   - Choose a splitting method (Equal Parts, Fixed Duration, or Custom Ranges)
   - Set additional options like output format, quality, and naming pattern
   - Select an output folder

3. **Process the file**:
   - Click the "Start Processing" button
   - Monitor the progress in the "Processing & Results" tab
   - View and play the resulting audio segments

## Naming Pattern Guide

**IMPORTANT: You type the pattern ONCE and it automatically names ALL your files!**

The naming pattern feature allows you to customize how your split audio files are named. Whether you're splitting into 10 files or 1000 files, you only need to set the pattern once and the system automatically generates all the file names for you.

### How It Works
1. **Automatic**: The system suggests a pattern based on your input file (e.g., "MySong_part_{number:03d}")
2. **One Pattern, All Files**: You type the pattern once and it applies to every single file automatically
3. **Optional**: You can leave the default pattern or customize it if you want

### Quick Example
- **Input file**: "MySong.mp3"
- **Pattern typed ONCE**: `MySong_part_{number:03d}`
- **System automatically creates**: MySong_part_001.mp3, MySong_part_002.mp3, MySong_part_003.mp3... up to MySong_part_1000.mp3 (or however many parts you choose)
- **You did NOT type 1000 patterns - just ONE!**

### Available Variables

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `{original_name}` | The original file name (without extension) | `MyAudio` |
| `{number}` | The segment number (starts from 1) | `1`, `2`, `3` |
| `{number:03d}` | The segment number with zero padding | `001`, `002`, `003` |
| `{start_time}` | Start time of the segment (MM:SS format) | `00:00`, `01:30` |
| `{end_time}` | End time of the segment (MM:SS format) | `01:30`, `03:00` |

### Pattern Examples

Here are some common naming patterns and what they produce:

#### Default Pattern
- **Pattern**: `{original_name}_part_{number:03d}`
- **Example**: If you split "MySong.mp3" into 5 parts, you get:
  - `MySong_part_001.mp3`
  - `MySong_part_002.mp3`
  - `MySong_part_003.mp3`
  - `MySong_part_004.mp3`
  - `MySong_part_005.mp3`

#### Simple Numbering
- **Pattern**: `{original_name}_{number}`
- **Example**: From "MySong.mp3":
  - `MySong_1.mp3`
  - `MySong_2.mp3`
  - `MySong_3.mp3`

#### With Time Information
- **Pattern**: `{original_name}_({start_time}-{end_time})`
- **Example**: From "MySong.mp3":
  - `MySong_(00:00-01:30).mp3`
  - `MySong_(01:30-03:00).mp3`
  - `MySong_(03:00-04:30).mp3`

#### Custom Format
- **Pattern**: `Part{number:02d}_of_{original_name}`
- **Example**: From "MySong.mp3":
  - `Part01_of_MySong.mp3`
  - `Part02_of_MySong.mp3`
  - `Part03_of_MySong.mp3`

### Live Preview

When you type a naming pattern in the Configuration tab, you'll see a live preview showing exactly what your files will be named. For example:

- **Pattern**: `{original_name}_segment_{number:03d}`
- **Preview**: `Example: MyAudio_segment_001.mp3`

This preview updates in real-time as you modify the pattern, so you can experiment and see the results immediately.

### Tips

1. **Always include `{number}`** or `{number:03d}` to distinguish between different segments
2. **Use zero padding** like `{number:03d}` for better file sorting (001, 002, 003 instead of 1, 2, 3)
3. **Avoid special characters** that might not be allowed in file names (like `/`, `\`, `<`, `>`, `:`, `"`, `|`, `?`, `*`)
4. **Keep it descriptive** but not too long for better file management

## Development

### Project Structure

```
audkyefo/
├── main.py                 # Entry point
├── ui/                     # User interface components
├── core/                   # Audio processing logic
├── utils/                  # Utility functions
├── resources/              # Application resources
├── tests/                  # Test files
├── requirements.txt        # Dependencies
├── build_exe.py            # PyInstaller build script
└── README.md               # This file
```

### Running Tests

```
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the GUI framework
- pydub and ffmpeg for audio processing
- mutagen for audio metadata handling