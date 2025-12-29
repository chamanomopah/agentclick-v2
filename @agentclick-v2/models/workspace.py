"""
Workspace dataclass for representing workspaces in the system.

This module defines the core data structure for workspaces, which are
collections of virtual agents organized by project or context.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .virtual_agent import VirtualAgent


@dataclass
class Workspace:
    """
    Represents a workspace in the AgentClick V2 system.

    A workspace is a collection of virtual agents organized by project,
    context, or user-defined criteria. Each workspace has its own folder
    and can contain multiple agents.

    Attributes:
        id: Unique identifier for the workspace
        name: Human-readable name of the workspace
        folder: Path to the workspace folder on disk
        emoji: Emoji icon for visual identification
        color: Hex color code for UI theming
        agents: List of virtual agents in this workspace

    Example:
        >>> workspace = Workspace(
        ...     id="workspace-1",
        ...     name="My Project",
        ...     folder=Path("~/projects/my-project"),
        ...     emoji="🚀",
        ...     color="#3498db",
        ...     agents=[]
        ... )
        >>> workspace.add_agent(agent)
    """
    id: str
    name: str
    folder: Path
    emoji: str
    color: str
    agents: list[VirtualAgent] = field(default_factory=list)
    _agent_index: dict[str, VirtualAgent] = field(
        default_factory=dict,
        init=False,
        repr=False,
        compare=False
    )

    def __post_init__(self):
        """Initialize the agent index after dataclass creation."""
        self._agent_index = {agent.id: agent for agent in self.agents}

    def add_agent(self, agent: VirtualAgent) -> None:
        """
        Add a virtual agent to this workspace.

        Args:
            agent: The VirtualAgent to add

        Example:
            >>> workspace.add_agent(my_agent)
        """
        self.agents.append(agent)
        self._agent_index[agent.id] = agent

    def remove_agent(self, agent_id: str) -> None:
        """
        Remove a virtual agent from this workspace by ID.

        If the agent is not found, this method does nothing (no-op).

        Args:
            agent_id: ID of the agent to remove

        Example:
            >>> workspace.remove_agent("agent-123")
        """
        self.agents = [a for a in self.agents if a.id != agent_id]
        self._agent_index.pop(agent_id, None)

    def get_agent(self, agent_id: str) -> Optional[VirtualAgent]:
        """
        Retrieve a virtual agent from this workspace by ID.

        Uses O(1) index lookup for optimal performance.

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            VirtualAgent if found, None otherwise

        Example:
            >>> agent = workspace.get_agent("agent-123")
            >>> if agent:
            ...     print(agent.name)
        """
        return self._agent_index.get(agent_id)

    def get_enabled_agents(self) -> list[VirtualAgent]:
        """
        Get all enabled virtual agents in this workspace.

        Returns:
            List of enabled VirtualAgent instances

        Example:
            >>> enabled = workspace.get_enabled_agents()
            >>> for agent in enabled:
            ...     print(f"{agent.name}: {agent.type}")
        """
        return [a for a in self.agents if a.enabled]
