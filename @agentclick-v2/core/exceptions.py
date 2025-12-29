"""
Custom exceptions for AgentClick V2.

This module defines the exception hierarchy used throughout the
AgentClick V2 system, including workspace and template-related errors.
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


class TemplateError(Exception):
    """
    Base exception for all template-related errors.

    This exception can be used to catch any template-related error.
    All specific template exceptions inherit from this class.

    Attributes:
        message: Error message describing what went wrong

    Example:
        >>> try:
        ...     # template operations
        ... except TemplateError as e:
        ...     print(f"Template error: {e}")
    """
    pass


class TemplateSyntaxError(TemplateError):
    """
    Exception raised when template syntax is invalid.

    This exception is raised when:
    - Template has unclosed {{ }} brackets
    - Template has malformed expressions
    - Other syntax errors are detected

    Attributes:
        message: Error message describing the syntax error

    Example:
        >>> try:
        ...     engine.validate_template('Invalid {{template')
        ... except TemplateSyntaxError as e:
        ...     print(f"Syntax error: {e}")
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a syntax error message.

        Args:
            message: Description of the syntax error
        """
        super().__init__(message)


class TemplateValidationError(TemplateError):
    """
    Exception raised when template validation fails.

    This exception is raised when:
    - Template contains invalid variables
    - Template structure is incorrect
    - Other validation rules are violated

    Attributes:
        message: Error message describing the validation error

    Example:
        >>> try:
        ...     engine.validate_template(invalid_template)
        ... except TemplateValidationError as e:
        ...     print(f"Validation error: {e}")
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a validation error message.

        Args:
            message: Description of the validation error
        """
        super().__init__(message)


class AgentExecutionError(Exception):
    """
    Base exception for agent execution errors.

    This exception is raised when agent execution fails for any reason
    other than SDK connection issues.

    Attributes:
        message: Error message describing what went wrong

    Example:
        >>> try:
        ...     await executor.execute(agent, input_text, workspace)
        ... except AgentExecutionError as e:
        ...     print(f"Execution error: {e}")
    """
    pass


class SDKConnectionError(Exception):
    """
    Exception raised when connection to Claude SDK fails.

    This exception is raised when:
    - SDK is not available
    - Network connection fails
    - SDK API returns an error
    - Authentication fails

    Attributes:
        message: Error message describing the connection issue

    Example:
        >>> try:
        ...     await executor.execute(agent, input_text, workspace)
        ... except SDKConnectionError as e:
        ...     print(f"SDK connection failed: {e}")
    """
    pass


class MigrationError(Exception):
    """
    Base exception for all migration-related errors.

    This exception is raised when migration from V1 to V2 fails for any reason.

    Attributes:
        message: Error message describing what went wrong

    Example:
        >>> try:
        ...     migrator.migrate()
        ... except MigrationError as e:
        ...     print(f"Migration failed: {e}")
    """
    pass
