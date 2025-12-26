# YouTube MP3 Downloader Workflow

## Single Download Process

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

## Batch Processing Workflow

### 1. Spreadsheet Loading
- User clicks "Load Spreadsheet" button
- Select CSV or Excel file with columns: YouTubeURL, Artist, Title, Album, TrackNumber
- Validate file format and column structure (case insensitive matching)
- Display preview of loaded data
- User confirms to start batch processing

### 2. Batch Processing Loop
For each row in the spreadsheet:

#### 2.1 Row Processing
- Extract data from current row
- Populate form fields automatically
- Update batch progress bar and status

#### 2.2 Single Download Workflow
- Execute complete single download process (steps 1-4 above)
- Browser automation → Download monitoring → Browser cleanup → Metadata application

#### 2.3 Row Completion
- Clear form fields
- Advance to next row
- Update progress indicators

### 3. Batch Completion
- Display completion message
- Reset batch processing state
- Re-enable all UI controls

### 4. Error Handling in Batch Mode
- Skip invalid rows and continue processing
- Display error messages for failed downloads
- Maintain progress tracking even with errors
- Allow user to cancel batch processing

## Key Timing Points

### Single Download
- **Browser Opens**: At start of process
- **Download Initiated**: When download button is clicked
- **Browser Closes**: After download file is detected and complete ✅
- **Metadata Applied**: After browser is closed
- **Process Complete**: After metadata is successfully applied

### Batch Processing
- **Batch Starts**: After user confirms spreadsheet preview
- **Per Row**: Complete single download workflow for each row
- **Progress Updates**: Real-time progress bar and status updates
- **Batch Complete**: After all rows processed or user cancellation

## Threading Model

- **Main Thread**: GUI updates and user interaction
- **Batch Processing Thread**: Handles batch workflow to prevent GUI blocking
- **Download Monitoring**: File system watching in separate thread
- **Coordination**: Event-based signaling between threads for download completion

This ensures the browser stays open long enough for each download to complete while providing automatic cleanup and seamless batch processing for multiple files.