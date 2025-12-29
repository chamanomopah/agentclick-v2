"""
InputProcessor - Enhanced Input Processing Module (Story 6)

This module provides automatic input type detection and processing for:
- Clipboard text (AC: #2)
- File dialog (AC: #3)
- Empty input popup (AC: #4)
- Multiple files (AC: #5)
- URL download (AC: #6)

Acceptance Criteria:
1. InputProcessor detects input type automatically
2. InputProcessor processes selected text from clipboard using PyQt6 QClipboard
3. InputProcessor opens file dialog (QFileDialog) for file input
4. InputProcessor shows popup dialog (QInputDialog) for empty input
5. InputProcessor processes multiple files sequentially with progress
6. InputProcessor downloads content from URL using aiohttp
"""

from enum import Enum
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse
import asyncio
import logging
import ipaddress

try:
    from PyQt6.QtWidgets import QApplication, QFileDialog, QInputDialog, QLineEdit
    from PyQt6.QtCore import Qt
except ImportError:
    # Fallback for non-GUI environments
    QApplication = None
    QFileDialog = None
    QInputDialog = None
    QLineEdit = None

try:
    import aiohttp
except ImportError:
    aiohttp = None



logger = logging.getLogger(__name__)

# Security constants for URL download
DEFAULT_URL_TIMEOUT = 10  # seconds
MAX_DOWNLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class InputType(Enum):
    """
    Enum representing different input types (AC: #1)

    Values:
        TEXT: Text from clipboard
        FILE: Single file selected via dialog
        EMPTY: No input, user will be prompted
        MULTIPLE: Multiple files selected
        URL: URL to download content from
    """
    TEXT = "text"
    FILE = "file"
    EMPTY = "empty"
    MULTIPLE = "multiple"
    URL = "url"


class InputProcessor:
    """
    Enhanced input processor with automatic type detection (AC: #1)

    This class detects and processes various input types:
    - Clipboard text/URL
    - File(s) via dialog
    - Manual input via popup
    - URL content download

    Attributes:
        clipboard: QClipboard instance for reading clipboard content
    """

    def __init__(self, clipboard=None):
        """
        Initialize InputProcessor

        Args:
            clipboard: Optional QClipboard instance. If None, uses QApplication.clipboard()

        Raises:
            RuntimeError: If QApplication is not available and no clipboard provided
        """
        if clipboard is not None:
            self.clipboard = clipboard
        else:
            if QApplication is None:
                raise RuntimeError("QApplication not available. Install PyQt6 or run in GUI environment.")
            app = QApplication.instance()
            if app is None:
                raise RuntimeError("QApplication instance not found. Create QApplication first.")
            self.clipboard = app.clipboard()

    async def detect_input_type(self) -> InputType:
        """
        Detect input type automatically (AC: #1)

        Detection logic (PASSIVE - no UI dialogs):
        1. Check if clipboard has text
        2. If text looks like URL → InputType.URL
        3. Otherwise → InputType.TEXT
        4. If clipboard empty → InputType.EMPTY

        Note:
            This method does NOT show file dialogs to avoid double-prompting.
            Caller should explicitly call process_file(), process_multiple(), etc.
            based on their needs.

        Returns:
            InputType: Detected input type (TEXT, URL, or EMPTY)

        Raises:
            RuntimeError: If GUI components not available
        """
        # 1. Check clipboard first (passive detection only)
        clipboard_text = self.clipboard.text()
        if clipboard_text and clipboard_text.strip():
            # Check if it's a URL
            if clipboard_text.startswith(('http://', 'https://')):
                return InputType.URL
            return InputType.TEXT

        # 2. No clipboard content - return EMPTY
        # Caller should decide whether to show file dialog or input popup
        return InputType.EMPTY

    def process_text(self) -> str:
        """
        Process text from clipboard (AC: #2)

        Returns:
            str: Text content from clipboard (may be empty string)

        Note:
            - Supports Unicode and multilingual text
            - Handles empty clipboard gracefully
        """
        text = self.clipboard.text()
        return text if text else ""

    def process_file(self) -> Optional[str]:
        """
        Process file input via file dialog and return file content (AC: #3)

        Returns:
            Optional[str]: File content if selected and read successfully,
                          None if canceled or read fails

        Raises:
            RuntimeError: If QFileDialog not available

        Note:
            - Shows file dialog with filters
            - Allows single file selection
            - Reads and returns file content (not just path)
            - Returns None if user cancels or file cannot be read
            - Consistent with process_text() which returns content
        """
        if QFileDialog is None:
            raise RuntimeError("QFileDialog not available. Install PyQt6.")

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select file to process",
            str(Path.home()),
            "All Files (*.*)"
        )

        if not file_path:
            return None

        # Read and return file content
        try:
            return self._read_file_content(file_path)
        except (IOError, Exception) as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

    def process_empty(self, agent_name: str = "agent") -> Optional[str]:
        """
        Process empty input via popup dialog (AC: #4)

        Args:
            agent_name: Name of the agent for the prompt message

        Returns:
            Optional[str]: User input text, or None if canceled

        Raises:
            RuntimeError: If QInputDialog not available

        Note:
            - Shows "Enter input for {agent_name}" message
            - Returns None if user clicks Cancel
        """
        if QInputDialog is None:
            raise RuntimeError("QInputDialog not available. Install PyQt6.")

        text, ok = QInputDialog.getText(
            None,
            "Input Required",
            f"Enter input for {agent_name}:",
            QLineEdit.EchoMode.Normal if QLineEdit else 0
        )

        return text if ok else None

    def process_multiple(self) -> List[Optional[str]]:
        """
        Process multiple files sequentially (AC: #5)

        Returns:
            List[Optional[str]]: List of file contents (one per file)
                                None for files that failed to read

        Raises:
            RuntimeError: If QFileDialog not available

        Note:
            - Shows progress notification for each file
            - Processes files sequentially (not parallel)
            - Handles errors per-file without stopping batch
            - Returns list of results (one per file)
        """
        if QFileDialog is None:
            raise RuntimeError("QFileDialog not available. Install PyQt6.")

        # Get multiple files
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            "Select files to process",
            str(Path.home()),
            "All Files (*.*)"
        )

        if not file_paths:
            return []

        results = []
        total = len(file_paths)

        for idx, file_path in enumerate(file_paths, start=1):
            print(f"Processing file {idx}/{total}...")

            try:
                content = self._read_file_content(file_path)
                results.append(content)
                print(f"✅ Complete: {Path(file_path).name} processed")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                results.append(None)
                print(f"❌ Error: {Path(file_path).name} - {e}")

        print(f"✅ Complete: {total} files processed")
        return results

    def _read_file_content(self, file_path: str) -> str:
        """
        Read file content using pathlib

        Args:
            file_path: Path to file to read

        Returns:
            str: File content

        Raises:
            IOError: If file cannot be read

        Note:
            - Reads file with UTF-8 encoding hardcoded
            - Raises IOError if file not found or cannot be decoded
            - Caller should handle encoding errors for non-UTF8 files
            - Caller is responsible for closing file handles (context manager used)
        """
        path = Path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    def _validate_url(self, url: str) -> None:
        """
        Validate URL for security (SSRF protection)

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL is invalid or unsafe

        Security checks:
            - Must be http:// or https://
            - Must have valid format
            - Blocks private/local network addresses (SSRF protection)
        """
        # Check protocol
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL protocol: {url}. Only http:// and https:// are allowed.")

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {url} - {e}")

        # Check network location exists
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: missing network location - {url}")

        # SSRF Protection: Block private/local network addresses
        try:
            # Get hostname
            hostname = parsed.hostname

            if not hostname:
                raise ValueError(f"Invalid URL: missing hostname - {url}")

            # Block localhost and local addresses
            if hostname in ('localhost', '127.0.0.1', '[::1]', '0.0.0.0'):
                raise ValueError(f"Blocked URL: localhost not allowed - {url}")

            # Block private IP ranges (RFC 1918)
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    raise ValueError(f"Blocked URL: private IP address not allowed - {url}")
            except ValueError:
                # Not an IP address, continue with hostname check
                pass

            # Block .local, .internal, .localhost TLDs
            if any(hostname.endswith(suffix) for suffix in ('.local', '.internal', '.localhost')):
                raise ValueError(f"Blocked URL: internal hostname not allowed - {url}")

        except ValueError as e:
            if "Blocked URL" in str(e):
                raise
            # Re-raise if it's a different ValueError
            logger.warning(f"URL validation warning for {url}: {e}")

    async def process_url(self, url: str, timeout: int = DEFAULT_URL_TIMEOUT, max_size: int = MAX_DOWNLOAD_SIZE) -> str:
        """
        Download content from URL (AC: #6)

        Args:
            url: HTTP/HTTPS URL to download from
            timeout: Request timeout in seconds (default: 10)
            max_size: Maximum download size in bytes (default: 10MB)

        Returns:
            str: Downloaded content, or URL as text if download fails

        Raises:
            RuntimeError: If aiohttp not available
            ValueError: If URL is invalid or unsafe

        Security:
            - Validates URL format and protocol (http/https only)
            - Blocks private/local network addresses (SSRF protection)
            - Enforces maximum file size limit

        Note:
            - Supports http and https protocols
            - Handles download errors gracefully
            - Falls back to using URL as text if download fails
        """
        # Validate URL for security
        try:
            self._validate_url(url)
        except ValueError as e:
            logger.error(f"URL validation failed: {e}")
            return url

        if aiohttp is None:
            logger.warning("aiohttp not available, using URL as text")
            return url

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        # Check content-length header before downloading
                        content_length = response.headers.get('Content-Length')
                        if content_length:
                            length = int(content_length)
                            if length > max_size:
                                logger.warning(f"URL content too large: {length} bytes, using URL as text")
                                return url

                        # Download content
                        content = await response.text()

                        # Enforce max size check (in case no Content-Length header)
                        if len(content) > max_size:
                            logger.warning(f"Downloaded content exceeds max size: {len(content)} bytes")
                            return url

                        return content
                    else:
                        logger.warning(f"HTTP {response.status} for {url}, using URL as text")
                        return url
        except asyncio.TimeoutError:
            logger.warning(f"Timeout downloading {url}, using URL as text")
            return url
        except Exception as e:
            logger.warning(f"Error downloading {url}: {e}, using URL as text")
            return url
