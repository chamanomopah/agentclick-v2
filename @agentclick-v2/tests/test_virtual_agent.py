"""
Tests for VirtualAgent dataclass.
"""
import pytest
import tempfile
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

    def test_load_content_reads_file(self):
        """Test load_content actually reads file content."""
        # Create temp file with known content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('print("hello world")')
            temp_path = Path(f.name)

        try:
            agent = VirtualAgent(
                id="test",
                type="command",
                name="Test",
                description="Test",
                source_file=temp_path,
                emoji="🤖",
                color="#000000",
                enabled=True,
                workspace_id=None,
                metadata={}
            )
            content = agent.load_content()
            assert content == 'print("hello world")'
        finally:
            temp_path.unlink()

    def test_load_content_raises_file_not_found(self):
        """Test load_content raises FileNotFoundError for missing file."""
        agent = VirtualAgent(
            id="test",
            type="command",
            name="Test",
            description="Test",
            source_file=Path("/non/existent/file.py"),
            emoji="🤖",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )
        with pytest.raises(FileNotFoundError, match="Agent source file not found"):
            agent.load_content()

    def test_extract_metadata_combines_metadata(self):
        """Test extract_metadata combines base and custom metadata."""
        agent = VirtualAgent(
            id="test-agent",
            type="skill",
            name="Test Agent",
            description="A test agent",
            source_file=Path("/test/agent.py"),
            emoji="🤖",
            color="#000000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={"category": "testing", "priority": "high"}
        )

        result = agent.extract_metadata()

        assert result["type"] == "skill"
        assert result["enabled"] is True
        assert result["has_workspace"] is True
        assert result["category"] == "testing"
        assert result["priority"] == "high"

    def test_extract_metadata_without_workspace(self):
        """Test extract_metadata with unassigned agent."""
        agent = VirtualAgent(
            id="test-agent",
            type="command",
            name="Test Agent",
            description="A test agent",
            source_file=Path("/test/agent.py"),
            emoji="🤖",
            color="#000000",
            enabled=False,
            workspace_id=None,
            metadata={}
        )

        result = agent.extract_metadata()

        assert result["type"] == "command"
        assert result["enabled"] is False
        assert result["has_workspace"] is False
        assert len(result) == 3  # Only base metadata

    def test_get_system_prompt_format(self):
        """Test get_system_prompt returns formatted string."""
        agent = VirtualAgent(
            id="git-commit",
            type="command",
            name="Git Commit",
            description="Commit changes to git repository",
            source_file=Path("/test/git.py"),
            emoji="📝",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        prompt = agent.get_system_prompt()

        assert "Git Commit" in prompt
        assert "Commit changes to git repository" in prompt
        assert "command" in prompt
        assert "Type:" in prompt

    def test_get_system_prompt_empty_description(self):
        """Test get_system_prompt with minimal agent."""
        agent = VirtualAgent(
            id="minimal",
            type="agent",
            name="Minimal",
            description="",
            source_file=Path("/test/minimal.py"),
            emoji="🔧",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        prompt = agent.get_system_prompt()

        assert "Minimal" in prompt
        assert "agent" in prompt


class TestVirtualAgentEdgeCases:
    """Test VirtualAgent edge cases."""

    def test_virtual_agent_with_empty_strings(self):
        """Test VirtualAgent with empty string fields."""
        agent = VirtualAgent(
            id="",  # Empty ID
            type="command",
            name="",  # Empty name
            description="",  # Empty description
            source_file=Path("/test/empty.py"),
            emoji="",  # Empty emoji
            color="",  # Empty color
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert agent.id == ""
        assert agent.name == ""
        assert agent.description == ""
        assert agent.emoji == ""
        assert agent.color == ""

    def test_virtual_agent_with_special_characters_in_id(self):
        """Test VirtualAgent with special characters in ID."""
        agent = VirtualAgent(
            id="agent-with-special.chars_123",
            type="skill",
            name="Special Agent",
            description="Agent with special chars",
            source_file=Path("/test/special.py"),
            emoji="⚡",
            color="#FF00FF",
            enabled=True,
            workspace_id=None,
            metadata={}
        )

        assert "agent-with-special.chars_123" == agent.id

    def test_virtual_agent_metadata_mutation(self):
        """Test that metadata dict can be mutated."""
        agent = VirtualAgent(
            id="test",
            type="command",
            name="Test",
            description="Test",
            source_file=Path("/test/test.py"),
            emoji="🧪",
            color="#000000",
            enabled=True,
            workspace_id=None,
            metadata={"initial": "value"}
        )

        # Modify metadata
        agent.metadata["new_key"] = "new_value"
        agent.metadata["initial"] = "modified"

        assert agent.metadata["new_key"] == "new_value"
        assert agent.metadata["initial"] == "modified"
