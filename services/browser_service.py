"""
Browser automation service for YouTube MP3 Downloader.

This module provides browser automation capabilities using Selenium WebDriver
to interact with the MP3 conversion website.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    WebDriverException, 
    TimeoutException, 
    NoSuchElementException,
    ElementNotInteractableException,
    SessionNotCreatedException,
    InvalidSessionIdException
)
import time
import logging
from typing import Optional, Tuple, Any
from selenium.webdriver.remote.webelement import WebElement

from ..exceptions import NetworkError, ElementLocationError, BrowserError
from ..services.error_handler import ErrorHandler


class BrowserService:
    """
    Service for automating browser interactions with the MP3 conversion website.
    
    Handles Chrome WebDriver initialization, navigation, element interaction,
    and cleanup operations.
    """
    
    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        Initialize the browser service.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Default timeout for element waits in seconds
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.conversion_wait_time = 5  # 5-second wait as per requirement 2.6
        
        # Initialize error handler
        self.error_handler = ErrorHandler()
        
    def open_browser(self) -> bool:
        """
        Initialize Chrome WebDriver with appropriate options.
        Enhanced with comprehensive error handling (Requirements 5.2, 5.3).
        
        Returns:
            bool: True if browser opened successfully, False otherwise
            
        Raises:
            BrowserError: If browser initialization fails
            
        Validates: Requirements 2.1
        """
        try:
            # Configure Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Add common options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Initialize the WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(self.timeout)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except SessionNotCreatedException as e:
            error_msg = "Failed to create browser session. Chrome or ChromeDriver may not be properly installed."
            self.error_handler.handle_browser_error(error_msg, "browser_initialization")
            raise BrowserError(error_msg) from e
            
        except WebDriverException as e:
            if "chromedriver" in str(e).lower():
                error_msg = "ChromeDriver not found. Please ensure ChromeDriver is installed and in your PATH."
            elif "chrome" in str(e).lower():
                error_msg = "Google Chrome browser not found. Please install Google Chrome."
            else:
                error_msg = f"Browser initialization failed: {str(e)}"
            
            self.error_handler.handle_browser_error(error_msg, "browser_initialization")
            raise BrowserError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error opening browser: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "browser_initialization")
            raise BrowserError(error_msg) from e
    
    def navigate_to_converter(self) -> bool:
        """
        Navigate to the MP3 conversion website.
        Enhanced with network error handling (Requirement 5.2).
        
        Returns:
            bool: True if navigation successful, False otherwise
            
        Raises:
            BrowserError: If browser is not initialized
            NetworkError: If navigation fails due to network issues
            
        Validates: Requirements 2.2
        """
        if not self.driver:
            error_msg = "Browser not initialized. Call open_browser() first."
            self.error_handler.handle_browser_error(error_msg, "navigation")
            raise BrowserError(error_msg)
            
        try:
            self.driver.get("https://mp3cow.com/")
            
            # Wait for page to fully load with timeout
            if not self.wait_for_page_load(timeout=15):
                self.logger.warning("Page may not have loaded completely, but continuing...")
            
            self.logger.info("Successfully navigated to mp3cow.com")
            return True
            
        except TimeoutException as e:
            error_msg = "Network timeout while loading the conversion website."
            self.error_handler.handle_network_error(error_msg, "https://mp3cow.com/", "page_navigation")
            raise NetworkError(error_msg, "https://mp3cow.com/") from e
            
        except WebDriverException as e:
            if "net::" in str(e) or "ERR_" in str(e):
                error_msg = "Network error: Unable to connect to the conversion website. Please check your internet connection."
                self.error_handler.handle_network_error(error_msg, "https://mp3cow.com/", "page_navigation")
                raise NetworkError(error_msg, "https://mp3cow.com/") from e
            else:
                error_msg = f"Browser error during navigation: {str(e)}"
                self.error_handler.handle_browser_error(error_msg, "navigation")
                raise BrowserError(error_msg) from e
                
        except Exception as e:
            error_msg = f"Unexpected error during navigation: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "navigation")
            raise BrowserError(error_msg) from e
    
    def input_youtube_url(self, url: str) -> bool:
        """
        Locate the URL input field and paste the YouTube URL.
        Enhanced with element location error handling (Requirement 5.3).
        
        Args:
            url: The YouTube URL to input
            
        Returns:
            bool: True if URL input successful, False otherwise
            
        Raises:
            BrowserError: If browser is not initialized
            ElementLocationError: If URL input field cannot be found
            
        Validates: Requirements 2.3, 2.4
        """
        if not self.driver:
            error_msg = "Browser not initialized. Call open_browser() first."
            self.error_handler.handle_browser_error(error_msg, "url_input")
            raise BrowserError(error_msg)
            
        try:
            # Use enhanced element waiting with custom timeout
            url_input = self.wait_for_element(By.ID, "url", timeout=15)
            if not url_input:
                error_msg = "URL input field with ID 'url'"
                self.error_handler.handle_element_location_error(error_msg, "ID: url", "url_input")
                raise ElementLocationError(error_msg, "ID: url")
            
            # Clear any existing content and input the URL
            url_input.clear()
            url_input.send_keys(url)
            
            self.logger.info(f"Successfully input YouTube URL: {url}")
            return True
            
        except ElementLocationError:
            # Re-raise element location errors
            raise
            
        except ElementNotInteractableException as e:
            error_msg = "URL input field is not interactable (may be hidden or disabled)"
            self.error_handler.handle_element_location_error(error_msg, "ID: url", "url_input")
            raise ElementLocationError(error_msg, "ID: url") from e
            
        except Exception as e:
            error_msg = f"Unexpected error inputting URL: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "url_input")
            raise BrowserError(error_msg) from e
    
    def click_convert_button(self) -> bool:
        """
        Click the conversion button to start the MP3 conversion process.
        Enhanced with element location error handling (Requirement 5.3).
        
        Returns:
            bool: True if button click successful, False otherwise
            
        Raises:
            BrowserError: If browser is not initialized
            ElementLocationError: If convert button cannot be found
            
        Validates: Requirements 2.5
        """
        if not self.driver:
            error_msg = "Browser not initialized. Call open_browser() first."
            self.error_handler.handle_browser_error(error_msg, "convert_button")
            raise BrowserError(error_msg)
            
        try:
            # Use enhanced element waiting
            convert_button = self.wait_for_element(By.ID, "bco")
            if not convert_button:
                error_msg = "convert button with ID 'bco'"
                self.error_handler.handle_element_location_error(error_msg, "ID: bco", "convert_button")
                raise ElementLocationError(error_msg, "ID: bco")
            
            # Click the convert button
            convert_button.click()
            
            self.logger.info("Successfully clicked convert button")
            return True
            
        except ElementLocationError:
            # Re-raise element location errors
            raise
            
        except ElementNotInteractableException as e:
            error_msg = "convert button is not interactable (may be disabled or hidden)"
            self.error_handler.handle_element_location_error(error_msg, "ID: bco", "convert_button")
            raise ElementLocationError(error_msg, "ID: bco") from e
            
        except Exception as e:
            error_msg = f"Unexpected error clicking convert button: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "convert_button")
            raise BrowserError(error_msg) from e
    
    def wait_and_download(self) -> bool:
        """
        Wait for conversion to complete and click the download button.
        Enhanced with element location error handling (Requirement 5.3).
        
        Returns:
            bool: True if download initiated successfully, False otherwise
            
        Raises:
            BrowserError: If browser is not initialized
            ElementLocationError: If download button cannot be found
            
        Validates: Requirements 2.7, 2.6
        """
        if not self.driver:
            error_msg = "Browser not initialized. Call open_browser() first."
            self.error_handler.handle_browser_error(error_msg, "download_button")
            raise BrowserError(error_msg)
            
        try:
            # Wait exactly 5 seconds for conversion to process (as per requirement 2.6)
            self.logger.info(f"Waiting {self.conversion_wait_time} seconds for conversion to complete...")
            time.sleep(self.conversion_wait_time)
            
            # Use robust element location with multiple strategies
            download_button = self._find_download_button()
            if not download_button:
                error_msg = "download button with text 'Download MP3'"
                self.error_handler.handle_element_location_error(error_msg, "Multiple strategies", "download_button")
                raise ElementLocationError(error_msg, "Multiple strategies")
            
            # Click the download button
            download_button.click()
            
            self.logger.info("Successfully clicked download button")
            return True
            
        except ElementLocationError:
            # Re-raise element location errors
            raise
            
        except ElementNotInteractableException as e:
            error_msg = "download button is not interactable (may be disabled or hidden)"
            self.error_handler.handle_element_location_error(error_msg, "Download button", "download_button")
            raise ElementLocationError(error_msg, "Download button") from e
            
        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "download_button")
            raise BrowserError(error_msg) from e
    
    def _find_download_button(self) -> Optional[WebElement]:
        """
        Robust element location for download button with multiple strategies.
        
        Returns:
            Optional[WebElement]: Download button element if found, None otherwise
        """
        strategies = [
            # Primary strategy: exact text match
            (By.XPATH, "//button[contains(text(), 'Download MP3')]"),
            # Fallback strategy: case-insensitive text match
            (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download mp3')]"),
            # Alternative strategy: look for download-related attributes
            (By.XPATH, "//button[contains(@class, 'download') or contains(@id, 'download')]"),
            # Broad strategy: any button with download in text or attributes
            (By.XPATH, "//*[contains(text(), 'Download') or contains(@class, 'download') or contains(@id, 'download')]")
        ]
        
        for by, locator in strategies:
            try:
                wait = WebDriverWait(self.driver, self.timeout)
                element = wait.until(EC.element_to_be_clickable((by, locator)))
                self.logger.info(f"Found download button using strategy: {locator}")
                return element
            except TimeoutException:
                self.logger.debug(f"Strategy failed: {locator}")
                continue
            except Exception as e:
                self.logger.debug(f"Strategy error: {locator} - {e}")
                continue
        
        self.logger.error("All strategies failed to locate download button")
        return None
    
    def wait_for_element(self, by: By, locator: str, timeout: Optional[int] = None) -> Optional[WebElement]:
        """
        Wait for an element to be present and interactable with custom timeout.
        Enhanced with detailed error reporting (Requirement 5.3).
        
        Args:
            by: Selenium By locator type
            locator: Element locator string
            timeout: Custom timeout in seconds (uses default if None)
            
        Returns:
            Optional[WebElement]: Element if found, None otherwise
            
        Raises:
            BrowserError: If browser is not initialized
            ElementLocationError: If element cannot be found within timeout
        """
        if not self.driver:
            error_msg = "Browser not initialized. Call open_browser() first."
            self.error_handler.handle_browser_error(error_msg, "element_wait")
            raise BrowserError(error_msg)
            
        wait_time = timeout if timeout is not None else self.timeout
        
        try:
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.element_to_be_clickable((by, locator)))
            return element
            
        except TimeoutException as e:
            error_msg = f"element with locator '{locator}'"
            self.error_handler.handle_element_location_error(error_msg, f"{by}: {locator}", "element_wait")
            return None  # Return None instead of raising to allow fallback strategies
            
        except InvalidSessionIdException as e:
            error_msg = "Browser session is invalid or has been closed"
            self.error_handler.handle_browser_error(error_msg, "element_wait")
            raise BrowserError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Error waiting for element {locator}: {str(e)}"
            self.error_handler.handle_browser_error(error_msg, "element_wait")
            return None
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for page to fully load by checking document ready state.
        
        Args:
            timeout: Custom timeout in seconds (uses default if None)
            
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        if not self.driver:
            self.logger.error("Browser not initialized. Call open_browser() first.")
            return False
            
        wait_time = timeout if timeout is not None else self.timeout
        
        try:
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info("Page loaded successfully")
            return True
        except TimeoutException:
            self.logger.error("Timeout waiting for page to load")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")
            return False
    
    def retry_operation(self, operation_func, max_retries: int = 3, delay: float = 1.0) -> Tuple[bool, Any]:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation_func: Function to retry (should return bool for success)
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            
        Returns:
            Tuple[bool, Any]: (success, result) where result is the operation return value
        """
        for attempt in range(max_retries + 1):
            try:
                result = operation_func()
                if result:  # Assuming operation returns True for success
                    return True, result
                    
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    self.logger.info(f"Operation failed, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.logger.error(f"Operation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    return False, None
        
        self.logger.error(f"Operation failed after {max_retries + 1} attempts")
        return False, None
    
    def close_browser(self) -> bool:
        """
        Clean up browser resources and close the WebDriver.
        
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.logger.info("Browser closed successfully")
                return True
            else:
                self.logger.warning("No browser instance to close")
                return True
                
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
            return False
    
    def is_browser_open(self) -> bool:
        """
        Check if the browser is currently open and responsive.
        
        Returns:
            bool: True if browser is open and responsive, False otherwise
        """
        if not self.driver:
            return False
            
        try:
            # Try to get the current URL to test if browser is responsive
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def get_current_url(self) -> Optional[str]:
        """
        Get the current URL of the browser.
        
        Returns:
            Optional[str]: Current URL if browser is open, None otherwise
        """
        if not self.driver:
            return None
            
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        self.open_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close_browser()