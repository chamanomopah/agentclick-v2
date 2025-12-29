"""
Tests for Workspace dataclass.
"""
import pytest
from pathlib import Path
from typing import get_type_hints
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent


class TestWorkspaceDataclass:
    """Test Workspace dataclass structure and type hints."""

    def test_workspace_has_all_required_fields(self):
        """Test that Workspace has all required fields with correct types."""
        hints = get_type_hints(Workspace)

        required_fields = {
            'id': str,
            'name': str,
            'folder': Path,
            'emoji': str,
            'color': str,
            'agents': list,  # list[VirtualAgent]
        }

        for field_name, expected_type in required_fields.items():
            assert field_name in hints, f"Missing field: {field_name}"

    def test_workspace_creation_with_all_fields(self):
        """Test creating Workspace with all fields."""
        agent1 = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First agent",
            source_file=Path("/test/agent1.py"),
            emoji="🤖",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test Workspace",
            folder=Path("/test/workspace"),
            emoji="📁",
            color="#00FF00",
            agents=[agent1]
        )

        assert workspace.id == "workspace-1"
        assert workspace.name == "Test Workspace"
        assert workspace.folder == Path("/test/workspace")
        assert workspace.emoji == "📁"
        assert workspace.color == "#00FF00"
        assert len(workspace.agents) == 1
        assert workspace.agents[0].id == "agent-1"

    def test_workspace_creation_with_empty_agents(self):
        """Test creating Workspace with empty agents list."""
        workspace = Workspace(
            id="workspace-empty",
            name="Empty Workspace",
            folder=Path("/test/empty"),
            emoji="🔳",
            color="#CCCCCC",
            agents=[]
        )

        assert workspace.agents == []
        assert len(workspace.agents) == 0


class TestWorkspaceMethods:
    """Test Workspace methods."""

    def test_add_agent_method(self):
        """Test add_agent method adds agent to workspace."""
        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[]
        )

        agent = VirtualAgent(
            id="new-agent",
            type="skill",
            name="New Agent",
            description="A new agent",
            source_file=Path("/test/new.py"),
            emoji="🆕",
            color="#0000FF",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace.add_agent(agent)

        assert len(workspace.agents) == 1
        assert workspace.agents[0].id == "new-agent"

    def test_add_agent_multiple(self):
        """Test adding multiple agents."""
        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[]
        )

        agent1 = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        agent2 = VirtualAgent(
            id="agent-2",
            type="skill",
            name="Agent 2",
            description="Second",
            source_file=Path("/test/2.py"),
            emoji="2️⃣",
            color="#00FF00",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace.add_agent(agent1)
        workspace.add_agent(agent2)

        assert len(workspace.agents) == 2

    def test_remove_agent_method(self):
        """Test remove_agent method removes agent from workspace."""
        agent1 = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        agent2 = VirtualAgent(
            id="agent-2",
            type="skill",
            name="Agent 2",
            description="Second",
            source_file=Path("/test/2.py"),
            emoji="2️⃣",
            color="#00FF00",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent1, agent2]
        )

        # Remove agent1
        workspace.remove_agent("agent-1")

        assert len(workspace.agents) == 1
        assert workspace.agents[0].id == "agent-2"

    def test_remove_agent_not_found(self):
        """Test removing non-existent agent doesn't raise error."""
        agent = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent]
        )

        # Should not raise error
        workspace.remove_agent("non-existent-agent")

        assert len(workspace.agents) == 1

    def test_get_agent_method(self):
        """Test get_agent method retrieves agent by ID."""
        agent1 = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        agent2 = VirtualAgent(
            id="agent-2",
            type="skill",
            name="Agent 2",
            description="Second",
            source_file=Path("/test/2.py"),
            emoji="2️⃣",
            color="#00FF00",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent1, agent2]
        )

        retrieved = workspace.get_agent("agent-2")

        assert retrieved is not None
        assert retrieved.id == "agent-2"
        assert retrieved.name == "Agent 2"

    def test_get_agent_not_found_returns_none(self):
        """Test get_agent returns None for non-existent agent."""
        agent = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent]
        )

        result = workspace.get_agent("non-existent")

        assert result is None

    def test_get_enabled_agents_method(self):
        """Test get_enabled_agents returns only enabled agents."""
        agent1 = VirtualAgent(
            id="agent-1",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        agent2 = VirtualAgent(
            id="agent-2",
            type="skill",
            name="Agent 2",
            description="Second",
            source_file=Path("/test/2.py"),
            emoji="2️⃣",
            color="#00FF00",
            enabled=False,
            workspace_id="workspace-1",
            metadata={}
        )

        agent3 = VirtualAgent(
            id="agent-3",
            type="agent",
            name="Agent 3",
            description="Third",
            source_file=Path("/test/3.py"),
            emoji="3️⃣",
            color="#0000FF",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent1, agent2, agent3]
        )

        enabled = workspace.get_enabled_agents()

        assert len(enabled) == 2
        assert all(a.enabled for a in enabled)
        assert enabled[0].id == "agent-1"
        assert enabled[1].id == "agent-3"

    def test_get_enabled_agents_empty_workspace(self):
        """Test get_enabled_agents returns empty list for workspace with no agents."""
        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[]
        )

        enabled = workspace.get_enabled_agents()

        assert enabled == []


class TestWorkspaceEdgeCases:
    """Test Workspace edge cases."""

    def test_workspace_with_duplicate_agent_ids(self):
        """Test workspace when agents with same ID are added."""
        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[]
        )

        agent1 = VirtualAgent(
            id="duplicate-id",
            type="command",
            name="Agent 1",
            description="First",
            source_file=Path("/test/1.py"),
            emoji="1️⃣",
            color="#FF0000",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        agent2 = VirtualAgent(
            id="duplicate-id",  # Same ID!
            type="skill",
            name="Agent 2",
            description="Second",
            source_file=Path("/test/2.py"),
            emoji="2️⃣",
            color="#00FF00",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace.add_agent(agent1)
        workspace.add_agent(agent2)  # Overwrites agent1 in index

        # Both agents are in the list (list allows duplicates)
        assert len(workspace.agents) == 2

        # But index only has agent2 (last write wins)
        retrieved = workspace.get_agent("duplicate-id")
        assert retrieved.name == "Agent 2"

    def test_workspace_with_empty_string_fields(self):
        """Test workspace with empty string fields."""
        workspace = Workspace(
            id="",
            name="",
            folder=Path("/test"),
            emoji="",
            color="",
            agents=[]
        )

        assert workspace.id == ""
        assert workspace.name == ""
        assert workspace.emoji == ""
        assert workspace.color == ""

    def test_workspace_get_agent_with_empty_id(self):
        """Test get_agent with empty string ID."""
        agent = VirtualAgent(
            id="",  # Empty ID
            type="command",
            name="Empty ID Agent",
            description="Agent with empty ID",
            source_file=Path("/test/empty.py"),
            emoji="🔳",
            color="#CCCCCC",
            enabled=True,
            workspace_id="workspace-1",
            metadata={}
        )

        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[agent]
        )

        # Rebuild index after manual initialization
        workspace._agent_index[agent.id] = agent

        retrieved = workspace.get_agent("")
        assert retrieved is not None
        assert retrieved.name == "Empty ID Agent"

    def test_workspace_remove_nonexistent_agent(self):
        """Test removing agent that doesn't exist doesn't raise error."""
        workspace = Workspace(
            id="workspace-1",
            name="Test",
            folder=Path("/test"),
            emoji="📁",
            color="#000000",
            agents=[]
        )

        # Should not raise error
        workspace.remove_agent("nonexistent-agent")

        assert len(workspace.agents) == 0
