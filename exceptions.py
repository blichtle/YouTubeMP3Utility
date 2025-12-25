"""
Custom exceptions for the YouTube MP3 Downloader application.

This module defines specific exception classes for different types of errors
that can occur during the download and metadata application process.
"""


class YouTubeDownloaderError(Exception):
    """Base exception class for YouTube MP3 Downloader errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class InputValidationError(YouTubeDownloaderError):
    """Exception raised for input validation errors (Requirement 5.1)."""
    
    def __init__(self, field_name: str, message: str):
        """
        Initialize input validation error.
        
        Args:
            field_name: Name of the field that failed validation
            message: Specific validation error message
        """
        super().__init__(message, "INPUT_VALIDATION_ERROR")
        self.field_name = field_name


class NetworkError(YouTubeDownloaderError):
    """Exception raised for network connectivity issues (Requirement 5.2)."""
    
    def __init__(self, message: str, url: str = None):
        """
        Initialize network error.
        
        Args:
            message: Network error description
            url: URL that caused the error (if applicable)
        """
        super().__init__(message, "NETWORK_ERROR")
        self.url = url


class ElementLocationError(YouTubeDownloaderError):
    """Exception raised when required page elements cannot be found (Requirement 5.3)."""
    
    def __init__(self, element_description: str, locator: str = None):
        """
        Initialize element location error.
        
        Args:
            element_description: Description of the element that couldn't be found
            locator: Selenium locator that failed (if applicable)
        """
        super().__init__(f"Could not locate {element_description}", "ELEMENT_LOCATION_ERROR")
        self.element_description = element_description
        self.locator = locator


class BrowserError(YouTubeDownloaderError):
    """Exception raised for browser automation errors."""
    
    def __init__(self, message: str, operation: str = None):
        """
        Initialize browser error.
        
        Args:
            message: Browser error description
            operation: Browser operation that failed (if applicable)
        """
        super().__init__(message, "BROWSER_ERROR")
        self.operation = operation


class DownloadError(YouTubeDownloaderError):
    """Exception raised for download-related errors (Requirement 5.4)."""
    
    def __init__(self, message: str, file_path: str = None):
        """
        Initialize download error.
        
        Args:
            message: Download error description
            file_path: Path where download was expected (if applicable)
        """
        super().__init__(message, "DOWNLOAD_ERROR")
        self.file_path = file_path


class MetadataError(YouTubeDownloaderError):
    """Exception raised for metadata processing errors (Requirement 5.5)."""
    
    def __init__(self, message: str, file_path: str = None):
        """
        Initialize metadata error.
        
        Args:
            message: Metadata error description
            file_path: Path to the file that caused the error (if applicable)
        """
        super().__init__(message, "METADATA_ERROR")
        self.file_path = file_path