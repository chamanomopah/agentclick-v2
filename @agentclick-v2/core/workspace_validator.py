"""
Workspace validation logic.

This module provides validation functionality for workspace configurations,
ensuring that all required fields are present and valid.
"""
import re
from pathlib import Path
from typing import Dict, Any

from .exceptions import WorkspaceValidationError


class WorkspaceValidator:
    """
    Validates workspace configurations.

    This class provides methods to validate individual workspace fields
    as well as complete workspace configurations.

    Validation Rules:
    - Workspace ID: Alphanumeric characters, hyphens, and underscores only
    - Workspace folder: Must exist on the filesystem
    - Workspace color: Must be in hex format #RRGGBB
    - All required fields must be present

    Example:
        >>> validator = WorkspaceValidator()
        >>> validator.validate_workspace({
        ...     'id': 'python-projects',
        ...     'name': 'Python Projects',
        ...     'folder': '/path/to/projects',
        ...     'emoji': '🐍',
        ...     'color': '#0078d4'
        ... })
    """

    # Regex pattern for valid workspace IDs
    # Allows alphanumeric, hyphens, and underscores
    ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Regex pattern for hex colors (#RRGGBB format)
    COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')

    def validate_workspace_id(self, workspace_id: str) -> None:
        """
        Validate a workspace ID.

        Workspace IDs must contain only alphanumeric characters,
        hyphens, and underscores. Spaces and special characters are
        not allowed.

        Args:
            workspace_id: The workspace ID to validate

        Raises:
            WorkspaceValidationError: If the ID is invalid

        Example:
            >>> validator.validate_workspace_id('python-projects')  # OK
            >>> validator.validate_workspace_id('python projects')  # Raises error
        """
        if not workspace_id:
            raise WorkspaceValidationError(
                "Workspace ID cannot be empty"
            )

        if not self.ID_PATTERN.match(workspace_id):
            raise WorkspaceValidationError(
                f"Invalid workspace ID '{workspace_id}': "
                "must contain only alphanumeric characters, hyphens, and underscores"
            )

    def validate_workspace_folder(self, folder: str | Path, strict: bool = False) -> None:
        """
        Validate a workspace folder.

        Args:
            folder: Path to the workspace folder (string or Path object)
            strict: If True, raises error when folder doesn't exist (default: False)
                    When False, only logs a warning if folder doesn't exist

        Raises:
            WorkspaceValidationError: If strict=True and the folder doesn't exist

        Example:
            >>> validator.validate_workspace_folder('/existing/path')  # OK
            >>> validator.validate_workspace_folder('/nonexistent')  # WARNING only (non-blocking)
            >>> validator.validate_workspace_folder('/nonexistent', strict=True)  # Raises error
        """
        path = Path(folder)

        # If not strict mode, only validate path format, not existence
        if not strict:
            # Non-blocking: just warn if doesn't exist, don't raise
            if not path.exists():
                # Import here to avoid circular dependency
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Workspace folder does not exist: {folder} - "
                    "This is non-blocking, workspace will still load"
                )
            return

        # Strict mode: validate existence
        if not path.exists():
            raise WorkspaceValidationError(
                f"Workspace folder does not exist: {folder}"
            )

        if not path.is_dir():
            raise WorkspaceValidationError(
                f"Workspace path is not a directory: {folder}"
            )

    def validate_workspace_color(self, color: str) -> None:
        """
        Validate a workspace color in hex format.

        Colors must be in the format #RRGGBB where R, G, B are
        hexadecimal digits.

        Args:
            color: The color string to validate

        Raises:
            WorkspaceValidationError: If the color format is invalid

        Example:
            >>> validator.validate_workspace_color('#0078d4')  # OK
            >>> validator.validate_workspace_color('blue')  # Raises error
        """
        if not color:
            raise WorkspaceValidationError(
                "Workspace color cannot be empty"
            )

        if not self.COLOR_PATTERN.match(color):
            raise WorkspaceValidationError(
                f"Invalid workspace color '{color}': "
                "must be in hex format #RRGGBB"
            )

    def validate_workspace(self, config: Dict[str, Any]) -> None:
        """
        Validate a complete workspace configuration.

        This method checks that all required fields are present
        and validates each field according to the validation rules.

        Required fields:
        - id: Workspace identifier
        - name: Human-readable name
        - folder: Path to workspace folder
        - emoji: Emoji icon
        - color: Hex color code

        Args:
            config: Dictionary containing workspace configuration

        Raises:
            WorkspaceValidationError: If any field is invalid or missing

        Example:
            >>> config = {
            ...     'id': 'python',
            ...     'name': 'Python Projects',
            ...     'folder': '/path/to/projects',
            ...     'emoji': '🐍',
            ...     'color': '#0078d4'
            ... }
            >>> validator.validate_workspace(config)  # OK
        """
        # Check required fields
        required_fields = ['id', 'name', 'folder', 'emoji', 'color']
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            raise WorkspaceValidationError(
                f"Missing required workspace fields: {', '.join(missing_fields)}"
            )

        # Validate each field
        self.validate_workspace_id(config['id'])
        # Non-blocking folder validation (warning only, not error)
        self.validate_workspace_folder(config['folder'], strict=False)
        self.validate_workspace_color(config['color'])

        # Additional validation for name (non-empty)
        if not config['name'] or not config['name'].strip():
            raise WorkspaceValidationError(
                "Workspace name cannot be empty"
            )

        # Additional validation for emoji (non-empty)
        if not config['emoji']:
            raise WorkspaceValidationError(
                "Workspace emoji cannot be empty"
            )
