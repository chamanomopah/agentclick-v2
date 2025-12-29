"""
ExecutionResult dataclass for agent execution outputs.

This module defines the result of executing a virtual agent.
"""
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ExecutionResult:
    """
    Represents the result of executing a virtual agent.

    ExecutionResult captures the output, status, and metadata from agent execution,
    allowing the system to track execution outcomes and handle errors appropriately.

    Attributes:
        output: The output string from agent execution (could be success message,
                error message, or partial result)
        status: Execution status - must be one of:
                - "success": Agent completed successfully
                - "error": Agent encountered an error
                - "partial": Agent partially completed (e.g., some steps failed)
        metadata: Additional execution metadata (execution time, error codes, etc.)

    Example:
        >>> result = ExecutionResult(
        ...     output="Files committed successfully",
        ...     status="success",
        ...     metadata={"execution_time": 1.23, "files_changed": 5}
        ... )
        >>> if result.is_success():
        ...     print(result.output)
    """
    output: str
    status: Literal["success", "error", "partial"]
    metadata: dict = field(default_factory=dict)

    def is_success(self) -> bool:
        """
        Check if the execution was successful.

        Returns:
            True if status is "success", False otherwise

        Example:
            >>> result = ExecutionResult("Done", "success", {})
            >>> result.is_success()
            True
        """
        return self.status == "success"
