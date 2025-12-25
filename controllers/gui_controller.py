"""
GUI Controller for the YouTube MP3 Downloader application.

This module provides the main GUI interface using Tkinter, handling user input,
validation, progress tracking, and status display.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
import re
import os

from ..models.data_models import UserInput, MetadataInfo
from ..exceptions import InputValidationError, MetadataError
from ..services.error_handler import ErrorHandler
from ..services.metadata_service import MetadataService


class GUIController:
    """
    Main GUI controller that manages the Tkinter interface for user input
    and progress tracking.
    """
    
    def __init__(self, on_submit_callback: Optional[Callable[[UserInput], None]] = None):
        """
        Initialize the GUI controller.
        
        Args:
            on_submit_callback: Callback function to handle form submission
        """
        self.on_submit_callback = on_submit_callback
        self.root = None
        self.input_fields = {}
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        self.submit_button = None
        self.clear_button = None
        self.load_mp3_button = None
        self.save_changes_button = None
        self.file_path_label = None
        self.current_mp3_file = None
        
        # Initialize services
        self.metadata_service = MetadataService()
        
        # Initialize error handler with GUI callback
        self.error_handler = ErrorHandler(gui_error_callback=self.show_error)
        
    def create_input_form(self) -> tk.Tk:
        """
        Creates the main GUI window with input form.
        
        Returns:
            tk.Tk: The main window root object
        """
        # Create main window
        self.root = tk.Tk()
        self.root.title("YouTube MP3 Downloader")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title label
        title_label = ttk.Label(main_frame, text="YouTube MP3 Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # MP3 file loading section
        self._create_mp3_loading_section(main_frame)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # Create input fields
        self._create_input_fields(main_frame)
        
        # Create button frame for submit and clear buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=(20, 10), 
                         sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Create submit button
        self.submit_button = ttk.Button(button_frame, text="Download & Tag MP3", 
                                       command=self._on_submit_clicked)
        self.submit_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # Create clear button
        self.clear_button = ttk.Button(button_frame, text="Clear All Fields", 
                                      command=self._on_clear_clicked)
        self.clear_button.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Create save changes button (initially hidden)
        self.save_changes_button = ttk.Button(button_frame, text="Save Changes to MP3", 
                                            command=self._on_save_changes_clicked)
        # Don't grid it initially - will be shown when MP3 is loaded
        
        # Create progress tracking components
        self._create_progress_components(main_frame)
        
        return self.root
    
    def _create_mp3_loading_section(self, parent_frame: ttk.Frame) -> None:
        """
        Creates the MP3 file loading section.
        
        Args:
            parent_frame: The parent frame to add components to
        """
        # MP3 loading frame
        mp3_frame = ttk.LabelFrame(parent_frame, text="Edit Existing MP3", padding="10")
        mp3_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        mp3_frame.columnconfigure(1, weight=1)
        
        # Load MP3 button
        self.load_mp3_button = ttk.Button(mp3_frame, text="Load MP3 File", 
                                         command=self._on_load_mp3_clicked)
        self.load_mp3_button.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        # File path label
        self.file_path_label = ttk.Label(mp3_frame, text="No file selected", 
                                        foreground="gray", font=("Arial", 9))
        self.file_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Instructions label
        instructions = ttk.Label(mp3_frame, 
                               text="Load an existing MP3 file to edit its metadata, or fill the form below to download from YouTube",
                               font=("Arial", 8), foreground="gray")
        instructions.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)
    
    def _create_input_fields(self, parent_frame: ttk.Frame) -> None:
        """
        Creates the input fields for the form.
        
        Args:
            parent_frame: The parent frame to add fields to
        """
        # YouTube URL field
        ttk.Label(parent_frame, text="YouTube URL:").grid(row=4, column=0, 
                                                          sticky=tk.W, pady=5)
        self.input_fields['youtube_url'] = ttk.Entry(parent_frame, width=50)
        self.input_fields['youtube_url'].grid(row=4, column=1, sticky=(tk.W, tk.E), 
                                             pady=5, padx=(10, 0))
        
        # Artist field
        ttk.Label(parent_frame, text="Artist:").grid(row=5, column=0, 
                                                    sticky=tk.W, pady=5)
        self.input_fields['artist'] = ttk.Entry(parent_frame, width=50)
        self.input_fields['artist'].grid(row=5, column=1, sticky=(tk.W, tk.E), 
                                        pady=5, padx=(10, 0))
        
        # Title field
        ttk.Label(parent_frame, text="Title:").grid(row=6, column=0, 
                                                   sticky=tk.W, pady=5)
        self.input_fields['title'] = ttk.Entry(parent_frame, width=50)
        self.input_fields['title'].grid(row=6, column=1, sticky=(tk.W, tk.E), 
                                       pady=5, padx=(10, 0))
        
        # Album field
        ttk.Label(parent_frame, text="Album:").grid(row=7, column=0, 
                                                   sticky=tk.W, pady=5)
        self.input_fields['album'] = ttk.Entry(parent_frame, width=50)
        self.input_fields['album'].grid(row=7, column=1, sticky=(tk.W, tk.E), 
                                       pady=5, padx=(10, 0))
        
        # Track Number field
        ttk.Label(parent_frame, text="Track Number:").grid(row=8, column=0, 
                                                          sticky=tk.W, pady=5)
        self.input_fields['track_number'] = ttk.Entry(parent_frame, width=50)
        self.input_fields['track_number'].grid(row=8, column=1, sticky=(tk.W, tk.E), 
                                              pady=5, padx=(10, 0))
    
    def _create_progress_components(self, parent_frame: ttk.Frame) -> None:
        """
        Creates the progress bar and status label components.
        
        Args:
            parent_frame: The parent frame to add components to
        """
        # Progress bar (Requirements 6.1, 6.2)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.grid(row=10, column=0, columnspan=2, pady=(10, 5), 
                              sticky=(tk.W, tk.E))
        
        # Status label (Requirements 6.2, 6.6)
        self.status_label = ttk.Label(parent_frame, text="Ready to download", 
                                     font=("Arial", 10))
        self.status_label.grid(row=11, column=0, columnspan=2, pady=(5, 0))
        
        # Initially hide progress components
        self.progress_bar.grid_remove()
        self.status_label.grid_remove()
    
    def validate_youtube_url(self, url: str) -> bool:
        """
        Validates if the provided URL is a valid YouTube URL format.
        
        Args:
            url: The URL string to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # YouTube URL patterns (Requirements 1.2)
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(www\.)?youtu\.be/[\w-]+',
            r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(www\.)?youtube\.com/v/[\w-]+'
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)
    
    def validate_track_number(self, track_num_str: str) -> bool:
        """
        Validates if the track number string represents a positive integer.
        
        Args:
            track_num_str: The track number string to validate
            
        Returns:
            bool: True if valid positive integer, False otherwise
        """
        try:
            track_num = int(track_num_str.strip())
            return track_num > 0
        except (ValueError, AttributeError):
            return False
    
    def _validate_form_input(self) -> tuple[bool, UserInput, list[str]]:
        """
        Validates all form input and creates UserInput object.
        Enhanced with comprehensive error handling (Requirement 5.1).
        
        Returns:
            tuple: (is_valid, user_input_object, error_messages)
        """
        errors = []
        
        # Get values from form
        youtube_url = self.input_fields['youtube_url'].get().strip()
        artist = self.input_fields['artist'].get().strip()
        title = self.input_fields['title'].get().strip()
        album = self.input_fields['album'].get().strip()
        track_number_str = self.input_fields['track_number'].get().strip()
        
        # Validate YouTube URL (Requirements 1.2, 5.1)
        if not youtube_url:
            error_msg = "YouTube URL is required."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("youtube_url", error_msg)
        elif not self.validate_youtube_url(youtube_url):
            error_msg = "Invalid YouTube URL format. Please enter a valid YouTube URL (youtube.com or youtu.be)."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("youtube_url", error_msg)
        
        # Validate text fields are not empty (Requirements 1.3, 5.1)
        if not artist:
            error_msg = "Artist field cannot be empty."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("artist", error_msg)
        elif len(artist) > 100:
            error_msg = "Artist name is too long (maximum 100 characters)."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("artist", error_msg)
        
        if not title:
            error_msg = "Title field cannot be empty."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("title", error_msg)
        elif len(title) > 100:
            error_msg = "Title is too long (maximum 100 characters)."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("title", error_msg)
        
        if not album:
            error_msg = "Album field cannot be empty."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("album", error_msg)
        elif len(album) > 100:
            error_msg = "Album name is too long (maximum 100 characters)."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("album", error_msg)
        
        # Validate track number (Requirements 1.4, 5.1)
        track_number = 0
        if not track_number_str:
            error_msg = "Track number is required."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("track_number", error_msg)
        elif not self.validate_track_number(track_number_str):
            error_msg = "Track number must be a positive integer (1-999)."
            errors.append(error_msg)
            self.error_handler.handle_input_validation_error("track_number", error_msg)
        else:
            track_number = int(track_number_str)
            if track_number > 999:
                error_msg = "Track number must be between 1 and 999."
                errors.append(error_msg)
                self.error_handler.handle_input_validation_error("track_number", error_msg)
        
        # Create UserInput object if no errors
        user_input = None
        if not errors:
            try:
                user_input = UserInput(
                    youtube_url=youtube_url,
                    artist=artist,
                    title=title,
                    album=album,
                    track_number=track_number
                )
            except Exception as e:
                error_msg = f"Error creating user input: {str(e)}"
                errors.append(error_msg)
                self.error_handler.handle_error(e, "User input creation")
        
        return len(errors) == 0, user_input, errors
    
    def _on_submit_clicked(self) -> None:
        """
        Handles the submit button click event.
        """
        # Validate form input
        is_valid, user_input, errors = self._validate_form_input()
        
        if not is_valid:
            # Show validation errors (Requirements 5.1)
            self.show_error("\n".join(errors))
            return
        
        # Disable submit button during processing
        self.submit_button.config(state='disabled')
        if self.clear_button:
            self.clear_button.config(state='disabled')
        
        # Show initial progress (Requirements 6.1)
        self.update_progress("Starting download process...", 0)
        
        # Call the submit callback if provided
        if self.on_submit_callback and user_input:
            try:
                self.on_submit_callback(user_input)
            except Exception as e:
                self.show_error(f"An error occurred: {str(e)}")
                self.hide_progress()
                self.submit_button.config(state='normal')
                if self.clear_button:
                    self.clear_button.config(state='normal')
    
    def _on_clear_clicked(self) -> None:
        """
        Handles the clear button click event.
        Clears all input fields and resets the form for a new session.
        """
        # Clear all input fields
        self._clear_form_fields()
        
        # Hide progress components and reset progress
        self.hide_progress()
        
        # Switch back to download mode if in edit mode
        if self.current_mp3_file:
            self._switch_to_download_mode()
        
        # Re-enable submit button if it was disabled
        if self.submit_button:
            self.submit_button.config(state='normal')
        
        # Update status to ready state
        if self.status_label:
            self.status_label.config(text="Ready to download")
        
        # Focus on the first field (YouTube URL) for convenience
        if 'youtube_url' in self.input_fields:
            self.input_fields['youtube_url'].focus_set()
    
    def _on_load_mp3_clicked(self) -> None:
        """
        Handles the load MP3 button click event.
        Opens a file dialog to select an MP3 file and loads its metadata.
        """
        # Open file dialog to select MP3 file
        file_path = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Validate the selected file
            if not self.metadata_service.validate_mp3_file(file_path):
                self.show_error("The selected file is not a valid MP3 file.")
                return
            
            # Load metadata from the file
            metadata_summary = self.metadata_service.get_metadata_summary(file_path)
            
            # Clear existing form data
            self._clear_form_fields()
            
            # Populate form fields with loaded metadata
            if metadata_summary.get('artist'):
                self.input_fields['artist'].insert(0, metadata_summary['artist'])
            
            if metadata_summary.get('title'):
                self.input_fields['title'].insert(0, metadata_summary['title'])
            
            if metadata_summary.get('album'):
                self.input_fields['album'].insert(0, metadata_summary['album'])
            
            if metadata_summary.get('track_number'):
                # Extract just the number part if it's in "1/10" format
                track_num = metadata_summary['track_number'].split('/')[0]
                self.input_fields['track_number'].insert(0, track_num)
            
            # Store the current file path
            self.current_mp3_file = file_path
            
            # Update file path label
            filename = os.path.basename(file_path)
            self.file_path_label.config(text=f"Loaded: {filename}", foreground="green")
            
            # Show save changes button and hide download button
            self._switch_to_edit_mode()
            
            # Show success message
            duration = metadata_summary.get('duration', 'Unknown')
            size = metadata_summary.get('file_size', 'Unknown')
            messagebox.showinfo("MP3 Loaded", 
                              f"Successfully loaded MP3 file:\n\n"
                              f"File: {filename}\n"
                              f"Duration: {duration}\n"
                              f"Size: {size}\n\n"
                              f"You can now edit the metadata and save changes.")
            
        except MetadataError as e:
            self.show_error(f"Error loading MP3 file: {e.message}")
        except Exception as e:
            self.show_error(f"Unexpected error loading MP3 file: {str(e)}")
    
    def _on_save_changes_clicked(self) -> None:
        """
        Handles the save changes button click event.
        Saves the current form data as metadata to the loaded MP3 file.
        """
        if not self.current_mp3_file:
            self.show_error("No MP3 file is currently loaded.")
            return
        
        # Validate form input (excluding YouTube URL for edit mode)
        is_valid, metadata_info = self._validate_metadata_only()
        
        if not is_valid:
            return
        
        try:
            # Disable buttons during processing
            self.save_changes_button.config(state='disabled')
            if self.clear_button:
                self.clear_button.config(state='disabled')
            
            # Show progress
            self.update_progress("Saving metadata changes...", 50)
            
            # Apply metadata to the file
            success = self.metadata_service.apply_metadata(self.current_mp3_file, metadata_info)
            
            if success:
                self.update_progress("Metadata saved successfully!", 100)
                filename = os.path.basename(self.current_mp3_file)
                messagebox.showinfo("Success", 
                                  f"Metadata changes saved successfully to:\n{filename}")
                self.hide_progress()
            else:
                self.show_error("Failed to save metadata changes.")
                self.hide_progress()
            
        except MetadataError as e:
            self.show_error(f"Error saving metadata: {e.message}")
            self.hide_progress()
        except Exception as e:
            self.show_error(f"Unexpected error saving metadata: {str(e)}")
            self.hide_progress()
        finally:
            # Re-enable buttons
            self.save_changes_button.config(state='normal')
            if self.clear_button:
                self.clear_button.config(state='normal')
    
    def _clear_form_fields(self) -> None:
        """
        Clears all form fields without affecting the loaded file state.
        """
        for field_name, field_widget in self.input_fields.items():
            field_widget.delete(0, tk.END)
    
    def _switch_to_edit_mode(self) -> None:
        """
        Switches the interface to edit mode for loaded MP3 files.
        """
        # Hide download button and show save changes button
        self.submit_button.grid_remove()
        self.save_changes_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # Disable YouTube URL field since it's not needed for editing
        self.input_fields['youtube_url'].config(state='disabled')
        
        # Update button frame to accommodate save button
        button_frame = self.save_changes_button.master
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def _switch_to_download_mode(self) -> None:
        """
        Switches the interface back to download mode.
        """
        # Show download button and hide save changes button
        self.save_changes_button.grid_remove()
        self.submit_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # Re-enable YouTube URL field
        self.input_fields['youtube_url'].config(state='normal')
        
        # Clear current file
        self.current_mp3_file = None
        self.file_path_label.config(text="No file selected", foreground="gray")
    
    def _validate_metadata_only(self) -> tuple[bool, Optional[MetadataInfo]]:
        """
        Validates form input for metadata editing (without YouTube URL requirement).
        
        Returns:
            tuple: (is_valid, metadata_info_object)
        """
        errors = []
        
        # Get values from form (excluding YouTube URL)
        artist = self.input_fields['artist'].get().strip()
        title = self.input_fields['title'].get().strip()
        album = self.input_fields['album'].get().strip()
        track_number_str = self.input_fields['track_number'].get().strip()
        
        # Validate text fields are not empty
        if not artist:
            errors.append("Artist field cannot be empty.")
        elif len(artist) > 100:
            errors.append("Artist name is too long (maximum 100 characters).")
        
        if not title:
            errors.append("Title field cannot be empty.")
        elif len(title) > 100:
            errors.append("Title is too long (maximum 100 characters).")
        
        if not album:
            errors.append("Album field cannot be empty.")
        elif len(album) > 100:
            errors.append("Album name is too long (maximum 100 characters).")
        
        # Validate track number
        track_number = 0
        if not track_number_str:
            errors.append("Track number is required.")
        elif not self.validate_track_number(track_number_str):
            errors.append("Track number must be a positive integer (1-999).")
        else:
            track_number = int(track_number_str)
            if track_number > 999:
                errors.append("Track number must be between 1 and 999.")
        
        # Show errors if any
        if errors:
            self.show_error("\n".join(errors))
            return False, None
        
        # Create MetadataInfo object
        try:
            metadata_info = MetadataInfo(
                artist=artist,
                title=title,
                album=album,
                track_number=track_number,
                original_filename=os.path.basename(self.current_mp3_file) if self.current_mp3_file else "unknown.mp3"
            )
            return True, metadata_info
        except Exception as e:
            self.show_error(f"Error creating metadata: {str(e)}")
            return False, None
    
    def show_error(self, message: str) -> None:
        """
        Displays an error message to the user with enhanced formatting.
        
        Args:
            message: The error message to display
        """
        # Show error dialog with better formatting
        messagebox.showerror("Error", message)
        
        # Also update status label if available
        if self.status_label:
            self.status_label.config(text="Error occurred - see dialog for details")
    
    def show_detailed_error(self, title: str, message: str, details: str = None) -> None:
        """
        Show a detailed error message with optional technical details.
        
        Args:
            title: Error dialog title
            message: Main error message
            details: Optional technical details
        """
        if details:
            full_message = f"{message}\n\nTechnical Details:\n{details}"
        else:
            full_message = message
            
        messagebox.showerror(title, full_message)
    
    def update_progress(self, message: str, progress_percent: int = 0) -> None:
        """
        Updates the progress display with a message and progress percentage.
        
        Args:
            message: Status message to display
            progress_percent: Progress percentage (0-100)
        """
        # Show progress components if hidden (Requirements 6.1)
        self.progress_bar.grid()
        self.status_label.grid()
        
        # Update progress bar and status (Requirements 6.2)
        self.progress_var.set(progress_percent)
        self.status_label.config(text=message)
        
        # Force GUI update
        if self.root:
            self.root.update_idletasks()
    
    def show_processing_status(self) -> None:
        """
        Shows "Processing download..." status during browser automation.
        """
        self.update_progress("Processing download...", 25)
    
    def show_waiting_status(self) -> None:
        """
        Shows "Waiting for download..." status during download monitoring.
        """
        self.update_progress("Waiting for download...", 50)
    
    def show_metadata_status(self) -> None:
        """
        Shows "Adding metadata..." status during metadata application.
        """
        self.update_progress("Adding metadata...", 75)
    
    def hide_progress(self) -> None:
        """
        Hides the progress components.
        """
        self.progress_bar.grid_remove()
        self.status_label.grid_remove()
        self.progress_var.set(0)
    
    def show_success(self, file_path: str) -> None:
        """
        Shows a success message with the final file location.
        
        Args:
            file_path: Path to the successfully processed file
        """
        # Complete progress (Requirements 6.6)
        self.update_progress("Download and metadata tagging completed!", 100)
        
        # Show success dialog
        message = f"Download and metadata tagging completed successfully!\n\nFile saved to:\n{file_path}"
        messagebox.showinfo("Success", message)
        
        # Hide progress and re-enable buttons
        self.hide_progress()
        if self.current_mp3_file:
            # In edit mode
            self.save_changes_button.config(state='normal')
        else:
            # In download mode
            self.submit_button.config(state='normal')
        if self.clear_button:
            self.clear_button.config(state='normal')
    
    def run(self) -> None:
        """
        Starts the GUI main loop.
        """
        if self.root:
            self.root.mainloop()
    
    def destroy(self) -> None:
        """
        Destroys the GUI window and cleans up resources.
        """
        if self.root:
            self.root.destroy()
            self.root = None