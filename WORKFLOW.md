# YouTube MP3 Downloader Workflow

## Complete Download Process

### 1. Browser Automation
- Open Chrome browser
- Navigate to mp3cow.com
- Input YouTube URL
- Click convert button
- Wait for conversion (5 seconds)
- Click download button
- **Browser stays open during download**

### 2. Download Monitoring
- Monitor Downloads folder for new MP3 files
- Wait for file to appear and complete downloading
- Detect when file is fully downloaded
- Verify file integrity

### 3. Browser Cleanup
- **Close browser after download is detected and complete**
- This ensures download completes before browser closes
- Provides clean user experience

### 4. Metadata Application
- Apply user-specified metadata to downloaded file
- Create backup before modification
- Update ID3 tags (Artist, Title, Album, Track Number)
- Verify metadata was applied successfully

### 5. Completion
- Show success message with file location
- Re-enable UI controls
- Ready for next operation

## Key Timing Points

- **Browser Opens**: At start of process
- **Download Initiated**: When download button is clicked
- **Browser Closes**: After download file is detected and complete ✅
- **Metadata Applied**: After browser is closed
- **Process Complete**: After metadata is successfully applied

This ensures the browser stays open long enough for the download to complete while still providing automatic cleanup for a better user experience.