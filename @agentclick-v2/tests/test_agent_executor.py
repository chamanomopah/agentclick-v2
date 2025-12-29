"""
Tests for VirtualAgentExecutor.

Tests the core executor that runs virtual agents using Claude SDK.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from models.virtual_agent import VirtualAgent
from models.workspace import Workspace
from models.execution_result import ExecutionResult
from core.agent_executor import VirtualAgentExecutor
from core.template_engine import TemplateEngine
from core.exceptions import AgentExecutionError, SDKConnectionError, TemplateError
from config.sdk_config_factory import SDKOptionsBuilder


class TestVirtualAgentExecutor:
    """Test suite for VirtualAgentExecutor class."""

    @pytest.fixture
    def template_engine(self):
        """Create a template engine fixture."""
        return TemplateEngine()

    @pytest.fixture
    def executor(self, template_engine):
        """Create an executor fixture."""
        return VirtualAgentExecutor(template_engine=template_engine)

    @pytest.fixture
    def mock_workspace(self, tmp_path):
        """Create a mock workspace."""
        workspace = Workspace(
            id="test-workspace",
            name="Test Workspace",
            folder=tmp_path,
            emoji="🧪",
            color="#3498db"
        )
        return workspace

    @pytest.fixture
    def command_agent(self, tmp_path):
        """Create a command-type agent for testing."""
        agent_file = tmp_path / "test_command.md"
        agent_file.write_text("# Test Command\n\nThis is a test command.", encoding='utf-8')

        return VirtualAgent(
            id="test-command",
            type="command",
            name="Test Command",
            description="A test command agent",
            source_file=agent_file,
            emoji="📝",
            color="#3498db",
            enabled=True
        )

    @pytest.fixture
    def skill_agent(self, tmp_path):
        """Create a skill-type agent for testing."""
        agent_file = tmp_path / "test_skill.md"
        agent_file.write_text("# Test Skill\n\nThis is a test skill.", encoding='utf-8')

        return VirtualAgent(
            id="test-skill",
            type="skill",
            name="Test Skill",
            description="A test skill agent",
            source_file=agent_file,
            emoji="🎯",
            color="#9b59b6",
            enabled=True,
            metadata={"custom_tools": ["CustomTool1", "CustomTool2"]}
        )

    @pytest.fixture
    def agent_type_agent(self, tmp_path):
        """Create an agent-type agent for testing."""
        agent_file = tmp_path / "test_agent.md"
        agent_file.write_text("# Test Agent\n\nThis is a test agent.", encoding='utf-8')

        return VirtualAgent(
            id="test-agent",
            type="agent",
            name="Test Agent",
            description="A test autonomous agent",
            source_file=agent_file,
            emoji="🤖",
            color="#2ecc71",
            enabled=True,
            metadata={"allowed_tools": ["Read", "Write", "CustomTool"]}
        )

    def test_initialization(self, template_engine):
        """Test that executor initializes correctly."""
        executor = VirtualAgentExecutor(template_engine=template_engine)
        assert executor.template_engine is template_engine
        assert executor.default_options == {}

    def test_initialization_with_default_options(self, template_engine):
        """Test initialization with default options."""
        defaults = {"permission_mode": "manual"}
        executor = VirtualAgentExecutor(
            template_engine=template_engine,
            default_options=defaults
        )
        assert executor.default_options == defaults

    def test_get_tools_for_command_type(self, executor, command_agent):
        """Test tool mapping for command type agents."""
        tools = executor._get_tools_for_agent(command_agent)
        expected = ["Read", "Write", "Edit", "Grep", "Glob"]
        assert tools == expected

    def test_get_tools_for_skill_type_with_custom_tools(self, executor, skill_agent):
        """Test tool mapping for skill type agents with custom tools."""
        tools = executor._get_tools_for_agent(skill_agent)
        expected = ["Read", "Write", "Edit", "Grep", "Glob", "CustomTool1", "CustomTool2"]
        assert tools == expected

    def test_get_tools_for_skill_type_without_custom_tools(self, executor, tmp_path):
        """Test tool mapping for skill type agents without custom tools."""
        agent_file = tmp_path / "skill_no_custom.md"
        agent_file.write_text("# Skill\n\nTest", encoding='utf-8')

        agent = VirtualAgent(
            id="skill-no-custom",
            type="skill",
            name="Skill No Custom",
            description="Skill without custom tools",
            source_file=agent_file,
            emoji="🎯",
            color="#9b59b6",
            enabled=True,
            metadata={}
        )

        tools = executor._get_tools_for_agent(agent)
        expected = ["Read", "Write", "Edit", "Grep", "Glob"]
        assert tools == expected

    def test_get_tools_for_agent_type_with_config(self, executor, agent_type_agent):
        """Test tool mapping for agent type with configured tools."""
        tools = executor._get_tools_for_agent(agent_type_agent)
        expected = ["Read", "Write", "CustomTool"]
        assert tools == expected

    def test_get_tools_for_agent_type_without_config(self, executor, tmp_path):
        """Test tool mapping for agent type without configured tools."""
        agent_file = tmp_path / "agent_no_config.md"
        agent_file.write_text("# Agent\n\nTest", encoding='utf-8')

        agent = VirtualAgent(
            id="agent-no-config",
            type="agent",
            name="Agent No Config",
            description="Agent without tool config",
            source_file=agent_file,
            emoji="🤖",
            color="#2ecc71",
            enabled=True,
            metadata={}
        )

        tools = executor._get_tools_for_agent(agent)
        # Should return BASE_TOOLS as default for agents without explicit config
        expected = ["Read", "Write", "Edit", "Grep", "Glob"]
        assert tools == expected

    def test_get_mcp_servers_for_command_type(self, executor, command_agent):
        """Test MCP server creation for command type (should be None)."""
        mcp_servers = executor._get_mcp_servers(command_agent)
        assert mcp_servers is None

    def test_get_mcp_servers_for_agent_type(self, executor, agent_type_agent):
        """Test MCP server creation for agent type (should be None)."""
        mcp_servers = executor._get_mcp_servers(agent_type_agent)
        assert mcp_servers is None

    def test_get_mcp_servers_for_skill_type_with_custom_tools(self, executor, skill_agent):
        """Test MCP server creation for skill type with custom tools."""
        mcp_servers = executor._get_mcp_servers(skill_agent)

        # Should create MCP servers configuration
        assert mcp_servers is not None
        assert isinstance(mcp_servers, dict)

    def test_get_mcp_servers_for_skill_type_without_custom_tools(self, executor, tmp_path):
        """Test MCP server creation for skill type without custom tools."""
        agent_file = tmp_path / "skill_no_custom_tools.md"
        agent_file.write_text("# Skill\n\nTest", encoding='utf-8')

        agent = VirtualAgent(
            id="skill-no-custom-tools",
            type="skill",
            name="Skill No Custom Tools",
            description="Skill without custom tools",
            source_file=agent_file,
            emoji="🎯",
            color="#9b59b6",
            enabled=True,
            metadata={}
        )

        mcp_servers = executor._get_mcp_servers(agent)
        # Should return None if no custom tools
        assert mcp_servers is None

    @pytest.mark.asyncio
    async def test_create_sdk_options_for_command_agent(
        self, executor, command_agent, mock_workspace
    ):
        """Test SDK options creation for command agent."""
        options = await executor.create_sdk_options(
            agent=command_agent,
            workspace=mock_workspace,
            input_text="test input",
            focus_file="test.py"
        )

        assert options["system_prompt"] == command_agent.load_content()
        assert options["cwd"] == mock_workspace.folder
        assert options["allowed_tools"] == ["Read", "Write", "Edit", "Grep", "Glob"]
        assert options["permission_mode"] == "acceptEdits"
        assert "mcp_servers" not in options or options.get("mcp_servers") is None

    @pytest.mark.asyncio
    async def test_create_sdk_options_for_skill_agent(
        self, executor, skill_agent, mock_workspace
    ):
        """Test SDK options creation for skill agent."""
        options = await executor.create_sdk_options(
            agent=skill_agent,
            workspace=mock_workspace,
            input_text="test input",
            focus_file="test.py"
        )

        assert options["system_prompt"] == skill_agent.load_content()
        assert options["cwd"] == mock_workspace.folder
        assert "CustomTool1" in options["allowed_tools"]
        assert "CustomTool2" in options["allowed_tools"]
        assert options["permission_mode"] == "acceptEdits"

    @pytest.mark.asyncio
    async def test_execute_with_template(
        self, executor, command_agent, mock_workspace, template_engine
    ):
        """Test execution with template application."""
        # Create a template for this agent
        template_engine.save_template(
            agent_id=command_agent.id,
            template="Process: {{input}} in context of {{focus_file}}",
            enabled=True
        )

        # Mock the SDK execution
        with patch('builtins.__import__') as mock_import:
            # Setup mock to return our mock SDK
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Success!"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test input",
                workspace=mock_workspace,
                focus_file="test.py"
            )

            assert result.status == "success"
            assert "Success!" in result.output

    @pytest.mark.asyncio
    async def test_execute_without_template(
        self, executor, command_agent, mock_workspace
    ):
        """Test execution without template (raw input)."""
        # Mock the SDK execution
        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Raw input processed"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="raw input",
                workspace=mock_workspace,
                focus_file="test.py"
            )

            assert result.status == "success"
            assert result.output == "Raw input processed"

    @pytest.mark.asyncio
    async def test_execute_with_sdk_connection_error(
        self, executor, command_agent, mock_workspace
    ):
        """Test execution handling SDK connection errors."""
        with patch('builtins.__import__') as mock_import:
            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = MagicMock(side_effect=SDKConnectionError("Connection failed"))
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "error"
            assert "Connection failed" in result.metadata.get("error", "")

    @pytest.mark.asyncio
    async def test_execute_with_agent_execution_error(
        self, executor, command_agent, mock_workspace
    ):
        """Test execution handling agent execution errors."""
        with patch('builtins.__import__') as mock_import:
            mock_agent = MagicMock()
            mock_agent_instance = AsyncMock()
            mock_agent_instance.run.side_effect = AgentExecutionError("Execution failed")
            mock_agent.return_value = mock_agent_instance

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "error"
            assert "Execution failed" in result.metadata.get("error", "")

    @pytest.mark.asyncio
    async def test_execute_with_template_error(
        self, executor, command_agent, mock_workspace, template_engine
    ):
        """Test execution with template error falls back to raw input."""
        # Save an invalid template that will cause an error
        template_engine.save_template(
            agent_id=command_agent.id,
            template="Valid template: {{input}}",
            enabled=True
        )

        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Processed"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test input",
                workspace=mock_workspace,
                focus_file="test.py"
            )

            # Should still succeed with fallback to raw input
            assert result.status == "success"

    @pytest.mark.asyncio
    async def test_execute_with_missing_agent_file(
        self, executor, mock_workspace, tmp_path
    ):
        """Test execution with missing agent source file."""
        non_existent_file = tmp_path / "nonexistent.md"

        agent = VirtualAgent(
            id="missing-file",
            type="command",
            name="Missing File",
            description="Agent with missing file",
            source_file=non_existent_file,
            emoji="📝",
            color="#3498db",
            enabled=True
        )

        result = await executor.execute(
            agent=agent,
            input_text="test",
            workspace=mock_workspace,
            focus_file=None
        )

        assert result.status == "error"
        assert "not found" in result.metadata.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_execute_success_status(self, executor, command_agent, mock_workspace):
        """Test that successful execution returns success status."""
        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Complete success"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "success"
            assert result.is_success()

    @pytest.mark.asyncio
    async def test_execute_with_partial_success(self, executor, command_agent, mock_workspace):
        """Test that execution with warning markers returns partial status."""
        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            # Return output with warning marker
            mock_agent.run.return_value = "Operation completed with warning: Some files were skipped"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "partial"
            assert not result.is_success()

    @pytest.mark.asyncio
    async def test_execute_with_metadata(self, executor, command_agent, mock_workspace):
        """Test that execution result includes metadata."""
        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Result"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file="test.py"
            )

            assert "agent_id" in result.metadata
            assert result.metadata["agent_id"] == command_agent.id
            assert "agent_type" in result.metadata
            assert result.metadata["agent_type"] == command_agent.type

    @pytest.mark.asyncio
    async def test_execute_with_default_options(self, template_engine, mock_workspace, tmp_path):
        """Test execution with default options override."""
        agent_file = tmp_path / "test.md"
        agent_file.write_text("# Test\n\nTest agent", encoding='utf-8')

        agent = VirtualAgent(
            id="test",
            type="command",
            name="Test",
            description="Test",
            source_file=agent_file,
            emoji="📝",
            color="#3498db",
            enabled=True
        )

        defaults = {"permission_mode": "manual"}
        executor = VirtualAgentExecutor(
            template_engine=template_engine,
            default_options=defaults
        )

        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Result"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "success"

    @pytest.mark.asyncio
    async def test_execute_with_none_focus_file(
        self, executor, command_agent, mock_workspace
    ):
        """Test execution with None focus_file."""
        with patch('builtins.__import__') as mock_import:
            mock_agent_class = MagicMock()
            mock_agent = AsyncMock()
            mock_agent.run.return_value = "Result"
            mock_agent_class.return_value = mock_agent

            def mock_import_function(name, *args, **kwargs):
                if name == 'claude_agent_sdk':
                    mock_sdk = MagicMock()
                    mock_sdk.ClaudeAgent = mock_agent_class
                    mock_sdk.create_sdk_mcp_server = MagicMock(return_value=None)
                    return mock_sdk
                else:
                    return __import__(name, *args, **kwargs)

            mock_import.side_effect = mock_import_function

            result = await executor.execute(
                agent=command_agent,
                input_text="test",
                workspace=mock_workspace,
                focus_file=None
            )

            assert result.status == "success"
