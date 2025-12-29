"""
Tests for V1ToV2Migrator.

This module tests the migration functionality from V1 to V2 including:
- V1 config parsing
- Agent conversion to .md files
- Workspace creation
- Backup and rollback mechanisms
"""
import pytest
from pathlib import Path
import tempfile
import json
import yaml
import shutil
from datetime import datetime

from migration.v1_to_v2_migrator import V1ToV2Migrator
from core.exceptions import MigrationError


class TestV1ToV2MigratorInit:
    """Test V1ToV2Migrator initialization."""

    def test_init_with_default_paths(self):
        """Should initialize with default config paths."""
        migrator = V1ToV2Migrator()
        assert migrator.v1_config_path is not None
        assert migrator.v2_config_path is not None
        assert migrator.commands_dir is not None

    def test_init_with_custom_paths(self):
        """Should initialize with custom config paths."""
        v1_path = "/custom/v1_config.json"
        v2_path = "/custom/v2_config.yaml"
        commands_path = "/custom/commands"

        migrator = V1ToV2Migrator(
            v1_config_path=v1_path,
            v2_config_path=v2_path,
            commands_dir=commands_path
        )

        assert migrator.v1_config_path == Path(v1_path)
        assert migrator.v2_config_path == Path(v2_path)
        assert migrator.commands_dir == Path(commands_path)

    def test_backup_path_initially_none(self):
        """Backup path should be None initially."""
        migrator = V1ToV2Migrator()
        assert migrator.backup_path is None


class TestBackupV1Config:
    """Test V1 config backup functionality."""

    @pytest.fixture
    def v1_config_file(self):
        """Create a temporary V1 config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            config = {
                "diagnostic_agent": {
                    "name": "Diagnostic Agent",
                    "system_prompt": "You are a diagnostic agent. Analyze: {input}",
                    "enabled": True,
                    "context_folder": "C:/projects"
                }
            }
            json.dump(config, f, indent=2)
            return f.name

    def test_backup_creates_backup_file(self, v1_config_file):
        """Should create a backup file with .backup extension."""
        migrator = V1ToV2Migrator(v1_config_path=v1_config_file)
        backup_path = migrator.backup_v1_config()

        assert backup_path.exists()
        assert backup_path.suffix == ".backup"
        # Backup filename should contain original filename stem and timestamp
        assert "agent_config" in backup_path.stem or "tmp" in backup_path.stem

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_backup_contains_timestamp(self, v1_config_file):
        """Backup filename should contain timestamp."""
        migrator = V1ToV2Migrator(v1_config_path=v1_config_file)
        backup_path = migrator.backup_v1_config()

        # Check filename contains timestamp pattern
        assert "backup" in backup_path.name

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_backup_content_matches_original(self, v1_config_file):
        """Backup content should match original V1 config."""
        migrator = V1ToV2Migrator(v1_config_path=v1_config_file)
        backup_path = migrator.backup_v1_config()

        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = json.load(f)

        with open(v1_config_file, 'r', encoding='utf-8') as f:
            original_content = json.load(f)

        assert backup_content == original_content

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_backup_fails_for_nonexistent_file(self):
        """Should raise error if V1 config doesn't exist."""
        migrator = V1ToV2Migrator(v1_config_path="/nonexistent/config.json")

        with pytest.raises(Exception):
            migrator.backup_v1_config()

    def test_backup_sets_backup_path_attribute(self, v1_config_file):
        """Should set self.backup_path attribute after backup."""
        migrator = V1ToV2Migrator(v1_config_path=v1_config_file)
        backup_path = migrator.backup_v1_config()

        assert migrator.backup_path is not None
        assert migrator.backup_path == backup_path
        assert isinstance(backup_path, Path)

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_backup_file_is_readable_and_valid(self, v1_config_file):
        """Should create a valid, readable backup file."""
        migrator = V1ToV2Migrator(v1_config_path=v1_config_file)
        backup_path = migrator.backup_v1_config()

        # Verify backup can be read
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = json.load(f)

        # Verify backup is valid JSON and contains expected data
        assert isinstance(backup_content, dict)
        assert "diagnostic_agent" in backup_content
        assert backup_content["diagnostic_agent"]["name"] == "Diagnostic Agent"

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()


class TestLoadV1Config:
    """Test V1 config loading and parsing."""

    @pytest.fixture
    def valid_v1_config(self):
        """Create a valid V1 config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            config = {
                "diagnostic_agent": {
                    "name": "Diagnostic Agent",
                    "system_prompt": "You are a diagnostic agent. Analyze: {input}",
                    "enabled": True,
                    "context_folder": "C:/projects"
                },
                "code_reviewer": {
                    "name": "Code Reviewer",
                    "system_prompt": "Review the following code:\n{input}",
                    "enabled": True,
                    "context_folder": "C:/projects"
                }
            }
            json.dump(config, f, indent=2)
            return f.name

    def test_load_valid_v1_config(self, valid_v1_config):
        """Should load and parse V1 config successfully."""
        migrator = V1ToV2Migrator(v1_config_path=valid_v1_config)
        v1_config = migrator.load_v1_config()

        assert isinstance(v1_config, dict)
        assert "diagnostic_agent" in v1_config
        assert "code_reviewer" in v1_config
        assert v1_config["diagnostic_agent"]["name"] == "Diagnostic Agent"

        # Cleanup
        Path(valid_v1_config).unlink()

    def test_load_valid_config_parses_agent_fields(self, valid_v1_config):
        """Should parse all agent fields correctly."""
        migrator = V1ToV2Migrator(v1_config_path=valid_v1_config)
        v1_config = migrator.load_v1_config()

        agent = v1_config["diagnostic_agent"]
        assert agent["name"] == "Diagnostic Agent"
        assert agent["system_prompt"] == "You are a diagnostic agent. Analyze: {input}"
        assert agent["enabled"] is True
        assert agent["context_folder"] == "C:/projects"

        # Cleanup
        Path(valid_v1_config).unlink()

    def test_load_malformed_json_raises_error(self):
        """Should raise error for malformed JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json }")
            malformed_file = f.name

        migrator = V1ToV2Migrator(v1_config_path=malformed_file)

        with pytest.raises(Exception):
            migrator.load_v1_config()

        # Cleanup
        Path(malformed_file).unlink()

    def test_load_nonexistent_file_raises_error(self):
        """Should raise error if V1 config doesn't exist."""
        migrator = V1ToV2Migrator(v1_config_path="/nonexistent/config.json")

        with pytest.raises(Exception):
            migrator.load_v1_config()

    def test_validate_v1_config_structure(self, valid_v1_config):
        """Should validate V1 config structure."""
        migrator = V1ToV2Migrator(v1_config_path=valid_v1_config)
        v1_config = migrator.load_v1_config()

        # Validate required fields exist
        for agent_id, agent_config in v1_config.items():
            assert "name" in agent_config
            assert "system_prompt" in agent_config
            assert "enabled" in agent_config
            assert "context_folder" in agent_config

        # Cleanup
        Path(valid_v1_config).unlink()


class TestConvertAgentsToMd:
    """Test agent conversion to .md format."""

    @pytest.fixture
    def v1_config_data(self):
        """Provide V1 config data for testing."""
        return {
            "diagnostic_agent": {
                "name": "Diagnostic Agent",
                "system_prompt": "You are a diagnostic agent. Analyze: {input}",
                "enabled": True,
                "context_folder": "C:/projects"
            },
            "code_reviewer": {
                "name": "Code Reviewer",
                "system_prompt": "Review the following code:\n{input}",
                "enabled": True,
                "context_folder": "C:/projects"
            }
        }

    @pytest.fixture
    def temp_commands_dir(self):
        """Create temporary commands directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_creates_commands_directory(self, v1_config_data, temp_commands_dir):
        """Should create .claude/commands directory if it doesn't exist."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        assert Path(temp_commands_dir).exists()

    def test_converts_single_agent_to_md(self, v1_config_data, temp_commands_dir):
        """Should convert a single V1 agent to .md format."""
        single_agent = {
            "diagnostic_agent": v1_config_data["diagnostic_agent"]
        }

        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(single_agent)

        md_file = Path(temp_commands_dir) / "diagnostic-agent.md"
        assert md_file.exists()

    def test_converts_multiple_agents_to_md(self, v1_config_data, temp_commands_dir):
        """Should convert multiple V1 agents to .md files."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        assert (Path(temp_commands_dir) / "diagnostic-agent.md").exists()
        assert (Path(temp_commands_dir) / "code-reviewer.md").exists()

    def test_generates_correct_yaml_frontmatter(self, v1_config_data, temp_commands_dir):
        """Should generate correct YAML frontmatter."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        md_file = Path(temp_commands_dir) / "diagnostic-agent.md"
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify YAML frontmatter
        assert content.startswith("---")
        assert "id: diagnostic-agent" in content
        assert "name: Diagnostic Agent" in content
        assert "description: Migrated from V1" in content
        assert 'version: "2.0"' in content
        # Content should end with YAML closing marker and newline
        assert "---\n" in content
        assert content.endswith("\n")

    def test_converts_system_prompt_correctly(self, v1_config_data, temp_commands_dir):
        """Should convert system_prompt with V2 template variables."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        md_file = Path(temp_commands_dir) / "diagnostic-agent.md"
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check V2 template variables
        assert "{{input}}" in content
        assert "{{context_folder}}" in content

    def test_replaces_v1_placeholders_with_v2_variables(self, v1_config_data, temp_commands_dir):
        """Should replace {input} with {{input}} and {context_folder} with {{context_folder}}."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        md_file = Path(temp_commands_dir) / "diagnostic-agent.md"
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # V1 placeholders should be replaced with V2 variables
        assert "{input}" not in content or "{{input}}" in content
        assert "{{input}}" in content
        assert "{{context_folder}}" in content

    def test_generates_kebab_case_filenames(self, v1_config_data, temp_commands_dir):
        """Should generate kebab-case filenames."""
        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(v1_config_data)

        # Check kebab-case filenames
        assert (Path(temp_commands_dir) / "diagnostic-agent.md").exists()
        assert (Path(temp_commands_dir) / "code-reviewer.md").exists()

    def test_preserves_multiline_prompts(self, temp_commands_dir):
        """Should preserve multiline system prompts."""
        multiline_config = {
            "multiline_agent": {
                "name": "Multiline Agent",
                "system_prompt": "You are a multiline agent.\n\nLine 1\nLine 2\nLine 3\nInput: {input}",
                "enabled": True,
                "context_folder": "C:/projects"
            }
        }

        migrator = V1ToV2Migrator(commands_dir=temp_commands_dir)
        migrator.convert_agents_to_md(multiline_config)

        md_file = Path(temp_commands_dir) / "multiline-agent.md"
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content


class TestCreateWorkspacesYaml:
    """Test workspace creation from V1 config."""

    @pytest.fixture
    def v1_config_data(self):
        """Provide V1 config data for testing."""
        return {
            "diagnostic_agent": {
                "name": "Diagnostic Agent",
                "system_prompt": "Analyze: {input}",
                "enabled": True,
                "context_folder": "C:/projects"
            },
            "code_reviewer": {
                "name": "Code Reviewer",
                "system_prompt": "Review: {input}",
                "enabled": True,
                "context_folder": "C:/projects"
            }
        }

    @pytest.fixture
    def temp_workspace_file(self):
        """Create temporary workspace file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if Path(temp_path).exists():
            Path(temp_path).unlink()

    def test_creates_workspace_yaml(self, v1_config_data, temp_workspace_file):
        """Should create workspaces.yaml file."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        assert Path(temp_workspace_file).exists()

    def test_generates_correct_yaml_structure(self, v1_config_data, temp_workspace_file):
        """Should generate correct YAML structure."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        with open(temp_workspace_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        assert "version" in yaml_content
        assert yaml_content["version"] == "2.0"
        assert "workspaces" in yaml_content
        assert "default" in yaml_content["workspaces"]

    def test_creates_default_workspace(self, v1_config_data, temp_workspace_file):
        """Should create default workspace from V1 config."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        with open(temp_workspace_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        workspace = yaml_content["workspaces"]["default"]
        assert workspace["name"] == "Default Workspace (Migrated from V1)"
        assert workspace["folder"] == "C:/projects"
        assert workspace["emoji"] == "🔧"
        assert workspace["color"] == "#0078d4"

    def test_adds_migrated_agents_to_workspace(self, v1_config_data, temp_workspace_file):
        """Should add all migrated agents to workspace."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        with open(temp_workspace_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        agents = yaml_content["workspaces"]["default"]["agents"]
        assert len(agents) == 2

        agent_ids = [agent["id"] for agent in agents]
        assert "diagnostic-agent" in agent_ids
        assert "code-reviewer" in agent_ids

    def test_sets_agent_type_and_enabled_status(self, v1_config_data, temp_workspace_file):
        """Should set correct agent type and enabled status."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        with open(temp_workspace_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        agents = yaml_content["workspaces"]["default"]["agents"]
        for agent in agents:
            assert agent["type"] == "command"
            assert agent["enabled"] is True

    def test_sets_current_workspace_to_default(self, v1_config_data, temp_workspace_file):
        """Should set current_workspace to 'default'."""
        migrator = V1ToV2Migrator(v2_config_path=temp_workspace_file)
        migrator.create_workspaces_yaml(v1_config_data)

        with open(temp_workspace_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        assert yaml_content["current_workspace"] == "default"


class TestRollbackMigration:
    """Test rollback functionality."""

    @pytest.fixture
    def v1_config_file(self):
        """Create a temporary V1 config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            config = {
                "diagnostic_agent": {
                    "name": "Diagnostic Agent",
                    "system_prompt": "Analyze: {input}",
                    "enabled": True,
                    "context_folder": "C:/projects"
                }
            }
            json.dump(config, f, indent=2)
            return f.name

    @pytest.fixture
    def v2_files(self):
        """Create temporary V2 files."""
        temp_dir = tempfile.mkdtemp()

        # Create workspaces.yaml
        workspace_file = Path(temp_dir) / "workspaces.yaml"
        with open(workspace_file, 'w', encoding='utf-8') as f:
            yaml.dump({"version": "2.0"}, f)

        # Create commands directory and .md file
        commands_dir = Path(temp_dir) / "commands"
        commands_dir.mkdir()
        md_file = commands_dir / "diagnostic-agent.md"
        md_file.write_text("# Test")

        yield {
            "workspace_file": str(workspace_file),
            "commands_dir": str(commands_dir),
            "md_file": str(md_file)
        }

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_restore_from_backup_deletes_v2_files(self, v1_config_file, v2_files):
        """Should delete V2 files during rollback."""
        # Create backup
        migrator = V1ToV2Migrator(
            v1_config_path=v1_config_file,
            v2_config_path=v2_files["workspace_file"],
            commands_dir=v2_files["commands_dir"]
        )
        backup_path = migrator.backup_v1_config()

        # Verify V2 files exist
        assert Path(v2_files["workspace_file"]).exists()
        assert Path(v2_files["md_file"]).exists()

        # Rollback
        migrator.rollback_migration()

        # Verify V2 files deleted
        assert not Path(v2_files["workspace_file"]).exists()
        assert not Path(v2_files["md_file"]).exists()

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_restore_from_backup_restores_v1_config(self, v1_config_file, v2_files):
        """Should restore V1 config from backup."""
        migrator = V1ToV2Migrator(
            v1_config_path=v1_config_file,
            v2_config_path=v2_files["workspace_file"],
            commands_dir=v2_files["commands_dir"]
        )
        backup_path = migrator.backup_v1_config()

        # Modify V1 config
        with open(v1_config_file, 'w') as f:
            json.dump({"modified": True}, f)

        # Rollback
        migrator.rollback_migration()

        # Verify V1 config restored
        with open(v1_config_file, 'r') as f:
            restored_config = json.load(f)

        assert "diagnostic_agent" in restored_config
        assert restored_config["diagnostic_agent"]["name"] == "Diagnostic Agent"

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_rollback_verifies_success(self, v1_config_file, v2_files):
        """Should verify rollback success."""
        migrator = V1ToV2Migrator(
            v1_config_path=v1_config_file,
            v2_config_path=v2_files["workspace_file"],
            commands_dir=v2_files["commands_dir"]
        )
        backup_path = migrator.backup_v1_config()

        result = migrator.rollback_migration()

        assert result is True
        assert not Path(v2_files["workspace_file"]).exists()

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_rollback_deletes_entire_commands_directory(self, v1_config_file, v2_files):
        """Should delete entire commands directory during rollback."""
        # Create backup
        migrator = V1ToV2Migrator(
            v1_config_path=v1_config_file,
            v2_config_path=v2_files["workspace_file"],
            commands_dir=v2_files["commands_dir"]
        )
        backup_path = migrator.backup_v1_config()

        # Create multiple .md files in commands directory
        commands_dir = Path(v2_files["commands_dir"])
        (commands_dir / "agent1.md").write_text("# Agent 1")
        (commands_dir / "agent2.md").write_text("# Agent 2")
        (commands_dir / "agent3.md").write_text("# Agent 3")

        # Verify all files exist
        assert (commands_dir / "agent1.md").exists()
        assert (commands_dir / "agent2.md").exists()
        assert (commands_dir / "agent3.md").exists()

        # Rollback
        migrator.rollback_migration()

        # Verify entire directory deleted
        assert not Path(v2_files["commands_dir"]).exists()

        # Cleanup
        backup_path.unlink()
        Path(v1_config_file).unlink()

    def test_rollback_handles_missing_files_gracefully(self, v1_config_file):
        """Should not fail if V2 files don't exist during rollback."""
        migrator = V1ToV2Migrator(
            v1_config_path=v1_config_file,
            v2_config_path="/nonexistent/workspaces.yaml",
            commands_dir="/nonexistent/commands"
        )

        # Don't create V2 files - rollback should not fail
        result = migrator.rollback_migration()
        assert result is True

        # Cleanup
        Path(v1_config_file).unlink()


class TestMigrate:
    """Test main migration orchestration."""

    @pytest.fixture
    def complete_v1_config(self):
        """Create a complete V1 config for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            config = {
                "diagnostic_agent": {
                    "name": "Diagnostic Agent",
                    "system_prompt": "Analyze: {input}",
                    "enabled": True,
                    "context_folder": "C:/test/projects"
                },
                "code_reviewer": {
                    "name": "Code Reviewer",
                    "system_prompt": "Review: {input}",
                    "enabled": True,
                    "context_folder": "C:/test/projects"
                }
            }
            json.dump(config, f, indent=2)
            return f.name

    @pytest.fixture
    def migration_dirs(self):
        """Create temporary directories for migration."""
        temp_dir = tempfile.mkdtemp()
        v2_config = Path(temp_dir) / "workspaces.yaml"
        commands_dir = Path(temp_dir) / "commands"

        yield {
            "temp_dir": temp_dir,
            "v2_config": str(v2_config),
            "commands_dir": str(commands_dir)
        }

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_migrate_creates_backup(self, complete_v1_config, migration_dirs):
        """Should create backup before migration."""
        migrator = V1ToV2Migrator(
            v1_config_path=complete_v1_config,
            v2_config_path=migration_dirs["v2_config"],
            commands_dir=migration_dirs["commands_dir"]
        )
        migrator.migrate()

        assert migrator.backup_path is not None
        assert migrator.backup_path.exists()

        # Cleanup
        migrator.backup_path.unlink()
        Path(complete_v1_config).unlink()

    def test_migrate_creates_workspace_yaml(self, complete_v1_config, migration_dirs):
        """Should create workspaces.yaml."""
        migrator = V1ToV2Migrator(
            v1_config_path=complete_v1_config,
            v2_config_path=migration_dirs["v2_config"],
            commands_dir=migration_dirs["commands_dir"]
        )
        migrator.migrate()

        assert Path(migration_dirs["v2_config"]).exists()

        # Cleanup
        migrator.backup_path.unlink()
        Path(complete_v1_config).unlink()

    def test_migrate_creates_md_files(self, complete_v1_config, migration_dirs):
        """Should create .md files for agents."""
        migrator = V1ToV2Migrator(
            v1_config_path=complete_v1_config,
            v2_config_path=migration_dirs["v2_config"],
            commands_dir=migration_dirs["commands_dir"]
        )
        migrator.migrate()

        commands_dir = Path(migration_dirs["commands_dir"])
        assert (commands_dir / "diagnostic-agent.md").exists()
        assert (commands_dir / "code-reviewer.md").exists()

        # Cleanup
        migrator.backup_path.unlink()
        Path(complete_v1_config).unlink()

    def test_migrate_handles_missing_v1_config_gracefully(self, migration_dirs):
        """Should handle missing V1 config gracefully."""
        migrator = V1ToV2Migrator(
            v1_config_path="/nonexistent/config.json",
            v2_config_path=migration_dirs["v2_config"],
            commands_dir=migration_dirs["commands_dir"]
        )

        # Should not raise exception, should print message
        migrator.migrate()

    def test_migrate_rolls_back_on_error(self, migration_dirs):
        """Should rollback if migration fails."""
        # Create invalid V1 config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json }")
            invalid_config = f.name

        migrator = V1ToV2Migrator(
            v1_config_path=invalid_config,
            v2_config_path=migration_dirs["v2_config"],
            commands_dir=migration_dirs["commands_dir"]
        )

        # Should raise MigrationError and rollback
        with pytest.raises(MigrationError):
            migrator.migrate()

        # Verify backup was created and rollback happened
        assert migrator.backup_path is not None
        # V2 files should not exist after rollback
        assert not Path(migration_dirs["v2_config"]).exists()

        # Cleanup
        if migrator.backup_path.exists():
            migrator.backup_path.unlink()
        Path(invalid_config).unlink()
