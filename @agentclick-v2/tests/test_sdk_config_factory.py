"""
Tests for SDK Config Factory.

Tests the SDKOptionsBuilder class which helps construct ClaudeAgentOptions
for the VirtualAgentExecutor.
"""
import pytest
from pathlib import Path
from config.sdk_config_factory import SDKOptionsBuilder


class TestSDKOptionsBuilder:
    """Test suite for SDKOptionsBuilder class."""

    def test_initialization(self):
        """Test that SDKOptionsBuilder initializes with empty state."""
        builder = SDKOptionsBuilder()
        # Should be able to build with defaults
        options = builder.build()
        assert options is not None
        assert isinstance(options, dict)

    def test_with_system_prompt(self):
        """Test setting system prompt."""
        builder = SDKOptionsBuilder()
        prompt = "You are a helpful assistant."
        result = builder.with_system_prompt(prompt)

        # Should return self for method chaining
        assert result is builder

        options = builder.build()
        assert options.get("system_prompt") == prompt

    def test_with_working_directory(self):
        """Test setting working directory."""
        builder = SDKOptionsBuilder()
        cwd = Path("/test/workspace")
        result = builder.with_working_directory(cwd)

        # Should return self for method chaining
        assert result is builder

        options = builder.build()
        assert options.get("cwd") == cwd

    def test_with_tools(self):
        """Test setting allowed tools."""
        builder = SDKOptionsBuilder()
        tools = ["Read", "Write", "Edit", "Grep", "Glob"]
        result = builder.with_tools(tools)

        # Should return self for method chaining
        assert result is builder

        options = builder.build()
        assert options.get("allowed_tools") == tools

    def test_with_mcp_servers(self):
        """Test setting MCP servers."""
        builder = SDKOptionsBuilder()
        mcp_servers = {"test-server": {"config": "value"}}
        result = builder.with_mcp_servers(mcp_servers)

        # Should return self for method chaining
        assert result is builder

        options = builder.build()
        assert options.get("mcp_servers") == mcp_servers

    def test_with_permission_mode(self):
        """Test setting permission mode."""
        builder = SDKOptionsBuilder()
        mode = "acceptEdits"
        result = builder.with_permission_mode(mode)

        # Should return self for method chaining
        assert result is builder

        options = builder.build()
        assert options.get("permission_mode") == mode

    def test_method_chaining(self):
        """Test that builder methods can be chained."""
        builder = SDKOptionsBuilder()
        options = (builder
                  .with_system_prompt("Test prompt")
                  .with_working_directory(Path("/test"))
                  .with_tools(["Read", "Write"])
                  .with_permission_mode("acceptEdits")
                  .build())

        assert options["system_prompt"] == "Test prompt"
        assert options["cwd"] == Path("/test")
        assert options["allowed_tools"] == ["Read", "Write"]
        assert options["permission_mode"] == "acceptEdits"

    def test_build_returns_new_options_each_time(self):
        """Test that build() can be called multiple times."""
        builder = SDKOptionsBuilder()
        builder.with_system_prompt("Test")

        options1 = builder.build()
        options2 = builder.build()

        # Should return dict each time
        assert isinstance(options1, dict)
        assert isinstance(options2, dict)

    def test_overwriting_values(self):
        """Test that values can be overwritten."""
        builder = SDKOptionsBuilder()
        builder.with_system_prompt("First")
        builder.with_system_prompt("Second")

        options = builder.build()
        assert options["system_prompt"] == "Second"

    def test_none_mcp_servers(self):
        """Test that None MCP servers is handled correctly."""
        builder = SDKOptionsBuilder()
        builder.with_mcp_servers(None)

        options = builder.build()
        # Should not include mcp_servers if None
        assert "mcp_servers" not in options or options.get("mcp_servers") is None

    def test_empty_tools_list(self):
        """Test that empty tools list is handled correctly."""
        builder = SDKOptionsBuilder()
        builder.with_tools([])

        options = builder.build()
        assert options.get("allowed_tools") == []

    def test_full_options_builder(self):
        """Test building complete options with all fields."""
        builder = SDKOptionsBuilder()

        options = (builder
                  .with_system_prompt("You are a test agent.")
                  .with_working_directory(Path("/workspace/test"))
                  .with_tools(["Read", "Write", "Edit", "Grep", "Glob"])
                  .with_mcp_servers({"mcp1": {"url": "http://test"}})
                  .with_permission_mode("acceptEdits")
                  .build())

        # Verify all fields
        assert options["system_prompt"] == "You are a test agent."
        assert options["cwd"] == Path("/workspace/test")
        assert options["allowed_tools"] == ["Read", "Write", "Edit", "Grep", "Glob"]
        assert options["mcp_servers"] == {"mcp1": {"url": "http://test"}}
        assert options["permission_mode"] == "acceptEdits"
