"""
Migration CLI for AgentClick V1 to V2

This script provides a command-line interface for migrating from V1 to V2.
It supports migration, rollback, dry-run mode, and verbose output.

Usage:
    python migration/migrate.py --migrate
    python migration/migrate.py --rollback
    python migration/migrate.py --dry-run
    python migration/migrate.py --migrate --verbose
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from migration.v1_to_v2_migrator import V1ToV2Migrator
from core.exceptions import MigrationError


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="AgentClick V1 to V2 Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview migration changes (safe, won't modify files)
  python migration/migrate.py --dry-run

  # Perform migration
  python migration/migrate.py --migrate

  # Perform migration with detailed output
  python migration/migrate.py --migrate --verbose

  # Rollback to V1 (restore from backup)
  python migration/migrate.py --rollback

  # Use custom paths
  python migration/migrate.py --migrate --v1-config path/to/config.json --v2-config path/to/workspaces.yaml
        """
    )

    # Mutually exclusive action group
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--migrate',
        action='store_true',
        help='Perform migration from V1 to V2'
    )
    action_group.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback migration and restore V1 config'
    )
    action_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview migration changes without executing'
    )

    # Optional path arguments
    parser.add_argument(
        '--v1-config',
        type=str,
        default='config/agent_config.json',
        help='Path to V1 configuration file (default: config/agent_config.json)'
    )
    parser.add_argument(
        '--v2-config',
        type=str,
        default='config/workspaces.yaml',
        help='Path to V2 workspace configuration (default: config/workspaces.yaml)'
    )
    parser.add_argument(
        '--commands-dir',
        type=str,
        default='.claude/commands',
        help='Path to commands directory for .md files (default: .claude/commands)'
    )

    # Optional flags
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress non-error output'
    )

    return parser.parse_args()


def print_dry_run_summary(migrator: V1ToV2Migrator, verbose: bool = False):
    """
    Print summary of changes that would be made during migration.

    Args:
        migrator: V1ToV2Migrator instance
        verbose: Whether to show verbose output
    """
    print("\n" + "="*60)
    print("DRY RUN MODE - Preview of migration changes")
    print("="*60)

    # Check if V1 config exists
    if not migrator.v1_config_path.exists():
        print("\nℹ️  No V1 config found at: {}".format(migrator.v1_config_path))
        print("   This appears to be a fresh install. No migration needed.")
        return

    try:
        # Load V1 config
        v1_config = migrator.load_v1_config()

        print("\n📋 Migration Summary:")
        print(f"   V1 Config: {migrator.v1_config_path}")
        print(f"   V2 Config: {migrator.v2_config_path}")
        print(f"   Commands Dir: {migrator.commands_dir}")
        print(f"   Agents to migrate: {len(v1_config)}")

        # Show agent details
        if verbose:
            print("\n📝 Agents to be converted:")
            for agent_id, agent_config in v1_config.items():
                print(f"   - {agent_id}")
                print(f"     Name: {agent_config['name']}")
                print(f"     Enabled: {agent_config['enabled']}")
                print(f"     Context Folder: {agent_config['context_folder']}")

        # Show workspace details
        first_agent = next(iter(v1_config.values()))
        default_folder = first_agent.get("context_folder", ".")

        print("\n🏠 Workspace to be created:")
        print(f"   ID: default")
        print(f"   Name: Default Workspace (Migrated from V1)")
        print(f"   Folder: {default_folder}")
        print(f"   Emoji: 🔧")
        print(f"   Color: #0078d4")

        # Show files to be created
        print("\n📄 Files to be created:")
        print(f"   - {migrator.v2_config_path}")
        for agent_id in v1_config.keys():
            agent_filename = f"{agent_id.replace('_', '-')}.md"
            print(f"   - {migrator.commands_dir / agent_filename}")

        # Show backup
        print("\n💾 Backup to be created:")
        print(f"   - {migrator.v1_config_path.stem}_<timestamp>.backup")

        # Validate YAML structure can be created
        print("\n🔍 Validating YAML structure...")
        try:
            import tempfile
            import yaml

            # Create temporary file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=True) as temp_yaml:
                temp_path = Path(temp_yaml.name)

                # Temporarily override v2_config_path for testing
                original_v2_path = migrator.v2_config_path
                migrator.v2_config_path = temp_path

                try:
                    # Test workspace creation
                    migrator.create_workspaces_yaml(v1_config)

                    # Verify YAML is valid by loading it
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)

                    print("   ✅ YAML structure is valid")

                finally:
                    # Restore original path
                    migrator.v2_config_path = original_v2_path

        except Exception as e:
            print(f"   ❌ YAML validation failed: {e}")
            print("\n⚠️  Migration would fail during workspace creation.")
            sys.exit(1)

        print("\n" + "="*60)
        print("✅ Dry run complete. No changes were made.")
        print("="*60)
        print("\n💡 To perform migration, run:")
        print("   python migration/migrate.py --migrate")

    except MigrationError as e:
        print(f"\n❌ Error during dry run: {e}")
        print("\n⚠️  Migration cannot proceed. Please fix the errors above.")
        sys.exit(1)


def perform_migration(migrator: V1ToV2Migrator, verbose: bool = False, quiet: bool = False):
    """
    Perform the migration from V1 to V2.

    Args:
        migrator: V1ToV2Migrator instance
        verbose: Whether to show verbose output
        quiet: Whether to suppress non-error output
    """
    try:
        if not quiet:
            print("\n" + "="*60)
            print("AgentClick V1 → V2 Migration")
            print("="*60)

        # Perform migration
        migrator.migrate()

        if not quiet:
            print("\n" + "="*60)
            print("✅ Migration completed successfully!")
            print("="*60)

    except MigrationError as e:
        if not quiet:
            print(f"\n❌ Migration failed: {e}")
            print("\n⚠️  An error occurred during migration.")
            print("   Changes have been rolled back automatically.")
            print("\n💡 For help, see: docs/MIGRATION_GUIDE.md")
        sys.exit(1)


def perform_rollback(migrator: V1ToV2Migrator, verbose: bool = False, quiet: bool = False):
    """
    Rollback migration and restore V1 configuration.

    Args:
        migrator: V1ToV2Migrator instance
        verbose: Whether to show verbose output
        quiet: Whether to suppress non-error output
    """
    try:
        if not quiet:
            print("\n" + "="*60)
            print("Rolling Back Migration")
            print("="*60)
            print("\n⚠️  This will:")
            print("   - Delete V2 workspace configuration")
            print("   - Delete converted agent .md files")
            print("   - Restore V1 configuration from backup")

        # Find most recent backup
        backup_dir = migrator.v1_config_path.parent
        backups = sorted(backup_dir.glob("*.backup"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not backups:
            if not quiet:
                print("\n❌ No backup files found in: {}".format(backup_dir))
                print("   Cannot rollback. Please restore manually if needed.")
            sys.exit(1)

        most_recent_backup = backups[0]

        if not quiet:
            print(f"\n📂 Most recent backup: {most_recent_backup.name}")
            confirm = input("\n⚠️  Are you sure you want to rollback? (yes/no): ")

            if confirm.lower() not in ['yes', 'y']:
                print("\n❌ Rollback cancelled.")
                sys.exit(0)

        # Set backup path and perform rollback
        migrator.backup_path = most_recent_backup
        success = migrator.rollback_migration()

        if success:
            if not quiet:
                print("\n" + "="*60)
                print("✅ Rollback completed successfully!")
                print("="*60)
                print("\n💡 Your V1 configuration has been restored.")
        else:
            if not quiet:
                print("\n❌ Rollback failed. Please restore manually.")
            sys.exit(1)

    except Exception as e:
        if not quiet:
            print(f"\n❌ Rollback failed: {e}")
            print("\n💡 For manual rollback steps, see: docs/MIGRATION_GUIDE.md")
        sys.exit(1)


def main():
    """Main entry point for the migration CLI."""
    # Parse arguments
    args = parse_arguments()

    # Create migrator instance
    migrator = V1ToV2Migrator(
        v1_config_path=args.v1_config,
        v2_config_path=args.v2_config,
        commands_dir=args.commands_dir
    )

    # Execute action
    try:
        if args.dry_run:
            # Preview mode
            print_dry_run_summary(migrator, verbose=args.verbose)

        elif args.migrate:
            # Perform migration
            perform_migration(migrator, verbose=args.verbose, quiet=args.quiet)

        elif args.rollback:
            # Rollback migration
            perform_rollback(migrator, verbose=args.verbose, quiet=args.quiet)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        if not args.quiet:
            print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
