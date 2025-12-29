"""
VirtualAgent dataclass for representing virtual agents in the system.

This module defines the core data structure for virtual agents, which can be
commands, skills, or autonomous agents.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


@dataclass
class VirtualAgent:
    """
    Represents a virtual agent in the AgentClick V2 system.

    A virtual agent can be a command, skill, or autonomous agent that can be
    invoked to perform tasks within workspaces.

    Attributes:
        id: Unique identifier for the agent
        type: Agent type - must be one of: "command", "skill", "agent"
        name: Human-readable name of the agent
        description: Detailed description of what the agent does
        source_file: Path to the agent's source code file
        emoji: Emoji icon for visual identification
        color: Hex color code for UI theming
        enabled: Whether the agent is currently active
        workspace_id: Optional ID of workspace this agent belongs to
        metadata: Additional flexible data about the agent

    Example:
        >>> agent = VirtualAgent(
        ...     id="git-commit",
        ...     type="command",
        ...     name="Git Commit",
        ...     description="Commit changes to git",
        ...     source_file=Path("/agents/git_commit.py"),
        ...     emoji="📝",
        ...     color="#FF5733",
        ...     enabled=True,
        ...     workspace_id="workspace-1",
        ...     metadata={"category": "git"}
        ... )
    """
    id: str
    type: Literal["command", "skill", "agent"]
    name: str
    description: str
    source_file: Path
    emoji: str
    color: str
    enabled: bool
    workspace_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def load_content(self) -> str:
        """
        Load and return the content of the agent's source file.

        Returns:
            str: The source code content

        Raises:
            FileNotFoundError: If source_file doesn't exist
            UnicodeDecodeError: If file is not valid UTF-8
            PermissionError: If file cannot be read
        """
        try:
            return self.source_file.read_text(encoding='utf-8')
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Agent source file not found: {self.source_file}") from e
        except UnicodeDecodeError as e:
            raise ValueError(f"Agent source file is not valid UTF-8: {self.source_file}") from e
        except PermissionError as e:
            raise PermissionError(f"Permission denied reading agent source file: {self.source_file}") from e

    def extract_metadata(self) -> dict:
        """
        Extract metadata from the agent's definition.

        Returns metadata dict with both explicit metadata and derived info.

        Returns:
            dict: Combined metadata from agent definition

        Example:
            >>> agent.extract_metadata()
            {'category': 'git', 'type': 'command', 'enabled': True}
        """
        base_metadata = {
            'type': self.type,
            'enabled': self.enabled,
            'has_workspace': self.workspace_id is not None
        }
        return {**base_metadata, **self.metadata}

    def get_system_prompt(self) -> str:
        """
        Generate a system prompt for this agent.

        Creates a formatted system prompt that can be used for LLM interactions.

        Returns:
            str: Formatted system prompt string

        Example:
            >>> agent.get_system_prompt()
            'You are Git Commit, a command agent...'
        """
        return (
            f"You are {self.name}, {self.description}. "
            f"Type: {self.type}. "
            f"Use your capabilities to assist the user effectively."
        )
