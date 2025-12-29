"""
AgentClick V2 - Core Components

This package contains the core business logic and components for the
AgentClick V2 system.
"""

from .exceptions import (
    WorkspaceError,
    WorkspaceNotFoundError,
    WorkspaceLoadError,
    WorkspaceValidationError,
    TemplateError,
    TemplateSyntaxError,
    TemplateValidationError,
    AgentExecutionError,
    SDKConnectionError
)
from .workspace_validator import WorkspaceValidator
from .workspace_manager import WorkspaceManager
from .template_engine import TemplateEngine, ValidationResult
from .agent_executor import VirtualAgentExecutor
from .input_processor import InputProcessor, InputType

__all__ = [
    "WorkspaceError",
    "WorkspaceNotFoundError",
    "WorkspaceLoadError",
    "WorkspaceValidationError",
    "TemplateError",
    "TemplateSyntaxError",
    "TemplateValidationError",
    "AgentExecutionError",
    "SDKConnectionError",
    "WorkspaceValidator",
    "WorkspaceManager",
    "TemplateEngine",
    "ValidationResult",
    "VirtualAgentExecutor",
    "InputProcessor",
    "InputType",
]
