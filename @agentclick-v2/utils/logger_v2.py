"""
Logger V2 - Activity log system for AgentClick V2 (Story 11)

This module provides the LoggerV2 class which manages activity logging with:
- Structured log entries with timestamps, levels, categories, and emoji icons
- Log filtering by level
- Log export to text and JSON formats
- Log persistence to disk
- Signal/slot integration for UI updates
- Automatic log rotation (max entries limit)

Log Levels:
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- SUCCESS: Successful operations
- WARNING: Warning messages
- ERROR: Error messages

Log Categories:
- AGENT_READY: Agent is ready to execute
- PROCESSING_START: Agent started processing
- COMPLETE: Operation completed successfully
- CLIPBOARD_COPY: Content copied to clipboard
- ERROR: Error occurred
- WORKSPACE_SWITCH: Workspace switched
- AGENT_SWITCH: Agent switched
- INFO: General info
- SUCCESS: Success message
- WARNING: Warning message

Example:
    >>> logger = LoggerV2()
    >>> logger.add_log_entry(
    ...     category=LogCategory.AGENT_READY,
    ...     message="Agent ready: verify-python"
    ... )
    >>> entries = logger.get_formatted_entries()
    >>> logger.export_to_text("activity_log.txt")
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict

from PyQt6.QtCore import QObject, pyqtSignal


logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


# Log level hierarchy for filtering (higher value = more severe)
LEVEL_HIERARCHY = {
    LogLevel.DEBUG: 0,
    LogLevel.INFO: 1,
    LogLevel.SUCCESS: 2,
    LogLevel.WARNING: 3,
    LogLevel.ERROR: 4
}


class LogCategory(str, Enum):
    """Log category enumeration."""

    AGENT_READY = "AGENT_READY"
    PROCESSING_START = "PROCESSING_START"
    COMPLETE = "COMPLETE"
    CLIPBOARD_COPY = "CLIPBOARD_COPY"
    ERROR = "ERROR"
    WORKSPACE_SWITCH = "WORKSPACE_SWITCH"
    AGENT_SWITCH = "AGENT_SWITCH"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"


# Category emoji mapping
CATEGORY_EMOJIS = {
    LogCategory.AGENT_READY: "✨",
    LogCategory.PROCESSING_START: "📖",
    LogCategory.COMPLETE: "✅",
    LogCategory.CLIPBOARD_COPY: "📋",
    LogCategory.ERROR: "❌",
    LogCategory.WORKSPACE_SWITCH: "🔄",
    LogCategory.AGENT_SWITCH: "🔀",
    LogCategory.INFO: "ℹ️",
    LogCategory.SUCCESS: "✅",
    LogCategory.WARNING: "⚠️",
}


class LoggerV2(QObject):
    """
    Activity logger for AgentClick V2.

    This logger manages activity logs with the following features:
    - Structured log entries with timestamps, levels, categories, and emojis
    - Automatic log rotation when max entries exceeded
    - Log filtering by level
    - Log export to text and JSON formats
    - Log persistence to disk
    - Signal emission for UI updates

    Signals:
        log_entry_added: Emitted when a new log entry is added
            Args:
                entry: The log entry dictionary
        log_cleared: Emitted when log is cleared

    Attributes:
        max_entries: Maximum number of log entries to keep (default: 1000)
        current_level: Current log level filter
        log_entries: List of log entries (newest first)

    Example:
        >>> logger = LoggerV2()
        >>> logger.add_log_entry(
        ...     category=LogCategory.AGENT_READY,
        ...     message="Agent ready: verify-python"
        ... )
        >>> formatted = logger.get_formatted_entries()
        >>> logger.export_to_text("activity_log.txt")
    """

    # Signals for UI updates
    log_entry_added = pyqtSignal(dict)
    log_cleared = pyqtSignal()

    def __init__(self, max_entries: int = 1000, level: LogLevel = LogLevel.INFO):
        """
        Initialize LoggerV2.

        Args:
            max_entries: Maximum number of log entries to keep (default: 1000)
            level: Current log level filter (default: INFO)

        Example:
            >>> logger = LoggerV2(max_entries=500, level=LogLevel.DEBUG)
        """
        super().__init__()

        self.max_entries = max_entries
        self.current_level = level
        self.log_entries: List[Dict[str, Any]] = []

        logger.info(f"LoggerV2 initialized (max_entries={max_entries}, level={level})")

    def add_log_entry(
        self,
        category: LogCategory,
        message: str,
        level: Optional[LogLevel] = None
    ) -> None:
        """
        Add a log entry.

        Args:
            category: Log category (from LogCategory enum)
            message: Log message
            level: Log level (optional, auto-detected from category if not provided)

        Example:
            >>> logger.add_log_entry(
            ...     category=LogCategory.AGENT_READY,
            ...     message="Agent ready: verify-python"
            ... )
        """
        # Auto-detect level from category if not provided
        if level is None:
            level = self._detect_level_from_category(category)

        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message,
            "emoji": CATEGORY_EMOJIS.get(category, "ℹ️")
        }

        # Add to beginning of list (newest first)
        self.log_entries.insert(0, entry)

        # Rotate if max entries exceeded
        if len(self.log_entries) > self.max_entries:
            # Remove oldest entries (from end of list)
            self.log_entries = self.log_entries[:self.max_entries]

        # Emit signal for UI update
        self.log_entry_added.emit(entry)

        logger.debug(f"Log entry added: {category} - {message}")

    def _detect_level_from_category(self, category: LogCategory) -> LogLevel:
        """
        Detect log level from category.

        Args:
            category: Log category

        Returns:
            Detected log level
        """
        if category == LogCategory.ERROR:
            return LogLevel.ERROR
        elif category == LogCategory.WARNING:
            return LogLevel.WARNING
        elif category in [LogCategory.COMPLETE, LogCategory.SUCCESS]:
            return LogLevel.SUCCESS
        else:
            return LogLevel.INFO

    def get_formatted_entries(self, filter_level: Optional[LogLevel] = None) -> List[str]:
        """
        Get formatted log entries as strings.

        Args:
            filter_level: Optional level filter (only show entries at or above this level)

        Returns:
            List of formatted log entry strings

        Example:
            >>> formatted = logger.get_formatted_entries()
            >>> for line in formatted:
            ...     print(line)
        """
        entries = self.get_filtered_entries(level=filter_level)
        formatted = []

        for entry in entries:
            # Parse timestamp to get time part
            try:
                dt = datetime.fromisoformat(entry['timestamp'])
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = entry['timestamp'][:8]  # Fallback to first 8 chars

            formatted_line = f"{entry['emoji']} {time_str} - {entry['message']}"
            formatted.append(formatted_line)

        return formatted

    def get_filtered_entries(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None
    ) -> List[Dict[str, Any]]:
        """
        Get filtered log entries.

        Args:
            level: Optional level filter (shows entries at or above this level)
            category: Optional category filter

        Returns:
            Filtered list of log entries

        Example:
            >>> errors = logger.get_filtered_entries(level=LogLevel.ERROR)
        """
        filtered = self.log_entries

        if level:
            # Filter by level hierarchy (show entries at or above this level)
            min_level = LEVEL_HIERARCHY.get(level, 0)
            filtered = [e for e in filtered if LEVEL_HIERARCHY.get(e['level'], 0) >= min_level]

        if category:
            filtered = [e for e in filtered if e['category'] == category]

        return filtered

    def clear_log(self) -> None:
        """
        Clear all log entries.

        Example:
            >>> logger.clear_log()
        """
        self.log_entries.clear()
        self.log_cleared.emit()
        logger.info("Log cleared")

    def export_to_text(self, file_path: str) -> None:
        """
        Export log to text format.

        Args:
            file_path: Path to export file

        Example:
            >>> logger.export_to_text("activity_log.txt")
        """
        formatted = self.get_formatted_entries()

        with open(file_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=== AgentClick V2 Activity Log ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total entries: {len(formatted)}\n")
            f.write("\n")

            # Entries (oldest first - reverse formatted list)
            for line in reversed(formatted):
                f.write(line + "\n")

        logger.info(f"Log exported to text: {file_path}")

    def export_to_json(self, file_path: str) -> None:
        """
        Export log to JSON format.

        Args:
            file_path: Path to export file

        Example:
            >>> logger.export_to_json("activity_log.json")
        """
        # Reverse entries for export (oldest first)
        export_data = {
            "generated": datetime.now().isoformat(),
            "entries": list(reversed(self.log_entries))
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Log exported to JSON: {file_path}")

    def save_log(self, file_path: str) -> None:
        """
        Save log to file for persistence.

        Args:
            file_path: Path to save file

        Example:
            >>> logger.save_log("activity_log.json")
        """
        self.export_to_json(file_path)

    def load_log(self, file_path: str) -> None:
        """
        Load log from file.

        Args:
            file_path: Path to load file

        Example:
            >>> logger.load_log("activity_log.json")
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"Log file not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load entries as they are in file (oldest first in file, so reverse for newest first)
            entries = data.get('entries', [])
            self.log_entries = list(reversed(entries))

            logger.info(f"Log loaded from file: {file_path} ({len(self.log_entries)} entries)")

        except Exception as e:
            logger.error(f"Failed to load log from {file_path}: {e}")
