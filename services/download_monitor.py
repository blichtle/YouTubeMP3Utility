"""
Download monitoring service for the YouTube MP3 Downloader application.

This module provides file system monitoring capabilities to detect new MP3 files
in the macOS Downloads folder and verify download completion.
"""

import os
import time
import threading
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from ..models.data_models import DownloadResult
from ..exceptions import DownloadError
from ..services.error_handler import ErrorHandler


class MP3FileHandler(FileSystemEventHandler):
    """
    File system event handler that monitors for new MP3 files.
    """
    
    def __init__(self, callback: Callable[[str], None]):
        """
        Initialize the MP3 file handler.
        
        Args:
            callback: Function to call when a new MP3 file is detected
        """
        super().__init__()
        self.callback = callback
        self.detected_files = set()
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: The file system event
        """
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = event.src_path
            if file_path.lower().endswith('.mp3') and file_path not in self.detected_files:
                self.detected_files.add(file_path)
                self.callback(file_path)
    
    def on_modified(self, event):
        """
        Handle file modification events (for files being written).
        
        Args:
            event: The file system event
        """
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            file_path = event.src_path
            if file_path.lower().endswith('.mp3') and file_path not in self.detected_files:
                # Check if this is a new file (recently created)
                try:
                    file_stat = os.stat(file_path)
                    creation_time = datetime.fromtimestamp(file_stat.st_ctime)
                    if datetime.now() - creation_time < timedelta(minutes=5):
                        self.detected_files.add(file_path)
                        self.callback(file_path)
                except (OSError, FileNotFoundError):
                    # File might have been deleted or moved
                    pass


class DownloadMonitor:
    """
    Service for monitoring the Downloads folder for new MP3 files.
    
    This class implements the requirements for download management:
    - Monitor macOS Downloads folder (Requirement 3.1)
    - Identify new MP3 files (Requirement 3.2)
    - Verify download completion (Requirement 3.3)
    - Handle concurrent downloads (Requirement 3.4)
    """
    
    def __init__(self):
        """Initialize the download monitor."""
        self.downloads_path = self._get_downloads_path()
        self.observer = None
        self.event_handler = None
        self.monitoring = False
        self.detected_files = []
        self.completion_timeout = 30  # seconds to wait for file completion
        self._lock = threading.Lock()
        
        # Initialize error handler
        self.error_handler = ErrorHandler()
    
    def _get_downloads_path(self) -> str:
        """
        Get the macOS Downloads folder path.
        Enhanced with error handling (Requirement 5.4).
        
        Returns:
            str: Path to the Downloads folder
            
        Raises:
            DownloadError: If Downloads folder cannot be found or accessed
        """
        # Try common macOS Downloads folder locations
        possible_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            "/Users/" + os.getenv("USER", "") + "/Downloads"
        ]
        
        for path in possible_paths:
            try:
                if os.path.exists(path) and os.path.isdir(path):
                    # Test write access
                    test_file = os.path.join(path, ".download_monitor_test")
                    try:
                        with open(test_file, 'w') as f:
                            f.write("test")
                        os.remove(test_file)
                        return path
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                continue
        
        error_msg = "Could not locate or access macOS Downloads folder. Please check folder permissions."
        self.error_handler.handle_error(DownloadError(error_msg), "downloads_path_detection")
        raise DownloadError(error_msg)
    
    def start_monitoring(self) -> bool:
        """
        Begin file system watching for new MP3 files.
        Enhanced with error handling (Requirement 5.4).
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
            
        Raises:
            DownloadError: If monitoring cannot be started
        """
        try:
            if self.monitoring:
                return True
            
            # Verify downloads path is still accessible
            if not os.path.exists(self.downloads_path) or not os.access(self.downloads_path, os.R_OK):
                error_msg = f"Downloads folder is not accessible: {self.downloads_path}"
                self.error_handler.handle_error(DownloadError(error_msg), "start_monitoring")
                raise DownloadError(error_msg)
            
            # Create event handler with callback
            self.event_handler = MP3FileHandler(self._on_mp3_detected)
            
            # Create and start observer
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.downloads_path, recursive=False)
            self.observer.start()
            
            self.monitoring = True
            return True
            
        except Exception as e:
            error_msg = f"Error starting download monitoring: {str(e)}"
            self.error_handler.handle_error(DownloadError(error_msg), "start_monitoring")
            raise DownloadError(error_msg) from e
    
    def stop_monitoring(self) -> bool:
        """
        Stop file system watching.
        
        Returns:
            bool: True if monitoring stopped successfully, False otherwise
        """
        try:
            if not self.monitoring or not self.observer:
                return True
            
            self.observer.stop()
            self.observer.join(timeout=5)
            self.monitoring = False
            self.observer = None
            self.event_handler = None
            
            return True
            
        except Exception as e:
            print(f"Error stopping download monitoring: {e}")
            return False
    
    def _on_mp3_detected(self, file_path: str) -> None:
        """
        Callback function called when a new MP3 file is detected.
        
        Args:
            file_path: Path to the detected MP3 file
        """
        with self._lock:
            if file_path not in [f['path'] for f in self.detected_files]:
                self.detected_files.append({
                    'path': file_path,
                    'detected_time': datetime.now(),
                    'completed': False
                })
    
    def detect_new_mp3(self, timeout: int = 60) -> Optional[str]:
        """
        Wait for and identify newly downloaded MP3 files.
        Enhanced with timeout and error handling (Requirement 5.4).
        
        Args:
            timeout: Maximum time to wait for a new file (seconds)
            
        Returns:
            Optional[str]: Path to the detected MP3 file, or None if timeout
            
        Raises:
            DownloadError: If monitoring is not active or other errors occur
        """
        if not self.monitoring:
            error_msg = "Download monitoring is not active. Call start_monitoring() first."
            self.error_handler.handle_error(DownloadError(error_msg), "detect_new_mp3")
            raise DownloadError(error_msg)
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                with self._lock:
                    # Check for new files that haven't been processed
                    for file_info in self.detected_files:
                        if not file_info['completed']:
                            file_path = file_info['path']
                            if self.wait_for_completion(file_path):
                                file_info['completed'] = True
                                return file_path
                
                time.sleep(0.5)  # Check every 500ms
            
            # Timeout reached
            error_msg = f"Download timeout: No MP3 file detected within {timeout} seconds."
            self.error_handler.handle_error(DownloadError(error_msg), "detect_new_mp3")
            return None
            
        except Exception as e:
            error_msg = f"Error detecting MP3 file: {str(e)}"
            self.error_handler.handle_error(DownloadError(error_msg), "detect_new_mp3")
            raise DownloadError(error_msg) from e
    
    def wait_for_completion(self, file_path: str) -> bool:
        """
        Ensure file is fully downloaded and accessible.
        Enhanced with detailed error handling (Requirement 5.4).
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file is complete and accessible, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            # Wait for file to stabilize (no size changes)
            stable_count = 0
            last_size = -1
            
            for attempt in range(self.completion_timeout):
                try:
                    current_size = os.path.getsize(file_path)
                    
                    if current_size == last_size and current_size > 0:
                        stable_count += 1
                        if stable_count >= 3:  # File size stable for 3 seconds
                            # Try to open the file to ensure it's not locked
                            try:
                                with open(file_path, 'rb') as f:
                                    # Read first few bytes to ensure file is accessible
                                    header = f.read(1024)
                                    # Basic MP3 header validation
                                    if len(header) >= 3 and (header[:3] == b'ID3' or header[:2] == b'\xff\xfb'):
                                        return True
                                    else:
                                        # File might still be downloading
                                        stable_count = 0
                            except (IOError, OSError) as e:
                                # File might still be locked
                                if attempt == self.completion_timeout - 1:
                                    error_msg = f"File access error after {self.completion_timeout} attempts: {str(e)}"
                                    self.error_handler.handle_error(DownloadError(error_msg, file_path), "wait_for_completion")
                                pass
                    else:
                        stable_count = 0
                        last_size = current_size
                    
                    time.sleep(1)
                    
                except (OSError, FileNotFoundError) as e:
                    # File might have been moved or deleted
                    error_msg = f"File system error while waiting for completion: {str(e)}"
                    self.error_handler.handle_error(DownloadError(error_msg, file_path), "wait_for_completion")
                    return False
            
            # Timeout reached without stable file
            error_msg = f"File did not stabilize within {self.completion_timeout} seconds"
            self.error_handler.handle_error(DownloadError(error_msg, file_path), "wait_for_completion")
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error waiting for file completion: {str(e)}"
            self.error_handler.handle_error(DownloadError(error_msg, file_path), "wait_for_completion")
            return False
    
    def get_recent_mp3_files(self, minutes: int = 5) -> List[str]:
        """
        Get list of MP3 files created in the last N minutes.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List[str]: List of file paths for recent MP3 files
        """
        recent_files = []
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        try:
            for file_name in os.listdir(self.downloads_path):
                if file_name.lower().endswith('.mp3'):
                    file_path = os.path.join(self.downloads_path, file_name)
                    try:
                        file_stat = os.stat(file_path)
                        creation_time = datetime.fromtimestamp(file_stat.st_ctime)
                        if creation_time > cutoff_time:
                            recent_files.append(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        
        except (OSError, FileNotFoundError):
            pass
        
        return sorted(recent_files, key=lambda x: os.path.getctime(x), reverse=True)
    
    def handle_concurrent_downloads(self) -> List[str]:
        """
        Handle cases where multiple files are downloading simultaneously.
        
        Returns:
            List[str]: List of all detected MP3 files that are complete
        """
        completed_files = []
        
        with self._lock:
            for file_info in self.detected_files:
                if not file_info['completed']:
                    file_path = file_info['path']
                    if self.wait_for_completion(file_path):
                        file_info['completed'] = True
                        completed_files.append(file_path)
        
        return completed_files
    
    def create_download_result(self, file_path: Optional[str], error_message: Optional[str] = None) -> DownloadResult:
        """
        Create a DownloadResult object based on the monitoring outcome.
        
        Args:
            file_path: Path to the downloaded file (if successful)
            error_message: Error message (if unsuccessful)
            
        Returns:
            DownloadResult: Result object with download information
        """
        success = file_path is not None and os.path.exists(file_path)
        
        return DownloadResult(
            success=success,
            file_path=file_path if success else None,
            error_message=error_message if not success else None,
            download_time=datetime.now()
        )
    
    def cleanup(self) -> None:
        """
        Clean up resources and reset state.
        """
        self.stop_monitoring()
        with self._lock:
            self.detected_files.clear()