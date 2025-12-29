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
    QDialog, QMessageBox, QTextEdit, QListWidget, QListWidgetItem,
    QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QShortcut, QKeySequence, QFont, QTextCharFormat, QSyntaxHighlighter

from models.workspace import Workspace
from models.virtual_agent import VirtualAgent
from core.workspace_manager import WorkspaceManager
from core.template_engine import TemplateEngine
from ui.workspace_dialog import WorkspaceDialog

logger = logging.getLogger(__name__)


class TemplateSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for template variables.

    Highlights {{variable}} patterns in blue bold text.
    """

    def __init__(self, document):
        """Initialize the highlighter with a document."""
        super().__init__(document)

    def highlightBlock(self, text: str) -> None:
        """
        Highlight {{variable}} patterns in the text block.

        Args:
            text: The text block to highlight
        """
        import re

        # Pattern to match {{variable_name}}
        pattern = re.compile(r'\{\{(\w+)\}\}')

        for match in pattern.finditer(text):
            # Create format for template variables
            format = QTextCharFormat()
            format.setForeground(QColor("#0066cc"))
            format.setFontWeight(QFont.Weight.Bold)

            # Apply formatting to the matched range
            self.setFormat(match.start(), match.end() - match.start(), format)


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

    # Constants for template preview sample data
    SAMPLE_INPUT = '<sample input>'
    SAMPLE_CONTEXT_FOLDER = 'C:/example'
    SAMPLE_FOCUS_FILE = 'main.py'

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
        self._current_agent_id: Optional[str] = None

        # Template engine for config tab
        self._template_engine = TemplateEngine()

        # Unsaved template changes tracking
        self._unsaved_template_changes = False
        self._last_saved_template = ""

        # Preview debounce timer
        self._preview_debounce_timer = QTimer()
        self._preview_debounce_timer.setSingleShot(True)
        self._preview_debounce_timer.timeout.connect(self._debounced_preview_update)

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
        Create the Config tab with template editor and agent management.

        This tab provides:
        - Current workspace and agent information
        - Input template editor with live preview
        - Agent list with enable/disable checkboxes
        - Scan for new agents button
        - Save template button

        Layout matches the specification in the story.
        """
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        layout.setSpacing(15)

        # === Header Section: Current Workspace and Agent ===
        self._current_workspace_label = QLabel("Current Workspace: -")
        self._current_workspace_label.setObjectName("current_workspace_label")
        self._current_workspace_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self._current_agent_label = QLabel("Current Agent: -")
        self._current_agent_label.setObjectName("current_agent_label")
        self._current_agent_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        layout.addWidget(self._current_workspace_label)
        layout.addWidget(self._current_agent_label)

        # === Input Template Section ===
        template_group = QGroupBox("Input Template")
        template_layout = QVBoxLayout(template_group)

        # Template editor (QTextEdit)
        self._template_editor = QTextEdit()
        self._template_editor.setObjectName("template_editor")
        self._template_editor.setPlaceholderText("Enter template using {{input}}, {{context_folder}}, {{focus_file}}...")
        self._template_editor.setMaximumHeight(100)

        # Add syntax highlighting for template variables
        self._template_highlighter = TemplateSyntaxHighlighter(self._template_editor.document())

        # Connect with debouncing (500ms delay)
        self._template_editor.textChanged.connect(self._on_template_changed_debounced)
        template_layout.addWidget(self._template_editor)

        # Live preview
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        template_layout.addWidget(preview_label)

        self._template_preview = QLabel()
        self._template_preview.setObjectName("template_preview")
        self._template_preview.setWordWrap(True)
        self._template_preview.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        self._template_preview.setMaximumHeight(80)
        self._template_preview.setText("<sample preview>")
        template_layout.addWidget(self._template_preview)

        # Validation error label
        self._validation_error_label = QLabel()
        self._validation_error_label.setObjectName("validation_error_label")
        self._validation_error_label.setWordWrap(True)
        self._validation_error_label.setStyleSheet("color: red;")
        self._validation_error_label.setVisible(False)
        template_layout.addWidget(self._validation_error_label)

        layout.addWidget(template_group)

        # === Available Agents Section ===
        agents_group = QGroupBox("Available Agents")
        agents_layout = QVBoxLayout(agents_group)

        # Agent list with checkboxes
        self._agent_list = QListWidget()
        self._agent_list.setObjectName("agent_list")
        self._agent_list.setMaximumHeight(120)
        agents_layout.addWidget(self._agent_list)

        layout.addWidget(agents_group)

        # === Action Buttons ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self._scan_agents_button = QPushButton("Scan for New Agents")
        self._scan_agents_button.setObjectName("scan_agents_button")
        self._scan_agents_button.clicked.connect(self._on_scan_agents)
        buttons_layout.addWidget(self._scan_agents_button)

        self._save_template_button = QPushButton("Save Template")
        self._save_template_button.setObjectName("save_template_button")
        self._save_template_button.clicked.connect(self._on_save_template)
        buttons_layout.addWidget(self._save_template_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Add tab (AC: #1 - ⚙️ Config)
        self._tab_widget.addTab(config_widget, "⚙️ Config")

        # Setup keyboard shortcuts (UX enhancement)
        self._setup_keyboard_shortcuts()

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

    # === Config Tab Methods ===

    def update_config_tab_workspace(self, workspace: Workspace, agent_id: Optional[str] = None) -> None:
        """
        Update the Config tab with workspace and agent information.

        Args:
            workspace: Current workspace
            agent_id: Optional current agent ID
        """
        # Store current workspace and agent ID
        self._current_workspace = workspace
        self._current_agent_id = agent_id

        # Update labels
        self._current_workspace_label.setText(f"Current Workspace: {workspace.name}")
        if agent_id:
            self._current_agent_label.setText(f"Current Agent: {agent_id}")
        else:
            self._current_agent_label.setText("Current Agent: -")

        # Populate agent list if workspace has agents
        if workspace.agents:
            self.populate_config_agent_list(workspace)

    def populate_config_agent_list(self, workspace: Workspace) -> None:
        """
        Populate the agent list with agents from the workspace.

        Args:
            workspace: Workspace containing agents
        """
        self._agent_list.clear()

        if not workspace.agents:
            return

        for agent in workspace.agents:
            # Create list item with emoji and name
            item_text = f"{agent.emoji} {agent.name} ({agent.id})"
            item = QListWidgetItem(item_text, self._agent_list)

            # Set checkbox state based on enabled status
            check_state = Qt.CheckState.Checked if agent.enabled else Qt.CheckState.Unchecked
            item.setCheckState(check_state)

            # Store agent reference in item data
            item.setData(Qt.ItemDataRole.UserRole, agent)

            self._agent_list.addItem(item)

        # Connect checkbox state change to handler (once, not in loop)
        try:
            self._agent_list.itemChanged.disconnect()
        except TypeError:
            pass  # No connections yet
        self._agent_list.itemChanged.connect(self._on_agent_checkbox_changed)

    def _on_agent_checkbox_changed(self, item: 'QListWidgetItem') -> None:
        """
        Handle agent checkbox state change.

        Updates agent enabled state and persists changes to workspaces.yaml.

        Args:
            item: List item that was changed
        """
        agent = item.data(Qt.ItemDataRole.UserRole)
        if agent and isinstance(agent, VirtualAgent):
            # Update agent enabled state
            agent.enabled = (item.checkState() == Qt.CheckState.Checked)
            logger.info(f"Agent {agent.id} enabled: {agent.enabled}")

            # Persist changes to workspaces.yaml (FIX: was missing)
            if self.workspace_manager and self._current_workspace:
                try:
                    self.workspace_manager.save_workspaces()
                    logger.info(f"Persisted agent state for {agent.id}")
                except Exception as e:
                    logger.error(f"Failed to persist agent state: {e}")
                    QMessageBox.warning(
                        self,
                        "Save Failed",
                        f"Agent state updated in memory but not saved to disk.\n\nError: {str(e)}"
                    )

    def _on_template_changed_debounced(self) -> None:
        """
        Handle template editor text change with debouncing.

        Restarts the debounce timer (500ms delay) to avoid excessive updates.
        """
        # Track unsaved changes
        template_text = self._template_editor.toPlainText()
        self._unsaved_template_changes = (template_text != self._last_saved_template)

        # Restart debounce timer
        self._preview_debounce_timer.start(500)

    def _debounced_preview_update(self) -> None:
        """
        Update preview and validation after debounce timer expires.

        Called 500ms after the last keystroke to avoid excessive updates.
        """
        self._on_template_changed()

    def _on_template_changed(self) -> None:
        """
        Handle template editor text change.

        Updates the live preview and validates the template.
        """
        template_text = self._template_editor.toPlainText()

        # Update preview
        self.update_template_preview()

        # Validate template
        validation = self.validate_template_text(template_text)

        # Show/hide validation errors
        if validation['errors']:
            self._validation_error_label.setText("\n".join(validation['errors']))
            self._validation_error_label.setVisible(True)
            self._save_template_button.setEnabled(False)
        else:
            self._validation_error_label.setVisible(False)
            self._save_template_button.setEnabled(True)

    def _warn_if_unsaved_changes(self) -> bool:
        """
        Warn user about unsaved template changes.

        Shows a dialog asking the user to save, discard, or cancel.

        Returns:
            True if user wants to continue (saved or discarded), False if cancelled
        """
        if not self._unsaved_template_changes:
            return True

        reply = QMessageBox.question(
            self,
            "Unsaved Template Changes",
            "You have unsaved template changes.\n\nDo you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )

        if reply == QMessageBox.StandardButton.Save:
            # Save and continue
            self._on_save_template()
            return self._unsaved_template_changes is False  # Check if save succeeded
        elif reply == QMessageBox.StandardButton.Discard:
            # Discard changes and continue
            self._unsaved_template_changes = False
            return True
        else:  # Cancel
            # Don't continue
            return False

    def update_template_preview(self) -> None:
        """
        Update the template preview with sample data.

        Uses sample data constants for consistent preview rendering.
        """
        template_text = self._template_editor.toPlainText()

        if not template_text.strip():
            self._template_preview.setText("<sample preview>")
            return

        # Create template engine for preview
        engine = TemplateEngine()

        # Use class constants for sample data
        sample_vars = {
            'input': self.SAMPLE_INPUT,
            'context_folder': self.SAMPLE_CONTEXT_FOLDER,
            'focus_file': self.SAMPLE_FOCUS_FILE
        }

        # Simple variable substitution for preview
        preview_text = template_text
        preview_text = preview_text.replace('{{input}}', sample_vars['input'])
        preview_text = preview_text.replace('{{context_folder}}', sample_vars['context_folder'])
        preview_text = preview_text.replace('{{focus_file}}', sample_vars['focus_file'])

        self._template_preview.setText(preview_text)

    def validate_template_text(self, template: str) -> dict:
        """
        Validate template text and return validation result.

        Args:
            template: Template text to validate

        Returns:
            Dictionary with 'is_valid', 'errors', and 'warnings' keys
        """
        engine = TemplateEngine()
        validation_result = engine.validate_template(template)

        return {
            'is_valid': validation_result.is_valid,
            'errors': validation_result.errors,
            'warnings': validation_result.warnings
        }

    def _on_save_template(self) -> None:
        """
        Handle Save Template button click.

        Validates and saves the current template to input_templates.yaml.
        Tracks saved state to detect unsaved changes.
        """
        template_text = self._template_editor.toPlainText()

        # Validate template
        validation = self.validate_template_text(template_text)

        if not validation['is_valid']:
            QMessageBox.warning(
                self,
                "Invalid Template",
                "Template has errors:\n" + "\n".join(validation['errors'])
            )
            return

        # Use stored agent ID instead of parsing label
        if not self._current_agent_id:
            QMessageBox.warning(
                self,
                "No Agent Selected",
                "Please select an agent to save its template."
            )
            return

        agent_id = self._current_agent_id

        try:
            # Save template
            engine = TemplateEngine()
            engine.save_template(agent_id, template_text, enabled=True)

            # Track saved state to detect unsaved changes
            self._last_saved_template = template_text
            self._unsaved_template_changes = False

            # Show success message
            QMessageBox.information(
                self,
                "Template Saved",
                f"Template for '{agent_id}' saved successfully."
            )

            logger.info(f"Saved template for agent: {agent_id}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save template:\n{str(e)}"
            )
            logger.error(f"Failed to save template for {agent_id}: {e}")

    def _on_scan_agents(self) -> None:
        """
        Handle Scan for New Agents button click.

        Triggers DynamicAgentLoader.scan_all() to discover new agents,
        updates the agent list, and shows a notification with the count.
        """
        import asyncio
        from core.agent_loader import DynamicAgentLoader

        # Show progress dialog
        progress = QProgressDialog(
            "Scanning for new agents...",
            "Cancel",
            0, 0,  # min, max (0,0 means indeterminate progress)
            self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Scanning Agents")
        progress.show()

        # Process events to ensure dialog renders
        QApplication.processEvents()

        try:
            # Run async scan in event loop
            loader = DynamicAgentLoader()

            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run the async scan
            new_agents = loop.run_until_complete(loader.scan_all())

            progress.close()

            # Update agent list if workspace is set
            if self._current_workspace and self.workspace_manager:
                # Refresh workspace from manager to get updated agents
                try:
                    updated_workspace = self.workspace_manager.get_workspace(self._current_workspace.id)
                    if updated_workspace:
                        self._current_workspace = updated_workspace
                        self.populate_config_agent_list(self._current_workspace)
                except Exception as e:
                    logger.warning(f"Could not refresh workspace after scan: {e}")

            # Show notification with count
            QMessageBox.information(
                self,
                "Scan Complete",
                f"Scanned {len(new_agents)} total agents.\n\n"
                f"Found agents from:\n"
                f"  • .claude/commands/ (command agents)\n"
                f"  • .claude/skills/ (skill agents)\n"
                f"  • .claude/agents/ (custom agents)"
            )

            logger.info(f"Scan complete: found {len(new_agents)} agents")

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Scan Failed",
                f"Failed to scan for new agents:\n\n{str(e)}\n\n"
                f"Please check the logs for details."
            )
            logger.error(f"Failed to scan for agents: {e}", exc_info=True)

    def _setup_keyboard_shortcuts(self) -> None:
        """
        Setup keyboard shortcuts for Config tab.

        Shortcuts:
        - Ctrl+S: Save template
        - Ctrl+R: Refresh agent list
        - Ctrl+P: Update preview
        """
        # Ctrl+S: Save template
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self._on_save_template)

        # Ctrl+R: Refresh agent list (placeholder for future implementation)
        shortcut_refresh = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_refresh.activated.connect(self._on_refresh_agents)

        # Ctrl+P: Update preview
        shortcut_preview = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut_preview.activated.connect(self.update_template_preview)

        logger.debug("Keyboard shortcuts configured: Ctrl+S (Save), Ctrl+R (Refresh), Ctrl+P (Preview)")

    def _on_refresh_agents(self) -> None:
        """
        Handle Ctrl+R shortcut to refresh agent list.

        Refreshes the agent list from the current workspace and provides user feedback.
        """
        # If current workspace is set, refresh the agent list
        if self._current_workspace:
            self.populate_config_agent_list(self._current_workspace)
            QMessageBox.information(
                self,
                "Refreshed",
                "Agent list has been refreshed."
            )
            logger.info("Agent list refreshed")
        else:
            QMessageBox.warning(
                self,
                "No Workspace",
                "No workspace is currently set.\n\nCannot refresh agent list."
            )
            logger.debug("No workspace set, cannot refresh agent list")

    def save_current_template(self) -> bool:
        """
        Save the current template (for testing purposes).

        Returns:
            True if save succeeded, False otherwise
        """
        template_text = self._template_editor.toPlainText()

        # Validate template
        validation = self.validate_template_text(template_text)

        if not validation['is_valid']:
            return False

        # Use stored agent ID
        if not self._current_agent_id:
            return False

        agent_id = self._current_agent_id

        try:
            # Save template
            engine = TemplateEngine()
            engine.save_template(agent_id, template_text, enabled=True)

            # Track saved state
            self._last_saved_template = template_text
            self._unsaved_template_changes = False

            logger.info(f"Saved template for agent: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save template for {agent_id}: {e}")
            return False
