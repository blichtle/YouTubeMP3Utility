"""
Metadata service for applying ID3 tags to MP3 files.

This module provides functionality to read existing MP3 metadata, apply new
metadata tags (Artist, Title, Album, Track Number), and preserve existing
metadata not specified by the user.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, Optional, List
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, ID3NoHeaderError
from mutagen import MutagenError

from ..models.data_models import MetadataInfo
from ..exceptions import MetadataError
from ..services.error_handler import ErrorHandler


class MetadataService:
    """
    Service for handling MP3 metadata operations using mutagen library.
    
    This service provides methods to read existing metadata, apply new metadata
    tags, validate MP3 files, and create backups before modification.
    """
    
    def __init__(self):
        """Initialize the metadata service."""
        # Initialize error handler
        self.error_handler = ErrorHandler()
    
    def read_metadata(self, file_path: str) -> Dict[str, str]:
        """
        Reads existing metadata from an MP3 file.
        Enhanced with comprehensive error handling (Requirement 5.5).
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Dict[str, str]: Dictionary containing existing metadata tags
            
        Raises:
            MetadataError: If file doesn't exist, is invalid, or cannot be read
        """
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "read_metadata")
            raise MetadataError(error_msg, file_path)
        
        if not self.validate_mp3_file(file_path):
            error_msg = f"Invalid MP3 file: {file_path}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "read_metadata")
            raise MetadataError(error_msg, file_path)
        
        try:
            audio_file = MP3(file_path, ID3=ID3)
            
            # Initialize empty metadata dictionary
            metadata = {}
            
            # Extract common ID3 tags if they exist
            if audio_file.tags:
                # Artist (TPE1)
                if 'TPE1' in audio_file.tags:
                    metadata['TPE1'] = str(audio_file.tags['TPE1'])
                
                # Title (TIT2)
                if 'TIT2' in audio_file.tags:
                    metadata['TIT2'] = str(audio_file.tags['TIT2'])
                
                # Album (TALB)
                if 'TALB' in audio_file.tags:
                    metadata['TALB'] = str(audio_file.tags['TALB'])
                
                # Track number (TRCK)
                if 'TRCK' in audio_file.tags:
                    metadata['TRCK'] = str(audio_file.tags['TRCK'])
                
                # Preserve all other existing tags
                for tag_key in audio_file.tags.keys():
                    if tag_key not in ['TPE1', 'TIT2', 'TALB', 'TRCK']:
                        try:
                            metadata[tag_key] = str(audio_file.tags[tag_key])
                        except Exception:
                            # Skip problematic tags to avoid corruption
                            continue
            
            return metadata
            
        except MutagenError as e:
            error_msg = f"Error reading metadata from {file_path}: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "read_metadata")
            raise MetadataError(error_msg, file_path) from e
            
        except Exception as e:
            error_msg = f"Unexpected error reading metadata from {file_path}: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "read_metadata")
            raise MetadataError(error_msg, file_path) from e
    
    def apply_metadata(self, file_path: str, metadata_info: MetadataInfo) -> bool:
        """
        Applies metadata to an MP3 file while preserving existing metadata.
        Enhanced with comprehensive error handling and file integrity preservation (Requirement 5.5).
        
        Args:
            file_path: Path to the MP3 file
            metadata_info: MetadataInfo object containing new metadata
            
        Returns:
            bool: True if metadata was applied successfully, False otherwise
            
        Raises:
            MetadataError: If file doesn't exist, is invalid, or metadata application fails
        """
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
            raise MetadataError(error_msg, file_path)
        
        if not self.validate_mp3_file(file_path):
            error_msg = f"Invalid MP3 file: {file_path}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
            raise MetadataError(error_msg, file_path)
        
        # Validate metadata info
        validation_errors = metadata_info.validate()
        if validation_errors:
            error_msg = f"Invalid metadata: {', '.join(validation_errors)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
            raise MetadataError(error_msg, file_path)
        
        # Create backup before modification (Requirement 5.5 - file integrity preservation)
        backup_path = None
        try:
            backup_path = self.backup_original(file_path)
        except Exception as e:
            error_msg = f"Failed to create backup before metadata modification: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
            raise MetadataError(error_msg, file_path) from e
        
        try:
            # Read existing metadata to preserve non-user-specified tags
            existing_metadata = self.read_metadata(file_path)
            
            # Load the MP3 file
            audio_file = MP3(file_path, ID3=ID3)
            
            # Initialize ID3 tags if they don't exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Apply new metadata from user input
            audio_file.tags['TPE1'] = TPE1(encoding=3, text=metadata_info.artist)
            audio_file.tags['TIT2'] = TIT2(encoding=3, text=metadata_info.title)
            audio_file.tags['TALB'] = TALB(encoding=3, text=metadata_info.album)
            audio_file.tags['TRCK'] = TRCK(encoding=3, text=str(metadata_info.track_number))
            
            # Preserve existing metadata not specified by user
            for tag_key, tag_value in existing_metadata.items():
                if tag_key not in ['TPE1', 'TIT2', 'TALB', 'TRCK']:
                    # Keep existing tags that aren't being overwritten
                    # Skip complex tags to avoid corruption
                    if len(tag_key) == 4 and tag_key.isalnum():
                        try:
                            # Only preserve simple text tags
                            continue
                        except Exception:
                            continue
            
            # Save the changes
            audio_file.save()
            
            # Verify the file is still valid after modification
            if not self.validate_mp3_file(file_path):
                raise MetadataError("File became invalid after metadata application")
            
            # Remove backup if successful
            if backup_path and os.path.exists(backup_path):
                os.remove(backup_path)
            
            return True
            
        except Exception as e:
            # Restore from backup if something went wrong (Requirement 5.5 - file integrity preservation)
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, file_path)
                except Exception as restore_error:
                    error_msg = f"Critical error: Failed to restore backup after metadata failure. Original error: {str(e)}, Restore error: {str(restore_error)}"
                    self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
                    raise MetadataError(error_msg, file_path) from e
            
            error_msg = f"Error applying metadata to {file_path}: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "apply_metadata")
            raise MetadataError(error_msg, file_path) from e
    
    def validate_mp3_file(self, file_path: str) -> bool:
        """
        Validates if a file is a valid MP3 file.
        Enhanced with detailed error reporting (Requirement 5.5).
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if valid MP3 file, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file extension
        if not file_path.lower().endswith('.mp3'):
            return False
        
        try:
            # Check file size (should be at least a few KB for a valid MP3)
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # Less than 1KB is suspicious
                return False
            
            # Try to load the file with mutagen
            audio_file = MP3(file_path)
            
            # Check if it has audio info (duration, bitrate, etc.)
            if audio_file.info is None:
                return False
            
            # Check if duration is reasonable (not zero or negative)
            if audio_file.info.length <= 0:
                return False
            
            # Check basic MP3 header
            with open(file_path, 'rb') as f:
                header = f.read(10)
                if len(header) >= 3:
                    # Check for ID3 tag or MP3 frame sync
                    if not (header[:3] == b'ID3' or 
                           (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)):
                        return False
            
            return True
            
        except (MutagenError, Exception) as e:
            # Log validation failure for debugging
            self.error_handler.handle_error(
                MetadataError(f"MP3 validation failed: {str(e)}", file_path), 
                "validate_mp3_file"
            )
            return False
    
    def backup_original(self, file_path: str) -> str:
        """
        Creates a backup of the original file before modification.
        Enhanced with error handling (Requirement 5.5).
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            str: Path to the backup file
            
        Raises:
            MetadataError: If backup creation fails
        """
        if not os.path.exists(file_path):
            error_msg = f"Cannot backup non-existent file: {file_path}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "backup_original")
            raise MetadataError(error_msg, file_path)
        
        # Create backup filename with timestamp to avoid conflicts
        file_path_obj = Path(file_path)
        timestamp = int(time.time())
        backup_path = str(file_path_obj.with_suffix(f"{file_path_obj.suffix}.backup.{timestamp}"))
        
        try:
            # Check available disk space
            file_size = os.path.getsize(file_path)
            available_space = shutil.disk_usage(file_path_obj.parent).free
            
            if available_space < file_size * 2:  # Need at least 2x file size for safety
                error_msg = f"Insufficient disk space to create backup. Need {file_size * 2} bytes, have {available_space} bytes."
                self.error_handler.handle_error(MetadataError(error_msg, file_path), "backup_original")
                raise MetadataError(error_msg, file_path)
            
            shutil.copy2(file_path, backup_path)
            
            # Verify backup was created successfully
            if not os.path.exists(backup_path) or os.path.getsize(backup_path) != file_size:
                error_msg = f"Backup verification failed for {file_path}"
                self.error_handler.handle_error(MetadataError(error_msg, file_path), "backup_original")
                raise MetadataError(error_msg, file_path)
            
            return backup_path
            
        except OSError as e:
            error_msg = f"Failed to create backup of {file_path}: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "backup_original")
            raise MetadataError(error_msg, file_path) from e
        except Exception as e:
            error_msg = f"Unexpected error creating backup of {file_path}: {str(e)}"
            self.error_handler.handle_error(MetadataError(error_msg, file_path), "backup_original")
            raise MetadataError(error_msg, file_path) from e
    
    def get_metadata_summary(self, file_path: str) -> Dict[str, Optional[str]]:
        """
        Gets a summary of the current metadata in a user-friendly format.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Dict[str, Optional[str]]: Dictionary with user-friendly metadata info
        """
        try:
            metadata = self.read_metadata(file_path)
            
            return {
                'artist': metadata.get('TPE1'),
                'title': metadata.get('TIT2'),
                'album': metadata.get('TALB'),
                'track_number': metadata.get('TRCK'),
                'file_size': self._get_file_size(file_path),
                'duration': self._get_duration(file_path)
            }
        except Exception:
            return {
                'artist': None,
                'title': None,
                'album': None,
                'track_number': None,
                'file_size': None,
                'duration': None
            }
    
    def _get_file_size(self, file_path: str) -> Optional[str]:
        """
        Gets the file size in a human-readable format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[str]: File size string or None if error
        """
        try:
            size_bytes = os.path.getsize(file_path)
            
            # Convert to MB
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.1f} MB"
        except OSError:
            return None
    
    def _get_duration(self, file_path: str) -> Optional[str]:
        """
        Gets the audio duration in a human-readable format.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Optional[str]: Duration string (MM:SS) or None if error
        """
        try:
            audio_file = MP3(file_path)
            if audio_file.info and audio_file.info.length:
                duration_seconds = int(audio_file.info.length)
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                return f"{minutes}:{seconds:02d}"
        except (MutagenError, Exception):
            pass
        
        return None