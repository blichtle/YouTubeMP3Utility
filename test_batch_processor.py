#!/usr/bin/env python3
"""
Test script for the batch processor functionality.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from youtube_mp3_downloader.services.batch_processor import BatchProcessor


def test_batch_processor():
    """Test the batch processor with the sample CSV file."""
    print("🧪 Testing Batch Processor...")
    
    # Create batch processor
    processor = BatchProcessor()
    
    # Test loading the sample CSV
    csv_path = "sample_batch.csv"
    
    try:
        print(f"📁 Loading {csv_path}...")
        success = processor.load_spreadsheet(csv_path)
        
        if success:
            print("✅ CSV loaded successfully")
            
            # Get batch summary
            summary = processor.get_batch_summary()
            print(f"📊 Summary: {summary['total_rows']} rows loaded")
            
            # Test processing each row
            row_count = 0
            while processor.has_more_rows():
                row_count += 1
                user_input = processor.get_current_row_data()
                
                if user_input:
                    print(f"📝 Row {row_count}: {user_input.artist} - {user_input.title}")
                    print(f"   URL: {user_input.youtube_url}")
                    print(f"   Album: {user_input.album}, Track: {user_input.track_number}")
                
                # Get progress info
                progress = processor.get_progress_info()
                print(f"   Progress: {progress['percentage']:.1f}% ({progress['current_row']}/{progress['total_rows']})")
                
                # Advance to next row
                processor.advance_to_next_row()
            
            print("✅ All rows processed successfully")
            return True
            
        else:
            print("❌ Failed to load CSV")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function."""
    print("🎵 YouTube MP3 Downloader - Batch Processor Test")
    print("=" * 50)
    
    success = test_batch_processor()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Batch processor test completed successfully!")
        print("\n💡 You can now test the full batch processing in the GUI:")
        print("   1. Run: ./run.sh")
        print("   2. Click 'Load Spreadsheet'")
        print("   3. Select 'sample_batch.csv'")
        print("   4. Confirm to start batch processing")
    else:
        print("❌ Batch processor test failed.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)