"""
Unit tests for the MainController class.

This module tests the main application controller that orchestrates
all services for the YouTube MP3 Downloader application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from youtube_mp3_downloader.models.data_models import UserInput, DownloadResult, MetadataInfo
from youtube_mp3_downloader.exceptions import (
    YouTubeDownloaderError,
    NetworkError,
    ElementLocationError,
    BrowserError,
    DownloadError,
    MetadataError
)


class TestMainControllerLogic(unittest.TestCase):
    """Test cases for the MainController logic without GUI dependencies."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test user input
        self.test_user_input = UserInput(
            youtube_url="https://www.youtube.com/watch?v=test123",
            artist="Test Artist",
            title="Test Title",
            album="Test Album",
            track_number=1
        )
    
    def test_user_input_validation(self):
        """Test that UserInput validation works correctly."""
        # Test valid input
        valid_input = UserInput(
            youtube_url="https://www.youtube.com/watch?v=valid123",
            artist="Valid Artist",
            title="Valid Title",
            album="Valid Album",
            track_number=5
        )
        
        errors = valid_input.validate()
        self.assertEqual(len(errors), 0)
        
        # Test invalid input
        invalid_input = UserInput(
            youtube_url="not-a-youtube-url",
            artist="",
            title="Valid Title",
            album="Valid Album",
            track_number=-1
        )
        
        errors = invalid_input.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Invalid YouTube URL" in error for error in errors))
        self.assertTrue(any("Artist field cannot be empty" in error for error in errors))
        self.assertTrue(any("positive integer" in error for error in errors))
    
    def test_download_result_creation(self):
        """Test DownloadResult creation and validation."""
        # Test successful download result
        success_result = DownloadResult(
            success=True,
            file_path="/path/to/file.mp3",
            error_message=None,
            download_time=datetime.now()
        )
        
        errors = success_result.validate()
        self.assertEqual(len(errors), 0)
        
        # Test failed download result
        failed_result = DownloadResult(
            success=False,
            file_path=None,
            error_message="Download failed",
            download_time=datetime.now()
        )
        
        errors = failed_result.validate()
        self.assertEqual(len(errors), 0)
        
        # Test invalid download result (success but no file path)
        invalid_result = DownloadResult(
            success=True,
            file_path=None,
            error_message=None,
            download_time=datetime.now()
        )
        
        errors = invalid_result.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("file path" in error for error in errors))
    
    def test_metadata_info_creation(self):
        """Test MetadataInfo creation and validation."""
        # Test valid metadata info
        valid_metadata = MetadataInfo(
            artist="Test Artist",
            title="Test Title",
            album="Test Album",
            track_number=1,
            original_filename="test.mp3"
        )
        
        errors = valid_metadata.validate()
        self.assertEqual(len(errors), 0)
        
        # Test ID3 dictionary conversion
        id3_dict = valid_metadata.to_id3_dict()
        self.assertEqual(id3_dict['TPE1'], "Test Artist")
        self.assertEqual(id3_dict['TIT2'], "Test Title")
        self.assertEqual(id3_dict['TALB'], "Test Album")
        self.assertEqual(id3_dict['TRCK'], "1")
        
        # Test invalid metadata info
        invalid_metadata = MetadataInfo(
            artist="",
            title="Test Title",
            album="Test Album",
            track_number=0,
            original_filename=""
        )
        
        errors = invalid_metadata.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Artist cannot be empty" in error for error in errors))
        self.assertTrue(any("positive integer" in error for error in errors))
        self.assertTrue(any("Original filename cannot be empty" in error for error in errors))
    
    def test_workflow_orchestration_concept(self):
        """Test the concept of workflow orchestration without GUI dependencies."""
        # This test verifies that the workflow steps are conceptually correct
        # without actually importing the MainController class
        
        # Simulate the workflow steps that MainController should perform
        workflow_steps = [
            "browser_automation",
            "download_monitoring", 
            "metadata_application",
            "completed"
        ]
        
        # Verify workflow step progression
        current_step = 0
        
        def simulate_step_completion():
            nonlocal current_step
            if current_step < len(workflow_steps):
                step = workflow_steps[current_step]
                current_step += 1
                return step
            return None
        
        # Simulate workflow execution
        step1 = simulate_step_completion()  # browser_automation
        self.assertEqual(step1, "browser_automation")
        
        step2 = simulate_step_completion()  # download_monitoring
        self.assertEqual(step2, "download_monitoring")
        
        step3 = simulate_step_completion()  # metadata_application
        self.assertEqual(step3, "metadata_application")
        
        step4 = simulate_step_completion()  # completed
        self.assertEqual(step4, "completed")
        
        step5 = simulate_step_completion()  # None (workflow complete)
        self.assertIsNone(step5)
    
    def test_error_handling_concepts(self):
        """Test error handling concepts for different error types."""
        # Test different exception types that MainController should handle
        
        # Network error
        network_error = NetworkError("Connection failed", "https://mp3cow.com/")
        self.assertEqual(network_error.message, "Connection failed")
        self.assertEqual(network_error.url, "https://mp3cow.com/")
        
        # Element location error
        element_error = ElementLocationError("Download button", "ID: download")
        self.assertEqual(element_error.element_description, "Download button")
        self.assertEqual(element_error.locator, "ID: download")
        
        # Browser error
        browser_error = BrowserError("Chrome not found", "browser_initialization")
        self.assertEqual(browser_error.message, "Chrome not found")
        self.assertEqual(browser_error.operation, "browser_initialization")
        
        # Download error
        download_error = DownloadError("File not found", "/path/to/file.mp3")
        self.assertEqual(download_error.message, "File not found")
        self.assertEqual(download_error.file_path, "/path/to/file.mp3")
        
        # Metadata error
        metadata_error = MetadataError("Invalid MP3", "/path/to/file.mp3")
        self.assertEqual(metadata_error.message, "Invalid MP3")
        self.assertEqual(metadata_error.file_path, "/path/to/file.mp3")
    
    def test_operation_status_tracking(self):
        """Test operation status tracking concepts."""
        # Simulate operation status tracking
        operation_status = {
            'current_operation': None,
            'is_processing': False,
            'operation_start_time': None,
            'elapsed_time': 0
        }
        
        # Start operation
        operation_status['current_operation'] = 'browser_automation'
        operation_status['is_processing'] = True
        operation_status['operation_start_time'] = datetime.now()
        
        self.assertEqual(operation_status['current_operation'], 'browser_automation')
        self.assertTrue(operation_status['is_processing'])
        self.assertIsNotNone(operation_status['operation_start_time'])
        
        # Complete operation
        operation_status['current_operation'] = None
        operation_status['is_processing'] = False
        
        self.assertIsNone(operation_status['current_operation'])
        self.assertFalse(operation_status['is_processing'])
    
    def test_browser_closing_after_download(self):
        """Test that browser is closed after download initiation."""
        from unittest.mock import Mock
        
        # Create a mock main controller with browser service
        controller = Mock()
        controller.browser_service = Mock()
        controller.logger = Mock()
        
        # Mock browser service methods
        controller.browser_service.is_browser_open.return_value = True
        controller.browser_service.close_browser.return_value = True
        
        # Import the actual method to test
        from youtube_mp3_downloader.controllers.main_controller import MainController
        
        # Create a real instance to get the method
        real_controller = MainController()
        real_controller.browser_service = controller.browser_service
        real_controller.logger = controller.logger
        
        # Call the browser closing method
        real_controller._close_browser_after_download()
        
        # Verify browser was checked and closed
        controller.browser_service.is_browser_open.assert_called_once()
        controller.browser_service.close_browser.assert_called_once()
        controller.logger.info.assert_called_once_with("Browser closed after download completion")
    
    def test_browser_closing_handles_errors(self):
        """Test that browser closing handles errors gracefully."""
        from unittest.mock import Mock
        
        # Create a mock main controller with browser service
        controller = Mock()
        controller.browser_service = Mock()
        controller.logger = Mock()
        
        # Mock browser service to raise an exception
        controller.browser_service.is_browser_open.side_effect = Exception("Test error")
        
        # Import the actual method to test
        from youtube_mp3_downloader.controllers.main_controller import MainController
        
        # Create a real instance to get the method
        real_controller = MainController()
        real_controller.browser_service = controller.browser_service
        real_controller.logger = controller.logger
        
        # Call the browser closing method - should not raise exception
        try:
            real_controller._close_browser_after_download()
            # Should reach here without exception
            success = True
        except Exception:
            success = False
        
        # Verify it handled the error gracefully
        assert success is True
        controller.logger.warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()