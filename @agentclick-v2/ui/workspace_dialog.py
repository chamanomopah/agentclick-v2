"""
Workspace Dialog - Dialog for creating and editing workspaces.

This module provides the WorkspaceDialog class which offers a form
interface for creating new workspaces or editing existing ones.
"""
import logging
import re
from pathlib import Path
from typing import Tuple, Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QColorDialog,
    QFileDialog, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from models.workspace import Workspace
from core.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


class WorkspaceDialog(QDialog):
    """
    Dialog for creating or editing workspace configurations.

    Provides a form with the following fields:
    - ID: Alphanumeric identifier (required, readonly in edit mode)
    - Name: Human-readable name (required)
    - Folder: Path to workspace folder (must exist)
    - Emoji: Emoji icon (optional, with defaults)
    - Color: Hex color code (with color picker dialog)

    The dialog validates inputs before accepting and shows appropriate
    error messages for invalid data.

    Attributes:
        mode: Either "create" or "edit"
        workspace_id: Current workspace ID (None in create mode)

    Example:
        >>> # Create mode
        >>> dialog = WorkspaceDialog(mode="create")
        >>> if dialog.exec() == QDialog.DialogCode.Accepted:
        ...     config = dialog.get_workspace_config()
        ...     # Use config to create workspace

        >>> # Edit mode
        >>> dialog = WorkspaceDialog(mode="edit", workspace=workspace)
        >>> if dialog.exec() == QDialog.DialogCode.Accepted:
        ...     updates = dialog.get_workspace_config()
        ...     # Use updates to modify workspace
    """

    def __init__(self, mode: str = "create", workspace: Optional[Workspace] = None,
                 workspace_manager: Optional[WorkspaceManager] = None, parent=None) -> None:
        """
        Initialize the WorkspaceDialog.

        Args:
            mode: Either "create" or "edit"
            workspace: Existing workspace (required for edit mode)
            workspace_manager: WorkspaceManager instance for duplicate ID validation (optional)
            parent: Parent widget (optional)

        Raises:
            ValueError: If mode is invalid or workspace missing for edit mode

        Example:
            >>> dialog = WorkspaceDialog(mode="create", workspace_manager=manager)
            >>> dialog = WorkspaceDialog(mode="edit", workspace=existing, workspace_manager=manager)
        """
        super().__init__(parent)

        # Validate mode
        if mode not in ["create", "edit"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'create' or 'edit'")

        if mode == "edit" and workspace is None:
            raise ValueError("Workspace must be provided for edit mode")

        self.mode = mode
        self._workspace = workspace
        self._workspace_manager = workspace_manager

        # Setup dialog
        self._setup_dialog()

        # Populate fields if in edit mode
        if mode == "edit" and workspace:
            self._populate_fields()

    def _setup_dialog(self) -> None:
        """
        Setup the dialog UI.

        Creates form layout with all input fields and buttons.
        """
        # Set window title based on mode (AC: #4)
        title = "Add Workspace" if self.mode == "create" else "Edit Workspace"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(450)

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Create form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # ID field (AC: #4)
        self._id_field = QLineEdit()
        self._id_field.setPlaceholderText("e.g., python-projects")
        self._id_field.setObjectName("id_field")

        # In edit mode, ID is readonly (AC: #4)
        if self.mode == "edit":
            self._id_field.setReadOnly(True)

        form_layout.addRow("ID:", self._id_field)

        # Name field (AC: #4)
        self._name_field = QLineEdit()
        self._name_field.setPlaceholderText("e.g., Python Projects")
        self._name_field.setObjectName("name_field")
        form_layout.addRow("Name:", self._name_field)

        # Folder field with browse button (AC: #4)
        folder_layout = QHBoxLayout()
        self._folder_field = QLineEdit()
        self._folder_field.setPlaceholderText("e.g., C:\\projects")
        self._folder_field.setObjectName("folder_field")
        folder_layout.addWidget(self._folder_field)

        self._browse_button = QPushButton("Browse...")
        self._browse_button.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self._browse_button)

        form_layout.addRow("Folder:", folder_layout)

        # Emoji field (AC: #4)
        self._emoji_field = QLineEdit()
        self._emoji_field.setPlaceholderText("e.g., 🐍")
        self._emoji_field.setMaxLength(2)  # Most emojis are 1-2 chars
        self._emoji_field.setObjectName("emoji_field")
        form_layout.addRow("Emoji:", self._emoji_field)

        # Color field with color picker button (AC: #4)
        color_layout = QHBoxLayout()
        self._color_field = QLineEdit()
        self._color_field.setText("#0078d4")  # Default color
        self._color_field.setObjectName("color_field")
        self._color_field.setMaxLength(7)  # #RRGGBB format
        color_layout.addWidget(self._color_field)

        self._color_button = QPushButton("Pick Color")
        self._color_button.clicked.connect(self._pick_color)
        color_layout.addWidget(self._color_button)

        form_layout.addRow("Color:", color_layout)

        # Add form layout to main layout
        layout.addLayout(form_layout)

        # Add help text
        help_label = QLabel(
            "<i>ID must contain only letters, numbers, and hyphens/underscores.<br>"
            "Folder must be an existing directory.</i>"
        )
        help_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(help_label)

        # Add button box (AC: #4)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _populate_fields(self) -> None:
        """
        Populate form fields from workspace (edit mode).

        Fills all fields with data from the existing workspace.
        """
        if not self._workspace:
            return

        self._id_field.setText(self._workspace.id)
        self._name_field.setText(self._workspace.name)
        self._folder_field.setText(str(self._workspace.folder))
        self._emoji_field.setText(self._workspace.emoji)
        self._color_field.setText(self._workspace.color)

    def _browse_folder(self) -> None:
        """
        Open folder browser dialog.

        Updates the folder field with the selected path.
        """
        # Get current folder as starting point
        current_folder = self._folder_field.text()
        if current_folder and Path(current_folder).exists():
            start_dir = current_folder
        else:
            start_dir = str(Path.home())

        # Open folder dialog
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Workspace Folder",
            start_dir
        )

        if folder:
            self._folder_field.setText(folder)

    def _pick_color(self) -> None:
        """
        Open color picker dialog.

        Updates the color field with the selected color in hex format.
        """
        # Get current color
        current_color = self._color_field.text()

        # Try to parse current color
        try:
            color = QColor(current_color)
        except:
            color = QColor("#0078d4")  # Default if invalid

        # Open color dialog
        selected_color = QColorDialog.getColor(
            color,
            self,
            "Select Workspace Color"
        )

        if selected_color.isValid():
            self._color_field.setText(selected_color.name())

    def validate(self) -> Tuple[bool, str]:
        """
        Validate the form inputs.

        Checks all fields for valid data according to workspace requirements:
        - ID: Alphanumeric with hyphens/underscores only, unique (in create mode)
        - Name: Required, non-empty
        - Folder: Must exist as directory
        - Emoji: Optional, any Unicode
        - Color: Valid hex color code (#RRGGBB)

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> is_valid, error = dialog.validate()
            >>> if not is_valid:
            ...     print(f"Error: {error}")
        """
        # Validate ID (only in create mode)
        if self.mode == "create":
            workspace_id = self._id_field.text().strip()
            if not workspace_id:
                return False, "Workspace ID is required"

            # Check ID format: alphanumeric, hyphens, underscores only
            if not re.match(r'^[a-zA-Z0-9_-]+$', workspace_id):
                return False, (
                    "Workspace ID must contain only letters, numbers, "
                    "hyphens (-), and underscores (_)"
                )

            # Check for duplicate workspace ID (CRITICAL FIX #1)
            if self._workspace_manager and workspace_id in self._workspace_manager.workspaces:
                return False, f"Workspace ID '{workspace_id}' already exists. Please choose a unique ID."

        # Validate name
        name = self._name_field.text().strip()
        if not name:
            return False, "Workspace name is required"

        # Validate folder
        folder_path = self._folder_field.text().strip()
        if not folder_path:
            return False, "Workspace folder is required"

        folder = Path(folder_path)
        if not folder.exists():
            return False, f"Folder does not exist: {folder_path}"

        if not folder.is_dir():
            return False, f"Path is not a directory: {folder_path}"

        # Validate emoji (optional, but if provided check length)
        emoji = self._emoji_field.text().strip()
        if emoji and len(emoji) > 10:  # Reasonable limit for emojis
            return False, "Emoji is too long (max 10 characters)"

        # Validate color format
        color = self._color_field.text().strip()
        if not color:
            return False, "Workspace color is required"

        # Check hex color format (#RRGGBB)
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return False, "Color must be in hex format (#RRGGBB)"

        # All validations passed
        return True, ""

    def accept(self) -> None:
        """
        Override accept to validate before closing.

        Shows error message if validation fails.
        """
        is_valid, error = self.validate()

        if not is_valid:
            QMessageBox.warning(
                self,
                "Validation Error",
                error,
                QMessageBox.StandardButton.Ok
            )
            return

        # Call parent accept
        super().accept()

    def get_workspace_config(self) -> Dict[str, str]:
        """
        Get the workspace configuration from form fields.

        Returns a dictionary with all workspace fields that can be used
        to create or update a workspace.

        Returns:
            Dictionary with keys: id, name, folder, emoji, color

        Example:
            >>> config = dialog.get_workspace_config()
            >>> manager.add_workspace(config)
        """
        return {
            'id': self._id_field.text().strip(),
            'name': self._name_field.text().strip(),
            'folder': self._folder_field.text().strip(),
            'emoji': self._emoji_field.text().strip() or "📁",  # Default emoji
            'color': self._color_field.text().strip()
        }

    # Getter methods for testing
    def get_id(self) -> str:
        """Get the current ID field value."""
        return self._id_field.text()

    def get_name(self) -> str:
        """Get the current name field value."""
        return self._name_field.text()

    def get_folder(self) -> str:
        """Get the current folder field value."""
        return self._folder_field.text()

    def get_emoji(self) -> str:
        """Get the current emoji field value."""
        return self._emoji_field.text()

    def get_color(self) -> str:
        """Get the current color field value."""
        return self._color_field.text()

    # Setter methods for testing
    def set_id(self, value: str) -> None:
        """Set the ID field value."""
        self._id_field.setText(value)

    def set_name(self, value: str) -> None:
        """Set the name field value."""
        self._name_field.setText(value)

    def set_folder(self, value: str) -> None:
        """Set the folder field value."""
        self._folder_field.setText(value)

    def set_emoji(self, value: str) -> None:
        """Set the emoji field value."""
        self._emoji_field.setText(value)

    def set_color(self, value: str) -> None:
        """Set the color field value."""
        self._color_field.setText(value)
