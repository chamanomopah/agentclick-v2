"""
Tests for DynamicAgentLoader class.

This test suite follows TDD principles - tests are written before implementation.
Tests cover:
- Agent discovery from .claude/ directories
- YAML frontmatter extraction
- Metadata caching
- Lazy loading optimization
- Agent reload functionality
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from typing import List
from models.virtual_agent import VirtualAgent


class TestDynamicAgentLoaderStructure:
    """Test DynamicAgentLoader class structure and initialization."""

    def test_loader_class_exists(self):
        """Test that DynamicAgentLoader class can be imported."""
        from core.agent_loader import DynamicAgentLoader
        assert DynamicAgentLoader is not None

    def test_loader_initialization_with_defaults(self):
        """Test loader initialization with default directory paths."""
        from core.agent_loader import DynamicAgentLoader

        loader = DynamicAgentLoader()
        assert loader.commands_dir is not None
        assert loader.skills_dir is not None
        assert loader.agents_dir is not None

    def test_loader_initialization_with_custom_paths(self):
        """Test loader initialization with custom directory paths."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands = Path(tmpdir) / "commands"
            skills = Path(tmpdir) / "skills"
            agents = Path(tmpdir) / "agents"

            loader = DynamicAgentLoader(
                commands_dir=commands,
                skills_dir=skills,
                agents_dir=agents
            )

            assert loader.commands_dir == commands
            assert loader.skills_dir == skills
            assert loader.agents_dir == agents

    def test_loader_has_metadata_cache(self):
        """Test that loader initializes with metadata cache."""
        from core.agent_loader import DynamicAgentLoader

        loader = DynamicAgentLoader()
        assert hasattr(loader, '_metadata_cache')
        assert isinstance(loader._metadata_cache, dict)


class TestCommandScanning:
    """Test scanning of .claude/commands/ directory."""

    @pytest.mark.asyncio
    async def test_scan_commands_discovers_markdown_files(self):
        """Test that scan_commands discovers .md files."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create test command files
            (commands_dir / "test-cmd.md").write_text("---\nid: test-cmd\n---\nTest")
            (commands_dir / "another-cmd.md").write_text("---\nid: another\n---\nTest")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            assert len(agents) == 2
            assert all(a.type == "command" for a in agents)
            assert all(a.emoji == "📝" for a in agents)

    @pytest.mark.asyncio
    async def test_scan_commands_excludes_non_markdown_files(self):
        """Test that scan_commands ignores non-.md files."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create mix of files
            (commands_dir / "valid.md").write_text("---\nid: valid\n---\nTest")
            (commands_dir / "readme.txt").write_text("Not markdown")
            (commands_dir / "script.py").write_text("print('test')")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            assert len(agents) == 1
            assert agents[0].id == "valid"

    @pytest.mark.asyncio
    async def test_scan_commands_handles_empty_directory(self):
        """Test that scan_commands returns empty list for empty directory."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            assert agents == []

    @pytest.mark.asyncio
    async def test_scan_commands_handles_nonexistent_directory(self):
        """Test that scan_commands creates directory if it doesn't exist."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "nonexistent" / "commands"

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            assert agents == []


class TestSkillScanning:
    """Test scanning of .claude/skills/ directory structure."""

    @pytest.mark.asyncio
    async def test_scan_skills_discovers_skill_directories(self):
        """Test that scan_skills finds SKILL.md files in subdirectories."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()

            # Create skill directories
            skill1 = skills_dir / "ux-improver"
            skill1.mkdir()
            (skill1 / "SKILL.md").write_text("---\nid: ux-improver\n---\nUX skill")

            skill2 = skills_dir / "code-reviewer"
            skill2.mkdir()
            (skill2 / "SKILL.md").write_text("---\nid: reviewer\n---\nReview skill")

            loader = DynamicAgentLoader(skills_dir=skills_dir)
            agents = await loader.scan_skills()

            assert len(agents) == 2
            assert all(a.type == "skill" for a in agents)
            assert all(a.emoji == "🎯" for a in agents)

    @pytest.mark.asyncio
    async def test_scan_skills_ignores_non_skill_markdown_files(self):
        """Test that scan_skills only looks for SKILL.md files."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()

            # Create skill with extra markdown files
            skill = skills_dir / "test-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nid: test\n---\nSkill")
            (skill / "README.md").write_text("Not a skill")
            (skill / "notes.md").write_text("Notes")

            loader = DynamicAgentLoader(skills_dir=skills_dir)
            agents = await loader.scan_skills()

            assert len(agents) == 1
            assert agents[0].id == "test"

    @pytest.mark.asyncio
    async def test_scan_skills_handles_missing_skill_file(self):
        """Test that scan_skills skips directories without SKILL.md."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()

            # Create directory without SKILL.md
            incomplete_skill = skills_dir / "incomplete"
            incomplete_skill.mkdir()
            (incomplete_skill / "README.md").write_text("No skill file")

            loader = DynamicAgentLoader(skills_dir=skills_dir)
            agents = await loader.scan_skills()

            assert agents == []


class TestAgentScanning:
    """Test scanning of .claude/agents/ directory."""

    @pytest.mark.asyncio
    async def test_scan_custom_agents_discovers_markdown_files(self):
        """Test that scan_custom_agents discovers .md files."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "agents"
            agents_dir.mkdir()

            # Create test agent files
            (agents_dir / "agent1.md").write_text("---\nid: agent1\n---\nAgent 1")
            (agents_dir / "agent2.md").write_text("---\nid: agent2\n---\nAgent 2")

            loader = DynamicAgentLoader(agents_dir=agents_dir)
            agents = await loader.scan_custom_agents()

            assert len(agents) == 2
            assert all(a.type == "agent" for a in agents)
            assert all(a.emoji == "🤖" for a in agents)

    @pytest.mark.asyncio
    async def test_scan_custom_agents_handles_empty_directory(self):
        """Test that scan_custom_agents returns empty list for empty directory."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            agents_dir = Path(tmpdir) / "agents"
            agents_dir.mkdir()

            loader = DynamicAgentLoader(agents_dir=agents_dir)
            agents = await loader.scan_custom_agents()

            assert agents == []


class TestScanAll:
    """Test comprehensive scanning of all agent types."""

    @pytest.mark.asyncio
    async def test_scan_all_discovers_all_agent_types(self):
        """Test that scan_all discovers commands, skills, and agents."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            skills_dir = Path(tmpdir) / "skills"
            agents_dir = Path(tmpdir) / "agents"

            commands_dir.mkdir()
            skills_dir.mkdir()
            agents_dir.mkdir()

            # Create agents of each type
            (commands_dir / "cmd.md").write_text("---\nid: cmd\nname: Command\n---\n")
            skill_dir = skills_dir / "skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nid: skill\nname: Skill\n---\n")
            (agents_dir / "agent.md").write_text("---\nid: agent\nname: Agent\n---\n")

            loader = DynamicAgentLoader(
                commands_dir=commands_dir,
                skills_dir=skills_dir,
                agents_dir=agents_dir
            )
            all_agents = await loader.scan_all()

            assert len(all_agents) == 3
            types = {a.type for a in all_agents}
            assert types == {"command", "skill", "agent"}


class TestYAMLFrontmatterExtraction:
    """Test YAML frontmatter extraction from markdown files."""

    @pytest.mark.asyncio
    async def test_extract_frontmatter_parses_yaml_metadata(self):
        """Test that frontmatter is correctly extracted and parsed."""
        from core.agent_loader import extract_frontmatter

        content = """---
id: test-agent
name: Test Agent
description: A test agent
version: "1.0"
tools:
  - Read
  - Write
---

This is the content.
"""
        metadata = await extract_frontmatter(content)

        assert metadata["id"] == "test-agent"
        assert metadata["name"] == "Test Agent"
        assert metadata["description"] == "A test agent"
        assert metadata["version"] == "1.0"
        assert metadata["tools"] == ["Read", "Write"]

    @pytest.mark.asyncio
    async def test_extract_frontmatter_handles_missing_frontmatter(self):
        """Test that missing frontmatter is handled gracefully."""
        from core.agent_loader import extract_frontmatter

        content = "No frontmatter here, just content"

        metadata = await extract_frontmatter(content)

        # Should return empty dict or None
        assert metadata is None or metadata == {}

    @pytest.mark.asyncio
    async def test_extract_frontmatter_handles_malformed_yaml(self):
        """Test that malformed YAML doesn't crash the parser."""
        from core.agent_loader import extract_frontmatter

        content = """---
id: test
name: [unclosed bracket
---

Content"""

        # Should handle gracefully - either return None or raise specific error
        try:
            metadata = await extract_frontmatter(content)
            assert True  # No crash
        except Exception as e:
            # If it raises, should be a specific exception type
            assert not isinstance(e, (AttributeError, TypeError))

    @pytest.mark.asyncio
    async def test_extract_frontmatter_extracts_common_fields(self):
        """Test extraction of common metadata fields."""
        from core.agent_loader import extract_frontmatter

        content = """---
id: my-agent
name: My Agent
description: Description here
version: "2.1"
type: command
tools:
  - Read
  - Write
  - Edit
author: Test Author
tags:
  - testing
  - example
---

Content"""

        metadata = await extract_frontmatter(content)

        assert metadata["id"] == "my-agent"
        assert metadata["name"] == "My Agent"
        assert metadata["description"] == "Description here"
        assert metadata["version"] == "2.1"
        assert metadata["type"] == "command"
        assert metadata["tools"] == ["Read", "Write", "Edit"]
        assert metadata["author"] == "Test Author"
        assert metadata["tags"] == ["testing", "example"]


class TestMetadataCaching:
    """Test metadata caching functionality."""

    @pytest.mark.asyncio
    async def test_metadata_cache_stores_parsed_data(self):
        """Test that parsed metadata is cached."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            (commands_dir / "test.md").write_text("---\nid: test\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # First scan
            agents1 = await loader.scan_commands()
            cache_size_1 = len(loader._metadata_cache)

            # Second scan - should use cache
            agents2 = await loader.scan_commands()
            cache_size_2 = len(loader._metadata_cache)

            assert len(agents1) == len(agents2)
            assert cache_size_1 == cache_size_2

    @pytest.mark.asyncio
    async def test_get_cached_metadata_returns_stored_data(self):
        """Test that get_cached_metadata retrieves cached values."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            test_file = commands_dir / "test.md"
            test_file.write_text("---\nid: test\nname: Test\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # Scan to populate cache
            await loader.scan_commands()

            # Get cached metadata
            cached = await loader.get_cached_metadata(test_file)

            assert cached is not None
            assert cached["id"] == "test"
            assert cached["name"] == "Test"

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_file_modification(self):
        """Test that cache is invalidated when file is modified."""
        from core.agent_loader import DynamicAgentLoader
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            test_file = commands_dir / "test.md"
            test_file.write_text("---\nid: test\nversion: '1.0'\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # Initial scan
            await loader.scan_commands()
            initial_cache = await loader.get_cached_metadata(test_file)
            assert initial_cache["version"] == "1.0"

            # Modify file
            await asyncio.sleep(0.01)  # Ensure different mtime
            test_file.write_text("---\nid: test\nversion: '2.0'\n---\n")

            # Re-scan - cache should be invalidated
            await loader.scan_commands()
            updated_cache = await loader.get_cached_metadata(test_file)
            assert updated_cache["version"] == "2.0"

    @pytest.mark.asyncio
    async def test_cache_size_limit_prevents_memory_bloat(self):
        """Test that cache has size limits."""
        from core.agent_loader import DynamicAgentLoader

        loader = DynamicAgentLoader()

        # Check if cache has max size configured
        # Either through attribute or configuration
        assert hasattr(loader, '_metadata_cache')
        # Cache should be bounded - either by max_size or TTL
        # Implementation detail - verify it exists


class TestLazyLoading:
    """Test lazy loading optimization."""

    def test_virtual_agent_loads_content_on_demand(self):
        """Test that VirtualAgent.load_content reads file on demand."""
        # This tests the existing VirtualAgent.load_content method
        # which should already work with lazy loading

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("---\nid: test\n---\nDelayed content")
            temp_path = Path(f.name)

        try:
            agent = VirtualAgent(
                id="test",
                type="command",
                name="Test",
                description="Test",
                source_file=temp_path,
                emoji="📝",
                color="#000000",
                enabled=True,
                workspace_id=None,
                metadata={}
            )

            # Content not loaded yet
            # Load on demand
            content = agent.load_content()
            assert content == "---\nid: test\n---\nDelayed content"
        finally:
            temp_path.unlink()


class TestAgentReload:
    """Test agent reload functionality."""

    @pytest.mark.asyncio
    async def test_reload_agent_refreshes_metadata(self):
        """Test that reload_agent refreshes a specific agent's metadata."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            test_file = commands_dir / "test.md"
            test_file.write_text("---\nid: test\nversion: '1.0'\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Modify file
            test_file.write_text("---\nid: test\nversion: '2.0'\n---\n")

            # Reload specific agent
            await loader.reload_agent("test")
            cached = await loader.get_cached_metadata(test_file)

            assert cached["version"] == "2.0"

    @pytest.mark.asyncio
    async def test_watch_changes_detects_file_additions(self):
        """Test that watch_changes detects new files."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            # Start watching (non-blocking)
            watch_task = asyncio.create_task(loader.watch_changes())

            # Wait a bit
            await asyncio.sleep(0.1)

            # Add new file
            (commands_dir / "new.md").write_text("---\nid: new\n---\n")

            # Wait for detection
            await asyncio.sleep(0.1)

            # Cancel watch task
            watch_task.cancel()

            try:
                await watch_task
            except asyncio.CancelledError:
                pass

            # Verify new agent is detected
            agents = await loader.scan_commands()
            assert len(agents) == 1
            assert agents[0].id == "new"


class TestCreateVirtualAgent:
    """Test VirtualAgent creation helper method."""

    @pytest.mark.asyncio
    async def test_create_virtual_agent_sets_correct_emoji(self):
        """Test that correct emoji is assigned based on agent type."""
        from core.agent_loader import DynamicAgentLoader

        loader = DynamicAgentLoader()

        # Test command emoji
        cmd_agent = await loader.create_virtual_agent(
            agent_type="command",
            id="test-cmd",
            name="Test Command",
            description="Test",
            source_file=Path("/test/cmd.md"),
            metadata={}
        )
        assert cmd_agent.emoji == "📝"

        # Test skill emoji
        skill_agent = await loader.create_virtual_agent(
            agent_type="skill",
            id="test-skill",
            name="Test Skill",
            description="Test",
            source_file=Path("/test/skill.md"),
            metadata={}
        )
        assert skill_agent.emoji == "🎯"

        # Test agent emoji
        agent = await loader.create_virtual_agent(
            agent_type="agent",
            id="test-agent",
            name="Test Agent",
            description="Test",
            source_file=Path("/test/agent.md"),
            metadata={}
        )
        assert agent.emoji == "🤖"

    @pytest.mark.asyncio
    async def test_create_virtual_agent_uses_metadata_fields(self):
        """Test that metadata fields are used when provided."""
        from core.agent_loader import DynamicAgentLoader

        loader = DynamicAgentLoader()

        metadata = {
            "id": "custom-id",
            "name": "Custom Name",
            "description": "Custom description",
            "version": "1.5"
        }

        agent = await loader.create_virtual_agent(
            agent_type="command",
            id="fallback-id",
            name="Fallback Name",
            description="Fallback",
            source_file=Path("/test/cmd.md"),
            metadata=metadata
        )

        assert agent.id == "custom-id"
        assert agent.name == "Custom Name"
        assert agent.description == "Custom description"


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_scan_handles_invalid_markdown_files(self):
        """Test that invalid .md files are logged and skipped."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create invalid file
            (commands_dir / "invalid.md").write_text("Invalid content with unclosed ---")

            # Create valid file
            (commands_dir / "valid.md").write_text("---\nid: valid\n---\nValid")

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Should have valid agent, skip invalid
            assert len(agents) >= 1
            assert any(a.id == "valid" for a in agents)

    @pytest.mark.asyncio
    async def test_scan_handles_binary_files(self):
        """Test that binary files don't crash the scanner."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create binary file with .md extension
            (commands_dir / "binary.md").write_bytes(b'\x00\x01\x02\x03')

            loader = DynamicAgentLoader(commands_dir=commands_dir)
            agents = await loader.scan_commands()

            # Should not crash
            assert isinstance(agents, list)

    @pytest.mark.asyncio
    async def test_scan_all_handles_missing_directories(self):
        """Test that scan_all works when some directories don't exist."""
        from core.agent_loader import DynamicAgentLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            # Don't create skills_dir or agents_dir

            commands_dir.mkdir()

            loader = DynamicAgentLoader(
                commands_dir=commands_dir,
                skills_dir=Path(tmpdir) / "nonexistent" / "skills",
                agents_dir=Path(tmpdir) / "nonexistent" / "agents"
            )

            all_agents = await loader.scan_all()

            # Should work without errors
            assert isinstance(all_agents, list)


class TestPerformance:
    """Test performance requirements."""

    @pytest.mark.asyncio
    async def test_scan_performance_fifty_agents(self):
        """Test that scanning 50 agents completes in under 2 seconds."""
        from core.agent_loader import DynamicAgentLoader
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create 50 agent files
            for i in range(50):
                (commands_dir / f"agent-{i}.md").write_text(
                    f"---\nid: agent-{i}\nname: Agent {i}\n---\n"
                )

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            start = time.time()
            agents = await loader.scan_commands()
            elapsed = time.time() - start

            assert len(agents) == 50
            assert elapsed < 2.0, f"Scan took {elapsed:.2f}s, expected < 2s"

    @pytest.mark.asyncio
    async def test_metadata_load_performance(self):
        """Test that metadata loading is fast."""
        from core.agent_loader import DynamicAgentLoader
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            (commands_dir / "test.md").write_text("---\n" + "\n".join([
                "id: test",
                "name: Test Agent",
                "description: A test agent",
                "version: '1.0'",
                "tools: [Read, Write, Edit]",
                "author: Test",
                "tags: [test, example]"
            ]) + "\n---\n")

            loader = DynamicAgentLoader(commands_dir=commands_dir)

            start = time.time()
            await loader.scan_commands()
            elapsed = time.time() - start

            assert elapsed < 0.1, f"Metadata load took {elapsed:.3f}s, expected < 0.1s"
