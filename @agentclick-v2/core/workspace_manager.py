"""
Workspace Manager for managing multiple workspaces.

This module provides the WorkspaceManager class which handles loading,
switching, adding, updating, and removing workspaces with persistence
to YAML configuration files.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, TypedDict
import asyncio
import yaml

from .exceptions import (
    WorkspaceNotFoundError,
    WorkspaceLoadError,
    WorkspaceValidationError
)
from .workspace_validator import WorkspaceValidator
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent
from utils.yaml_helpers import load_yaml, save_yaml, load_yaml_async, save_yaml_async


class WorkspaceConfigDict(TypedDict):
    """Type definition for workspace configuration dictionary."""
    id: str
    name: str
    folder: str | Path
    emoji: str
    color: str


class WorkspaceManager:
    """
    Manages multiple workspaces with isolated contexts.

    The WorkspaceManager is responsible for:
    - Loading workspaces from YAML configuration
    - Switching between workspaces
    - Adding, updating, and removing workspaces
    - Persisting workspace state to disk
    - Validating workspace configurations

    The manager uses a singleton-like pattern and maintains the current
    workspace state in memory while persisting to disk for durability.

    Attributes:
        config_path: Path to the workspaces.yaml configuration file
        workspaces: Dictionary mapping workspace IDs to Workspace objects
        current_workspace_id: ID of the currently active workspace

    Example:
        >>> manager = WorkspaceManager()
        >>> await manager.load_workspaces()
        >>> manager.switch_workspace('python')
        >>> current = manager.get_current_workspace()
        >>> print(current.name)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the WorkspaceManager.

        Args:
            config_path: Path to the workspaces.yaml file.
                        Defaults to 'config/workspaces.yaml' if not provided.

        Example:
            >>> manager = WorkspaceManager()
            >>> manager = WorkspaceManager(config_path='/custom/path/workspaces.yaml')
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config/workspaces.yaml in project root
            self.config_path = Path(__file__).parent.parent / 'config' / 'workspaces.yaml'

        self.workspaces: Dict[str, Workspace] = {}
        self.current_workspace_id: Optional[str] = None
        self.validator = WorkspaceValidator()

    async def load_workspaces(self) -> None:
        """
        Load workspaces from the YAML configuration file.

        This method reads the workspaces.yaml file asynchronously, validates each
        workspace configuration, and populates the workspaces dictionary. It also
        sets the current workspace from the configuration.

        Raises:
            WorkspaceLoadError: If the file cannot be loaded or parsed
            WorkspaceValidationError: If any workspace configuration is invalid

        Example:
            >>> manager = WorkspaceManager()
            >>> await manager.load_workspaces()
            >>> print(f"Loaded {len(manager.workspaces)} workspaces")
        """
        try:
            # Use async YAML loading to avoid blocking
            data = await load_yaml_async(self.config_path)

            if data is None:
                raise WorkspaceLoadError(
                    f"Workspace configuration file is empty: {self.config_path}"
                )

            # Validate version
            if data.get('version') != '2.0':
                raise WorkspaceLoadError(
                    f"Unsupported configuration version: {data.get('version')}. "
                    "Expected version 2.0"
                )

            # Load current workspace
            self.current_workspace_id = data.get('current_workspace')

            # Load workspaces
            workspaces_data = data.get('workspaces', {})

            for workspace_id, workspace_config in workspaces_data.items():
                # Add the ID to the config for validation
                workspace_config['id'] = workspace_id

                # Validate the workspace
                self.validator.validate_workspace(workspace_config)

                # Load agents from config if present
                agents_data = workspace_config.get('agents', [])
                agents = []
                for agent_data in agents_data:
                    # Create VirtualAgent from saved data
                    agent = VirtualAgent(
                        id=agent_data.get('id', ''),
                        type=agent_data.get('type', 'command'),
                        name=agent_data.get('name', f"Agent {agent_data.get('id', 'Unknown')}"),
                        description=agent_data.get('description', ''),
                        enabled=agent_data.get('enabled', True),
                        workspace_id=workspace_id
                    )
                    agents.append(agent)

                # Create Workspace object with agents
                workspace = Workspace(
                    id=workspace_id,
                    name=workspace_config['name'],
                    folder=Path(workspace_config['folder']),
                    emoji=workspace_config['emoji'],
                    color=workspace_config['color'],
                    agents=agents
                )

                self.workspaces[workspace_id] = workspace

        except FileNotFoundError:
            raise WorkspaceLoadError(
                f"Workspace configuration file not found: {self.config_path}"
            )
        except (WorkspaceLoadError, WorkspaceValidationError):
            raise
        except (yaml.YAMLError, IOError, OSError) as e:
            raise WorkspaceLoadError(
                f"Failed to load workspace configuration: {str(e)}"
            ) from e

    def switch_workspace(self, workspace_id: str) -> None:
        """
        Switch to a different workspace.

        This method changes the current workspace and persists the change
        to the YAML configuration file.

        Args:
            workspace_id: ID of the workspace to switch to

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist

        Example:
            >>> manager.switch_workspace('python')
            >>> print(manager.current_workspace_id)
            python
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        self.current_workspace_id = workspace_id
        self._persist_state()

    def switch_to_next_workspace(self) -> None:
        """
        Switch to the next workspace in the list.

        Cycles through workspaces in order. If at the end, wraps to the beginning.
        Raises an error if there are no workspaces.

        Raises:
            ValueError: If there are no workspaces

        Example:
            >>> manager.switch_to_next_workspace()
            >>> # If current is "python", switches to next workspace
        """
        workspace_list = self.list_workspaces()
        if len(workspace_list) == 0:
            raise ValueError("No workspaces available to switch to")

        if len(workspace_list) == 1:
            # Only one workspace, no need to switch
            return

        # Find current workspace index
        current_index = -1
        for i, ws in enumerate(workspace_list):
            if ws.id == self.current_workspace_id:
                current_index = i
                break

        # Calculate next index (wrap to beginning if at end)
        next_index = (current_index + 1) % len(workspace_list)

        # Switch to next workspace
        next_workspace = workspace_list[next_index]
        self.switch_workspace(next_workspace.id)

    def get_current_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.

        Returns:
            Workspace object if a workspace is current, None otherwise

        Example:
            >>> current = manager.get_current_workspace()
            >>> if current:
            ...     print(f"Current workspace: {current.name}")
        """
        if self.current_workspace_id is None:
            return None

        return self.workspaces.get(self.current_workspace_id)

    def list_workspaces(self) -> List[Workspace]:
        """
        List all workspaces.

        Returns:
            List of all Workspace objects

        Example:
            >>> workspaces = manager.list_workspaces()
            >>> for ws in workspaces:
            ...     print(f"{ws.id}: {ws.name}")
        """
        return list(self.workspaces.values())

    def add_workspace(self, config: WorkspaceConfigDict) -> None:
        """
        Add a new workspace.

        Validates the workspace configuration and adds it to the manager.
        The change is persisted to the YAML file.

        Args:
            config: Dictionary containing workspace configuration with keys:
                   - id (str): Workspace identifier
                   - name (str): Human-readable name
                   - folder (str | Path): Path to workspace folder
                   - emoji (str): Emoji icon
                   - color (str): Hex color code (#RRGGBB)

        Raises:
            WorkspaceValidationError: If the configuration is invalid

        Example:
            >>> manager.add_workspace({
            ...     'id': 'rust',
            ...     'name': 'Rust Projects',
            ...     'folder': '/rust',
            ...     'emoji': '🦀',
            ...     'color': '#dea584'
            ... })
        """
        # Validate the configuration
        self.validator.validate_workspace(config)

        workspace_id = config['id']

        # Check for duplicate workspace ID
        if workspace_id in self.workspaces:
            raise WorkspaceValidationError(
                f"Workspace '{workspace_id}' already exists"
            )

        # Create Workspace object
        workspace = Workspace(
            id=workspace_id,
            name=config['name'],
            folder=Path(config['folder']),
            emoji=config['emoji'],
            color=config['color']
        )

        self.workspaces[workspace_id] = workspace
        self._persist_state()

    def update_workspace(self, workspace_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing workspace.

        Applies the provided updates to the workspace configuration.
        The workspace ID cannot be changed. The change is persisted.

        Args:
            workspace_id: ID of the workspace to update
            updates: Dictionary of fields to update (keys: 'name', 'folder', 'emoji', 'color')

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist
            WorkspaceValidationError: If the updates are invalid

        Example:
            >>> manager.update_workspace('python', {
            ...     'name': 'Python Projects (Updated)',
            ...     'emoji': '🐍🚀'
            ... })
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        workspace = self.workspaces[workspace_id]

        # Apply updates
        if 'name' in updates:
            if not updates['name'] or not updates['name'].strip():
                raise WorkspaceValidationError("Workspace name cannot be empty")
            workspace.name = updates['name']
        if 'folder' in updates:
            new_folder = Path(updates['folder'])
            self.validator.validate_workspace_folder(new_folder)
            workspace.folder = new_folder
        if 'emoji' in updates:
            if not updates['emoji']:
                raise WorkspaceValidationError("Workspace emoji cannot be empty")
            workspace.emoji = updates['emoji']
        if 'color' in updates:
            self.validator.validate_workspace_color(updates['color'])
            workspace.color = updates['color']

        self._persist_state()

    def remove_workspace(self, workspace_id: str) -> None:
        """
        Remove a workspace.

        Removes the workspace from the manager. The last workspace
        cannot be removed. If the removed workspace was current,
        current_workspace_id is set to None.

        Args:
            workspace_id: ID of the workspace to remove

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist
            ValueError: If attempting to remove the last workspace

        Example:
            >>> manager.remove_workspace('old-workspace')
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        # Prevent removing the last workspace
        if len(self.workspaces) == 1:
            raise ValueError(
                "Cannot remove the last workspace. "
                "At least one workspace must exist."
            )

        # Clear current workspace if we're removing it
        if self.current_workspace_id == workspace_id:
            self.current_workspace_id = None

        del self.workspaces[workspace_id]
        self._persist_state()

    def get_workspace_agents(self, workspace_id: str) -> List:
        """
        Get all agents in a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of agents in the workspace

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist

        Example:
            >>> agents = manager.get_workspace_agents('python')
            >>> for agent in agents:
            ...     print(f"{agent.id}: {agent.type}")
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        workspace = self.workspaces[workspace_id]
        return workspace.agents

    def assign_agent_to_workspace(self, workspace_id: str, agent: Any) -> None:
        """
        Assign an agent to a workspace.

        Args:
            workspace_id: ID of the workspace
            agent: VirtualAgent instance to assign

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist

        Example:
            >>> manager.assign_agent_to_workspace('python', my_agent)
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        workspace = self.workspaces[workspace_id]
        workspace.add_agent(agent)

    def remove_agent_from_workspace(self, workspace_id: str, agent_id: str) -> None:
        """
        Remove an agent from a workspace.

        Args:
            workspace_id: ID of the workspace
            agent_id: ID of the agent to remove

        Raises:
            WorkspaceNotFoundError: If the workspace doesn't exist

        Example:
            >>> manager.remove_agent_from_workspace('python', 'agent-123')
        """
        if workspace_id not in self.workspaces:
            raise WorkspaceNotFoundError(workspace_id)

        workspace = self.workspaces[workspace_id]
        workspace.remove_agent(agent_id)

    def _persist_state(self) -> None:
        """
        Persist the current manager state to the YAML file.

        This is an internal method that saves the workspaces dictionary
        and current workspace ID to the configuration file.
        """
        # Build data structure
        data = {
            'version': '2.0',
            'current_workspace': self.current_workspace_id,
            'workspaces': {}
        }

        for workspace_id, workspace in self.workspaces.items():
            # Serialize agents to dict
            agents_data = []
            for agent in workspace.agents:
                agents_data.append({
                    'id': agent.id,
                    'type': agent.type,
                    'name': agent.name,
                    'description': agent.description,
                    'enabled': agent.enabled
                })

            data['workspaces'][workspace_id] = {
                'name': workspace.name,
                'folder': str(workspace.folder),
                'emoji': workspace.emoji,
                'color': workspace.color,
                'agents': agents_data
            }

        # Save to file
        save_yaml(self.config_path, data)
