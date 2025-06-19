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