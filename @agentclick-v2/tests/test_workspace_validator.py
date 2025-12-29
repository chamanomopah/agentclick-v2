"""
Tests for WorkspaceValidator.

This module tests the workspace configuration validation logic.
"""
import pytest
from pathlib import Path
import tempfile

from core.exceptions import WorkspaceValidationError
from core.workspace_validator import WorkspaceValidator


class TestWorkspaceValidator:
    """Test the WorkspaceValidator class."""

    def test_validate_workspace_id_valid(self):
        """Should accept valid workspace IDs."""
        validator = WorkspaceValidator()

        # Valid cases
        validator.validate_workspace_id("python")  # lowercase
        validator.validate_workspace_id("python-projects")  # with hyphen
        validator.validate_workspace_id("python_projects")  # with underscore
        validator.validate_workspace_id("PythonProjects")  # mixed case
        validator.validate_workspace_id("py")  # short
        validator.validate_workspace_id("python123")  # with numbers

    def test_validate_workspace_id_invalid(self):
        """Should reject invalid workspace IDs."""
        validator = WorkspaceValidator()

        # Invalid cases
        with pytest.raises(WorkspaceValidationError, match="alphanumeric"):
            validator.validate_workspace_id("python projects")  # spaces

        with pytest.raises(WorkspaceValidationError, match="alphanumeric"):
            validator.validate_workspace_id("python.projects")  # dots

        with pytest.raises(WorkspaceValidationError, match="alphanumeric"):
            validator.validate_workspace_id("python@projects")  # special chars

        with pytest.raises(WorkspaceValidationError):
            validator.validate_workspace_id("")  # empty string

    def test_validate_workspace_folder_exists(self):
        """Should accept existing folders."""
        validator = WorkspaceValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory that exists
            existing_dir = Path(temp_dir) / "existing"
            existing_dir.mkdir()

            # Should not raise
            validator.validate_workspace_folder(existing_dir)

    def test_validate_workspace_folder_not_exists(self):
        """Should reject non-existent folders."""
        validator = WorkspaceValidator()

        non_existent = Path("/non/existent/path/that/does/not/exist")

        with pytest.raises(WorkspaceValidationError, match="does not exist"):
            validator.validate_workspace_folder(non_existent)

    def test_validate_workspace_folder_with_string(self):
        """Should accept string paths that exist."""
        validator = WorkspaceValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Should not raise with string
            validator.validate_workspace_folder(temp_dir)

    def test_validate_workspace_color_valid(self):
        """Should accept valid hex colors."""
        validator = WorkspaceValidator()

        # Valid cases
        validator.validate_workspace_color("#0078d4")  # blue
        validator.validate_workspace_color("#ff0000")  # red
        validator.validate_workspace_color("#00ff00")  # green
        validator.validate_workspace_color("#000000")  # black
        validator.validate_workspace_color("#ffffff")  # white
        validator.validate_workspace_color("#ABCDEF")  # uppercase

    def test_validate_workspace_color_invalid(self):
        """Should reject invalid hex colors."""
        validator = WorkspaceValidator()

        # Missing hash
        with pytest.raises(WorkspaceValidationError, match="color"):
            validator.validate_workspace_color("0078d4")

        # Too short
        with pytest.raises(WorkspaceValidationError, match="color"):
            validator.validate_workspace_color("#00f")

        # Too long
        with pytest.raises(WorkspaceValidationError, match="color"):
            validator.validate_workspace_color("#0078d4ff")

        # Invalid characters
        with pytest.raises(WorkspaceValidationError, match="color"):
            validator.validate_workspace_color("#gggggg")

        # Empty
        with pytest.raises(WorkspaceValidationError, match="color"):
            validator.validate_workspace_color("")

    def test_validate_workspace_complete_valid(self):
        """Should validate complete workspace config."""
        validator = WorkspaceValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                'id': 'python-projects',
                'name': 'Python Projects',
                'folder': temp_dir,
                'emoji': '🐍',
                'color': '#0078d4'
            }

            # Should not raise
            validator.validate_workspace(config)

    def test_validate_workspace_missing_fields(self):
        """Should reject workspace config with missing fields."""
        validator = WorkspaceValidator()

        # Missing id
        with pytest.raises(WorkspaceValidationError, match="required"):
            validator.validate_workspace({
                'name': 'Python Projects',
                'folder': '/tmp',
                'emoji': '🐍',
                'color': '#0078d4'
            })

        # Missing name
        with pytest.raises(WorkspaceValidationError, match="required"):
            validator.validate_workspace({
                'id': 'python',
                'folder': '/tmp',
                'emoji': '🐍',
                'color': '#0078d4'
            })

        # Missing folder
        with pytest.raises(WorkspaceValidationError, match="required"):
            validator.validate_workspace({
                'id': 'python',
                'name': 'Python',
                'emoji': '🐍',
                'color': '#0078d4'
            })

        # Missing emoji
        with pytest.raises(WorkspaceValidationError, match="required"):
            validator.validate_workspace({
                'id': 'python',
                'name': 'Python',
                'folder': '/tmp',
                'color': '#0078d4'
            })

        # Missing color
        with pytest.raises(WorkspaceValidationError, match="required"):
            validator.validate_workspace({
                'id': 'python',
                'name': 'Python',
                'folder': '/tmp',
                'emoji': '🐍'
            })

    def test_validate_workspace_multiple_errors(self):
        """Should collect all validation errors."""
        validator = WorkspaceValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                'id': 'python with spaces',  # invalid
                'name': 'Python Projects',
                'folder': '/nonexistent/path',  # doesn't exist
                'emoji': '🐍',
                'color': 'invalid'  # invalid color
            }

            # Should raise on first error (could be extended to collect all)
            with pytest.raises(WorkspaceValidationError):
                validator.validate_workspace(config)

    def test_validate_workspace_with_pathlib(self):
        """Should accept pathlib.Path for folder."""
        validator = WorkspaceValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                'id': 'test-workspace',
                'name': 'Test',
                'folder': Path(temp_dir),  # Using Path object
                'emoji': '🧪',
                'color': '#00ff00'
            }

            # Should not raise
            validator.validate_workspace(config)

    def test_validate_workspace_id_start_with_number(self):
        """Should allow IDs starting with numbers."""
        validator = WorkspaceValidator()

        # Should not raise
        validator.validate_workspace_id("123workspace")
        validator.validate_workspace_id("99-bottles-of-beer")
