"""
Tests for InputProcessor module (Story 6)

Test coverage:
- InputType enum (AC: #1)
- InputProcessor class initialization
- Input type detection (AC: #1)
- Clipboard integration (AC: #2)
- File dialog integration (AC: #3)
- Empty input popup (AC: #4)
- Multiple file processing (AC: #5)
- URL download (AC: #6)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from enum import Enum

from core.input_processor import InputProcessor, InputType


class TestInputTypeEnum:
    """Test InputType enum (AC: #1)"""

    def test_input_type_enum_values(self):
        """Test that InputType has all required values"""
        assert InputType.TEXT.value == "text"
        assert InputType.FILE.value == "file"
        assert InputType.EMPTY.value == "empty"
        assert InputType.MULTIPLE.value == "multiple"
        assert InputType.URL.value == "url"

    def test_input_type_enum_is_enum(self):
        """Test that InputType is an Enum"""
        assert issubclass(InputType, Enum)


class TestInputProcessorInit:
    """Test InputProcessor class initialization"""

    def test_init_with_clipboard(self):
        """Test InputProcessor initialization with clipboard reference"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        assert processor.clipboard == mock_clipboard

    @patch('core.input_processor.QApplication')
    def test_init_without_clipboard_uses_default(self, mock_qapp):
        """Test InputProcessor initialization without clipboard uses default"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard

        processor = InputProcessor()

        assert processor.clipboard == mock_clipboard
        mock_qapp.instance.assert_called_once()


class TestInputTypeDetection:
    """Test input type detection (AC: #1)"""

    @pytest.mark.asyncio
    async def test_detect_clipboard_text(self):
        """Test detection of text input from clipboard"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = "Sample text from clipboard"
        processor = InputProcessor(clipboard=mock_clipboard)

        input_type = await processor.detect_input_type()

        assert input_type == InputType.TEXT

    @pytest.mark.asyncio
    async def test_detect_clipboard_url(self):
        """Test detection of URL input from clipboard"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = "https://example.com"
        processor = InputProcessor(clipboard=mock_clipboard)

        input_type = await processor.detect_input_type()

        assert input_type == InputType.URL

    @pytest.mark.asyncio
    async def test_detect_clipboard_http_url(self):
        """Test detection of HTTP URL input from clipboard"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = "http://example.com"
        processor = InputProcessor(clipboard=mock_clipboard)

        input_type = await processor.detect_input_type()

        assert input_type == InputType.URL

    @pytest.mark.asyncio
    async def test_detect_empty_clipboard(self):
        """Test detection of empty clipboard (passive detection - no dialogs)"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = ""
        processor = InputProcessor(clipboard=mock_clipboard)

        # detect_input_type no longer shows dialogs - returns EMPTY directly
        input_type = await processor.detect_input_type()

        assert input_type == InputType.EMPTY


class TestClipboardIntegration:
    """Test clipboard integration (AC: #2)"""

    def test_process_text_from_clipboard(self):
        """Test processing text from clipboard"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = "Sample text"
        processor = InputProcessor(clipboard=mock_clipboard)

        result = processor.process_text()

        assert result == "Sample text"
        mock_clipboard.text.assert_called_once()

    def test_process_text_unicode_support(self):
        """Test processing Unicode text from clipboard"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = "Hello 世界 🌍"
        processor = InputProcessor(clipboard=mock_clipboard)

        result = processor.process_text()

        assert result == "Hello 世界 🌍"
        mock_clipboard.text.assert_called_once()

    def test_process_text_empty_clipboard(self):
        """Test handling empty clipboard gracefully"""
        mock_clipboard = Mock()
        mock_clipboard.text.return_value = ""
        processor = InputProcessor(clipboard=mock_clipboard)

        result = processor.process_text()

        assert result == ""
        mock_clipboard.text.assert_called_once()


class TestFileDialogIntegration:
    """Test file dialog integration (AC: #3)"""

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    @patch('core.input_processor.Path')
    def test_process_file_single_file(self, mock_path, mock_filedialog, mock_qapp):
        """Test processing a single file (returns content, not path)"""
        test_content = "Sample file content"
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_filedialog.getOpenFileName.return_value = ("/path/to/file.txt", "")

        processor = InputProcessor()

        # Mock _read_file_content to return content
        with patch.object(processor, '_read_file_content', return_value=test_content):
            result = processor.process_file()

            assert result == test_content  # Returns content, not path
            mock_filedialog.getOpenFileName.assert_called_once()

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_file_user_cancels(self, mock_filedialog, mock_qapp):
        """Test handling when user cancels file dialog"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_filedialog.getOpenFileName.return_value = ("", "")

        processor = InputProcessor()
        result = processor.process_file()

        assert result is None
        mock_filedialog.getOpenFileName.assert_called_once()

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_file_read_error(self, mock_filedialog, mock_qapp):
        """Test handling file read error"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_filedialog.getOpenFileName.return_value = ("/path/to/file.txt", "")

        processor = InputProcessor()

        # Mock _read_file_content to raise error
        with patch.object(processor, '_read_file_content', side_effect=IOError("Read error")):
            result = processor.process_file()

            # Should return None on error
            assert result is None


class TestEmptyInputPopup:
    """Test empty input popup dialog (AC: #4)"""

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QInputDialog')
    def test_process_empty_user_enters_text(self, mock_inputdialog, mock_qapp):
        """Test popup dialog when user enters text"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_inputdialog.getText.return_value = ("User input text", True)

        processor = InputProcessor()
        result = processor.process_empty("TestAgent")

        assert result == "User input text"
        mock_inputdialog.getText.assert_called_once()

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QInputDialog')
    def test_process_empty_user_cancels(self, mock_inputdialog, mock_qapp):
        """Test popup dialog when user cancels"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_inputdialog.getText.return_value = ("", False)

        processor = InputProcessor()
        result = processor.process_empty("TestAgent")

        assert result is None
        mock_inputdialog.getText.assert_called_once()

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QInputDialog')
    def test_process_empty_dialog_message(self, mock_inputdialog, mock_qapp):
        """Test that popup shows correct message"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_inputdialog.getText.return_value = ("input", True)

        processor = InputProcessor()
        processor.process_empty("MyAgent")

        # Verify the dialog was called with correct title/label
        call_args = mock_inputdialog.getText.call_args
        assert "MyAgent" in str(call_args)


class TestMultipleFileProcessing:
    """Test multiple file processing (AC: #5)"""

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_multiple_files(self, mock_filedialog, mock_qapp):
        """Test processing multiple files sequentially"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        files = ["/path/file1.txt", "/path/file2.txt", "/path/file3.txt"]
        mock_filedialog.getOpenFileNames.return_value = (files, "")

        processor = InputProcessor()
        with patch.object(processor, '_read_file_content', side_effect=["content1", "content2", "content3"]):
            results = processor.process_multiple()

            assert len(results) == 3
            assert results[0] == "content1"
            assert results[1] == "content2"
            assert results[2] == "content3"

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_multiple_user_cancels(self, mock_filedialog, mock_qapp):
        """Test when user cancels multiple file selection"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_filedialog.getOpenFileNames.return_value = ([], "")

        processor = InputProcessor()
        results = processor.process_multiple()

        assert results == []

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_multiple_handles_errors_per_file(self, mock_filedialog, mock_qapp):
        """Test that errors in one file don't stop processing of others"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        files = ["/path/file1.txt", "/path/file2.txt", "/path/file3.txt"]
        mock_filedialog.getOpenFileNames.return_value = (files, "")

        def mock_read(file_path):
            if "file2" in file_path:
                raise IOError("Read error")
            return "content"

        processor = InputProcessor()
        with patch.object(processor, '_read_file_content', side_effect=mock_read):
            results = processor.process_multiple()

            # Should still process files 1 and 3
            assert len(results) == 3
            assert results[0] == "content"
            assert results[1] is None  # Error case
            assert results[2] == "content"

    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.QFileDialog')
    def test_process_multiple_progress_notification_format(self, mock_filedialog, mock_qapp, capsys):
        """Test that progress notifications match the exact format specified in Dev Notes"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        files = ["file1.py", "file2.py", "file3.py"]
        mock_filedialog.getOpenFileNames.return_value = (files, "")

        processor = InputProcessor()
        with patch.object(processor, '_read_file_content', return_value="content"):
            results = processor.process_multiple()

            # Capture output
            captured = capsys.readouterr()

            # Verify exact format from Dev Notes
            assert "Processing file 1/3..." in captured.out
            assert "✅ Complete: file1.py processed" in captured.out
            assert "Processing file 2/3..." in captured.out
            assert "✅ Complete: file2.py processed" in captured.out
            assert "Processing file 3/3..." in captured.out
            assert "✅ Complete: 3 files processed" in captured.out


class TestURLDownload:
    """Test URL download functionality (AC: #6)"""

    @pytest.mark.asyncio
    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.aiohttp')
    async def test_process_url_https_success(self, mock_aiohttp, mock_qapp):
        """Test downloading content from HTTPS URL"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_response = MagicMock()
        mock_response.status = 200

        # Mock text() as an async function
        async def mock_text():
            return "<html>Downloaded content</html>"
        mock_response.text = mock_text

        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session

        processor = InputProcessor()
        result = await processor.process_url("https://example.com")

        assert result == "<html>Downloaded content</html>"
        mock_session.get.assert_called_once_with("https://example.com", timeout=10)

    @pytest.mark.asyncio
    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.aiohttp')
    async def test_process_url_http_success(self, mock_aiohttp, mock_qapp):
        """Test downloading content from HTTP URL"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_response = MagicMock()
        mock_response.status = 200

        # Mock text() as an async function
        async def mock_text():
            return "HTTP content"
        mock_response.text = mock_text

        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session

        processor = InputProcessor()
        result = await processor.process_url("http://example.com")

        assert result == "HTTP content"

    @pytest.mark.asyncio
    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.aiohttp')
    async def test_process_url_timeout(self, mock_aiohttp, mock_qapp):
        """Test handling timeout on URL download"""
        import asyncio

        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_session = MagicMock()
        mock_session.get.side_effect = asyncio.TimeoutError()
        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session

        processor = InputProcessor()
        result = await processor.process_url("https://example.com")

        # Should return URL as text on error (configurable fallback)
        assert result == "https://example.com"

    @pytest.mark.asyncio
    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.aiohttp')
    async def test_process_url_connection_error(self, mock_aiohttp, mock_qapp):
        """Test handling connection error on URL download"""
        import aiohttp

        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_session = MagicMock()
        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session

        processor = InputProcessor()
        result = await processor.process_url("https://example.com")

        # Should return URL as text on error
        assert result == "https://example.com"

    @pytest.mark.asyncio
    async def test_process_url_blocks_file_protocol(self):
        """Test that file:// URLs are blocked for security"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        # file:// protocol should be blocked
        result = await processor.process_url("file:///etc/passwd")

        # Should return URL as text (not downloaded)
        assert result == "file:///etc/passwd"

    @pytest.mark.asyncio
    async def test_process_url_blocks_ftp_protocol(self):
        """Test that ftp:// URLs are blocked for security"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        # ftp:// protocol should be blocked
        result = await processor.process_url("ftp://internal-server/file")

        # Should return URL as text (not downloaded)
        assert result == "ftp://internal-server/file"

    @pytest.mark.asyncio
    async def test_process_url_blocks_localhost(self):
        """Test that localhost URLs are blocked for security (SSRF protection)"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        # localhost should be blocked
        result = await processor.process_url("http://localhost:8080/admin")

        # Should return URL as text (not downloaded)
        assert result == "http://localhost:8080/admin"

    @pytest.mark.asyncio
    async def test_process_url_blocks_private_ip(self):
        """Test that private IP addresses are blocked for security (SSRF protection)"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        # 192.168.x.x is private IP range
        result = await processor.process_url("http://192.168.1.1/secret")

        # Should return URL as text (not downloaded)
        assert result == "http://192.168.1.1/secret"

    @pytest.mark.asyncio
    async def test_process_url_blocks_internal_hostname(self):
        """Test that internal hostnames are blocked for security"""
        mock_clipboard = Mock()
        processor = InputProcessor(clipboard=mock_clipboard)

        # .internal TLD should be blocked
        result = await processor.process_url("http://internal.local/config")

        # Should return URL as text (not downloaded)
        assert result == "http://internal.local/config"

    @pytest.mark.asyncio
    @patch('core.input_processor.QApplication')
    @patch('core.input_processor.aiohttp')
    async def test_process_url_enforces_max_size(self, mock_aiohttp, mock_qapp):
        """Test that download size limit is enforced"""
        mock_clipboard = Mock()
        mock_qapp.instance.return_value.clipboard.return_value = mock_clipboard
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {'Content-Length': str(20 * 1024 * 1024)}  # 20 MB

        async def mock_text():
            return "Large content"
        mock_response.text = mock_text

        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session

        processor = InputProcessor()
        result = await processor.process_url("https://example.com/large")

        # Should return URL as text (file too large)
        assert result == "https://example.com/large"
