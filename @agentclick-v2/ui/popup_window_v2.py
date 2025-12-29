"""
Detailed Popup V2 - Main popup window with tabs.

This module provides the DetailedPopupV2 class which displays a larger
detailed popup window (600x500px) with Activity, Config, and Workspaces tabs.
"""
import logging
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QGroupBox, QTableWidget, QPushButton,
    QTableWidgetItem, QHeaderView, QLabel, QAbstractItemView,
    QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from models.workspace import Workspace
from core.workspace_manager import WorkspaceManager
from ui.workspace_dialog import WorkspaceDialog

logger = logging.getLogger(__name__)


class DetailedPopupV2(QMainWindow):
    """
    Detailed popup window with Activity, Config, and Workspaces tabs.

    A 600x500px window with three tabs:
    - 📋 Activity: Shows agent activity log (Story 11)
    - ⚙️ Config: Configuration and templates editor (Story 10)
    - 💼 Workspaces: Workspace management (this story)

    The Workspaces tab includes:
    - Current workspace section with details
    - List of all workspaces
    - Action buttons (Add, Edit, Switch, Delete)

    Attributes:
        workspace_manager: WorkspaceManager instance for workspace operations
        _current_workspace: Currently displayed workspace

    Example:
        >>> popup = DetailedPopupV2()
        >>> popup.set_workspace_manager(manager)
        >>> popup.update_current_workspace(workspace)
        >>> popup.show()
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the DetailedPopupV2 window.

        Args:
            parent: Parent widget (optional)

        Example:
            >>> popup = DetailedPopupV2()
        """
        super().__init__(parent)

        # Set window properties (AC: #1)
        self.setWindowTitle("AgentClick V2")
        self.setFixedSize(600, 500)

        # Initialize workspace manager reference
        self.workspace_manager: Optional[WorkspaceManager] = None
        self._current_workspace: Optional[Workspace] = None

        # Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Setup the user interface.

        Creates the tab widget with three tabs and their content.
        """
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create tab widget (AC: #1)
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Create tabs
        self._create_activity_tab()
        self._create_config_tab()
        self._create_workspaces_tab()

        # Add tab widget to layout
        main_layout.addWidget(self._tab_widget)

    def _create_activity_tab(self) -> None:
        """
        Create the Activity tab (placeholder for Story 11).

        This tab will show agent activity log in the future.
        """
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)

        # Placeholder label
        placeholder_label = QLabel("Activity log coming soon (Story 11)")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #888; font-size: 14pt;")
        layout.addWidget(placeholder_label)

        # Add tab (AC: #1 - 📋 Activity)
        self._tab_widget.addTab(activity_widget, "📋 Activity")

    def _create_config_tab(self) -> None:
        """
        Create the Config tab (placeholder for Story 10).

        This tab will show configuration and templates editor in the future.
        """
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)

        # Placeholder label
        placeholder_label = QLabel("Configuration editor coming soon (Story 10)")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #888; font-size: 14pt;")
        layout.addWidget(placeholder_label)

        # Add tab (AC: #1 - ⚙️ Config)
        self._tab_widget.addTab(config_widget, "⚙️ Config")

    def _create_workspaces_tab(self) -> None:
        """
        Create the Workspaces tab with current workspace and workspace list.

        Layout:
        - Current Workspace section (top)
        - All Workspaces list (middle)
        - Action buttons (bottom)
        """
        workspaces_widget = QWidget()
        layout = QVBoxLayout(workspaces_widget)
        layout.setSpacing(15)

        # Create current workspace section (AC: #2)
        self._current_workspace_group = QGroupBox("Current Workspace")
        self._current_workspace_group.setObjectName("current_workspace_group")
        current_layout = QVBoxLayout(self._current_workspace_group)

        # Current workspace details (placeholder labels)
        self._current_emoji_label = QLabel("Emoji: -")
        self._current_name_label = QLabel("Name: -")
        self._current_folder_label = QLabel("Folder: -")
        self._current_color_label = QLabel("Color: -")
        self._current_agents_label = QLabel("Agents: -")

        current_layout.addWidget(self._current_emoji_label)
        current_layout.addWidget(self._current_name_label)
        current_layout.addWidget(self._current_folder_label)
        current_layout.addWidget(self._current_color_label)
        current_layout.addWidget(self._current_agents_label)

        layout.addWidget(self._current_workspace_group)

        # Create workspace list section (AC: #3)
        list_group = QGroupBox("All Workspaces")
        list_layout = QVBoxLayout(list_group)

        # Create table widget
        self._workspace_table = QTableWidget()
        self._workspace_table.setObjectName("workspace_list_table")
        self._workspace_table.setColumnCount(4)
        self._workspace_table.setHorizontalHeaderLabels(["", "Name", "Emoji", "Agents"])
        self._workspace_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._workspace_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._workspace_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        list_layout.addWidget(self._workspace_table)
        layout.addWidget(list_group)

        # Create action buttons (AC: #4)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self._add_button = QPushButton("Add Workspace")
        self._add_button.setObjectName("add_workspace_button")
        self._add_button.clicked.connect(self._on_add_workspace)
        self._edit_button = QPushButton("Edit Workspace")
        self._edit_button.setObjectName("edit_workspace_button")
        self._edit_button.clicked.connect(self._on_edit_workspace)
        self._switch_button = QPushButton("Switch Workspace")
        self._switch_button.setObjectName("switch_workspace_button")
        self._switch_button.clicked.connect(self._on_switch_workspace)
        self._delete_button = QPushButton("Delete Workspace")
        self._delete_button.setObjectName("delete_workspace_button")
        self._delete_button.clicked.connect(self._on_delete_workspace)

        buttons_layout.addWidget(self._add_button)
        buttons_layout.addWidget(self._edit_button)
        buttons_layout.addWidget(self._switch_button)
        buttons_layout.addWidget(self._delete_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Add tab (AC: #1 - 💼 Workspaces)
        self._tab_widget.addTab(workspaces_widget, "💼 Workspaces")

    def set_workspace_manager(self, manager: WorkspaceManager) -> None:
        """
        Set the workspace manager for workspace operations.

        Args:
            manager: WorkspaceManager instance

        Example:
            >>> popup.set_workspace_manager(manager)
        """
        self.workspace_manager = manager
        logger.info("Workspace manager set for DetailedPopupV2")

    def connect_mini_popup_double_click(self, mini_popup: 'MiniPopupV2') -> None:
        """
        Connect mini popup double-click signal to workspace switching.

        This connects the mini popup's workspace_switch_requested signal
        to switch to the next workspace via the workspace manager.

        Args:
            mini_popup: MiniPopupV2 instance to connect

        Example:
            >>> popup.connect_mini_popup_double_click(mini_popup)
            >>> # Now double-clicking mini popup will switch workspace
        """
        if not self.workspace_manager:
            logger.warning("Cannot connect mini popup: no workspace manager set")
            return

        mini_popup.workspace_switch_requested.connect(
            self.workspace_manager.switch_to_next_workspace
        )
        logger.info("Mini popup double-click connected to workspace switching")

    def update_current_workspace(self, workspace: Workspace) -> None:
        """
        Update the current workspace display.

        Updates the window title and current workspace section
        with the provided workspace information.

        Args:
            workspace: Workspace object to display

        Example:
            >>> popup.update_current_workspace(workspace)
        """
        self._current_workspace = workspace

        # Update window title (AC: #1)
        self.setWindowTitle(f"AgentClick V2 - {workspace.name}")

        # Update current workspace section (AC: #2)
        self._current_emoji_label.setText(f"Emoji: {workspace.emoji}")
        self._current_name_label.setText(f"Name: {workspace.name}")
        self._current_folder_label.setText(f"Folder: {workspace.folder}")
        self._current_color_label.setText(f"Color: {workspace.color}")

        # Defensive check for agents attribute (FIX #6)
        agent_count = len(workspace.agents) if workspace.agents else 0
        self._current_agents_label.setText(f"Agents: {agent_count} active")

        # Style the current workspace section with workspace color
        self._apply_workspace_color(workspace.color)

    def _apply_workspace_color(self, color: str) -> None:
        """
        Apply workspace color to current workspace section.

        Args:
            color: Hex color code (e.g., "#0078d4")
        """
        self._current_workspace_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {color};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

    def refresh_workspace_list(self) -> None:
        """
        Refresh the workspace list from the workspace manager.

        Loads all workspaces from the manager and updates the table.
        Highlights the current workspace.

        Example:
            >>> popup.refresh_workspace_list()
        """
        if not self.workspace_manager:
            logger.warning("Cannot refresh workspace list: no workspace manager set")
            return

        # Clear existing rows
        self._workspace_table.setRowCount(0)

        # Get all workspaces
        workspaces = self.workspace_manager.list_workspaces()

        # Populate table
        for row, workspace in enumerate(workspaces):
            self._workspace_table.insertRow(row)

            # Checkbox column (for enabled/disabled state - future use)
            checkbox_item = QTableWidgetItem()
            checkbox_item.setCheckState(Qt.CheckState.Checked)
            self._workspace_table.setItem(row, 0, checkbox_item)

            # Name column
            name_item = QTableWidgetItem(workspace.name)
            self._workspace_table.setItem(row, 1, name_item)

            # Emoji column
            emoji_item = QTableWidgetItem(workspace.emoji)
            self._workspace_table.setItem(row, 2, emoji_item)

            # Agent count column - defensive check (FIX #6)
            agent_count = len(workspace.agents) if workspace.agents else 0
            agents_item = QTableWidgetItem(str(agent_count))
            self._workspace_table.setItem(row, 3, agents_item)

            # Highlight current workspace
            if self.workspace_manager.current_workspace_id == workspace.id:
                self._workspace_table.selectRow(row)

        # Update delete button state (AC: #4)
        self._update_delete_button_state()

    def _update_delete_button_state(self) -> None:
        """
        Update delete button state based on workspace count.

        Disables delete button if only one workspace exists.
        """
        if not self.workspace_manager:
            return

        workspace_count = len(self.workspace_manager.workspaces)
        # Disable delete if only one workspace (AC: #4)
        self._delete_button.setEnabled(workspace_count > 1)
        if workspace_count <= 1:
            self._delete_button.setToolTip("Cannot delete last workspace")
        else:
            self._delete_button.setToolTip("Delete selected workspace")

    def _on_add_workspace(self) -> None:
        """
        Handle Add Workspace button click.

        Opens WorkspaceDialog in create mode and adds the workspace
        if accepted.
        """
        if not self.workspace_manager:
            QMessageBox.warning(
                self,
                "Error",
                "Workspace manager not initialized"
            )
            return

        # Open dialog in create mode (AC: #4) - pass workspace_manager for duplicate ID validation
        dialog = WorkspaceDialog(mode="create", workspace_manager=self.workspace_manager, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Get workspace config from dialog
                config = dialog.get_workspace_config()

                # Add workspace via manager
                self.workspace_manager.add_workspace(config)

                # Refresh list
                self.refresh_workspace_list()

                logger.info(f"Added workspace: {config['id']}")

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add workspace: {str(e)}"
                )
                logger.error(f"Failed to add workspace: {e}")

    def _on_edit_workspace(self) -> None:
        """
        Handle Edit Workspace button click.

        Opens WorkspaceDialog in edit mode for the selected workspace
        and updates it if accepted.
        """
        if not self.workspace_manager:
            QMessageBox.warning(
                self,
                "Error",
                "Workspace manager not initialized"
            )
            return

        # Get selected workspace
        selected_row = self._workspace_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a workspace to edit"
            )
            return

        # Get workspace ID from selected row
        workspaces = list(self.workspace_manager.workspaces.values())
        if selected_row >= len(workspaces):
            return

        workspace = workspaces[selected_row]

        # Open dialog in edit mode (AC: #4) - pass workspace_manager for validation
        dialog = WorkspaceDialog(mode="edit", workspace=workspace, workspace_manager=self.workspace_manager, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Get updates from dialog
                updates = dialog.get_workspace_config()

                # Remove 'id' from updates (can't change ID)
                updates.pop('id', None)

                # Update workspace via manager
                self.workspace_manager.update_workspace(workspace.id, updates)

                # Refresh list
                self.refresh_workspace_list()

                # Update current workspace display if it was edited
                if workspace.id == self.workspace_manager.current_workspace_id:
                    updated_workspace = self.workspace_manager.workspaces[workspace.id]
                    self.update_current_workspace(updated_workspace)

                logger.info(f"Edited workspace: {workspace.id}")

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to edit workspace: {str(e)}"
                )
                logger.error(f"Failed to edit workspace: {e}")

    def _on_switch_workspace(self) -> None:
        """
        Handle Switch Workspace button click.

        Switches to the selected workspace.
        """
        if not self.workspace_manager:
            QMessageBox.warning(
                self,
                "Error",
                "Workspace manager not initialized"
            )
            return

        # Get selected workspace
        selected_row = self._workspace_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a workspace to switch to"
            )
            return

        # Get workspace ID from selected row
        workspaces = list(self.workspace_manager.workspaces.values())
        if selected_row >= len(workspaces):
            return

        workspace = workspaces[selected_row]

        # Don't switch if already current
        if workspace.id == self.workspace_manager.current_workspace_id:
            QMessageBox.information(
                self,
                "Already Current",
                f"This is already the current workspace"
            )
            return

        try:
            # Switch workspace (AC: #4)
            self.workspace_manager.switch_workspace(workspace.id)

            # Update display
            self.update_current_workspace(workspace)

            # Refresh list to highlight new current workspace
            self.refresh_workspace_list()

            logger.info(f"Switched to workspace: {workspace.id}")

        except Exception as e:
            # Improved error handling (FIX #5)
            error_type = type(e).__name__
            if error_type == "WorkspaceNotFoundError":
                QMessageBox.critical(
                    self,
                    "Workspace Not Found",
                    f"The selected workspace no longer exists.\n\nPlease refresh the workspace list."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Switch Failed",
                    f"Failed to switch workspace:\n{str(e)}\n\nPlease check the logs for details."
                )
            logger.error(f"Failed to switch workspace: {e}", exc_info=True)

    def _on_delete_workspace(self) -> None:
        """
        Handle Delete Workspace button click.

        Deletes the selected workspace after confirmation.
        """
        if not self.workspace_manager:
            QMessageBox.warning(
                self,
                "Error",
                "Workspace manager not initialized"
            )
            return

        # Get selected workspace
        selected_row = self._workspace_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a workspace to delete"
            )
            return

        # Get workspace ID from selected row
        workspaces = list(self.workspace_manager.workspaces.values())
        if selected_row >= len(workspaces):
            return

        workspace = workspaces[selected_row]

        # Confirm deletion (AC: #4)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the workspace '{workspace.name}'?\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete workspace via manager (AC: #4)
                self.workspace_manager.remove_workspace(workspace.id)

                # Refresh list
                self.refresh_workspace_list()

                # Update current workspace display if it was deleted
                current_workspace = self.workspace_manager.get_current_workspace()
                if current_workspace:
                    self.update_current_workspace(current_workspace)

                logger.info(f"Deleted workspace: {workspace.id}")

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete workspace: {str(e)}"
                )
                logger.error(f"Failed to delete workspace: {e}")
