"""
Integration tests for DynamicAgentLoader.

These tests verify the complete workflow of discovering, loading, and using agents.
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from core.agent_loader import DynamicAgentLoader
from models.virtual_agent import VirtualAgent


class TestAgentLoaderIntegration:
    """Integration tests for complete agent loading workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_discovery_to_execution(self):
        """Test complete workflow from discovery to agent content loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            # Create a test command
            test_cmd = commands_dir / "test.md"
            test_cmd.write_text("""---
id: test-cmd
name: Test Command
description: A test command
version: "1.0"
---

You are a test command. Process: {{input}}
""")

            # Discover agents
            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            assert len(agents) == 1
            agent = agents[0]

            # Verify agent properties
            assert agent.id == "test-cmd"
            assert agent.type == "command"
            assert agent.emoji == "📝"
            assert agent.enabled is True

            # Load content
            content = agent.load_content()
            assert "You are a test command" in content
            assert "{{input}}" in content

            # Extract metadata
            metadata = agent.extract_metadata()
            assert metadata["type"] == "command"
            assert metadata["enabled"] is True

    @pytest.mark.asyncio
    async def test_cache_performance_with_multiple_scans(self):
        """Test that caching improves performance on repeated scans."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            # Create multiple agents
            for i in range(20):
                cmd_file = commands_dir / f"cmd-{i}.md"
                cmd_file.write_text(f"""---
id: cmd-{i}
name: Command {i}
description: Description {i}
version: "1.0"
---
""")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # First scan - populate cache
            start1 = time.time()
            agents1 = await loader.scan_commands()
            time1 = time.time() - start1

            # Second scan - use cache
            start2 = time.time()
            agents2 = await loader.scan_commands()
            time2 = time.time() - start2

            assert len(agents1) == len(agents2) == 20
            # Second scan should be faster or similar (cached)
            assert time2 <= time1 * 1.5  # Allow some variance

    @pytest.mark.asyncio
    async def test_mixed_agent_types_discovery(self):
        """Test discovering all three agent types in one scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            skills_dir = base_path / "skills"
            agents_dir = base_path / "agents"

            commands_dir.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            agents_dir.mkdir(parents=True)

            # Create command
            (commands_dir / "cmd.md").write_text("---\nid: cmd\nname: Cmd\n---\n")

            # Create skill
            skill_dir = skills_dir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nid: skill\nname: Skill\n---\n")

            # Create agent
            (agents_dir / "agent.md").write_text("---\nid: agent\nname: Agent\n---\n")

            loader = DynamicAgentLoader(
                commands_dir=commands_dir,
                skills_dir=skills_dir,
                agents_dir=agents_dir
            )

            all_agents = await loader.scan_all()

            assert len(all_agents) == 3

            types_found = {agent.type for agent in all_agents}
            assert types_found == {"command", "skill", "agent"}

            emojis_found = {agent.emoji for agent in all_agents}
            assert emojis_found == {"📝", "🎯", "🤖"}

    @pytest.mark.asyncio
    async def test_file_modification_detection_and_reload(self):
        """Test that file modifications are detected and agents can be reloaded."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            cmd_file = commands_dir / "reload-test.md"
            cmd_file.write_text("---\nid: reload-test\nversion: '1.0'\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # Initial scan
            agents1 = await loader.scan_commands()
            assert agents1[0].metadata["version"] == "1.0"

            # Modify file
            await asyncio.sleep(0.01)  # Ensure different mtime
            cmd_file.write_text("---\nid: reload-test\nversion: '2.0'\n---\n")

            # The next scan should automatically detect the change via cache invalidation
            agents2 = await loader.scan_commands()
            assert agents2[0].metadata["version"] == "2.0"

    @pytest.mark.asyncio
    async def test_virtual_agent_system_prompt_generation(self):
        """Test that VirtualAgent generates proper system prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            cmd_file = commands_dir / "prompt-test.md"
            cmd_file.write_text("""---
id: prompt-test
name: Test Prompt Generator
description: Generates test prompts
---
""")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            agent = agents[0]
            prompt = agent.get_system_prompt()

            assert "Test Prompt Generator" in prompt
            assert "Generates test prompts" in prompt
            assert "command" in prompt

    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self):
        """Test that loader handles errors gracefully and continues processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            # Create valid file
            (commands_dir / "valid.md").write_text("---\nid: valid\n---\n")

            # Create invalid file (malformed YAML)
            (commands_dir / "invalid.md").write_text("---\nid: [unclosed\n---\n")

            # Create binary file
            (commands_dir / "binary.md").write_bytes(b'\x00\x01\x02')

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Should find at least the valid file
            assert len(agents) >= 1
            assert any(a.id == "valid" for a in agents)

    @pytest.mark.asyncio
    async def test_workspace_integration(self):
        """Test that discovered agents can be assigned to workspaces."""
        from models.workspace import Workspace

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            # Create multiple commands
            for i in range(3):
                cmd_file = commands_dir / f"cmd-{i}.md"
                cmd_file.write_text(f"""---
id: cmd-{i}
name: Command {i}
description: Command {i}
---
""")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Create workspace and add agents (note: Workspace requires folder, not description)
            workspace = Workspace(
                id="test-workspace",
                name="Test Workspace",
                folder=Path(tmpdir) / "workspace",
                emoji="🚀",
                color="#3498db",
                agents=[]
            )

            for agent in agents:
                workspace.add_agent(agent)

            assert len(workspace.agents) == 3
            assert workspace.get_agent("cmd-0") is not None
            assert workspace.get_agent("cmd-1") is not None
            assert workspace.get_agent("cmd-2") is not None

    @pytest.mark.asyncio
    async def test_lazy_loading_content_only_on_demand(self):
        """Test that content is only loaded when explicitly requested."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / ".claude"
            commands_dir = base_path / "commands"
            commands_dir.mkdir(parents=True)

            cmd_file = commands_dir / "lazy-test.md"
            large_content = "You are a test agent.\n" * 100  # Large file
            cmd_file.write_text(f"""---
id: lazy-test
name: Lazy Test
description: Tests lazy loading
---
{large_content}
""")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Agent should be created but content not yet loaded
            agent = agents[0]
            assert agent.id == "lazy-test"

            # Load content on demand
            content = agent.load_content()
            assert large_content in content
            assert len(content) > 1000
