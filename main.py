#!/usr/bin/env python3
"""
Main entry point for the YouTube MP3 Downloader application.

This script initializes and starts the YouTube MP3 Downloader with the main controller
that orchestrates all services (GUI, browser automation, download monitoring, and metadata processing).
"""

import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from youtube_mp3_downloader.controllers.main_controller import MainController
from youtube_mp3_downloader.exceptions import YouTubeDownloaderError


def setup_logging():
    """Set up logging configuration for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('youtube_mp3_downloader.log')
        ]
    )


def main():
    """
    Main entry point for the application.
    
    Initializes the main controller and starts the complete YouTube MP3 Downloader application.
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting YouTube MP3 Downloader application")
        
        # Initialize the main controller
        main_controller = MainController()
        
        # Start the application (this will create and run the GUI)
        main_controller.start_application()
        
        logger.info("Application started successfully")
        
    except YouTubeDownloaderError as e:
        logger.error(f"Application error: {e.message}")
        print(f"Application Error: {e.message}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error starting application: {e}")
        print(f"Unexpected Error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("Application shutdown")


if __name__ == "__main__":
    main()