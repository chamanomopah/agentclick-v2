"""
Tests for Config Tab in DetailedPopupV2.

This module tests the Config tab functionality including:
- Template editor with live preview
- Template validation
- Agent list with enable/disable checkboxes
- Scan for new agents functionality
"""
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QTabWidget, QTextEdit, QLabel, QListWidget, QPushButton, QCheckBox
from PyQt6.QtCore import Qt

from ui.popup_window_v2 import DetailedPopupV2
from core.workspace_manager import WorkspaceManager
from core.template_engine import TemplateEngine
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent


# Fixtures
@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
    agents = [
        VirtualAgent(
            id="verify-python",
            type="command",
            name="Verify Python",
            description="Verify Python scripts",
            source_file=Path("/test/verify-python.md"),
            emoji="📝",
            color="#3498db",
            enabled=True
        ),
        VirtualAgent(
            id="ux-ui-improver",
            type="skill",
            name="UX/UI Improver",
            description="Improve UX/UI",
            source_file=Path("/test/ux-ui-improver/SKILL.md"),
            emoji="🎯",
            color="#9b59b6",
            enabled=True
        ),
        VirtualAgent(
            id="review-code",
            type="command",
            name="Review Code",
            description="Review code",
            source_file=Path("/test/review-code.md"),
            emoji="📝",
            color="#3498db",
            enabled=False
        )
    ]

    return Workspace(
        id="python",
        name="Python Projects",
        folder=Path("/python"),
        emoji="🐍",
        color="#0078d4",
        agents=agents
    )


class TestConfigTabStructure:
    """Test suite for Config tab structure and layout."""

    def test_config_tab_exists(self, qapp):
        """Test that Config tab exists (AC: #1, #2, #3, #4, #5)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        assert tab_widget is not None

        # Find Config tab (index 1)
        config_tab = tab_widget.widget(1)
        assert config_tab is not None
        assert tab_widget.tabText(1) == "⚙️ Config"

    def test_config_tab_has_workspace_labels(self, qapp):
        """Test that Config tab shows current workspace and agent info (AC: #1)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find workspace and agent labels
        workspace_label = config_tab.findChild(QLabel, "current_workspace_label")
        agent_label = config_tab.findChild(QLabel, "current_agent_label")

        assert workspace_label is not None
        assert agent_label is not None

    def test_config_tab_has_template_editor(self, qapp):
        """Test that Config tab has template editor (AC: #2)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find template editor
        template_editor = config_tab.findChild(QTextEdit, "template_editor")
        assert template_editor is not None
        assert template_editor.isReadOnly() is False

    def test_config_tab_has_preview_label(self, qapp):
        """Test that Config tab has preview label (AC: #2)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find preview label
        preview_label = config_tab.findChild(QLabel, "template_preview")
        assert preview_label is not None

    def test_config_tab_has_agent_list(self, qapp):
        """Test that Config tab has agent list (AC: #3)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find agent list
        agent_list = config_tab.findChild(QListWidget, "agent_list")
        assert agent_list is not None

    def test_config_tab_has_scan_button(self, qapp):
        """Test that Config tab has scan button (AC: #4)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find scan button
        scan_button = config_tab.findChild(QPushButton, "scan_agents_button")
        assert scan_button is not None
        assert "Scan" in scan_button.text()

    def test_config_tab_has_save_button(self, qapp):
        """Test that Config tab has save button (AC: #5)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        # Find save button
        save_button = config_tab.findChild(QPushButton, "save_template_button")
        assert save_button is not None
        assert "Save" in save_button.text()


class TestConfigTabFunctionality:
    """Test suite for Config tab functionality."""

    def test_update_workspace_info(self, qapp, sample_workspace):
        """Test that workspace and agent labels update (AC: #1)."""
        popup = DetailedPopupV2()

        # Update workspace info
        popup.update_config_tab_workspace(sample_workspace, "verify-python")

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        workspace_label = config_tab.findChild(QLabel, "current_workspace_label")
        agent_label = config_tab.findChild(QLabel, "current_agent_label")

        assert "Python Projects" in workspace_label.text()
        assert "verify-python" in agent_label.text()

    def test_template_editor_updates_preview(self, qapp):
        """Test that template editor updates preview in real-time (AC: #2)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        template_editor = config_tab.findChild(QTextEdit, "template_editor")
        preview_label = config_tab.findChild(QLabel, "template_preview")

        # Set template text
        template_editor.setPlainText("Input: {{input}}\nFolder: {{context_folder}}")

        # Trigger preview update
        popup.update_template_preview()

        # Verify preview shows substituted values
        preview_text = preview_label.text()
        assert "<sample input>" in preview_text
        assert "C:/example" in preview_text

    def test_populate_agent_list(self, qapp, sample_workspace_with_agents):
        """Test that agent list populates with checkboxes (AC: #3)."""
        popup = DetailedPopupV2()

        # Populate agent list
        popup.populate_config_agent_list(sample_workspace_with_agents)

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        agent_list = config_tab.findChild(QListWidget, "agent_list")

        # Check that all agents are in the list
        assert agent_list.count() == 3

        # Check first item
        first_item = agent_list.item(0)
        assert "verify-python" in first_item.text()
        assert first_item.checkState() == Qt.CheckState.Checked

        # Check third item (disabled)
        third_item = agent_list.item(2)
        assert "review-code" in third_item.text()
        assert third_item.checkState() == Qt.CheckState.Unchecked

    def test_agent_checkbox_toggles_enable(self, qapp, sample_workspace_with_agents):
        """Test that checkbox toggles agent enabled state (AC: #3)."""
        popup = DetailedPopupV2()

        # Populate agent list
        popup.populate_config_agent_list(sample_workspace_with_agents)

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        agent_list = config_tab.findChild(QListWidget, "agent_list")

        # Uncheck first item
        first_item = agent_list.item(0)
        first_item.setCheckState(Qt.CheckState.Unchecked)

        # Verify agent was disabled
        agent = sample_workspace_with_agents.agents[0]
        assert agent.enabled is False

    def test_save_template_validates(self, qapp):
        """Test that save button validates template (AC: #5)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        template_editor = config_tab.findChild(QTextEdit, "template_editor")

        # Set invalid template (unclosed bracket)
        template_editor.setPlainText("Input: {{input")

        # Try to save - should fail validation
        result = popup.save_current_template()

        assert result is False

    def test_save_template_succeeds(self, qapp, tmp_path):
        """Test that save button saves valid template (AC: #6)."""
        popup = DetailedPopupV2()

        tab_widget = popup.findChild(QTabWidget)
        config_tab = tab_widget.widget(1)

        template_editor = config_tab.findChild(QTextEdit, "template_editor")

        # Set current agent ID (required for save)
        popup._current_agent_id = "test-agent"

        # Set valid template
        template_editor.setPlainText("Input: {{input}}\nContext: {{context_folder}}")

        # Save template
        result = popup.save_current_template()

        assert result is True

    def test_scan_agents_button_works(self, qapp):
        """Test that scan button exists and method can be called (AC: #4)."""
        popup = DetailedPopupV2()

        # Verify method exists
        assert hasattr(popup, '_on_scan_agents')
        assert callable(popup._on_scan_agents)

        # Call method directly (should not raise)
        popup._on_scan_agents()


class TestTemplateValidation:
    """Test suite for template validation in Config tab."""

    def test_valid_template_passes_validation(self, qapp):
        """Test that valid template passes validation."""
        popup = DetailedPopupV2()

        template = "Input: {{input}}\nContext: {{context_folder}}"
        result = popup.validate_template_text(template)

        assert result['is_valid'] is True
        assert len(result['errors']) == 0

    def test_unclosed_bracket_fails_validation(self, qapp):
        """Test that unclosed bracket fails validation."""
        popup = DetailedPopupV2()

        template = "Input: {{input"
        result = popup.validate_template_text(template)

        assert result['is_valid'] is False
        assert len(result['errors']) > 0
        assert "unclosed" in result['errors'][0].lower()

    def test_unknown_variable_shows_warning(self, qapp):
        """Test that unknown variable shows warning."""
        popup = DetailedPopupV2()

        template = "Input: {{input}}\nUnknown: {{unknown_var}}"
        result = popup.validate_template_text(template)

        # Should be valid but with warnings
        assert result['is_valid'] is True
        assert len(result['warnings']) > 0
        assert "unknown" in result['warnings'][0].lower()
