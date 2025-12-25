# Requirements Document

## Introduction

A Python desktop application that automates the process of downloading MP3 files from YouTube videos and adding custom metadata tags. The application provides a simple GUI for users to input YouTube URLs and metadata information, then automates the download process through a web browser and applies the metadata to the downloaded MP3 file.

## Glossary

- **Application**: The YouTube MP3 Downloader desktop application
- **Browser_Controller**: Component that controls web browser automation
- **Metadata_Tagger**: Component that applies ID3 tags to MP3 files
- **GUI**: Graphical user interface for user input
- **Download_Monitor**: Component that monitors the downloads folder for new files

## Requirements

### Requirement 1: User Input Interface

**User Story:** As a user, I want to enter YouTube video information and metadata through a simple form, so that I can prepare for downloading and tagging MP3 files.

#### Acceptance Criteria

1. THE GUI SHALL display input fields for YouTube URL, Artist, Title, Album, and Track Number
2. WHEN a user enters a YouTube URL, THE Application SHALL validate it as a proper YouTube URL format
3. WHEN a user enters metadata information, THE Application SHALL accept text input for Artist, Title, and Album fields
4. WHEN a user enters track number, THE Application SHALL accept numeric input and validate it as a positive integer
5. THE GUI SHALL provide a submit button to initiate the download process

### Requirement 2: Browser Automation

**User Story:** As a user, I want the application to automatically navigate to the MP3 conversion website and initiate the download, so that I don't have to manually perform these steps.

#### Acceptance Criteria

1. WHEN the submit button is clicked, THE Browser_Controller SHALL open a web browser
2. WHEN the browser opens, THE Browser_Controller SHALL navigate to https://mp3cow.com/
3. WHEN the page loads, THE Browser_Controller SHALL locate the input field with ID "url"
4. WHEN the input field is found, THE Browser_Controller SHALL paste the YouTube URL into the field
5. WHEN the URL is pasted, THE Browser_Controller SHALL click the input button with ID "bco"
6. WHEN the conversion starts, THE Browser_Controller SHALL wait 5 seconds
7. WHEN the wait period ends, THE Browser_Controller SHALL locate and click the button with text "Download MP3"

### Requirement 3: Download Management

**User Story:** As a user, I want the application to automatically detect when the MP3 file is downloaded, so that metadata can be applied without manual intervention.

#### Acceptance Criteria

1. WHEN the download begins, THE Download_Monitor SHALL monitor the macOS Downloads folder
2. WHEN a new MP3 file appears in the Downloads folder, THE Download_Monitor SHALL identify it as the target file
3. WHEN the download completes, THE Download_Monitor SHALL verify the file is fully downloaded and accessible
4. THE Download_Monitor SHALL handle cases where multiple files are downloading simultaneously

### Requirement 4: Metadata Application

**User Story:** As a user, I want the downloaded MP3 file to have proper metadata tags, so that it displays correctly in my music library.

#### Acceptance Criteria

1. WHEN the MP3 file is detected, THE Metadata_Tagger SHALL read the current file metadata
2. WHEN applying metadata, THE Metadata_Tagger SHALL set the Artist tag from user input
3. WHEN applying metadata, THE Metadata_Tagger SHALL set the Title tag from user input
4. WHEN applying metadata, THE Metadata_Tagger SHALL set the Album tag from user input
5. WHEN applying metadata, THE Metadata_Tagger SHALL set the Track Number tag from user input
6. WHEN metadata is applied, THE Metadata_Tagger SHALL save the changes to the MP3 file
7. THE Metadata_Tagger SHALL preserve existing metadata not specified by the user

### Requirement 5: Error Handling

**User Story:** As a user, I want to receive clear feedback when errors occur, so that I can understand what went wrong and take appropriate action.

#### Acceptance Criteria

1. WHEN an invalid YouTube URL is entered, THE Application SHALL display an error message and prevent submission
2. WHEN the browser fails to load the conversion website, THE Application SHALL display a connection error message
3. WHEN required page elements are not found, THE Browser_Controller SHALL report element location errors
4. WHEN the download fails or times out, THE Application SHALL notify the user of the download failure
5. WHEN metadata application fails, THE Metadata_Tagger SHALL report the specific error and leave the original file unchanged
6. THE Application SHALL provide clear, actionable error messages for all failure scenarios

### Requirement 6: User Feedback

**User Story:** As a user, I want to see the progress of the download and metadata application process, so that I know the application is working and when it's complete.

#### Acceptance Criteria

1. WHEN the process starts, THE GUI SHALL display a progress indicator
2. WHEN each major step completes, THE GUI SHALL update the progress status
3. WHEN the browser automation is running, THE GUI SHALL show "Processing download..." status
4. WHEN monitoring for download, THE GUI SHALL show "Waiting for download..." status
5. WHEN applying metadata, THE GUI SHALL show "Adding metadata..." status
6. WHEN the process completes successfully, THE GUI SHALL display a success message with the final file location