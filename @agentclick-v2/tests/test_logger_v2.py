"""
Tests for Logger V2 - Activity log system (Story 11)

This test module covers:
- Logger initialization and configuration
- Log entry creation and formatting
- Log filtering by category
- Log export functionality
- Log persistence
- Signal/slot integration
"""
import pytest
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from utils.logger_v2 import LoggerV2, LogLevel, LogCategory


class TestLoggerV2Initialization:
    """Test logger initialization and configuration."""

    def test_logger_initialization(self):
        """Test logger initializes with default settings."""
        logger = LoggerV2()

        assert logger.max_entries == 1000
        assert logger.current_level == LogLevel.INFO
        assert len(logger.log_entries) == 0

    def test_logger_initialization_with_custom_max_entries(self):
        """Test logger initializes with custom max entries."""
        logger = LoggerV2(max_entries=500)

        assert logger.max_entries == 500

    def test_logger_initialization_with_custom_level(self):
        """Test logger initializes with custom log level."""
        logger = LoggerV2(level=LogLevel.DEBUG)

        assert logger.current_level == LogLevel.DEBUG


class TestLogEntryCreation:
    """Test log entry creation and formatting."""

    def test_add_log_entry_basic(self):
        """Test adding a basic log entry."""
        logger = LoggerV2()
        logger.add_log_entry(
            category=LogCategory.AGENT_READY,
            message="Agent ready: test-agent"
        )

        assert len(logger.log_entries) == 1

        entry = logger.log_entries[0]
        assert entry['category'] == LogCategory.AGENT_READY
        assert entry['message'] == "Agent ready: test-agent"
        assert 'timestamp' in entry
        assert 'emoji' in entry
        assert entry['emoji'] == "✨"

    def test_add_log_entry_all_categories(self):
        """Test adding entries for all log categories."""
        logger = LoggerV2()

        # Test all categories
        test_cases = [
            (LogCategory.AGENT_READY, "✨"),
            (LogCategory.PROCESSING_START, "📖"),
            (LogCategory.COMPLETE, "✅"),
            (LogCategory.CLIPBOARD_COPY, "📋"),
            (LogCategory.ERROR, "❌"),
            (LogCategory.WORKSPACE_SWITCH, "🔄"),
            (LogCategory.AGENT_SWITCH, "🔀"),
        ]

        for category, expected_emoji in test_cases:
            logger.add_log_entry(
                category=category,
                message=f"Test {category}"
            )

        assert len(logger.log_entries) == len(test_cases)

        # Check in reverse order (newest first)
        for i, (category, expected_emoji) in enumerate(reversed(test_cases)):
            entry = logger.log_entries[i]
            assert entry['category'] == category
            assert entry['emoji'] == expected_emoji

    def test_add_log_entry_with_level(self):
        """Test adding log entry with custom level."""
        logger = LoggerV2()
        logger.add_log_entry(
            category=LogCategory.INFO,
            message="Info message",
            level=LogLevel.INFO
        )

        entry = logger.log_entries[0]
        assert entry['level'] == LogLevel.INFO

    def test_add_log_entry_rotation(self):
        """Test log rotation when max entries exceeded."""
        logger = LoggerV2(max_entries=5)

        # Add 10 entries
        for i in range(10):
            logger.add_log_entry(
                category=LogCategory.INFO,
                message=f"Entry {i}"
            )

        # Should only keep 5 most recent
        assert len(logger.log_entries) == 5

        # Check that oldest entries are removed
        messages = [entry['message'] for entry in logger.log_entries]
        assert "Entry 0" not in messages
        assert "Entry 9" in messages

    def test_get_formatted_entries(self):
        """Test getting formatted log entries."""
        logger = LoggerV2()
        logger.add_log_entry(
            category=LogCategory.COMPLETE,
            message="Complete (142 chars)"
        )
        logger.add_log_entry(
            category=LogCategory.CLIPBOARD_COPY,
            message="Copied to clipboard"
        )

        formatted = logger.get_formatted_entries()

        assert len(formatted) == 2
        # Newest first (clipboard copy was added last)
        assert "📋" in formatted[0]
        assert "Copied to clipboard" in formatted[0]
        assert "✅" in formatted[1]
        assert "Complete (142 chars)" in formatted[1]

    def test_get_filtered_entries(self):
        """Test filtering entries by level hierarchy."""
        logger = LoggerV2()

        # Add mixed entries
        logger.add_log_entry(LogCategory.INFO, "Info message", level=LogLevel.INFO)
        logger.add_log_entry(LogCategory.ERROR, "Error message", level=LogLevel.ERROR)
        logger.add_log_entry(LogCategory.SUCCESS, "Success message", level=LogLevel.SUCCESS)
        logger.add_log_entry(LogCategory.ERROR, "Another error", level=LogLevel.ERROR)
        logger.add_log_entry(LogCategory.WARNING, "Warning message", level=LogLevel.WARNING)

        # Filter by ERROR level (should show only errors - highest level)
        error_entries = logger.get_filtered_entries(level=LogLevel.ERROR)
        assert len(error_entries) == 2
        assert all(e['level'] == LogLevel.ERROR for e in error_entries)

        # Filter by WARNING level (should show warnings AND errors)
        warning_entries = logger.get_filtered_entries(level=LogLevel.WARNING)
        assert len(warning_entries) == 3  # 2 errors + 1 warning
        assert all(e['level'] in [LogLevel.WARNING, LogLevel.ERROR] for e in warning_entries)

        # Filter by SUCCESS level (should show success, warnings, and errors)
        success_entries = logger.get_filtered_entries(level=LogLevel.SUCCESS)
        assert len(success_entries) == 4  # 2 errors + 1 warning + 1 success

        # Filter by INFO level (should show everything)
        info_entries = logger.get_filtered_entries(level=LogLevel.INFO)
        assert len(info_entries) == 5  # All entries

    def test_detect_level_from_category(self):
        """Test automatic level detection from category."""
        logger = LoggerV2()

        # Test ERROR category
        assert logger._detect_level_from_category(LogCategory.ERROR) == LogLevel.ERROR

        # Test WARNING category
        assert logger._detect_level_from_category(LogCategory.WARNING) == LogLevel.WARNING

        # Test COMPLETE category (should map to SUCCESS)
        assert logger._detect_level_from_category(LogCategory.COMPLETE) == LogLevel.SUCCESS

        # Test SUCCESS category
        assert logger._detect_level_from_category(LogCategory.SUCCESS) == LogLevel.SUCCESS

        # Test other categories (should map to INFO)
        assert logger._detect_level_from_category(LogCategory.AGENT_READY) == LogLevel.INFO
        assert logger._detect_level_from_category(LogCategory.PROCESSING_START) == LogLevel.INFO
        assert logger._detect_level_from_category(LogCategory.CLIPBOARD_COPY) == LogLevel.INFO

    def test_clear_log(self):
        """Test clearing log entries."""
        logger = LoggerV2()
        logger.add_log_entry(LogCategory.INFO, "Test message")

        assert len(logger.log_entries) == 1

        logger.clear_log()

        assert len(logger.log_entries) == 0


class TestLogExport:
    """Test log export functionality."""

    def test_export_to_text(self, tmp_path):
        """Test exporting log to text format."""
        logger = LoggerV2()
        logger.add_log_entry(LogCategory.COMPLETE, "Complete (142 chars)")
        logger.add_log_entry(LogCategory.CLIPBOARD_COPY, "Copied to clipboard")

        # Export to temp file
        export_path = tmp_path / "activity_log.txt"
        logger.export_to_text(str(export_path))

        # Verify file exists and has content
        assert export_path.exists()

        content = export_path.read_text(encoding='utf-8')
        assert "AgentClick V2 Activity Log" in content
        assert "✅" in content
        assert "Complete (142 chars)" in content
        assert "📋" in content
        assert "Copied to clipboard" in content

    def test_export_to_json(self, tmp_path):
        """Test exporting log to JSON format."""
        logger = LoggerV2()
        logger.add_log_entry(LogCategory.COMPLETE, "Complete (142 chars)")
        logger.add_log_entry(LogCategory.CLIPBOARD_COPY, "Copied to clipboard")

        # Export to temp file
        export_path = tmp_path / "activity_log.json"
        logger.export_to_json(str(export_path))

        # Verify file exists and has valid JSON
        assert export_path.exists()

        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'generated' in data
        assert 'entries' in data
        assert len(data['entries']) == 2
        assert data['entries'][0]['message'] == "Complete (142 chars)"

    def test_export_empty_log(self, tmp_path):
        """Test exporting empty log creates valid files."""
        logger = LoggerV2()

        # Export text
        text_path = tmp_path / "empty_log.txt"
        logger.export_to_text(str(text_path))
        assert text_path.exists()

        # Export JSON
        json_path = tmp_path / "empty_log.json"
        logger.export_to_json(str(json_path))
        assert json_path.exists()


class TestLogSignals:
    """Test signal emission for UI updates."""

    def test_log_entry_added_signal(self):
        """Test that log_entry_added signal is emitted."""
        logger = LoggerV2()

        # Track signal emissions
        received = []
        logger.log_entry_added.connect(lambda entry: received.append(entry))

        logger.add_log_entry(
            category=LogCategory.INFO,
            message="Test message"
        )

        assert len(received) == 1
        assert received[0]['message'] == "Test message"

    def test_log_cleared_signal(self):
        """Test that log_cleared signal is emitted."""
        logger = LoggerV2()
        logger.add_log_entry(LogCategory.INFO, "Test message")

        # Track signal emissions
        received = []
        logger.log_cleared.connect(lambda: received.append(True))

        logger.clear_log()

        assert len(received) == 1


class TestLogPersistence:
    """Test log persistence to disk."""

    def test_save_and_load_log(self, tmp_path):
        """Test saving and loading log from file."""
        logger = LoggerV2()
        logger.add_log_entry(LogCategory.COMPLETE, "Complete (142 chars)")
        logger.add_log_entry(LogCategory.CLIPBOARD_COPY, "Copied to clipboard")

        # Save log
        log_path = tmp_path / "activity_log.json"
        logger.save_log(str(log_path))

        # Create new logger and load
        logger2 = LoggerV2()
        logger2.load_log(str(log_path))

        # Verify entries loaded (newest first)
        assert len(logger2.log_entries) == 2
        assert logger2.log_entries[0]['message'] == "Copied to clipboard"
        assert logger2.log_entries[1]['message'] == "Complete (142 chars)"

    def test_load_nonexistent_log(self, tmp_path):
        """Test loading nonexistent log doesn't crash."""
        logger = LoggerV2()

        # Should not raise exception
        logger.load_log(str(tmp_path / "nonexistent.json"))

        assert len(logger.log_entries) == 0


class TestLogLevelAndCategoryEnums:
    """Test LogLevel and LogCategory enums."""

    def test_log_levels(self):
        """Test LogLevel enum values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.SUCCESS == "SUCCESS"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"

    def test_log_categories(self):
        """Test LogCategory enum values."""
        assert LogCategory.AGENT_READY == "AGENT_READY"
        assert LogCategory.PROCESSING_START == "PROCESSING_START"
        assert LogCategory.COMPLETE == "COMPLETE"
        assert LogCategory.CLIPBOARD_COPY == "CLIPBOARD_COPY"
        assert LogCategory.ERROR == "ERROR"
        assert LogCategory.WORKSPACE_SWITCH == "WORKSPACE_SWITCH"
        assert LogCategory.AGENT_SWITCH == "AGENT_SWITCH"
        assert LogCategory.INFO == "INFO"
        assert LogCategory.SUCCESS == "SUCCESS"
        assert LogCategory.WARNING == "WARNING"
