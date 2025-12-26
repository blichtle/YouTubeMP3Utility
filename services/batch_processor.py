"""
Batch processing service for handling multiple downloads from spreadsheet files.

This module provides functionality to load spreadsheet files (CSV, Excel) and
process multiple YouTube downloads automatically.
"""

import pandas as pd
import os
import logging
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path

from ..models.data_models import UserInput
from ..exceptions import InputValidationError, YouTubeDownloaderError


class BatchProcessor:
    """
    Service for processing batch downloads from spreadsheet files.
    
    Supports CSV and Excel files with columns: YouTubeURL, Artist, Title, Album, TrackNumber
    """
    
    def __init__(self):
        """Initialize the batch processor."""
        self.logger = logging.getLogger(__name__)
        self.current_batch = None
        self.current_row_index = 0
        self.total_rows = 0
        self.progress_callback = None
        self.download_callback = None
        
    def load_spreadsheet(self, file_path: str) -> bool:
        """
        Load a spreadsheet file and validate its structure.
        
        Args:
            file_path: Path to the CSV or Excel file
            
        Returns:
            bool: True if loaded successfully, False otherwise
            
        Raises:
            YouTubeDownloaderError: If file cannot be loaded or has invalid structure
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise YouTubeDownloaderError(f"File not found: {file_path}")
            
            # Determine file type and load accordingly
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise YouTubeDownloaderError(f"Unsupported file format: {file_extension}. Please use CSV or Excel files.")
            
            # Validate and normalize column names
            df = self._validate_and_normalize_columns(df)
            
            # Remove empty rows
            df = df.dropna(subset=['youtubeurl']).reset_index(drop=True)
            
            if len(df) == 0:
                raise YouTubeDownloaderError("No valid rows found in the spreadsheet.")
            
            # Store the batch data
            self.current_batch = df
            self.current_row_index = 0
            self.total_rows = len(df)
            
            self.logger.info(f"Successfully loaded {self.total_rows} rows from {file_path}")
            return True
            
        except pd.errors.EmptyDataError:
            raise YouTubeDownloaderError("The spreadsheet file is empty.")
        except pd.errors.ParserError as e:
            raise YouTubeDownloaderError(f"Error parsing spreadsheet file: {str(e)}")
        except Exception as e:
            raise YouTubeDownloaderError(f"Error loading spreadsheet: {str(e)}")
    
    def _validate_and_normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and normalize column names to match expected format.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with normalized column names
            
        Raises:
            YouTubeDownloaderError: If required columns are missing
        """
        # Expected columns (case insensitive)
        required_columns = {
            'youtubeurl': ['youtubeurl', 'youtube_url', 'youtube url', 'url'],
            'artist': ['artist'],
            'title': ['title'],
            'album': ['album'],
            'tracknumber': ['tracknumber', 'track_number', 'track number', 'track']
        }
        
        # Normalize column names to lowercase and remove spaces/underscores
        df.columns = df.columns.str.lower().str.replace(' ', '').str.replace('_', '')
        
        # Create mapping of found columns
        column_mapping = {}
        for standard_name, variations in required_columns.items():
            found = False
            for variation in variations:
                normalized_variation = variation.lower().replace(' ', '').replace('_', '')
                if normalized_variation in df.columns:
                    column_mapping[normalized_variation] = standard_name
                    found = True
                    break
            
            if not found:
                raise YouTubeDownloaderError(f"Required column '{standard_name}' not found. Expected one of: {', '.join(variations)}")
        
        # Rename columns to standard names
        df = df.rename(columns=column_mapping)
        
        # Select only the required columns
        df = df[list(required_columns.keys())]
        
        return df
    
    def get_current_row_data(self) -> Optional[UserInput]:
        """
        Get the current row data as a UserInput object.
        
        Returns:
            Optional[UserInput]: UserInput object for current row, None if no more rows
        """
        if not self.has_more_rows():
            return None
        
        try:
            row = self.current_batch.iloc[self.current_row_index]
            
            # Convert track number to integer, default to 1 if invalid
            try:
                track_number = int(float(row['tracknumber'])) if pd.notna(row['tracknumber']) else 1
            except (ValueError, TypeError):
                track_number = 1
            
            # Create UserInput object
            user_input = UserInput(
                youtube_url=str(row['youtubeurl']).strip(),
                artist=str(row['artist']).strip() if pd.notna(row['artist']) else "",
                title=str(row['title']).strip() if pd.notna(row['title']) else "",
                album=str(row['album']).strip() if pd.notna(row['album']) else "",
                track_number=track_number
            )
            
            return user_input
            
        except Exception as e:
            self.logger.error(f"Error processing row {self.current_row_index + 1}: {str(e)}")
            return None
    
    def advance_to_next_row(self) -> bool:
        """
        Advance to the next row in the batch.
        
        Returns:
            bool: True if advanced successfully, False if no more rows
        """
        if self.has_more_rows():
            self.current_row_index += 1
            return True
        return False
    
    def has_more_rows(self) -> bool:
        """
        Check if there are more rows to process.
        
        Returns:
            bool: True if there are more rows, False otherwise
        """
        return (self.current_batch is not None and 
                self.current_row_index < self.total_rows)
    
    def get_progress_info(self) -> Dict[str, Any]:
        """
        Get current progress information.
        
        Returns:
            Dict[str, Any]: Progress information including current row, total rows, percentage
        """
        if self.current_batch is None:
            return {
                'current_row': 0,
                'total_rows': 0,
                'percentage': 0,
                'is_active': False
            }
        
        percentage = (self.current_row_index / self.total_rows * 100) if self.total_rows > 0 else 0
        
        return {
            'current_row': self.current_row_index + 1,  # 1-based for display
            'total_rows': self.total_rows,
            'percentage': percentage,
            'is_active': True
        }
    
    def reset_batch(self) -> None:
        """Reset the batch processor to initial state."""
        self.current_batch = None
        self.current_row_index = 0
        self.total_rows = 0
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set a callback function to be called when progress updates.
        
        Args:
            callback: Function to call with progress information
        """
        self.progress_callback = callback
    
    def set_download_callback(self, callback: Callable[[UserInput], None]) -> None:
        """
        Set a callback function to be called for each download.
        
        Args:
            callback: Function to call to initiate download
        """
        self.download_callback = callback
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded batch.
        
        Returns:
            Dict[str, Any]: Summary information about the batch
        """
        if self.current_batch is None:
            return {'loaded': False}
        
        # Get sample of first few rows for preview
        preview_rows = []
        for i in range(min(3, len(self.current_batch))):
            row = self.current_batch.iloc[i]
            preview_rows.append({
                'youtube_url': str(row['youtubeurl'])[:50] + '...' if len(str(row['youtubeurl'])) > 50 else str(row['youtubeurl']),
                'artist': str(row['artist']) if pd.notna(row['artist']) else '',
                'title': str(row['title']) if pd.notna(row['title']) else '',
                'album': str(row['album']) if pd.notna(row['album']) else '',
                'track_number': row['tracknumber'] if pd.notna(row['tracknumber']) else 1
            })
        
        return {
            'loaded': True,
            'total_rows': self.total_rows,
            'preview_rows': preview_rows,
            'columns_found': list(self.current_batch.columns)
        }