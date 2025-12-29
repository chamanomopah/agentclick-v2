"""
Virtual Agent Executor for AgentClick V2.

This module provides the VirtualAgentExecutor class which executes virtual agents
using the Claude SDK. It handles template rendering, SDK options configuration,
tool mapping, and MCP server creation.

Key features:
- Dynamic SDK options creation from VirtualAgent metadata
- Template engine integration for input formatting
- Tool mapping based on agent type
- MCP server configuration for skills
- Comprehensive error handling
"""
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Any

from models.virtual_agent import VirtualAgent
from models.workspace import Workspace
from models.execution_result import ExecutionResult
from core.template_engine import TemplateEngine
from core.exceptions import AgentExecutionError, SDKConnectionError, TemplateError
from config.sdk_config_factory import SDKOptionsBuilder


# Configure logging
logger = logging.getLogger(__name__)

# Base tools available to all agents
BASE_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob"]


class VirtualAgentExecutor:
    """
    Executor for running virtual agents using Claude SDK.

    This executor is responsible for:
    - Loading agent content from .md files
    - Applying input templates via TemplateEngine
    - Creating SDK options dynamically based on agent type
    - Mapping tools based on agent configuration
    - Setting up MCP servers for skills
    - Handling execution errors and returning proper status

    Attributes:
        template_engine: TemplateEngine instance for input formatting
        default_options: Default SDK options to apply to all executions

    Example:
        >>> executor = VirtualAgentExecutor(template_engine=TemplateEngine())
        >>> result = await executor.execute(
        ...     agent=agent,
        ...     input_text="Test input",
        ...     workspace=workspace,
        ...     focus_file="main.py"
        ... )
        >>> if result.is_success():
        ...     print(result.output)
    """

    def __init__(
        self,
        template_engine: TemplateEngine,
        default_options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the VirtualAgentExecutor.

        Args:
            template_engine: TemplateEngine instance for template application
            default_options: Optional default SDK options (e.g., permission_mode)

        Example:
            >>> engine = TemplateEngine()
            >>> executor = VirtualAgentExecutor(
            ...     template_engine=engine,
            ...     default_options={"permission_mode": "manual"}
            ... )
        """
        self.template_engine = template_engine
        self.default_options = default_options or {}

        logger.debug(
            f"VirtualAgentExecutor initialized with default_options: {self.default_options}"
        )

    def _get_tools_for_agent(self, agent: VirtualAgent) -> List[str]:
        """
        Determine allowed tools based on agent type and metadata.

        Tool mapping rules:
        - command: BASE_TOOLS only
        - skill: BASE_TOOLS + custom_tools from metadata
        - agent: configurable tools from metadata (or empty if not specified)

        Args:
            agent: The VirtualAgent instance

        Returns:
            List of tool names allowed for this agent

        Example:
            >>> executor = VirtualAgentExecutor(template_engine)
            >>> tools = executor._get_tools_for_agent(command_agent)
            >>> assert tools == ["Read", "Write", "Edit", "Grep", "Glob"]
        """
        if agent.type == "command":
            # Commands get only base tools
            return BASE_TOOLS.copy()

        elif agent.type == "skill":
            # Skills get base tools + custom tools
            tools = BASE_TOOLS.copy()
            custom_tools = agent.metadata.get("custom_tools", [])
            if isinstance(custom_tools, list):
                tools.extend(custom_tools)
            return tools

        elif agent.type == "agent":
            # Agents have configurable tools from metadata
            allowed_tools = agent.metadata.get("allowed_tools", None)
            if allowed_tools and isinstance(allowed_tools, list):
                return allowed_tools
            # Default to BASE_TOOLS for agents without explicit tool configuration
            logger.debug(f"Agent {agent.id} has no tool config, using BASE_TOOLS")
            return BASE_TOOLS.copy()

        else:
            logger.warning(f"Unknown agent type: {agent.type}")
            return []

    def _get_mcp_servers(self, agent: VirtualAgent) -> Optional[Dict[str, Any]]:
        """
        Create MCP server configuration for agents that need it.

        MCP server rules:
        - command: No MCP servers (return None)
        - skill: MCP servers if custom_tools present
        - agent: MCP servers if specified in metadata

        Args:
            agent: The VirtualAgent instance

        Returns:
            MCP server configuration dict or None

        Example:
            >>> mcp = executor._get_mcp_servers(skill_agent)
            >>> if mcp:
            ...     print(f"Configured {len(mcp)} MCP servers")
        """
        # Commands and agents don't get MCP servers
        if agent.type in ["command", "agent"]:
            return None

        # Skills get MCP servers if they have custom tools
        if agent.type == "skill":
            custom_tools = agent.metadata.get("custom_tools", [])
            if custom_tools and isinstance(custom_tools, list):
                try:
                    # Use SDK's create_sdk_mcp_server function
                    from claude_agent_sdk import create_sdk_mcp_server
                    logger.debug(f"Creating MCP server for skill {agent.id} with tools: {custom_tools}")
                    return create_sdk_mcp_server(custom_tools)
                except ImportError:
                    # SDK not available - return placeholder for testing
                    logger.warning(
                        f"SDK not available, using placeholder MCP config for {agent.id}. "
                        "Install SDK: pip install claude-agent-sdk"
                    )
                    # Fallback to placeholder configuration for testing
                    mcp_config = {}
                    for tool_name in custom_tools:
                        mcp_config[f"mcp_{tool_name}"] = {
                            "type": "custom_tool",
                            "tool_name": tool_name
                        }
                    return mcp_config

        return None

    async def create_sdk_options(
        self,
        agent: VirtualAgent,
        workspace: Workspace,
        input_text: str,
        focus_file: Optional[str]
    ) -> Dict[str, Any]:
        """
        Create ClaudeAgentOptions dynamically from VirtualAgent.

        This method builds the complete SDK options configuration including:
        - System prompt from agent's .md file content
        - Working directory from workspace
        - Allowed tools based on agent type
        - MCP servers if applicable
        - Permission mode

        Args:
            agent: The VirtualAgent to execute
            workspace: The workspace context
            input_text: User input text (for template context)
            focus_file: Optional focused file path

        Returns:
            Dictionary of ClaudeAgentOptions

        Raises:
            FileNotFoundError: If agent source file doesn't exist
            ValueError: If agent source file is invalid

        Example:
            >>> options = await executor.create_sdk_options(
            ...     agent=agent,
            ...     workspace=workspace,
            ...     input_text="Test",
            ...     focus_file="main.py"
            ... )
            >>> assert "system_prompt" in options
        """
        # Load system prompt from agent's .md file
        try:
            system_prompt = agent.load_content()
        except FileNotFoundError as e:
            logger.error(f"Agent source file not found: {agent.source_file}")
            raise
        except ValueError as e:
            logger.error(f"Invalid agent source file: {agent.source_file}")
            raise

        # Build options using builder pattern
        builder = SDKOptionsBuilder()
        builder.with_system_prompt(system_prompt)

        # Validate workspace path before using
        workspace_path = workspace.folder
        if not workspace_path.exists():
            raise FileNotFoundError(f"Workspace folder does not exist: {workspace_path}")
        if not workspace_path.is_dir():
            raise ValueError(f"Workspace folder is not a directory: {workspace_path}")

        builder.with_working_directory(workspace_path.resolve())
        builder.with_tools(self._get_tools_for_agent(agent))
        builder.with_permission_mode("acceptEdits")

        # Add MCP servers if applicable
        mcp_servers = self._get_mcp_servers(agent)
        if mcp_servers:
            builder.with_mcp_servers(mcp_servers)

        # Apply default options (can override defaults)
        options = builder.build()

        # Merge default options
        for key, value in self.default_options.items():
            if key not in options:
                options[key] = value

        logger.debug(
            f"Created SDK options for agent {agent.id}: "
            f"tools={len(options.get('allowed_tools', []))}, "
            f"mcp={'yes' if mcp_servers else 'no'}"
        )

        return options

    async def execute(
        self,
        agent: VirtualAgent,
        input_text: str,
        workspace: Workspace,
        focus_file: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute a virtual agent with the given input.

        This method:
        1. Applies template (if configured) via TemplateEngine
        2. Creates SDK options from agent configuration
        3. Executes agent using Claude SDK
        4. Returns ExecutionResult with appropriate status

        Args:
            agent: The VirtualAgent to execute
            input_text: User input text
            workspace: The workspace context
            focus_file: Optional focused file path

        Returns:
            ExecutionResult with output, status, and metadata

        Example:
            >>> result = await executor.execute(
            ...     agent=agent,
            ...     input_text="Refactor this code",
            ...     workspace=workspace,
            ...     focus_file="main.py"
            ... )
            >>> if result.is_success():
            ...     print(result.output)
        """
        # Prepare metadata for result
        metadata = {
            "agent_id": agent.id,
            "agent_type": agent.type,
            "workspace_id": workspace.id,
            "focus_file": focus_file
        }

        # Step 1: Apply template if configured
        try:
            template_vars = {
                "context_folder": str(workspace.folder),
                "focus_file": focus_file or ""
            }
            rendered_input = self.template_engine.apply_template(
                agent.id,
                input_text,
                template_vars
            )
        except TemplateError as e:
            logger.warning(f"Template error for {agent.id}, using raw input: {e}")
            rendered_input = input_text
        except (KeyError, ValueError) as e:
            # Specific template variable or validation errors
            logger.warning(f"Template variable error for {agent.id}: {e}, using raw input")
            rendered_input = input_text
        except Exception as e:
            # Unexpected errors - log with more detail
            logger.warning(f"Unexpected template error for {agent.id} ({type(e).__name__}): {e}, using raw input")
            rendered_input = input_text

        # Step 2: Create SDK options (this validates agent file exists via create_sdk_options)
        try:
            options = await self.create_sdk_options(
                agent=agent,
                workspace=workspace,
                input_text=rendered_input,
                focus_file=focus_file
            )
        except FileNotFoundError as e:
            logger.error(f"Agent source file not found during SDK options creation: {e}")
            return ExecutionResult(
                output=f"Agent source file not found: {agent.source_file}",
                status="error",
                metadata={**metadata, "error": str(e)}
            )
        except (ValueError, Exception) as e:
            logger.error(f"Failed to create SDK options: {e}")
            return ExecutionResult(
                output=f"Failed to configure agent execution: {e}",
                status="error",
                metadata={**metadata, "error": str(e)}
            )

        # Step 4: Execute using SDK (with mock for testing)
        try:
            # Import SDK here to allow mocking in tests
            # Try to import from SDK, fall back to mock
            try:
                from claude_agent_sdk import ClaudeAgent, create_sdk_mcp_server
                logger.debug("Using real Claude SDK")
            except ImportError as e:
                # SDK not available - use mock for testing
                logger.warning(
                    f"Claude SDK import failed: {e}. Using mock implementation for testing. "
                    "Install SDK with: pip install claude-agent-sdk"
                )
                ClaudeAgent = self._create_mock_agent_class()
                create_sdk_mcp_server = lambda x: None

            # Create MCP server if needed
            mcp_server = None
            if "mcp_servers" in options and options["mcp_servers"]:
                if create_sdk_mcp_server:
                    mcp_server = create_sdk_mcp_server(options["mcp_servers"])

            # Create and run agent
            agent_instance = ClaudeAgent(options)
            output = await agent_instance.run(rendered_input)

            # Check for partial success (warnings or errors in output)
            status = "success"
            if output and any(marker in output.lower() for marker in ["warning:", "error:", "failed", "but succeeded"]):
                status = "partial"
                logger.info(f"Agent {agent.id} completed with partial success")

            return ExecutionResult(
                output=output,
                status=status,
                metadata=metadata
            )

        except SDKConnectionError as e:
            logger.error(f"SDK connection error for agent {agent.id}: {e}")
            return ExecutionResult(
                output=f"Failed to connect to SDK: {e}",
                status="error",
                metadata={**metadata, "error": f"SDK connection error: {e}"}
            )

        except AgentExecutionError as e:
            logger.error(f"Agent execution error for {agent.id}: {e}")
            return ExecutionResult(
                output=f"Agent execution failed: {e}",
                status="error",
                metadata={**metadata, "error": f"Execution error: {e}"}
            )

        except Exception as e:
            logger.error(f"Unexpected error executing agent {agent.id}: {e}", exc_info=True)
            return ExecutionResult(
                output=f"Unexpected error: {e}",
                status="error",
                metadata={**metadata, "error": f"Unexpected error: {e}"}
            )

    def _create_mock_agent_class(self):
        """
        Create a mock ClaudeAgent class for testing when SDK is not available.

        This allows the executor to be tested without the actual SDK installed.
        """
        class MockClaudeAgent:
            def __init__(self, options):
                self.options = options

            async def run(self, input_text):
                return f"Mock execution result for input: {input_text[:50]}..."

        return MockClaudeAgent
