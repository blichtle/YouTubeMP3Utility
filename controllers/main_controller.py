"""
Main application controller for the YouTube MP3 Downloader.

This module provides the central orchestration controller that coordinates
all services (GUI, browser automation, download monitoring, and metadata processing)
to implement the complete download and tagging workflow.
"""

import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.data_models import UserInput, DownloadResult, MetadataInfo
from ..controllers.gui_controller import GUIController
from ..services.browser_service import BrowserService
from ..services.download_monitor import DownloadMonitor
from ..services.metadata_service import MetadataService
from ..services.error_handler import ErrorHandler
from ..exceptions import (
    YouTubeDownloaderError,
    InputValidationError,
    NetworkError,
    ElementLocationError,
    BrowserError,
    DownloadError,
    MetadataError
)


class MainController:
    """
    Main application controller that orchestrates the entire download and tagging process.
    
    This controller implements the complete workflow:
    1. GUI input collection and validation
    2. Browser automation for download initiation
    3. Download monitoring and file detection
    4. Metadata application to downloaded files
    5. Progress tracking and error handling throughout
    """
    
    def __init__(self):
        """Initialize the main controller with all required services."""
        # Initialize error handler first
        self.error_handler = ErrorHandler()
        
        # Initialize services
        self.gui_controller = GUIController(on_submit_callback=self._handle_download_request)
        self.browser_service = BrowserService(headless=False)
        self.download_monitor = DownloadMonitor()
        self.metadata_service = MetadataService()
        
        # Update error handler with GUI callback
        self.error_handler.gui_error_callback = self.gui_controller.show_error
        
        # State tracking
        self.current_operation = None
        self.operation_start_time = None
        self.is_processing = False
        
        # Configuration
        self.download_timeout = 300  # 5 minutes timeout for downloads
        self.max_retry_attempts = 3
        
    def start_application(self) -> None:
        """
        Start the application by creating and showing the GUI.
        
        This is the main entry point for the application.
        """
        try:
            # Create the GUI
            root = self.gui_controller.create_input_form()
            
            # Start the GUI main loop
            self.gui_controller.run()
            
        except Exception as e:
            error_msg = f"Failed to start application: {str(e)}"
            self.error_handler.handle_error(YouTubeDownloaderError(error_msg), "application_startup")
            raise YouTubeDownloaderError(error_msg) from e
    
    def _handle_download_request(self, user_input: UserInput) -> None:
        """
        Handle a download request from the GUI.
        
        This method runs the complete workflow in a separate thread to avoid
        blocking the GUI.
        
        Args:
            user_input: Validated user input from the GUI form
        """
        if self.is_processing:
            self.gui_controller.show_error("A download is already in progress. Please wait for it to complete.")
            return
        
        # Start processing in a separate thread to avoid blocking GUI
        processing_thread = threading.Thread(
            target=self._execute_download_workflow,
            args=(user_input,),
            daemon=True
        )
        processing_thread.start()
    
    def _execute_download_workflow(self, user_input: UserInput) -> None:
        """
        Execute the complete download and metadata tagging workflow.
        
        This method orchestrates all services to complete the download process:
        1. Browser automation for download initiation
        2. Download monitoring and file detection
        3. Metadata application
        4. Progress tracking and error handling
        
        Args:
            user_input: Validated user input from the GUI form
        """
        self.is_processing = True
        self.operation_start_time = datetime.now()
        download_result = None
        
        try:
            # Step 1: Browser Automation (Requirements 2.1-2.7)
            self.current_operation = "browser_automation"
            self.gui_controller.show_processing_status()
            
            success = self._execute_browser_automation(user_input.youtube_url)
            if not success:
                return  # Error already handled in browser automation
            
            # Step 2: Download Monitoring (Requirements 3.1-3.4)
            self.current_operation = "download_monitoring"
            self.gui_controller.show_waiting_status()
            
            download_result = self._execute_download_monitoring()
            if not download_result or not download_result.success:
                return  # Error already handled in download monitoring
            
            # Step 3: Metadata Application (Requirements 4.1-4.7)
            self.current_operation = "metadata_application"
            self.gui_controller.show_metadata_status()
            
            success = self._execute_metadata_application(download_result.file_path, user_input)
            if not success:
                return  # Error already handled in metadata application
            
            # Step 4: Success (Requirements 6.6)
            self.current_operation = "completed"
            self.gui_controller.show_success(download_result.file_path)
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"Unexpected error during {self.current_operation}: {str(e)}"
            self.error_handler.handle_error(YouTubeDownloaderError(error_msg), self.current_operation)
            self.gui_controller.show_error(f"An unexpected error occurred: {str(e)}")
            
        finally:
            # Always clean up resources
            self._cleanup_resources()
            self.is_processing = False
            self.current_operation = None
    
    def _execute_browser_automation(self, youtube_url: str) -> bool:
        """
        Execute browser automation to initiate the download.
        
        Args:
            youtube_url: The YouTube URL to download
            
        Returns:
            bool: True if browser automation succeeded, False otherwise
        """
        try:
            # Open browser (Requirement 2.1)
            if not self.browser_service.open_browser():
                self.gui_controller.show_error("Failed to open browser. Please ensure Chrome is installed.")
                return False
            
            # Navigate to converter website (Requirement 2.2)
            if not self.browser_service.navigate_to_converter():
                self.gui_controller.show_error("Failed to navigate to conversion website. Please check your internet connection.")
                return False
            
            # Input YouTube URL (Requirements 2.3, 2.4)
            if not self.browser_service.input_youtube_url(youtube_url):
                self.gui_controller.show_error("Failed to input YouTube URL. The website may have changed.")
                return False
            
            # Click convert button (Requirement 2.5)
            if not self.browser_service.click_convert_button():
                self.gui_controller.show_error("Failed to start conversion. The website may have changed.")
                return False
            
            # Wait and click download (Requirements 2.6, 2.7)
            if not self.browser_service.wait_and_download():
                self.gui_controller.show_error("Failed to initiate download. The conversion may have failed.")
                return False
            
            return True
            
        except NetworkError as e:
            self.gui_controller.show_error(f"Network error: {e.message}")
            return False
            
        except ElementLocationError as e:
            self.gui_controller.show_error(f"Website error: Could not find {e.element_description}. The website may have changed.")
            return False
            
        except BrowserError as e:
            self.gui_controller.show_error(f"Browser error: {e.message}")
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error during browser automation: {str(e)}"
            self.error_handler.handle_error(YouTubeDownloaderError(error_msg), "browser_automation")
            self.gui_controller.show_error(error_msg)
            return False
    
    def _execute_download_monitoring(self) -> Optional[DownloadResult]:
        """
        Execute download monitoring to detect the downloaded MP3 file.
        
        Returns:
            Optional[DownloadResult]: Download result if successful, None otherwise
        """
        try:
            # Start monitoring (Requirement 3.1)
            if not self.download_monitor.start_monitoring():
                self.gui_controller.show_error("Failed to start download monitoring. Please check Downloads folder permissions.")
                return None
            
            # Wait for new MP3 file (Requirements 3.2, 3.3)
            file_path = self.download_monitor.detect_new_mp3(timeout=self.download_timeout)
            
            if not file_path:
                # Check for recent files as fallback (Requirement 3.4)
                recent_files = self.download_monitor.get_recent_mp3_files(minutes=10)
                if recent_files:
                    file_path = recent_files[0]  # Use most recent file
                else:
                    self.gui_controller.show_error(f"Download timeout: No MP3 file detected within {self.download_timeout // 60} minutes.")
                    return None
            
            # Create successful download result
            return self.download_monitor.create_download_result(file_path)
            
        except DownloadError as e:
            self.gui_controller.show_error(f"Download error: {e.message}")
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error during download monitoring: {str(e)}"
            self.error_handler.handle_error(YouTubeDownloaderError(error_msg), "download_monitoring")
            self.gui_controller.show_error(error_msg)
            return None
        
        finally:
            # Always stop monitoring
            self.download_monitor.stop_monitoring()
    
    def _execute_metadata_application(self, file_path: str, user_input: UserInput) -> bool:
        """
        Execute metadata application to tag the downloaded MP3 file.
        
        Args:
            file_path: Path to the downloaded MP3 file
            user_input: User input containing metadata information
            
        Returns:
            bool: True if metadata application succeeded, False otherwise
        """
        try:
            # Create metadata info object
            metadata_info = MetadataInfo(
                artist=user_input.artist,
                title=user_input.title,
                album=user_input.album,
                track_number=user_input.track_number,
                original_filename=file_path
            )
            
            # Validate metadata info
            validation_errors = metadata_info.validate()
            if validation_errors:
                self.gui_controller.show_error(f"Invalid metadata: {', '.join(validation_errors)}")
                return False
            
            # Apply metadata (Requirements 4.1-4.7)
            if not self.metadata_service.apply_metadata(file_path, metadata_info):
                self.gui_controller.show_error("Failed to apply metadata to the MP3 file.")
                return False
            
            return True
            
        except MetadataError as e:
            self.gui_controller.show_error(f"Metadata error: {e.message}")
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error during metadata application: {str(e)}"
            self.error_handler.handle_error(YouTubeDownloaderError(error_msg), "metadata_application")
            self.gui_controller.show_error(error_msg)
            return False
    
    def _cleanup_resources(self) -> None:
        """
        Clean up all resources and reset state.
        
        This method ensures proper cleanup of browser sessions, file monitors,
        and other resources regardless of success or failure.
        """
        try:
            # Close browser
            if self.browser_service:
                self.browser_service.close_browser()
            
            # Stop download monitoring
            if self.download_monitor:
                self.download_monitor.stop_monitoring()
                self.download_monitor.cleanup()
            
        except Exception as e:
            # Log cleanup errors but don't propagate them
            self.error_handler.handle_error(
                YouTubeDownloaderError(f"Error during cleanup: {str(e)}"),
                "resource_cleanup"
            )
    
    def get_operation_status(self) -> Dict[str, Any]:
        """
        Get the current operation status for monitoring/debugging.
        
        Returns:
            Dict[str, Any]: Status information dictionary
        """
        return {
            'current_operation': self.current_operation,
            'is_processing': self.is_processing,
            'operation_start_time': self.operation_start_time,
            'elapsed_time': (datetime.now() - self.operation_start_time).total_seconds() 
                           if self.operation_start_time else 0,
            'browser_open': self.browser_service.is_browser_open() if self.browser_service else False,
            'monitoring_active': self.download_monitor.monitoring if self.download_monitor else False
        }
    
    def cancel_operation(self) -> bool:
        """
        Cancel the current operation if possible.
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        if not self.is_processing:
            return True
        
        try:
            # Clean up resources
            self._cleanup_resources()
            
            # Reset state
            self.is_processing = False
            self.current_operation = None
            
            # Update GUI
            self.gui_controller.hide_progress()
            self.gui_controller.submit_button.config(state='normal')
            
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                YouTubeDownloaderError(f"Error canceling operation: {str(e)}"),
                "operation_cancellation"
            )
            return False
    
    def retry_current_operation(self, user_input: UserInput) -> None:
        """
        Retry the current operation with the same user input.
        
        Args:
            user_input: The original user input to retry with
        """
        if self.is_processing:
            self.gui_controller.show_error("Cannot retry while an operation is in progress.")
            return
        
        # Reset state and retry
        self._cleanup_resources()
        self._handle_download_request(user_input)
    
    def shutdown(self) -> None:
        """
        Shutdown the application gracefully.
        
        This method ensures all resources are cleaned up before the application exits.
        """
        try:
            # Cancel any ongoing operations
            if self.is_processing:
                self.cancel_operation()
            
            # Clean up resources
            self._cleanup_resources()
            
            # Destroy GUI
            if self.gui_controller:
                self.gui_controller.destroy()
            
        except Exception as e:
            # Log shutdown errors but don't prevent shutdown
            self.error_handler.handle_error(
                YouTubeDownloaderError(f"Error during shutdown: {str(e)}"),
                "application_shutdown"
            )