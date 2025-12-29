"""
Tests for DetailedPopupV2 - Main popup window with tabs.

This module tests the DetailedPopupV2 class which provides the main
detailed popup window with Activity, Config, and Workspaces tabs.
"""
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QTabWidget, QGroupBox, QTableWidget, QPushButton
from PyQt6.QtCore import Qt

from ui.popup_window_v2 import DetailedPopupV2
from ui.mini_popup_v2 import MiniPopupV2
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent
from core.workspace_manager import WorkspaceManager


# Fixtures
@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestDetailedPopupV2:
    """Test suite for DetailedPopupV2 class."""

    def test_initialization_creates_window(self, qapp):
        """Test that DetailedPopupV2 can be initialized."""
        popup = DetailedPopupV2()

        # Check window properties (AC: #1)
        assert popup.windowTitle() == "AgentClick V2"
        assert popup.width() == 600
        assert popup.height() == 500

    def test_has_three_tabs(self, qapp):
        """Test that popup has exactly 3 tabs (AC: #1)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        assert tab_widget is not None
        assert tab_widget.count() == 3

        # Check tab titles
        assert tab_widget.tabText(0) == "📋 Activity"
        assert tab_widget.tabText(1) == "⚙️ Config"
        assert tab_widget.tabText(2) == "💼 Workspaces"

    def test_workspaces_tab_has_current_workspace_section(self, qapp):
        """Test that Workspaces tab has current workspace section (AC: #2)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        workspaces_tab = tab_widget.widget(2)

        # Find the current workspace group box
        current_section = workspaces_tab.findChild(QGroupBox, "current_workspace_group")
        assert current_section is not None
        assert "Current Workspace" in current_section.title()

    def test_workspaces_tab_has_workspace_list(self, qapp):
        """Test that Workspaces tab has workspace list (AC: #3)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        workspaces_tab = tab_widget.widget(2)

        # Find the workspace list table
        workspace_list = workspaces_tab.findChild(QTableWidget, "workspace_list_table")
        assert workspace_list is not None

    def test_workspaces_tab_has_action_buttons(self, qapp):
        """Test that Workspaces tab has 4 action buttons (AC: #4)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        workspaces_tab = tab_widget.widget(2)

        # Find all buttons
        add_button = workspaces_tab.findChild(QPushButton, "add_workspace_button")
        edit_button = workspaces_tab.findChild(QPushButton, "edit_workspace_button")
        switch_button = workspaces_tab.findChild(QPushButton, "switch_workspace_button")
        delete_button = workspaces_tab.findChild(QPushButton, "delete_workspace_button")

        assert add_button is not None
        assert add_button.text() == "Add Workspace"
        assert edit_button is not None
        assert edit_button.text() == "Edit Workspace"
        assert switch_button is not None
        assert switch_button.text() == "Switch Workspace"
        assert delete_button is not None
        assert delete_button.text() == "Delete Workspace"

    def test_can_set_workspace_manager(self, qapp):
        """Test that workspace manager can be set."""
        popup = DetailedPopupV2()

        # Create a workspace manager
        config_path = Path(__file__).parent.parent / 'config' / 'workspaces.yaml'
        manager = WorkspaceManager(str(config_path))

        popup.set_workspace_manager(manager)
        assert popup.workspace_manager is manager

    def test_update_header_with_workspace_name(self, qapp):
        """Test that header updates with workspace name."""
        popup = DetailedPopupV2()

        # Create test workspace
        workspace = Workspace(
            id="test",
            name="Test Workspace",
            folder=Path("/tmp/test"),
            emoji="🧪",
            color="#0078d4"
        )

        popup.update_current_workspace(workspace)
        assert "Test Workspace" in popup.windowTitle()

    def test_can_connect_mini_popup_double_click(self, qapp):
        """Test that mini popup double-click can be connected to workspace switching."""
        from ui.mini_popup_v2 import MiniPopupV2

        popup = DetailedPopupV2()

        # Create a workspace manager and manually add workspaces
        import tempfile
        config_path = tempfile.mktemp(suffix='.yaml')
        manager = WorkspaceManager(config_path)

        # Manually add workspaces to manager (bypassing async file loading)
        from models.workspace import Workspace
        ws1 = Workspace(
            id='workspace1',
            name='Workspace 1',
            folder=Path(__file__).parent,
            emoji='🧪',
            color='#0078d4'
        )
        ws2 = Workspace(
            id='workspace2',
            name='Workspace 2',
            folder=Path(__file__).parent,
            emoji='🎯',
            color='#ff0000'
        )

        manager.workspaces['workspace1'] = ws1
        manager.workspaces['workspace2'] = ws2
        manager.current_workspace_id = 'workspace1'

        popup.set_workspace_manager(manager)

        # Create mini popup
        mini_popup = MiniPopupV2()

        # Connect double-click signal
        popup.connect_mini_popup_double_click(mini_popup)

        # Verify connection was successful (no exception raised)
        assert popup.workspace_manager is not None
        assert manager.current_workspace_id == 'workspace1'

        # Simulate double-click to trigger workspace switch
        mini_popup.workspace_switch_requested.emit()

        # Verify workspace switched to next
        assert manager.current_workspace_id == 'workspace2'


@pytest.fixture
def sample_workspace():
    """Create a sample workspace for testing."""
    return Workspace(
        id="python",
        name="Python Projects",
        folder=Path("/python"),
        emoji="🐍",
        color="#0078d4"
    )


@pytest.fixture
def sample_workspace_with_agents():
    """Create a sample workspace with agents."""
    agent1 = VirtualAgent(
        id="agent1",
        type="command",
        name="Test Agent 1",
        description="Test",
        workspace_id="python"
    )
    agent2 = VirtualAgent(
        id="agent2",
        type="skill",
        name="Test Agent 2",
        description="Test",
        workspace_id="python"
    )

    workspace = Workspace(
        id="python",
        name="Python Projects",
        folder=Path("/python"),
        emoji="🐍",
        color="#0078d4",
        agents=[agent1, agent2]
    )
    return workspace
