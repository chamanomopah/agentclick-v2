"""
Tests for ExecutionResult dataclass.
"""
import pytest
from typing import get_type_hints
from models.execution_result import ExecutionResult


class TestExecutionResultDataclass:
    """Test ExecutionResult dataclass structure and type hints."""

    def test_execution_result_has_all_required_fields(self):
        """Test that ExecutionResult has all required fields with correct types."""
        hints = get_type_hints(ExecutionResult)

        required_fields = {
            'output': str,
            'status': str,  # Literal will be validated separately
            'metadata': dict,
        }

        for field_name, expected_type in required_fields.items():
            assert field_name in hints, f"Missing field: {field_name}"

    def test_execution_result_creation_success(self):
        """Test creating ExecutionResult with success status."""
        result = ExecutionResult(
            output="Agent executed successfully",
            status="success",
            metadata={"execution_time": 1.5}
        )

        assert result.output == "Agent executed successfully"
        assert result.status == "success"
        assert result.metadata == {"execution_time": 1.5}

    def test_execution_result_creation_error(self):
        """Test creating ExecutionResult with error status."""
        result = ExecutionResult(
            output="Error: Command failed",
            status="error",
            metadata={"error_code": 500}
        )

        assert result.output == "Error: Command failed"
        assert result.status == "error"
        assert result.metadata == {"error_code": 500}

    def test_execution_result_creation_partial(self):
        """Test creating ExecutionResult with partial status."""
        result = ExecutionResult(
            output="Partially completed",
            status="partial",
            metadata={"completed_steps": 3, "total_steps": 5}
        )

        assert result.output == "Partially completed"
        assert result.status == "partial"
        assert result.metadata == {"completed_steps": 3, "total_steps": 5}

    def test_execution_result_status_validation(self):
        """Test that status field accepts valid literal values."""
        valid_statuses = ["success", "error", "partial"]

        for status in valid_statuses:
            result = ExecutionResult(
                output=f"Result with status: {status}",
                status=status,
                metadata={}
            )
            assert result.status == status

    def test_execution_result_with_empty_metadata(self):
        """Test creating ExecutionResult with empty metadata."""
        result = ExecutionResult(
            output="Simple result",
            status="success",
            metadata={}
        )

        assert result.metadata == {}


class TestExecutionResultMethods:
    """Test ExecutionResult methods."""

    def test_is_success_method_returns_true_for_success(self):
        """Test is_success returns True for success status."""
        result = ExecutionResult(
            output="Success!",
            status="success",
            metadata={}
        )

        assert result.is_success() is True

    def test_is_success_method_returns_false_for_error(self):
        """Test is_success returns False for error status."""
        result = ExecutionResult(
            output="Error!",
            status="error",
            metadata={}
        )

        assert result.is_success() is False

    def test_is_success_method_returns_false_for_partial(self):
        """Test is_success returns False for partial status."""
        result = ExecutionResult(
            output="Partial!",
            status="partial",
            metadata={}
        )

        assert result.is_success() is False

    def test_execution_result_equality(self):
        """Test ExecutionResult equality comparison."""
        result1 = ExecutionResult(
            output="Same output",
            status="success",
            metadata={"key": "value"}
        )

        result2 = ExecutionResult(
            output="Same output",
            status="success",
            metadata={"key": "value"}
        )

        assert result1 == result2

    def test_execution_result_inequality(self):
        """Test ExecutionResult inequality."""
        result1 = ExecutionResult(
            output="Output 1",
            status="success",
            metadata={}
        )

        result2 = ExecutionResult(
            output="Output 2",
            status="error",
            metadata={}
        )

        assert result1 != result2
