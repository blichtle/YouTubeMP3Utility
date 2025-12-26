#!/usr/bin/env python3
"""
Simple GUI test script to verify the clear button functionality.
This script opens the GUI for manual testing of the clear button.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from youtube_mp3_downloader.controllers.gui_controller import GUIController


def test_callback(user_input):
    """Test callback function that just prints the input."""
    print(f"Received input: {user_input}")
    print("This is just a test - no actual download will occur.")


def main():
    """Main function to test the GUI."""
    print("🧪 Testing YouTube MP3 Downloader GUI...")
    print("📝 Instructions:")
    print("   1. Test 'Load MP3 File' to load an existing MP3 and edit its metadata")
    print("   2. Fill in some test data in the form fields")
    print("   3. Click 'Clear All Fields' to test the clear functionality")
    print("   4. Verify all fields are cleared and form is reset")
    print("   5. Test switching between download mode and edit mode")
    print("   6. Note: Browser will auto-close after download initiation")
    print("   7. Close the window when done testing")
    print()
    
    # Create GUI controller with test callback
    gui_controller = GUIController(on_submit_callback=test_callback)
    
    # Create and show the GUI
    root = gui_controller.create_input_form()
    
    # Add some test data for demonstration
    gui_controller.input_fields['youtube_url'].insert(0, "https://www.youtube.com/watch?v=example")
    gui_controller.input_fields['artist'].insert(0, "Test Artist")
    gui_controller.input_fields['title'].insert(0, "Test Song")
    gui_controller.input_fields['album'].insert(0, "Test Album")
    gui_controller.input_fields['track_number'].insert(0, "1")
    
    print("✅ GUI opened with test data. Test the new MP3 loading and editing functionality!")
    print("💡 Tip: The browser will automatically close after download starts for a cleaner experience.")
    
    # Run the GUI
    gui_controller.run()
    
    print("👋 GUI test completed.")


if __name__ == "__main__":
    main()