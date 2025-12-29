"""
Custom exceptions for workspace management.

This module defines the exception hierarchy used by the WorkspaceManager
and related components. All exceptions inherit from WorkspaceError for
easy catching of workspace-related errors.
"""


class WorkspaceError(Exception):
    """
    Base exception for all workspace-related errors.

    This exception can be used to catch any workspace-related error.
    All specific workspace exceptions inherit from this class.

    Attributes:
        message: Error message describing what went wrong

    Example:
        >>> try:
        ...     # workspace operations
        ... except WorkspaceError as e:
        ...     print(f"Workspace error: {e}")
    """
    pass


class WorkspaceNotFoundError(WorkspaceError):
    """
    Exception raised when attempting to access a non-existent workspace.

    This exception is raised when trying to switch to, update, or remove
    a workspace that doesn't exist in the configuration.

    Attributes:
        workspace_id: The ID of the workspace that was not found

    Example:
        >>> try:
        ...     manager.switch_workspace("non-existent")
        ... except WorkspaceNotFoundError as e:
        ...     print(f"Workspace {e.workspace_id} not found")
    """

    def __init__(self, workspace_id: str):
        """
        Initialize the exception with a workspace ID.

        Args:
            workspace_id: The ID of the workspace that was not found
        """
        self.workspace_id = workspace_id
        super().__init__(f"Workspace '{workspace_id}' not found")


class WorkspaceLoadError(WorkspaceError):
    """
    Exception raised when loading workspace configuration fails.

    This exception is raised when:
    - The workspaces.yaml file cannot be read
    - The YAML format is invalid
    - Required configuration keys are missing
    - File I/O errors occur during loading

    Example:
        >>> try:
        ...     await manager.load_workspaces()
        ... except WorkspaceLoadError as e:
        ...     print(f"Failed to load: {e}")
    """

    def __init__(self, message: str):
        """
        Initialize the exception with an error message.

        Args:
            message: Description of the loading error
        """
        super().__init__(message)


class WorkspaceValidationError(WorkspaceError):
    """
    Exception raised when workspace configuration validation fails.

    This exception is raised when:
    - Workspace ID contains invalid characters
    - Workspace folder doesn't exist
    - Color format is invalid (not #RRGGBB)
    - Other validation rules are violated

    Example:
        >>> try:
        ...     manager.add_workspace(invalid_config)
        ... except WorkspaceValidationError as e:
        ...     print(f"Validation error: {e}")
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a validation error message.

        Args:
            message: Description of the validation error
        """
        super().__init__(message)
