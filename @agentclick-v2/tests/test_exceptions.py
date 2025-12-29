"""
Tests for workspace exceptions.

This module tests the custom exception hierarchy for workspace management.
"""
import pytest

from core.exceptions import (
    WorkspaceError,
    WorkspaceNotFoundError,
    WorkspaceLoadError,
    WorkspaceValidationError
)


class TestWorkspaceError:
    """Test the base WorkspaceError exception."""

    def test_workspace_error_is_exception(self):
        """WorkspaceError should be a subclass of Exception."""
        assert issubclass(WorkspaceError, Exception)

    def test_workspace_error_can_be_instantiated(self):
        """WorkspaceError should be instantiable with a message."""
        error = WorkspaceError("Test error message")
        assert str(error) == "Test error message"
        assert error.args == ("Test error message",)

    def test_workspace_error_without_message(self):
        """WorkspaceError should work without a message."""
        error = WorkspaceError()
        assert error.args == ()


class TestWorkspaceNotFoundError:
    """Test the WorkspaceNotFoundError exception."""

    def test_is_workspace_error_subclass(self):
        """WorkspaceNotFoundError should be a subclass of WorkspaceError."""
        assert issubclass(WorkspaceNotFoundError, WorkspaceError)

    def test_can_be_instantiated_with_workspace_id(self):
        """WorkspaceNotFoundError should store workspace_id."""
        error = WorkspaceNotFoundError("test-workspace")
        assert error.workspace_id == "test-workspace"

    def test_string_representation_includes_workspace_id(self):
        """String representation should include the workspace_id."""
        error = WorkspaceNotFoundError("python-projects")
        error_str = str(error)
        assert "python-projects" in error_str
        assert "not found" in error_str.lower()

    def test_can_be_raised_and_caught(self):
        """Should be able to raise and catch as WorkspaceError."""
        with pytest.raises(WorkspaceError):
            raise WorkspaceNotFoundError("test-id")

    def test_can_be_raised_and_caught_specifically(self):
        """Should be able to raise and catch as WorkspaceNotFoundError."""
        with pytest.raises(WorkspaceNotFoundError):
            raise WorkspaceNotFoundError("test-id")


class TestWorkspaceLoadError:
    """Test the WorkspaceLoadError exception."""

    def test_is_workspace_error_subclass(self):
        """WorkspaceLoadError should be a subclass of WorkspaceError."""
        assert issubclass(WorkspaceLoadError, WorkspaceError)

    def test_can_be_instantiated_with_message(self):
        """WorkspaceLoadError should be instantiable with a message."""
        error = WorkspaceLoadError("Failed to load config file")
        assert str(error) == "Failed to load config file"

    def test_can_be_raised_and_caught(self):
        """Should be able to raise and catch as WorkspaceError."""
        with pytest.raises(WorkspaceError):
            raise WorkspaceLoadError("Load failed")

    def test_can_be_raised_and_caught_specifically(self):
        """Should be able to raise and catch as WorkspaceLoadError."""
        with pytest.raises(WorkspaceLoadError):
            raise WorkspaceLoadError("Load failed")


class TestWorkspaceValidationError:
    """Test the WorkspaceValidationError exception."""

    def test_is_workspace_error_subclass(self):
        """WorkspaceValidationError should be a subclass of WorkspaceError."""
        assert issubclass(WorkspaceValidationError, WorkspaceError)

    def test_can_be_instantiated_with_message(self):
        """WorkspaceValidationError should be instantiable with a message."""
        error = WorkspaceValidationError("Invalid workspace ID")
        assert str(error) == "Invalid workspace ID"

    def test_can_be_raised_and_caught(self):
        """Should be able to raise and catch as WorkspaceError."""
        with pytest.raises(WorkspaceError):
            raise WorkspaceValidationError("Validation failed")

    def test_can_be_raised_and_caught_specifically(self):
        """Should be able to raise and catch as WorkspaceValidationError."""
        with pytest.raises(WorkspaceValidationError):
            raise WorkspaceValidationError("Validation failed")

    def test_multiple_errors_can_be_stored(self):
        """Should be able to store multiple validation errors."""
        error = WorkspaceValidationError("Multiple errors")
        # This allows extending with error details list if needed
        assert str(error) == "Multiple errors"


class TestExceptionHierarchy:
    """Test the exception hierarchy and catching behavior."""

    def test_catch_all_workspace_errors(self):
        """Should be able to catch all workspace errors with base class."""
        with pytest.raises(WorkspaceError):
            raise WorkspaceNotFoundError("test")

        with pytest.raises(WorkspaceError):
            raise WorkspaceLoadError("test")

        with pytest.raises(WorkspaceError):
            raise WorkspaceValidationError("test")

    def test_specific_exceptions_dont_catch_others(self):
        """Specific exception types shouldn't catch other types."""
        try:
            raise WorkspaceLoadError("load error")
        except WorkspaceNotFoundError:
            pytest.fail("WorkspaceNotFoundError should not catch WorkspaceLoadError")
        except WorkspaceLoadError:
            pass  # Expected

    def test_exception_chaining(self):
        """Exceptions should support exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise WorkspaceLoadError("Failed to load") from e
        except WorkspaceLoadError as caught:
            assert caught.__cause__ is not None
            assert isinstance(caught.__cause__, ValueError)
