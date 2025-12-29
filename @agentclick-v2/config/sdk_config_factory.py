"""
SDK Config Factory for AgentClick V2.

This module provides the SDKOptionsBuilder class which helps construct
ClaudeAgentOptions for the VirtualAgentExecutor using the Builder pattern.
"""
from pathlib import Path
from typing import Optional, Dict, List, Any


class SDKOptionsBuilder:
    """
    Builder class for constructing ClaudeAgentOptions.

    This class implements the Builder pattern to make it easy to construct
    SDK option dictionaries with all required configuration for agent execution.

    Attributes:
        _options: Internal dictionary storing the option values

    Example:
        >>> builder = SDKOptionsBuilder()
        >>> options = (builder
        ...     .with_system_prompt("You are helpful.")
        ...     .with_working_directory(Path("/workspace"))
        ...     .with_tools(["Read", "Write"])
        ...     .with_permission_mode("acceptEdits")
        ...     .build())
    """

    def __init__(self):
        """
        Initialize the SDKOptionsBuilder with empty options.
        """
        self._options: Dict[str, Any] = {}

    def with_system_prompt(self, system_prompt: str) -> 'SDKOptionsBuilder':
        """
        Set the system prompt for the agent.

        Args:
            system_prompt: The system prompt text to use

        Returns:
            self for method chaining

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> builder.with_system_prompt("You are a test agent.")
        """
        self._options["system_prompt"] = system_prompt
        return self

    def with_working_directory(self, cwd: Path) -> 'SDKOptionsBuilder':
        """
        Set the working directory for the agent.

        Args:
            cwd: Path to the working directory

        Returns:
            self for method chaining

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> builder.with_working_directory(Path("/workspace"))
        """
        self._options["cwd"] = cwd
        return self

    def with_tools(self, tools: List[str]) -> 'SDKOptionsBuilder':
        """
        Set the allowed tools for the agent.

        Args:
            tools: List of tool names to allow (e.g., ["Read", "Write", "Edit"])

        Returns:
            self for method chaining

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> builder.with_tools(["Read", "Write", "Edit"])
        """
        self._options["allowed_tools"] = tools
        return self

    def with_mcp_servers(self, mcp_servers: Optional[Dict[str, Any]]) -> 'SDKOptionsBuilder':
        """
        Set the MCP servers for the agent.

        Args:
            mcp_servers: Dictionary of MCP server configurations, or None

        Returns:
            self for method chaining

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> builder.with_mcp_servers({"server1": {"url": "http://..."}})
        """
        if mcp_servers is not None:
            self._options["mcp_servers"] = mcp_servers
        return self

    def with_permission_mode(self, permission_mode: str) -> 'SDKOptionsBuilder':
        """
        Set the permission mode for the agent.

        Args:
            permission_mode: Permission mode (e.g., "acceptEdits", "manual")

        Returns:
            self for method chaining

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> builder.with_permission_mode("acceptEdits")
        """
        self._options["permission_mode"] = permission_mode
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build and return the ClaudeAgentOptions dictionary.

        Returns:
            Dictionary containing all configured options

        Example:
            >>> builder = SDKOptionsBuilder()
            >>> options = builder.with_system_prompt("Test").build()
            >>> assert options["system_prompt"] == "Test"
        """
        # Return a copy to prevent external modification
        return self._options.copy()
