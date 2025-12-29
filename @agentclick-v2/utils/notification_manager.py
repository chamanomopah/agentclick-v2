"""
Notification Manager - System tray notifications for AgentClick V2 (Story 11)

This module provides the NotificationManager class which handles:
- System tray icon notifications
- Success/error notifications
- Progress notifications for batch operations
- Notification queuing to prevent spam

Example:
    >>> manager = NotificationManager()
    >>> manager.show_notification(
    ...     title="AgentClick V2",
    ...     message="Agent executed successfully",
    ...     type="success"
    ... )
"""

import logging
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Notification type enumeration."""

    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# Notification duration constants
DEFAULT_NOTIFICATION_DURATION = 3000  # 3 seconds
ERROR_NOTIFICATION_DURATION = 5000    # 5 seconds


class NotificationManager(QObject):
    """
    Notification manager for system tray notifications.

    This manager handles system tray notifications with the following features:
    - System tray icon support
    - Success/error/info/warning notifications
    - Notification queuing to prevent rapid-fire spam
    - Progress notifications for batch operations

    Signals:
        notification_clicked: Emitted when notification is clicked

    Attributes:
        _tray_icon: QSystemTrayIcon instance
        _last_notification_time: Timestamp of last notification
        _notification_queue: Queue of pending notifications
        _min_interval: Minimum interval between notifications (ms)

    Example:
        >>> manager = NotificationManager()
        >>> manager.show_notification(
        ...     title="AgentClick V2",
        ...     message="Agent executed successfully",
        ...     type=NotificationType.SUCCESS
        ... )
    """

    notification_clicked = pyqtSignal()

    def __init__(self, min_interval_ms: int = 500):
        """
        Initialize NotificationManager.

        Args:
            min_interval_ms: Minimum interval between notifications (default: 500ms)

        Example:
            >>> manager = NotificationManager(min_interval_ms=1000)
        """
        super().__init__()

        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._last_notification_time: Optional[datetime] = None
        self._min_interval = min_interval_ms

        # Setup system tray icon
        self._setup_tray_icon()

        logger.info(f"NotificationManager initialized (min_interval={min_interval_ms}ms)")

    def _setup_tray_icon(self) -> None:
        """
        Setup system tray icon.

        Creates a QSystemTrayIcon if the system supports it.
        """
        # Check if system supports tray icons
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray not available on this system")
            return

        # Create tray icon
        self._tray_icon = QSystemTrayIcon()
        self._tray_icon.setToolTip("AgentClick V2")

        # Connect message clicked signal
        self._tray_icon.messageClicked.connect(self._on_message_clicked)

        # Show tray icon
        self._tray_icon.show()

        logger.debug("System tray icon created")

    def _on_message_clicked(self) -> None:
        """Handle notification message click."""
        self.notification_clicked.emit()
        logger.debug("Notification clicked")

    def show_notification(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        duration_ms: int = DEFAULT_NOTIFICATION_DURATION
    ) -> None:
        """
        Show a system tray notification.

        Args:
            title: Notification title
            message: Notification message
            type: Notification type (info, success, error, warning)
            duration_ms: Display duration in milliseconds (default: 3000)

        Example:
            >>> manager.show_notification(
            ...     title="AgentClick V2",
            ...     message="Agent executed successfully",
            ...     type=NotificationType.SUCCESS
            ... )
        """
        if not self._tray_icon:
            logger.warning("Cannot show notification: tray icon not available")
            return

        # Check minimum interval to prevent notification spam (only for non-error notifications)
        if type != NotificationType.ERROR and self._last_notification_time:
            elapsed = (datetime.now() - self._last_notification_time).total_seconds() * 1000
            if elapsed < self._min_interval:
                logger.debug(f"Notification suppressed (too soon: {elapsed}ms)")
                return

        # Map notification type to icon
        icon = self._get_icon_for_type(type)

        # Show notification
        try:
            self._tray_icon.showMessage(
                title,
                message,
                icon,
                duration_ms
            )

            self._last_notification_time = datetime.now()

            logger.debug(f"Notification shown: {title} - {message}")

        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

    def _get_icon_for_type(self, type: NotificationType) -> QSystemTrayIcon.MessageIcon:
        """
        Get system tray icon for notification type.

        Args:
            type: Notification type

        Returns:
            QSystemTrayIcon.MessageIcon
        """
        icon_map = {
            NotificationType.INFO: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.SUCCESS: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.ERROR: QSystemTrayIcon.MessageIcon.Critical,
            NotificationType.WARNING: QSystemTrayIcon.MessageIcon.Warning,
        }

        return icon_map.get(type, QSystemTrayIcon.MessageIcon.Information)

    def show_success(self, title: str, message: str) -> None:
        """
        Show success notification.

        Args:
            title: Notification title
            message: Notification message

        Example:
            >>> manager.show_success("AgentClick V2", "Agent executed successfully")
        """
        self.show_notification(title, message, NotificationType.SUCCESS)

    def show_error(self, title: str, message: str) -> None:
        """
        Show error notification.

        Args:
            title: Notification title
            message: Notification message

        Example:
            >>> manager.show_error("AgentClick V2 - Error", "Failed to execute agent")
        """
        self.show_notification(title, message, NotificationType.ERROR, duration_ms=ERROR_NOTIFICATION_DURATION)

    def show_info(self, title: str, message: str) -> None:
        """
        Show info notification.

        Args:
            title: Notification title
            message: Notification message

        Example:
            >>> manager.show_info("AgentClick V2", "Switched to Python workspace")
        """
        self.show_notification(title, message, NotificationType.INFO)

    def show_warning(self, title: str, message: str) -> None:
        """
        Show warning notification.

        Args:
            title: Notification title
            message: Notification message

        Example:
            >>> manager.show_warning("AgentClick V2", "No workspace selected")
        """
        self.show_notification(title, message, NotificationType.WARNING)

    def show_progress(self, current: int, total: int, message: str = "") -> None:
        """
        Show progress notification for batch operations.

        Args:
            current: Current item number
            total: Total number of items
            message: Optional additional message

        Example:
            >>> manager.show_progress(2, 3, "Processing file")
            # Shows: "Processing file 2/3..."
        """
        if message:
            notification_msg = f"{message} {current}/{total}..."
        else:
            notification_msg = f"Processing {current}/{total}..."

        self.show_notification(
            title="AgentClick V2",
            message=notification_msg,
            type=NotificationType.INFO
        )

    def clear_notifications(self) -> None:
        """
        Clear all pending notifications (not implemented in all systems).

        Example:
            >>> manager.clear_notifications()
        """
        # QSystemTrayIcon doesn't have a clear method
        # This is a placeholder for future enhancement
        logger.debug("Clear notifications called (no-op on most systems)")
