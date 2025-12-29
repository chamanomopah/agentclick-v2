"""
AgentClick V2 - Core Data Models

This package contains the core data structures for the AgentClick V2 system.

Main Classes:
    VirtualAgent: Represents a virtual agent (command, skill, or agent)
    Workspace: Represents a workspace containing multiple agents
    TemplateConfig: Configuration for agent prompt templates
    ExecutionResult: Result of executing a virtual agent

Type Aliases:
    AgentList: List of VirtualAgent instances
    AgentType: Literal type for agent types ("command", "skill", "agent")
    ExecutionStatus: Literal type for execution statuses
    WorkspaceList: List of Workspace instances
"""
from models.virtual_agent import VirtualAgent
from models.workspace import Workspace
from models.template_config import TemplateConfig
from models.execution_result import ExecutionResult
from typing import Literal, List

# Export all main classes
__all__ = [
    "VirtualAgent",
    "Workspace",
    "TemplateConfig",
    "ExecutionResult",
    # Type aliases
    "AgentList",
    "AgentType",
    "ExecutionStatus",
    "WorkspaceList",
]

# Type Aliases
AgentList = List[VirtualAgent]
"""Type alias for a list of VirtualAgent instances."""

AgentType = Literal["command", "skill", "agent"]
"""Type alias for valid agent type literals."""

ExecutionStatus = Literal["success", "error", "partial"]
"""Type alias for valid execution status literals."""

WorkspaceList = List[Workspace]
"""Type alias for a list of Workspace instances."""
