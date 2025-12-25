"""
Unit tests for the GUI Controller.

Tests the validation logic and core functionality of the GUI controller
without requiring a GUI environment.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock tkinter before importing GUI controller
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

from youtube_mp3_downloader.controllers.gui_controller import GUIController
from youtube_mp3_downloader.models.data_models import UserInput


class TestGUIController:
    """Test cases for the GUIController class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.callback_mock = Mock()
        self.gui = GUIController(on_submit_callback=self.callback_mock)
    
    def test_validate_youtube_url_valid_urls(self):
        """Test YouTube URL validation with valid URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert self.gui.validate_youtube_url(url), f"URL should be valid: {url}"
    
    def test_validate_youtube_url_invalid_urls(self):
        """Test YouTube URL validation with invalid URLs."""
        invalid_urls = [
            "",
            "not_a_url",
            "https://www.google.com",
            "https://vimeo.com/123456",
            "youtube.com/watch?v=dQw4w9WgXcQ",  # Missing protocol
            "https://www.youtube.com/",  # Missing video ID
            "https://www.youtube.com/watch",  # Missing video ID
            None
        ]
        
        for url in invalid_urls:
            assert not self.gui.validate_youtube_url(url), f"URL should be invalid: {url}"
    
    def test_validate_track_number_valid_numbers(self):
        """Test track number validation with valid numbers."""
        valid_numbers = ["1", "10", "99", "  5  ", "123"]
        
        for num in valid_numbers:
            assert self.gui.validate_track_number(num), f"Track number should be valid: {num}"
    
    def test_validate_track_number_invalid_numbers(self):
        """Test track number validation with invalid numbers."""
        invalid_numbers = ["0", "-1", "abc", "", "  ", "1.5", "1a", None]
        
        for num in invalid_numbers:
            assert not self.gui.validate_track_number(num), f"Track number should be invalid: {num}"
    
    @patch('youtube_mp3_downloader.controllers.gui_controller.messagebox')
    def test_show_error(self, mock_messagebox):
        """Test error message display."""
        error_message = "Test error message"
        self.gui.show_error(error_message)
        
        mock_messagebox.showerror.assert_called_once_with("Error", error_message)
    
    @patch('youtube_mp3_downloader.controllers.gui_controller.messagebox')
    def test_show_success(self, mock_messagebox):
        """Test success message display."""
        file_path = "/path/to/file.mp3"
        
        # Mock the GUI components
        self.gui.progress_var = Mock()
        self.gui.status_label = Mock()
        self.gui.progress_bar = Mock()
        self.gui.submit_button = Mock()
        self.gui.clear_button = Mock()
        
        self.gui.show_success(file_path)
        
        # Verify success dialog was shown
        expected_message = f"Download and metadata tagging completed successfully!\n\nFile saved to:\n{file_path}"
        mock_messagebox.showinfo.assert_called_once_with("Success", expected_message)
        
        # Verify buttons were re-enabled
        self.gui.submit_button.config.assert_called_with(state='normal')
        self.gui.clear_button.config.assert_called_with(state='normal')
    
    def test_clear_button_functionality(self):
        """Test that the clear button clears all fields and resets the form."""
        # Mock the GUI components
        mock_entry_youtube = Mock()
        mock_entry_artist = Mock()
        mock_entry_title = Mock()
        mock_entry_album = Mock()
        mock_entry_track = Mock()
        
        self.gui.input_fields = {
            'youtube_url': mock_entry_youtube,
            'artist': mock_entry_artist,
            'title': mock_entry_title,
            'album': mock_entry_album,
            'track_number': mock_entry_track
        }
        
        self.gui.progress_var = Mock()
        self.gui.status_label = Mock()
        self.gui.progress_bar = Mock()
        self.gui.submit_button = Mock()
        
        # Call clear functionality
        self.gui._on_clear_clicked()
        
        # Verify all fields are cleared
        mock_entry_youtube.delete.assert_called_once_with(0, sys.modules['tkinter'].END)
        mock_entry_artist.delete.assert_called_once_with(0, sys.modules['tkinter'].END)
        mock_entry_title.delete.assert_called_once_with(0, sys.modules['tkinter'].END)
        mock_entry_album.delete.assert_called_once_with(0, sys.modules['tkinter'].END)
        mock_entry_track.delete.assert_called_once_with(0, sys.modules['tkinter'].END)
        
        # Verify submit button is re-enabled
        self.gui.submit_button.config.assert_called_with(state='normal')
        
        # Verify focus is set to YouTube URL field
        mock_entry_youtube.focus_set.assert_called_once()
    
    def test_load_mp3_functionality(self):
        """Test that loading an MP3 file populates the form correctly."""
        # Mock the GUI components
        mock_entry_youtube = Mock()
        mock_entry_artist = Mock()
        mock_entry_title = Mock()
        mock_entry_album = Mock()
        mock_entry_track = Mock()
        
        self.gui.input_fields = {
            'youtube_url': mock_entry_youtube,
            'artist': mock_entry_artist,
            'title': mock_entry_title,
            'album': mock_entry_album,
            'track_number': mock_entry_track
        }
        
        self.gui.file_path_label = Mock()
        self.gui.metadata_service = Mock()
        self.gui.submit_button = Mock()
        self.gui.save_changes_button = Mock()
        
        # Mock metadata service responses
        self.gui.metadata_service.validate_mp3_file.return_value = True
        self.gui.metadata_service.get_metadata_summary.return_value = {
            'artist': 'Test Artist',
            'title': 'Test Title',
            'album': 'Test Album',
            'track_number': '5',
            'duration': '3:45',
            'file_size': '4.2 MB'
        }
        
        # Mock file dialog
        with patch('youtube_mp3_downloader.controllers.gui_controller.filedialog.askopenfilename') as mock_dialog:
            with patch('youtube_mp3_downloader.controllers.gui_controller.messagebox.showinfo') as mock_info:
                with patch('youtube_mp3_downloader.controllers.gui_controller.os.path.basename') as mock_basename:
                    mock_dialog.return_value = '/path/to/test.mp3'
                    mock_basename.return_value = 'test.mp3'
                    
                    # Call load MP3 functionality
                    self.gui._on_load_mp3_clicked()
                    
                    # Verify file dialog was opened
                    mock_dialog.assert_called_once()
                    
                    # Verify metadata service was called
                    self.gui.metadata_service.validate_mp3_file.assert_called_once_with('/path/to/test.mp3')
                    self.gui.metadata_service.get_metadata_summary.assert_called_once_with('/path/to/test.mp3')
                    
                    # Verify form fields were cleared and populated
                    mock_entry_artist.delete.assert_called_with(0, sys.modules['tkinter'].END)
                    mock_entry_artist.insert.assert_called_with(0, 'Test Artist')
                    mock_entry_title.insert.assert_called_with(0, 'Test Title')
                    mock_entry_album.insert.assert_called_with(0, 'Test Album')
                    mock_entry_track.insert.assert_called_with(0, '5')
                    
                    # Verify success message was shown
                    mock_info.assert_called_once()
    
    def test_validate_metadata_only(self):
        """Test metadata-only validation for edit mode."""
        # Mock the GUI components with valid data
        mock_entry_artist = Mock()
        mock_entry_title = Mock()
        mock_entry_album = Mock()
        mock_entry_track = Mock()
        
        mock_entry_artist.get.return_value = "Test Artist"
        mock_entry_title.get.return_value = "Test Title"
        mock_entry_album.get.return_value = "Test Album"
        mock_entry_track.get.return_value = "1"
        
        self.gui.input_fields = {
            'artist': mock_entry_artist,
            'title': mock_entry_title,
            'album': mock_entry_album,
            'track_number': mock_entry_track
        }
        
        self.gui.current_mp3_file = "/path/to/test.mp3"
        
        # Call validation
        is_valid, metadata_info = self.gui._validate_metadata_only()
        
        # Verify validation passed
        assert is_valid is True
        assert metadata_info is not None
        assert metadata_info.artist == "Test Artist"
        assert metadata_info.title == "Test Title"
        assert metadata_info.album == "Test Album"
        assert metadata_info.track_number == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])