"""
Tests for WorkspaceDialog - Dialog for creating/editing workspaces.

This module tests the WorkspaceDialog class which provides a form
for creating and editing workspace configurations.
"""
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QDialogButtonBox
from PyQt6.QtGui import QColor

from ui.workspace_dialog import WorkspaceDialog
from models.workspace import Workspace
from core.workspace_manager import WorkspaceManager


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
    """Create a sample workspace for editing."""
    return Workspace(
        id="python",
        name="Python Projects",
        folder=Path("/python"),
        emoji="🐍",
        color="#0078d4"
    )


class TestWorkspaceDialog:
    """Test suite for WorkspaceDialog class."""

    def test_create_mode_initialization(self, qapp):
        """Test dialog initialization in create mode."""
        dialog = WorkspaceDialog(mode="create")

        # Check dialog properties
        assert dialog.windowTitle() == "Add Workspace"
        assert dialog.mode == "create"

        # Check that fields are empty
        assert dialog.get_id() == ""
        assert dialog.get_name() == ""
        assert dialog.get_folder() == ""
        assert dialog.get_emoji() == ""
        assert dialog.get_color() == "#0078d4"  # Default color

    def test_edit_mode_initialization(self, qapp, sample_workspace):
        """Test dialog initialization in edit mode."""
        dialog = WorkspaceDialog(mode="edit", workspace=sample_workspace)

        # Check dialog properties
        assert dialog.windowTitle() == "Edit Workspace"
        assert dialog.mode == "edit"

        # Check that fields are populated
        assert dialog.get_id() == "python"
        assert dialog.get_name() == "Python Projects"
        assert dialog.get_folder() == str(Path("/python"))  # Normalize path
        assert dialog.get_emoji() == "🐍"
        assert dialog.get_color() == "#0078d4"

    def test_id_field_is_readonly_in_edit_mode(self, qapp, sample_workspace):
        """Test that ID field is readonly in edit mode."""
        dialog = WorkspaceDialog(mode="edit", workspace=sample_workspace)

        id_field = dialog.findChild(QLineEdit, "id_field")
        assert id_field is not None
        assert id_field.isReadOnly() is True

    def test_id_field_is_editable_in_create_mode(self, qapp):
        """Test that ID field is editable in create mode."""
        dialog = WorkspaceDialog(mode="create")

        id_field = dialog.findChild(QLineEdit, "id_field")
        assert id_field is not None
        assert id_field.isReadOnly() is False

    def test_has_ok_and_cancel_buttons(self, qapp):
        """Test that dialog has OK and Cancel buttons."""
        dialog = WorkspaceDialog(mode="create")

        button_box = dialog.findChild(QDialogButtonBox)
        assert button_box is not None

        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        assert ok_button is not None
        assert cancel_button is not None

    def test_validates_empty_name(self, qapp):
        """Test that empty name is rejected."""
        dialog = WorkspaceDialog(mode="create")

        # Set ID first (required in create mode)
        dialog.set_id("test-workspace")
        # Set empty name
        dialog.set_name("")

        # Try to validate
        is_valid, error = dialog.validate()

        assert is_valid is False
        assert "name" in error.lower()

    def test_validates_invalid_color_format(self, qapp):
        """Test that invalid color format is rejected."""
        dialog = WorkspaceDialog(mode="create")

        # Set required fields first
        dialog.set_id("test-workspace")
        dialog.set_name("Test")
        dialog.set_folder(str(Path(__file__).parent))
        # Set invalid color
        dialog.set_color("invalid-color")

        # Try to validate
        is_valid, error = dialog.validate()

        assert is_valid is False
        assert "color" in error.lower()

    def test_validates_nonexistent_folder(self, qapp):
        """Test that nonexistent folder is rejected."""
        dialog = WorkspaceDialog(mode="create")

        # Set required fields first
        dialog.set_id("test-workspace")
        dialog.set_name("Test")
        # Set nonexistent folder
        dialog.set_folder("/nonexistent/folder/path/12345")

        # Try to validate
        is_valid, error = dialog.validate()

        assert is_valid is False
        assert "folder" in error.lower() or "exist" in error.lower()

    def test_validates_invalid_id_format(self, qapp):
        """Test that invalid ID format is rejected."""
        dialog = WorkspaceDialog(mode="create")

        # Set invalid ID (with spaces and special chars)
        dialog.set_id("invalid id with spaces!")

        # Try to validate
        is_valid, error = dialog.validate()

        assert is_valid is False
        assert "id" in error.lower()

    def test_accepts_valid_workspace_data(self, qapp):
        """Test that valid workspace data is accepted."""
        dialog = WorkspaceDialog(mode="create")

        # Set valid data
        dialog.set_id("test-workspace")
        dialog.set_name("Test Workspace")
        dialog.set_folder(str(Path(__file__).parent))  # Use existing folder
        dialog.set_emoji("🧪")
        dialog.set_color("#00ff00")

        # Try to validate
        is_valid, error = dialog.validate()

        assert is_valid is True
        assert error == ""

    def test_get_workspace_config_returns_dict(self, qapp):
        """Test that get_workspace_config returns proper dict."""
        dialog = WorkspaceDialog(mode="create")

        # Set data
        dialog.set_id("test-workspace")
        dialog.set_name("Test Workspace")
        dialog.set_folder("/test/folder")
        dialog.set_emoji("🧪")
        dialog.set_color("#00ff00")

        # Get config
        config = dialog.get_workspace_config()

        assert isinstance(config, dict)
        assert config["id"] == "test-workspace"
        assert config["name"] == "Test Workspace"
        assert config["folder"] == "/test/folder"
        assert config["emoji"] == "🧪"
        assert config["color"] == "#00ff00"

    def test_validates_duplicate_workspace_id(self, qapp):
        """Test that duplicate workspace IDs are rejected when workspace_manager is provided."""
        import tempfile

        # Create workspace manager and manually add an existing workspace
        config_path = tempfile.mktemp(suffix='.yaml')
        manager = WorkspaceManager(config_path)

        # Manually add a workspace to manager
        from models.workspace import Workspace
        existing_ws = Workspace(
            id='existing-workspace',
            name='Existing Workspace',
            folder=Path(__file__).parent,
            emoji='🧪',
            color='#0078d4'
        )
        manager.workspaces['existing-workspace'] = existing_ws

        # Create dialog with workspace_manager
        dialog = WorkspaceDialog(mode="create", workspace_manager=manager)

        # Try to use duplicate ID
        dialog.set_id("existing-workspace")
        dialog.set_name("Test")
        dialog.set_folder(str(Path(__file__).parent))
        dialog.set_color("#0078d4")

        # Should fail validation
        is_valid, error = dialog.validate()

        assert is_valid is False
        assert "already exists" in error.lower()
