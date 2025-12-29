"""
Mini Popup V2 - Compact display of workspace and agent information.

This module provides the MiniPopupV2 widget which displays the current workspace
and agent in a compact 80x60px popup format with emoji, name, and type icon.
"""
import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from models.workspace import Workspace
from models.virtual_agent import VirtualAgent

logger = logging.getLogger(__name__)


class MiniPopupV2(QWidget):
    """
    Mini popup widget displaying workspace and agent information.

    A compact 80x60px widget that shows:
    - Workspace emoji (left)
    - Agent name (center, truncated if needed)
    - Agent type icon (right: 📝 command, 🎯 skill, 🤖 agent)

    The background color matches the workspace color for visual context.

    Signals:
        workspace_switch_requested: Emitted when double-click to switch workspace

    Attributes:
        _workspace_emoji_label: QLabel showing workspace emoji
        _agent_name_label: QLabel showing agent name (truncated)
        _agent_type_icon_label: QLabel showing agent type icon

    Example:
        >>> popup = MiniPopupV2()
        >>> popup.update_display(workspace, agent)
        >>> popup.show()
    """

    # Signal emitted when double-click to switch workspace (AC: #5)
    # This signal should be connected to: workspace_manager.switch_to_next_workspace
    workspace_switch_requested = pyqtSignal()

    # Agent type to emoji mapping
    AGENT_TYPE_ICONS = {
        "command": "📝",
        "skill": "🎯",
        "agent": "🤖"
    }

    # Maximum length for agent name before truncation (AC: #2 - max 10-12 chars)
    MAX_AGENT_NAME_LENGTH = 12

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the MiniPopupV2 widget.

        Args:
            parent: Parent widget (optional)

        Example:
            >>> popup = MiniPopupV2()
        """
        super().__init__(parent)

        # Set fixed size (AC: #5)
        self.setFixedSize(80, 60)

        # Initialize labels
        self._workspace_emoji_label = QLabel()
        self._agent_name_label = QLabel()
        self._agent_type_icon_label = QLabel()

        # Setup layout
        self._setup_layout()

        # Apply default styling
        self._apply_default_style()

    def _setup_layout(self) -> None:
        """
        Setup the horizontal layout for the mini popup.

        Creates a QHBoxLayout with three elements:
        - Workspace emoji (left)
        - Agent name (center)
        - Agent type icon (right)
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Workspace emoji (left)
        self._workspace_emoji_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Set initial font size for emoji
        emoji_font = self._workspace_emoji_label.font()
        emoji_font.setPointSize(18)
        self._workspace_emoji_label.setFont(emoji_font)
        layout.addWidget(self._workspace_emoji_label)

        # Agent name (center, expanding)
        self._agent_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        name_font = self._agent_name_label.font()
        name_font.setPointSize(9)
        self._agent_name_label.setFont(name_font)
        layout.addWidget(self._agent_name_label, 1)  # Stretch = 1 to take available space

        # Agent type icon (right)
        self._agent_type_icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        type_font = self._agent_type_icon_label.font()
        type_font.setPointSize(16)
        self._agent_type_icon_label.setFont(type_font)
        layout.addWidget(self._agent_type_icon_label)

        self.setLayout(layout)

    def _apply_default_style(self, color: str = "#0078d4") -> None:
        """
        Apply default styling to the widget.

        Args:
            color: Background color in hex format (default: #0078d4)
        """
        self.setStyleSheet(f"""
            MiniPopupV2 {{
                background-color: {color};
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
            }}
            QLabel {{
                color: white;
                font-size: 9pt;
                background-color: transparent;
                border: none;
            }}
        """)

    def update_display(self, workspace: Optional[Workspace], agent: Optional[VirtualAgent]) -> None:
        """
        Update the popup display with workspace and agent information.

        Args:
            workspace: Workspace object (optional)
            agent: VirtualAgent object (optional)

        Example:
            >>> popup.update_display(workspace, agent)
        """
        # Update workspace emoji
        if workspace:
            self._workspace_emoji_label.setText(workspace.emoji)

            # Update background color from workspace
            self.set_workspace_color(workspace.color)

        # Update agent name
        if agent:
            truncated_name = self._truncate_agent_name(agent.name)
            self._agent_name_label.setText(truncated_name)

            # Update agent type icon with validation
            if agent.type not in self.AGENT_TYPE_ICONS:
                logger.warning(f"Unknown agent type: '{agent.type}', using default icon 📝")
            type_icon = self.AGENT_TYPE_ICONS.get(agent.type, "📝")
            self._agent_type_icon_label.setText(type_icon)

            # Update tooltip with hotkey hints
            workspace_name = workspace.name if workspace else 'Unknown'
            tooltip_text = (
                f"{workspace_name} - {agent.name} ({agent.type})\n"
                f"Press Pause to execute, Ctrl+Pause for next agent"
            )
            self.setToolTip(tooltip_text)

    def set_workspace_color(self, color: str) -> None:
        """
        Set the workspace background color.

        Args:
            color: Hex color code (e.g., "#0078d4")

        Example:
            >>> popup.set_workspace_color("#0078d4")
        """
        self._apply_default_style(color)

    def _truncate_agent_name(self, name: str) -> str:
        """
        Truncate agent name if it exceeds maximum length.

        Args:
            name: Agent name to truncate

        Returns:
            Truncated name with ellipsis if too long, otherwise original name

        Raises:
            ValueError: If name is None or not a string

        Example:
            >>> popup._truncate_agent_name("verify-py")
            'verify-py'
            >>> popup._truncate_agent_name("very-long-name")
            'very-long...'
        """
        if name is None or not isinstance(name, str):
            raise ValueError(f"Agent name must be a non-null string, got: {type(name)}")

        if len(name) <= self.MAX_AGENT_NAME_LENGTH:
            return name

        # Truncate and add ellipsis
        return name[:self.MAX_AGENT_NAME_LENGTH - 3] + "..."

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse double-click event (AC: #5).

        Emits workspace_switch_requested signal to trigger workspace switching.

        Args:
            event: Mouse double-click event

        Example:
            >>> When user double-clicks the mini popup, this method is called
            >>> and emits the workspace_switch_requested signal
        """
        super().mouseDoubleClickEvent(event)

        # Emit signal to request workspace switch (AC: #5)
        self.workspace_switch_requested.emit()

        logger.info("Mini popup double-clicked - workspace switch requested")
