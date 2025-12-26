# Implementation Plan: YouTube MP3 Downloader

## Overview

This implementation plan breaks down the YouTube MP3 Downloader into discrete coding tasks that build incrementally. The approach follows the modular architecture defined in the design, implementing core functionality first, then adding browser automation, file monitoring, and metadata processing capabilities.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure for modular components
  - Set up requirements.txt with selenium, mutagen, hypothesis, pytest
  - Create main entry point and basic project configuration
  - _Requirements: All requirements (foundational setup)_

- [x] 2. Implement core data models and validation
  - [x] 2.1 Create UserInput, DownloadResult, and MetadataInfo data classes
    - Write Python dataclasses with proper type hints
    - Implement validation methods for each model
    - _Requirements: 1.2, 1.4_

  - [ ]* 2.2 Write property test for URL validation
    - **Property 1: YouTube URL Validation**
    - **Validates: Requirements 1.2**

  - [ ]* 2.3 Write property test for track number validation
    - **Property 3: Track Number Validation**
    - **Validates: Requirements 1.4**

- [x] 3. Build GUI controller with Tkinter
  - [x] 3.1 Create main GUI window with input form
    - Implement Tkinter form with 5 input fields and submit button
    - Add input validation and error display capabilities
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 3.2 Implement progress tracking and status display
    - Add progress bar and status label components
    - Create methods for updating progress and showing messages
    - _Requirements: 6.1, 6.2, 6.6_

  - [ ]* 3.3 Write property test for text input acceptance
    - **Property 2: Text Input Acceptance**
    - **Validates: Requirements 1.3**

  - [ ]* 3.4 Write unit tests for GUI components
    - Test form creation, input validation, and error display
    - Test progress tracking and status updates
    - _Requirements: 1.1, 1.5, 6.1, 6.2, 6.6_

- [x] 4. Checkpoint - Ensure GUI tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement browser automation service
  - [x] 5.1 Create browser service with Selenium WebDriver
    - Implement Chrome WebDriver initialization and cleanup
    - Add methods for navigation and element interaction
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7_

  - [x] 5.2 Add timing and wait functionality
    - Implement explicit waits and 5-second delay mechanism
    - Add robust element location with timeout handling
    - _Requirements: 2.6_

  - [ ]* 5.3 Write property test for browser navigation sequence
    - **Property 4: Browser Navigation Sequence**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.7**

  - [ ]* 5.4 Write property test for timing consistency
    - **Property 5: Timing Consistency**
    - **Validates: Requirements 2.6**

- [x] 6. Build download monitoring service
  - [x] 6.1 Implement file system watcher for Downloads folder
    - Create monitor that detects new MP3 files in macOS Downloads
    - Add file completion verification and concurrent download handling
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 6.2 Write property test for file detection
    - **Property 6: File Detection**
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 6.3 Write property test for download completion verification
    - **Property 7: Download Completion Verification**
    - **Validates: Requirements 3.3**

  - [ ]* 6.4 Write property test for concurrent download handling
    - **Property 8: Concurrent Download Handling**
    - **Validates: Requirements 3.4**

- [x] 7. Create metadata service with mutagen
  - [x] 7.1 Implement MP3 metadata reading and writing
    - Use mutagen library to read existing metadata
    - Create methods to apply Artist, Title, Album, Track Number tags
    - Ensure preservation of existing metadata not specified by user
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 7.2 Write property test for metadata application
    - **Property 9: Metadata Application**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7**

- [x] 8. Implement comprehensive error handling
  - [x] 8.1 Add error handling for input validation and browser automation
    - Implement error detection and user notification for invalid inputs
    - Add network error handling and element location error reporting
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 8.2 Add error handling for download and metadata operations
    - Implement download failure detection and metadata error handling
    - Ensure file integrity preservation on metadata failures
    - _Requirements: 5.4, 5.5_

  - [ ]* 8.3 Write property tests for error handling scenarios
    - **Property 10: Invalid Input Error Handling**
    - **Property 11: Network Error Handling**
    - **Property 12: Element Location Error Handling**
    - **Property 13: Download Failure Handling**
    - **Property 14: Metadata Error Handling**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [-] 9. Build main application controller
  - [x] 9.1 Create orchestration controller that coordinates all services
    - Implement main workflow that connects GUI, browser, monitor, and metadata services
    - Add centralized error handling and resource cleanup
    - _Requirements: All requirements (orchestration)_

  - [ ]* 9.2 Write property test for progress tracking
    - **Property 15: Progress Tracking**
    - **Validates: Requirements 6.1, 6.2, 6.6**

- [-] 10. Integration and end-to-end testing
  - [x] 10.1 Wire all components together in main application
    - Connect GUI controller to main controller
    - Ensure proper service initialization and cleanup
    - _Requirements: All requirements_

  - [ ]* 10.2 Write integration tests for complete workflow
    - Test end-to-end download and metadata application process
    - Test error scenarios and recovery mechanisms
    - _Requirements: All requirements_

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement batch processing functionality
  - [x] 12.1 Create batch processor service for spreadsheet handling
    - Implement CSV and Excel file loading with pandas
    - Add case-insensitive column matching and validation
    - Create row iteration and progress tracking functionality
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 12.2 Integrate batch processing into GUI
    - Add "Load Spreadsheet" button and batch processing section
    - Implement batch progress bar and status display
    - Add confirmation dialog with data preview
    - _Requirements: 7.1, 7.9, 7.10_

  - [x] 12.3 Implement automatic batch workflow
    - Create threaded batch processing to avoid GUI blocking
    - Implement automatic form population and download triggering
    - Add proper coordination between batch processor and main controller
    - _Requirements: 7.4, 7.5, 7.6, 7.7, 7.13_

  - [x] 12.4 Add batch processing state management
    - Implement clear fields integration with batch reset
    - Add error handling for invalid rows and processing failures
    - Create completion notification and state cleanup
    - _Requirements: 7.8, 7.11, 7.12_

  - [x] 12.5 Write comprehensive batch processing tests
    - Create unit tests for batch processor service
    - Implement complete workflow integration tests
    - Add sample CSV file for testing
    - _Requirements: 7.1-7.13_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using hypothesis library
- Unit tests validate specific examples and edge cases
- Browser automation requires ChromeDriver installation
- File monitoring is macOS-specific (Downloads folder path)
- Metadata operations require valid MP3 files for testing