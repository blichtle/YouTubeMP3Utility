"""
Error handling service for the YouTube MP3 Downloader application.

This module provides centralized error handling, logging, and user notification
functionality for all types of errors that can occur during operation.
"""

import logging
import traceback
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from ..exceptions import (
    YouTubeDownloaderError,
    InputValidationError,
    NetworkError,
    ElementLocationError,
    BrowserError,
    DownloadError,
    MetadataError
)


class ErrorHandler:
    """
    Centralized error handling service that provides logging, user notification,
    and recovery strategies for different types of errors.
    """
    
    def __init__(self, gui_error_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the error handler.
        
        Args:
            gui_error_callback: Callback function to display errors in GUI
        """
        self.gui_error_callback = gui_error_callback
        self.logger = logging.getLogger(__name__)
        self.error_history = []
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging configuration for error tracking."""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.ERROR)
    
    def handle_error(self, error: Exception, context: str = None) -> Dict[str, Any]:
        """
        Handle an error with appropriate logging and user notification.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Dict[str, Any]: Error information dictionary
        """
        error_info = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'user_message': self._get_user_friendly_message(error),
            'suggested_actions': self._get_suggested_actions(error)
        }
        
        # Log the error
        self._log_error(error_info)
        
        # Store in error history
        self.error_history.append(error_info)
        
        # Notify user through GUI if callback is available
        if self.gui_error_callback:
            self.gui_error_callback(error_info['user_message'])
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """
        Log error information with appropriate level.
        
        Args:
            error_info: Dictionary containing error details
        """
        log_message = f"Error in {error_info['context'] or 'unknown context'}: {error_info['message']}"
        
        if error_info['error_type'] in ['NetworkError', 'ElementLocationError']:
            self.logger.warning(log_message)
        else:
            self.logger.error(log_message)
            
        # Log full traceback for debugging
        self.logger.debug(f"Full traceback: {error_info['traceback']}")
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """
        Convert technical error messages to user-friendly messages.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly error message
        """
        if isinstance(error, InputValidationError):
            return f"Input Error: {error.message}"
        
        elif isinstance(error, NetworkError):
            if "connection" in error.message.lower():
                return ("Network Connection Error: Unable to connect to the conversion website. "
                       "Please check your internet connection and try again.")
            elif "timeout" in error.message.lower():
                return ("Network Timeout: The website is taking too long to respond. "
                       "Please try again in a few moments.")
            else:
                return f"Network Error: {error.message}"
        
        elif isinstance(error, ElementLocationError):
            return ("Website Error: The conversion website appears to have changed. "
                   f"Could not find the required {error.element_description}. "
                   "Please try again later or contact support if the problem persists.")
        
        elif isinstance(error, BrowserError):
            if "chromedriver" in error.message.lower():
                return ("Browser Error: Chrome browser or ChromeDriver is not properly installed. "
                       "Please ensure Chrome is installed and ChromeDriver is in your PATH.")
            else:
                return f"Browser Error: {error.message}"
        
        elif isinstance(error, DownloadError):
            return f"Download Error: {error.message}"
        
        elif isinstance(error, MetadataError):
            return f"Metadata Error: {error.message}"
        
        elif isinstance(error, YouTubeDownloaderError):
            return f"Application Error: {error.message}"
        
        else:
            return f"Unexpected Error: {str(error)}"
    
    def _get_suggested_actions(self, error: Exception) -> list[str]:
        """
        Get suggested actions for the user based on the error type.
        
        Args:
            error: The exception that occurred
            
        Returns:
            list[str]: List of suggested actions
        """
        if isinstance(error, InputValidationError):
            return [
                "Please correct the input and try again",
                "Ensure all required fields are filled out properly"
            ]
        
        elif isinstance(error, NetworkError):
            return [
                "Check your internet connection",
                "Try again in a few moments",
                "Verify that the conversion website (mp3cow.com) is accessible"
            ]
        
        elif isinstance(error, ElementLocationError):
            return [
                "Try again in a few minutes",
                "The website may have been updated - contact support if the issue persists",
                "Check if the conversion website is working properly in your browser"
            ]
        
        elif isinstance(error, BrowserError):
            return [
                "Ensure Google Chrome is installed on your system",
                "Check that ChromeDriver is properly installed and in your PATH",
                "Try restarting the application"
            ]
        
        elif isinstance(error, DownloadError):
            return [
                "Check that you have sufficient disk space",
                "Ensure the Downloads folder is accessible",
                "Try the download again"
            ]
        
        elif isinstance(error, MetadataError):
            return [
                "Ensure the MP3 file is not corrupted",
                "Check that the file is not being used by another application",
                "Try again with a different file"
            ]
        
        else:
            return [
                "Try restarting the application",
                "Contact support if the problem persists"
            ]
    
    def handle_input_validation_error(self, field_name: str, message: str) -> None:
        """
        Handle input validation errors (Requirement 5.1).
        
        Args:
            field_name: Name of the field that failed validation
            message: Validation error message
        """
        error = InputValidationError(field_name, message)
        self.handle_error(error, f"Input validation for {field_name}")
    
    def handle_network_error(self, message: str, url: str = None, context: str = None) -> None:
        """
        Handle network connectivity errors (Requirement 5.2).
        
        Args:
            message: Network error description
            url: URL that caused the error
            context: Additional context
        """
        error = NetworkError(message, url)
        self.handle_error(error, context or "Network operation")
    
    def handle_element_location_error(self, element_description: str, locator: str = None, context: str = None) -> None:
        """
        Handle element location errors (Requirement 5.3).
        
        Args:
            element_description: Description of the element that couldn't be found
            locator: Selenium locator that failed
            context: Additional context
        """
        error = ElementLocationError(element_description, locator)
        self.handle_error(error, context or "Element location")
    
    def handle_browser_error(self, message: str, operation: str = None, context: str = None) -> None:
        """
        Handle browser automation errors.
        
        Args:
            message: Browser error description
            operation: Browser operation that failed
            context: Additional context
        """
        error = BrowserError(message, operation)
        self.handle_error(error, context or "Browser operation")
    
    def get_error_history(self) -> list[Dict[str, Any]]:
        """
        Get the history of errors that have occurred.
        
        Returns:
            list[Dict[str, Any]]: List of error information dictionaries
        """
        return self.error_history.copy()
    
    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history.clear()
    
    def is_recoverable_error(self, error: Exception) -> bool:
        """
        Determine if an error is recoverable (user can retry).
        
        Args:
            error: The exception to check
            
        Returns:
            bool: True if the error is recoverable, False otherwise
        """
        recoverable_types = [
            NetworkError,
            ElementLocationError,
            DownloadError
        ]
        
        return any(isinstance(error, error_type) for error_type in recoverable_types)
    
    def should_retry_operation(self, error: Exception, attempt_count: int, max_attempts: int = 3) -> bool:
        """
        Determine if an operation should be retried based on the error and attempt count.
        
        Args:
            error: The exception that occurred
            attempt_count: Current attempt number
            max_attempts: Maximum number of attempts allowed
            
        Returns:
            bool: True if the operation should be retried, False otherwise
        """
        if attempt_count >= max_attempts:
            return False
        
        # Only retry for certain types of errors
        retryable_types = [
            NetworkError,
            ElementLocationError
        ]
        
        return any(isinstance(error, error_type) for error_type in retryable_types)