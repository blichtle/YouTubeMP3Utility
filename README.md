# YouTube MP3 Downloader

A Python desktop application that automates the process of downloading MP3 files from YouTube videos and applying custom metadata tags.

## Features

- Simple GUI built with Tkinter for user input
- Browser automation using Selenium WebDriver with auto-close after download
- File system monitoring for download detection
- MP3 metadata manipulation using mutagen library
- Modular architecture with clear separation of concerns
- **Clear All Fields button** - Easily reset the form to start a new session
- **Load and Edit MP3 Files** - Select existing MP3 files to view and edit their metadata
- **Save Changes to MP3** - Update metadata tags (Artist, Title, Album, Track Number) in existing files
- Progress tracking and status updates during download process
- Comprehensive error handling and validation
- **Auto-close Browser** - Browser window closes automatically after download completes

## Quick Start

**Option 1: Use the setup script (recommended)**
```bash
cd youtube_mp3_downloader
./setup.sh
./run.sh
```

**Option 2: Manual setup**
Follow the installation steps below.

## Installation

1. Navigate to the project directory:
   ```bash
   cd youtube_mp3_downloader
   ```

2. **Install Python with tkinter support** (if not already available):
   
   **On macOS:**
   ```bash
   # Accept Xcode license (if needed)
   sudo xcodebuild -license accept
   
   # Install Python with tkinter using Homebrew
   brew install python-tk
   ```
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install python3-tk
   ```
   
   **On Windows:**
   Tkinter is usually included with Python installations from python.org

3. **Create and activate a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. (Optional) Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

**Note:** This application requires a GUI environment and tkinter support.

**With convenience script:**
```bash
./run.sh
```

### Usage Modes

**1. Download from YouTube (Original functionality):**
- Fill in the YouTube URL and desired metadata
- Click "Download & Tag MP3" to download and apply metadata

**2. Edit Existing MP3 Files (New functionality):**
- Click "Load MP3 File" to select an existing MP3 file
- The form will populate with the current metadata
- Edit any fields as desired
- Click "Save Changes to MP3" to update the file

**With virtual environment (recommended):**
```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python main.py
```

**Without virtual environment:**
```bash
python3 main.py
```

Or if you installed the package:
```bash
youtube-mp3-downloader
```

### Troubleshooting

**If you get a "ModuleNotFoundError: No module named '_tkinter'" error:**

This means your Python installation doesn't include tkinter. Install it using:

```bash
# macOS with Homebrew
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk
```

**Testing without GUI:**

You can test the core functionality without the GUI by running the unit tests:

```bash
# With virtual environment activated
pytest tests/unit/ -v

# Or without virtual environment
python3 -m pytest tests/unit/ -v
```

Or run the core functionality test:

```bash
# With virtual environment activated
python test_core.py

# Or without virtual environment  
python3 test_core.py
```

**Testing GUI functionality:**

To test the GUI and new MP3 editing functionality:

```bash
# With virtual environment activated
python test_gui.py
```

This opens the GUI with test data so you can verify both the clear button and MP3 loading functionality work correctly.

**Testing with your own MP3 files:**

To test the MP3 editing feature:
1. Run the application: `./run.sh`
2. Click "Load MP3 File" 
3. Select any MP3 file from your computer
4. Edit the metadata fields
5. Click "Save Changes to MP3" to update the file

## Project Structure

```
youtube_mp3_downloader/
├── controllers/          # GUI and main application controllers
│   ├── gui_controller.py # Enhanced with MP3 loading and editing
│   └── main_controller.py
├── services/            # Core services (browser, download monitor, metadata)
│   ├── metadata_service.py # Enhanced with metadata reading capabilities
│   ├── browser_service.py
│   ├── download_monitor.py
│   └── error_handler.py
├── models/              # Data models
├── tests/               # Unit, integration, and property tests
├── .kiro/               # Kiro IDE specifications and documentation
├── venv/                # Virtual environment (created after setup)
├── main.py              # Application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup configuration
├── setup.sh            # Setup script for easy installation
├── run.sh              # Run script for easy execution
├── test_core.py        # Core functionality test script
├── test_gui.py         # GUI functionality test script
└── README.md           # This file
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/property/
```

### Configuration

Application settings can be modified in `config.py`, including:
- Browser timeout settings
- Download paths
- Converter website configuration
- GUI settings

## Requirements

- Python 3.8+
- Selenium WebDriver
- Tkinter (usually included with Python)
- See `requirements.txt` for complete dependency list

## New in This Version

### MP3 Metadata Editor
- **Load Existing MP3 Files**: Click "Load MP3 File" to select and load any MP3 file from your computer
- **Auto-populate Form**: The application automatically reads and displays the current metadata (Artist, Title, Album, Track Number)
- **Edit and Save**: Modify any metadata fields and click "Save Changes to MP3" to update the file
- **Dual Mode Interface**: Seamlessly switch between YouTube download mode and MP3 editing mode
- **File Safety**: Automatic backup creation before making changes to ensure file integrity
- **Validation**: Comprehensive validation of MP3 files and metadata before processing

### Enhanced User Experience
- **Clear All Fields**: Reset the entire form with one click
- **Smart Button Management**: Interface adapts based on current mode (download vs. edit)
- **Progress Tracking**: Real-time feedback during metadata operations
- **Error Handling**: Detailed error messages and recovery options
- **Auto-close Browser**: Browser window automatically closes after download completes for cleaner experience

## License

This project is for educational and personal use.