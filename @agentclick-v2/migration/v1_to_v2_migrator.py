"""
V1 to V2 Migration Module

This module handles migration from AgentClick V1 to V2, including:
- Reading V1 config/agent_config.json
- Converting V1 hardcoded agents to .md files
- Creating V2 workspace configuration
- Backup and rollback mechanisms
"""

import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re

from core.exceptions import MigrationError


class V1ToV2Migrator:
    """
    Migrates AgentClick V1 configuration to V2 format.

    This class handles the complete migration process from V1 to V2,
    including backup, conversion, and rollback capabilities.

    Attributes:
        v1_config_path (Path): Path to V1 agent_config.json
        v2_config_path (Path): Path to V2 workspaces.yaml
        commands_dir (Path): Path to .claude/commands directory
        backup_path (Optional[Path]): Path to backup file created during migration

    Example:
        >>> migrator = V1ToV2Migrator()
        >>> migrator.migrate()
        >>> print("Migration complete!")
    """

    def __init__(
        self,
        v1_config_path: str = "config/agent_config.json",
        v2_config_path: str = "config/workspaces.yaml",
        commands_dir: str = ".claude/commands"
    ):
        """
        Initialize the V1ToV2Migrator.

        Args:
            v1_config_path: Path to V1 configuration file
            v2_config_path: Path to V2 workspace configuration file
            commands_dir: Path to commands directory for .md files
        """
        self.v1_config_path = Path(v1_config_path)
        self.v2_config_path = Path(v2_config_path)
        self.commands_dir = Path(commands_dir)
        self.backup_path: Optional[Path] = None

    def backup_v1_config(self) -> Path:
        """
        Create a backup of the V1 configuration file.

        Creates a timestamped backup of the V1 config file before migration.
        The backup filename includes a timestamp to prevent overwriting
        previous backups.

        Returns:
            Path: Path to the created backup file

        Raises:
            MigrationError: If backup creation fails

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> backup_path = migrator.backup_v1_config()
            >>> print(f"Backup created at: {backup_path}")
        """
        if not self.v1_config_path.exists():
            raise MigrationError(
                f"V1 config file not found: {self.v1_config_path}"
            )

        # Generate timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use the original stem (without extension) to preserve naming
        backup_filename = f"{self.v1_config_path.stem}_{timestamp}.backup"
        backup_path = self.v1_config_path.with_name(backup_filename)

        try:
            # Copy file to backup location
            shutil.copy2(self.v1_config_path, backup_path)

            # Verify backup was actually created
            if not backup_path.exists():
                raise MigrationError(
                    f"Backup file not created after copy: {backup_path}"
                )

            # Verify backup file size matches source
            if backup_path.stat().st_size != self.v1_config_path.stat().st_size:
                raise MigrationError(
                    f"Backup file size mismatch: expected {self.v1_config_path.stat().st_size} bytes, got {backup_path.stat().st_size} bytes"
                )

            self.backup_path = backup_path
            print(f"✅ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            raise MigrationError(f"Failed to create backup: {e}")

    def load_v1_config(self) -> Dict[str, Any]:
        """
        Load and parse the V1 configuration file.

        Reads the V1 agent_config.json file and validates its structure.

        Returns:
            Dict: Parsed V1 configuration

        Raises:
            MigrationError: If V1 config is missing or malformed

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> v1_config = migrator.load_v1_config()
            >>> print(f"Loaded {len(v1_config)} agents")
        """
        if not self.v1_config_path.exists():
            raise MigrationError(
                f"V1 config file not found: {self.v1_config_path}"
            )

        try:
            with open(self.v1_config_path, 'r', encoding='utf-8') as f:
                v1_config = json.load(f)

            # Validate V1 config structure
            self._validate_v1_config(v1_config)
            print(f"✅ Loaded V1 config with {len(v1_config)} agents")
            return v1_config

        except json.JSONDecodeError as e:
            raise MigrationError(f"Malformed V1 config JSON: {e}")
        except Exception as e:
            raise MigrationError(f"Failed to load V1 config: {e}")

    def _validate_v1_config(self, v1_config: Dict[str, Any]) -> None:
        """
        Validate V1 configuration structure.

        Args:
            v1_config: Parsed V1 configuration dictionary

        Raises:
            MigrationError: If V1 config structure is invalid
        """
        if not isinstance(v1_config, dict):
            raise MigrationError("V1 config must be a dictionary")

        for agent_id, agent_config in v1_config.items():
            if not isinstance(agent_config, dict):
                raise MigrationError(f"Agent '{agent_id}' config must be a dictionary")

            # Check required fields
            required_fields = ["name", "system_prompt", "enabled", "context_folder"]
            for field in required_fields:
                if field not in agent_config:
                    raise MigrationError(
                        f"Agent '{agent_id}' missing required field: {field}"
                    )

    def convert_agents_to_md(self, v1_config: Dict[str, Any]) -> None:
        """
        Convert V1 agents to .md files in .claude/commands/ directory.

        Args:
            v1_config: Parsed V1 configuration

        Raises:
            MigrationError: If conversion fails

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> v1_config = migrator.load_v1_config()
            >>> migrator.convert_agents_to_md(v1_config)
        """
        # Create commands directory if it doesn't exist
        self.commands_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created commands directory: {self.commands_dir}")

        # Convert each agent
        for agent_id, agent_config in v1_config.items():
            try:
                md_content = self._convert_agent_to_md(agent_id, agent_config)
                md_filename = self._to_kebab_case(agent_id) + ".md"
                md_filepath = self.commands_dir / md_filename

                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                print(f"✅ Created agent file: {md_filename}")

            except Exception as e:
                raise MigrationError(f"Failed to convert agent '{agent_id}': {e}")

    def _convert_agent_to_md(self, agent_id: str, agent_config: Dict[str, Any]) -> str:
        """
        Convert a single V1 agent to .md format.

        Args:
            agent_id: V1 agent identifier
            agent_config: V1 agent configuration

        Returns:
            str: .md file content with YAML frontmatter
        """
        # Generate YAML frontmatter
        agent_name = agent_config["name"]
        agent_id_kebab = self._to_kebab_case(agent_id)

        frontmatter = f"""---
id: {agent_id_kebab}
name: {agent_name}
description: Migrated from V1
version: "2.0"
---
"""

        # Convert system_prompt from V1 to V2 format
        system_prompt = agent_config["system_prompt"]

        # Replace V1 placeholders with V2 template variables
        system_prompt = system_prompt.replace("{input}", "{{input}}")
        system_prompt = system_prompt.replace("{context_folder}", "{{context_folder}}")

        # Add context folder variable if it exists
        context_folder = agent_config.get("context_folder", "")
        if context_folder:
            system_prompt += f"\n\nContext: {{{{context_folder}}}}"

        # Ensure content ends with single newline
        content = frontmatter + system_prompt
        if not content.endswith("\n"):
            content += "\n"

        return content

    def _to_kebab_case(self, text: str) -> str:
        """
        Convert string to kebab-case.

        Args:
            text: Input string

        Returns:
            str: kebab-case string
        """
        # Replace underscores and spaces with hyphens
        kebab = re.sub(r'[_\s]+', '-', text)
        # Convert to lowercase
        kebab = kebab.lower()
        return kebab

    def create_workspaces_yaml(self, v1_config: Dict[str, Any]) -> None:
        """
        Create V2 workspaces.yaml from V1 configuration.

        Args:
            v1_config: Parsed V1 configuration

        Raises:
            MigrationError: If workspace creation fails

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> v1_config = migrator.load_v1_config()
            >>> migrator.create_workspaces_yaml(v1_config)
        """
        try:
            # Get context folder from first agent (or use default)
            first_agent = next(iter(v1_config.values()))
            default_folder = first_agent.get("context_folder", ".")

            # Build agent list for workspace
            agents = []
            for agent_id, agent_config in v1_config.items():
                agent_id_kebab = self._to_kebab_case(agent_id)
                agents.append({
                    "type": "command",
                    "id": agent_id_kebab,
                    "enabled": agent_config.get("enabled", True)
                })

            # Create workspace structure
            workspace_config = {
                "version": "2.0",
                "current_workspace": "default",
                "workspaces": {
                    "default": {
                        "name": "Default Workspace (Migrated from V1)",
                        "folder": default_folder,
                        "emoji": "🔧",
                        "color": "#0078d4",
                        "agents": agents
                    }
                }
            }

            # Ensure parent directory exists
            self.v2_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write workspace config
            with open(self.v2_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(workspace_config, f, default_flow_style=False, allow_unicode=True)

            print(f"✅ Created workspace config: {self.v2_config_path}")
            print(f"   - {len(agents)} agents migrated to default workspace")

        except Exception as e:
            raise MigrationError(f"Failed to create workspaces.yaml: {e}")

    def rollback_migration(self) -> bool:
        """
        Rollback migration by restoring V1 config and deleting V2 files.

        Returns:
            bool: True if rollback succeeded, False otherwise

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> success = migrator.rollback_migration()
            >>> if success:
            ...     print("Rollback successful")
        """
        try:
            # Delete V2 files
            if self.v2_config_path.exists():
                self.v2_config_path.unlink()
                print(f"✅ Deleted: {self.v2_config_path}")

            # Delete .md files in commands directory
            if self.commands_dir.exists():
                shutil.rmtree(self.commands_dir)
                print(f"✅ Deleted: {self.commands_dir}")

            # Restore V1 config from backup
            if self.backup_path and self.backup_path.exists():
                shutil.copy2(self.backup_path, self.v1_config_path)
                print(f"✅ Restored V1 config from: {self.backup_path}")

            print("✅ Rollback complete")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def migrate(self) -> None:
        """
        Execute the complete migration process.

        This method orchestrates the entire migration:
        1. Backup V1 config
        2. Load V1 config
        3. Convert agents to .md files
        4. Create workspaces.yaml
        5. Verify migration

        If any step fails, automatically rollback to restore V1 config.

        Raises:
            MigrationError: If migration fails (rollback will be attempted)

        Example:
            >>> migrator = V1ToV2Migrator()
            >>> migrator.migrate()
            >>> print("Migration complete!")
        """
        print("\n🚀 Starting V1 → V2 migration...")

        # Check if V1 config exists
        if not self.v1_config_path.exists():
            print("ℹ️  No V1 config found. This appears to be a fresh install.")
            print("   No migration needed.")
            return

        # Check if V2 config already exists
        if self.v2_config_path.exists():
            print(f"\n⚠️  WARNING: V2 config already exists: {self.v2_config_path}")
            print("   Migration will overwrite existing configuration!")
            confirm = input("\n   Do you want to continue? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("   Migration cancelled.")
                return

        if self.commands_dir.exists():
            md_files = list(self.commands_dir.glob("*.md"))
            if md_files:
                print(f"\n⚠️  WARNING: {len(md_files)} agent .md files already exist in {self.commands_dir}")
                print("   Migration may overwrite existing agents!")
                confirm = input("\n   Do you want to continue? (yes/no): ")
                if confirm.lower() not in ['yes', 'y']:
                    print("   Migration cancelled.")
                    return

        try:
            # Step 1: Backup V1 config
            print("\n📦 Step 1: Backing up V1 config...")
            self.backup_v1_config()

            # Step 2: Load V1 config
            print("\n📖 Step 2: Loading V1 config...")
            v1_config = self.load_v1_config()

            # Step 3: Convert agents to .md files
            print("\n🔄 Step 3: Converting agents to .md format...")
            self.convert_agents_to_md(v1_config)

            # Step 4: Create workspaces.yaml
            print("\n🏠 Step 4: Creating workspace configuration...")
            self.create_workspaces_yaml(v1_config)

            # Step 5: Verify migration
            print("\n✅ Step 5: Verifying migration...")
            self._verify_migration()

            print("\n" + "="*60)
            print("✅ MIGRATION COMPLETE!")
            print("="*60)
            print(f"\n📝 Summary:")
            print(f"   - V1 config backed up to: {self.backup_path}")
            print(f"   - V2 workspace config: {self.v2_config_path}")
            print(f"   - Agent .md files: {self.commands_dir}")
            print(f"   - Total agents migrated: {len(v1_config)}")
            print(f"\n💡 You can now use AgentClick V2!")
            print(f"   To rollback, run: python migration/migrate.py --rollback")

        except MigrationError:
            # Re-raise MigrationError as-is
            raise
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")

            # Attempt rollback
            if self.backup_path:
                print("\n🔄 Rolling back changes...")
                self.rollback_migration()
                print("✅ V1 config restored. Migration aborted.")

            raise MigrationError(f"Migration failed and rolled back: {e}")

    def _verify_migration(self) -> None:
        """
        Verify that migration was successful.

        Raises:
            MigrationError: If verification fails
        """
        # Check V2 config exists
        if not self.v2_config_path.exists():
            raise MigrationError("V2 workspace config not created")

        # Check commands directory exists
        if not self.commands_dir.exists():
            raise MigrationError("Commands directory not created")

        # Check at least one .md file exists
        md_files = list(self.commands_dir.glob("*.md"))
        if not md_files:
            raise MigrationError("No agent .md files created")

        print(f"✅ Verification passed: {len(md_files)} agent files created")
