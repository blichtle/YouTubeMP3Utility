"""
Unit tests for the MetadataService class.

Tests basic functionality of reading and writing MP3 metadata using mutagen.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK

from youtube_mp3_downloader.services.metadata_service import MetadataService
from youtube_mp3_downloader.models.data_models import MetadataInfo


class TestMetadataService:
    """Test cases for MetadataService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = MetadataService()
        self.test_metadata = MetadataInfo(
            artist="Test Artist",
            title="Test Title",
            album="Test Album",
            track_number=1,
            original_filename="test.mp3"
        )
    
    def test_validate_mp3_file_with_invalid_extension(self):
        """Test validation fails for non-MP3 files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.service.validate_mp3_file(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)
    
    def test_validate_mp3_file_nonexistent(self):
        """Test validation fails for non-existent files."""
        result = self.service.validate_mp3_file("/nonexistent/file.mp3")
        assert result is False
    
    @patch('youtube_mp3_downloader.services.metadata_service.MP3')
    @patch('builtins.open', create=True)
    @patch('os.path.getsize')
    def test_validate_mp3_file_valid(self, mock_getsize, mock_open, mock_mp3):
        """Test validation passes for valid MP3 files."""
        # Mock file size check
        mock_getsize.return_value = 5000  # 5KB file
        
        # Mock MP3 file with valid info
        mock_audio = MagicMock()
        mock_audio.info.length = 180.0  # 3 minutes
        mock_mp3.return_value = mock_audio
        
        # Mock file header check
        mock_file = MagicMock()
        mock_file.read.return_value = b'ID3\x03\x00\x00\x00\x00\x00\x00'  # Valid ID3 header
        mock_open.return_value.__enter__.return_value = mock_file
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.service.validate_mp3_file(temp_path)
            assert result is True
        finally:
            os.unlink(temp_path)
    
    def test_read_metadata_file_not_found(self):
        """Test reading metadata from non-existent file raises MetadataError."""
        from youtube_mp3_downloader.exceptions import MetadataError
        with pytest.raises(MetadataError):
            self.service.read_metadata("/nonexistent/file.mp3")
    
    @patch('youtube_mp3_downloader.services.metadata_service.MP3')
    def test_read_metadata_empty_tags(self, mock_mp3):
        """Test reading metadata from file with no tags."""
        # Mock MP3 file with no tags
        mock_audio = MagicMock()
        mock_audio.tags = None
        mock_mp3.return_value = mock_audio
        
        with patch.object(self.service, 'validate_mp3_file', return_value=True):
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                result = self.service.read_metadata(temp_path)
                assert result == {}
            finally:
                os.unlink(temp_path)
    
    @patch('youtube_mp3_downloader.services.metadata_service.MP3')
    def test_read_metadata_with_tags(self, mock_mp3):
        """Test reading metadata from file with existing tags."""
        # Mock MP3 file with tags
        mock_audio = MagicMock()
        
        # Create a proper mock tags object that behaves like a dict
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: key in ['TPE1', 'TIT2', 'TALB', 'TRCK']
        mock_tags.__getitem__ = lambda self, key: {
            'TPE1': MagicMock(__str__=lambda self: "Existing Artist"),
            'TIT2': MagicMock(__str__=lambda self: "Existing Title"),
            'TALB': MagicMock(__str__=lambda self: "Existing Album"),
            'TRCK': MagicMock(__str__=lambda self: "2")
        }[key]
        mock_tags.keys.return_value = ['TPE1', 'TIT2', 'TALB', 'TRCK', 'TCON']  # Include extra tag
        
        mock_audio.tags = mock_tags
        mock_mp3.return_value = mock_audio
        
        with patch.object(self.service, 'validate_mp3_file', return_value=True):
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                result = self.service.read_metadata(temp_path)
                assert result['TPE1'] == "Existing Artist"
                assert result['TIT2'] == "Existing Title"
                assert result['TALB'] == "Existing Album"
                assert result['TRCK'] == "2"
            finally:
                os.unlink(temp_path)
    
    def test_apply_metadata_file_not_found(self):
        """Test applying metadata to non-existent file raises MetadataError."""
        from youtube_mp3_downloader.exceptions import MetadataError
        with pytest.raises(MetadataError):
            self.service.apply_metadata("/nonexistent/file.mp3", self.test_metadata)
    
    def test_apply_metadata_invalid_metadata(self):
        """Test applying invalid metadata raises MetadataError."""
        from youtube_mp3_downloader.exceptions import MetadataError
        invalid_metadata = MetadataInfo(
            artist="",  # Empty artist should be invalid
            title="Test Title",
            album="Test Album",
            track_number=1,
            original_filename="test.mp3"
        )
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch.object(self.service, 'validate_mp3_file', return_value=True):
                with pytest.raises(MetadataError):
                    self.service.apply_metadata(temp_path, invalid_metadata)
        finally:
            os.unlink(temp_path)
    
    def test_backup_original_file_not_found(self):
        """Test backup creation fails for non-existent file."""
        from youtube_mp3_downloader.exceptions import MetadataError
        with pytest.raises(MetadataError):
            self.service.backup_original("/nonexistent/file.mp3")
    
    def test_backup_original_success(self):
        """Test successful backup creation."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name
        
        try:
            backup_path = self.service.backup_original(temp_path)
            
            # Verify backup was created
            assert os.path.exists(backup_path)
            assert '.mp3.backup.' in backup_path  # Updated to match actual implementation
            
            # Verify backup has same content
            with open(temp_path, 'rb') as original:
                with open(backup_path, 'rb') as backup:
                    assert original.read() == backup.read()
            
            # Clean up backup
            os.unlink(backup_path)
        finally:
            os.unlink(temp_path)
    
    def test_get_metadata_summary_file_error(self):
        """Test metadata summary returns None values for file errors."""
        result = self.service.get_metadata_summary("/nonexistent/file.mp3")
        
        expected = {
            'artist': None,
            'title': None,
            'album': None,
            'track_number': None,
            'file_size': None,
            'duration': None
        }
        
        assert result == expected