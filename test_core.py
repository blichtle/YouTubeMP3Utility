#!/usr/bin/env python3
"""
Test script to verify core functionality without GUI.
This can be used to test the application when tkinter is not available.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from youtube_mp3_downloader.services.browser_service import BrowserService
from youtube_mp3_downloader.services.metadata_service import MetadataService
from youtube_mp3_downloader.services.download_monitor import DownloadMonitor
from youtube_mp3_downloader.services.error_handler import ErrorHandler
from youtube_mp3_downloader.models.data_models import UserInput, MetadataInfo
from youtube_mp3_downloader.exceptions import YouTubeDownloaderError


def test_core_services():
    """Test that all core services can be instantiated."""
    print("Testing core services...")
    
    try:
        # Test service instantiation
        browser_service = BrowserService()
        print("✓ BrowserService instantiated successfully")
        
        metadata_service = MetadataService()
        print("✓ MetadataService instantiated successfully")
        
        download_monitor = DownloadMonitor()
        print("✓ DownloadMonitor instantiated successfully")
        
        error_handler = ErrorHandler()
        print("✓ ErrorHandler instantiated successfully")
        
        # Test data models
        user_input = UserInput(
            youtube_url="https://www.youtube.com/watch?v=test",
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            track_number=1
        )
        print("✓ UserInput model created successfully")
        
        metadata_info = MetadataInfo(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            track_number=1,
            original_filename="test_song.mp3"
        )
        print("✓ MetadataInfo model created successfully")
        
        # Test exception
        try:
            raise YouTubeDownloaderError("Test error")
        except YouTubeDownloaderError as e:
            print(f"✓ YouTubeDownloaderError works: {e.message}")
        
        print("\n🎉 All core services are working correctly!")
        print("Note: GUI functionality requires tkinter to be installed.")
        
    except Exception as e:
        print(f"❌ Error testing core services: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_core_services()
    sys.exit(0 if success else 1)