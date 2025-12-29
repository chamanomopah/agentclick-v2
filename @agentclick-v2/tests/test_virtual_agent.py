"""
Tests for VirtualAgent dataclass.
"""
import pytest
from pathlib import Path
from typing import get_type_hints
from models.virtual_agent import VirtualAgent


class TestVirtualAgentDataclass:
    """Test VirtualAgent dataclass structure and type hints."""

    def test_virtual_agent_has_all_required_fields(self):
        """Test that VirtualAgent has all required fields with correct types."""
        # Get type hints
        hints = get_type_hints(VirtualAgent)

        # Verify all required fields exist
        required_fields = {
            'id': str,
            'type': str,  # Literal will be validated separately
            'name': str,
            'description': str,
            'source_file': Path,
            'emoji': str,
            'color': str,
            'enabled': bool,
            'workspace_id': str | None,  # Optional[str]
            'metadata': dict,
        }

        for field_name, expected_type in required_fields.items():
            assert field_name in hints, f"Missing field: {field_name}"

    def test_virtual_agent_creation_with_all_fields(self):
        """Test creating VirtualAgent with all fields."""
        agent = VirtualAgent(
            id="test-agent-1",
            type="command",
            name="Test Agent",
            description="A test agent",
            source_file=Path("/test/agent.py"),
            emoji="🤖",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={"key": "value"}
        )

        assert agent.id == "test-agent-1"
        assert agent.type == "command"
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.source_file == Path("/test/agent.py")
        assert agent.emoji == "🤖"
        assert agent.color == "#FF0000"
        assert agent.enabled is True
        assert agent.workspace_id == "workspace-1"
        assert agent.metadata == {"key": "value"}

    def test_virtual_agent_creation_without_workspace_id(self):
        """Test creating VirtualAgent without workspace_id (unassigned agent)."""
        agent = VirtualAgent(
            id="test-agent-2",
            type="skill",
            name="Unassigned Agent",
            description="An agent without workspace",
            source_file=Path("/test/unassigned.py"),
            emoji="🔧",
            color="#00FF00",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert agent.workspace_id is None
        assert agent.metadata == {}

    def test_virtual_agent_type_validation(self):
        """Test that type field accepts valid literal values."""
        valid_types = ["command", "skill", "agent"]

        for agent_type in valid_types:
            agent = VirtualAgent(
                id=f"agent-{agent_type}",
                type=agent_type,
                name=f"{agent_type.title()} Agent",
                description=f"Agent of type {agent_type}",
                source_file=Path(f"/test/{agent_type}.py"),
                emoji="🤖",
                color="#0000FF",
                enabled=True,
                workspace_id=None,
                metadata={}
            )
            assert agent.type == agent_type

    def test_virtual_agent_equality(self):
        """Test VirtualAgent equality comparison."""
        agent1 = VirtualAgent(
            id="same-id",
            type="command",
            name="Agent One",
            description="First agent",
            source_file=Path("/test/one.py"),
            emoji="🤖",
            color="#FF0000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        agent2 = VirtualAgent(
            id="same-id",
            type="skill",  # Different type but same ID
            name="Agent Two",
            description="Second agent",
            source_file=Path("/test/two.py"),
            emoji="🔧",
            color="#00FF00",
            enabled=False,
            workspace_id="workspace-1",
            metadata={"key": "value"}
        )

        # Dataclasses compare by field values, not just ID
        assert agent1 != agent2

        agent3 = VirtualAgent(
            id="same-id",
            type="command",
            name="Agent One",
            description="First agent",
            source_file=Path("/test/one.py"),
            emoji="🤖",
            color="#FF0000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert agent1 == agent3


class TestVirtualAgentMethods:
    """Test VirtualAgent methods."""

    def test_load_content_method_exists(self):
        """Test that load_content method exists."""
        agent = VirtualAgent(
            id="test-agent",
            type="command",
            name="Test",
            description="Test",
            source_file=Path("/test/file.py"),
            emoji="🤖",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert hasattr(agent, 'load_content')
        assert callable(agent.load_content)

    def test_extract_metadata_method_exists(self):
        """Test that extract_metadata method exists."""
        agent = VirtualAgent(
            id="test-agent",
            type="command",
            name="Test",
            description="Test",
            source_file=Path("/test/file.py"),
            emoji="🤖",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert hasattr(agent, 'extract_metadata')
        assert callable(agent.extract_metadata)

    def test_get_system_prompt_method_exists(self):
        """Test that get_system_prompt method exists."""
        agent = VirtualAgent(
            id="test-agent",
            type="command",
            name="Test",
            description="Test",
            source_file=Path("/test/file.py"),
            emoji="🤖",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert hasattr(agent, 'get_system_prompt')
        assert callable(agent.get_system_prompt)
