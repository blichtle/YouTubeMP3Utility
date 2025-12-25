"""
Data models for the YouTube MP3 Downloader application.

This module contains the core data classes used throughout the application
for representing user input, download results, and metadata information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import re


@dataclass
class UserInput:
    """
    Represents user input from the GUI form.
    
    Attributes:
        youtube_url: The YouTube video URL to download
        artist: The artist name for metadata
        title: The song title for metadata
        album: The album name for metadata
        track_number: The track number for metadata
    """
    youtube_url: str
    artist: str
    title: str
    album: str
    track_number: int
    
    def validate(self) -> List[str]:
        """
        Validates all user input fields and returns a list of validation errors.
        
        Returns:
            List[str]: List of validation error messages. Empty list if all valid.
        """
        errors = []
        
        # Validate YouTube URL (Requirements 1.2)
        if not self._is_valid_youtube_url(self.youtube_url):
            errors.append("Invalid YouTube URL format. Please enter a valid YouTube URL.")
        
        # Validate text fields are not empty (Requirements 1.3)
        if not self.artist.strip():
            errors.append("Artist field cannot be empty.")
        
        if not self.title.strip():
            errors.append("Title field cannot be empty.")
        
        if not self.album.strip():
            errors.append("Album field cannot be empty.")
        
        # Validate track number (Requirements 1.4)
        if not self._is_valid_track_number(self.track_number):
            errors.append("Track number must be a positive integer.")
        
        return errors
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """
        Validates if the provided URL is a valid YouTube URL format.
        
        Args:
            url: The URL string to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # YouTube URL patterns
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(www\.)?youtu\.be/[\w-]+',
            r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(www\.)?youtube\.com/v/[\w-]+'
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)
    
    def _is_valid_track_number(self, track_num: int) -> bool:
        """
        Validates if the track number is a positive integer.
        
        Args:
            track_num: The track number to validate
            
        Returns:
            bool: True if valid positive integer, False otherwise
        """
        return isinstance(track_num, int) and track_num > 0


@dataclass
class DownloadResult:
    """
    Represents the result of a download operation.
    
    Attributes:
        success: Whether the download was successful
        file_path: Path to the downloaded file (if successful)
        error_message: Error message (if unsuccessful)
        download_time: Timestamp when download completed
    """
    success: bool
    file_path: Optional[str]
    error_message: Optional[str]
    download_time: datetime
    
    def validate(self) -> List[str]:
        """
        Validates the download result data.
        
        Returns:
            List[str]: List of validation error messages. Empty list if all valid.
        """
        errors = []
        
        # If successful, file_path should be provided
        if self.success and not self.file_path:
            errors.append("Successful download must have a file path.")
        
        # If unsuccessful, error_message should be provided
        if not self.success and not self.error_message:
            errors.append("Failed download must have an error message.")
        
        # Download time should be valid
        if not isinstance(self.download_time, datetime):
            errors.append("Download time must be a valid datetime object.")
        
        return errors


@dataclass
class MetadataInfo:
    """
    Represents metadata information to be applied to an MP3 file.
    
    Attributes:
        artist: The artist name
        title: The song title
        album: The album name
        track_number: The track number
        original_filename: The original filename before metadata application
    """
    artist: str
    title: str
    album: str
    track_number: int
    original_filename: str
    
    def validate(self) -> List[str]:
        """
        Validates the metadata information.
        
        Returns:
            List[str]: List of validation error messages. Empty list if all valid.
        """
        errors = []
        
        # Validate required text fields
        if not self.artist.strip():
            errors.append("Artist cannot be empty.")
        
        if not self.title.strip():
            errors.append("Title cannot be empty.")
        
        if not self.album.strip():
            errors.append("Album cannot be empty.")
        
        if not self.original_filename.strip():
            errors.append("Original filename cannot be empty.")
        
        # Validate track number
        if not isinstance(self.track_number, int) or self.track_number <= 0:
            errors.append("Track number must be a positive integer.")
        
        return errors
    
    def to_id3_dict(self) -> Dict[str, str]:
        """
        Converts metadata to a dictionary compatible with mutagen ID3 tags.
        
        Returns:
            Dict[str, str]: Dictionary with ID3 tag keys and values
        """
        return {
            'TPE1': self.artist,      # Artist
            'TIT2': self.title,       # Title
            'TALB': self.album,       # Album
            'TRCK': str(self.track_number)  # Track number
        }