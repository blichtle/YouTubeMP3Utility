"""
Configuration settings for the YouTube MP3 Downloader application.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DOWNLOADS_FOLDER = Path.home() / "Downloads"

# Browser automation settings
BROWSER_TIMEOUT = 30  # seconds
CONVERSION_WAIT_TIME = 5  # seconds as specified in requirements
DOWNLOAD_TIMEOUT = 300  # 5 minutes maximum wait for download

# Target website configuration
CONVERTER_URL = "https://mp3cow.com/"
URL_INPUT_ID = "url"
CONVERT_BUTTON_ID = "bco"
DOWNLOAD_BUTTON_TEXT = "Download MP3"

# File monitoring settings
MONITOR_TIMEOUT = 60  # seconds to wait for file detection
FILE_COMPLETION_CHECK_INTERVAL = 1  # seconds between file completion checks

# Metadata settings
SUPPORTED_FORMATS = ['.mp3']
BACKUP_SUFFIX = '.backup'

# GUI settings
WINDOW_TITLE = "YouTube MP3 Downloader"
WINDOW_SIZE = "600x400"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"