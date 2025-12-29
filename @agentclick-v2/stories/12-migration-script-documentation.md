# Story 12: Migration Script & Documentation

Status: backlog

## Story

As a V1 user,
I want to migrate my configuration to V2 automatically,
so that I can upgrade without losing my settings.

## Acceptance Criteria

1. Migration script reads V1 `config/agent_config.json` and parses agent configurations
2. Migration script converts V1 hardcoded agents to .md files in `.claude/commands/` directory
3. Migration script creates default workspace in `config/workspaces.yaml` with migrated agents
4. Migration script backs up V1 config to `.json.backup` before migration
5. Migration script provides rollback mechanism to restore from backup
6. User guide documents installation, configuration, and usage with screenshots and examples
7. Migration guide documents V1 → V2 upgrade process step-by-step

## Tasks / Subtasks

- [ ] Implement V1ToV2Migrator class (AC: #1, #2, #3, #4, #5)
  - [ ] Create `migration/v1_to_v2_migrator.py`
  - [ ] Implement __init__ with v1_config_path and v2_config_path parameters
  - [ ] Implement backup_v1_config() method
  - [ ] Implement load_v1_config() method
  - [ ] Implement convert_agents_to_md() method
  - [ ] Implement create_workspaces_yaml() method
  - [ ] Implement rollback_migration() method
  - [ ] Implement migrate() main orchestration method

- [ ] Implement V1 config parsing (AC: #1)
  - [ ] Read `config/agent_config.json` (V1 format)
  - [ ] Parse agent configurations (name, system_prompt, enabled, context_folder)
  - [ ] Validate V1 config structure
  - [ ] Handle missing or malformed V1 config gracefully

- [ ] Implement agent conversion to .md (AC: #2)
  - [ ] Create `.claude/commands/` directory if not exists
  - [ ] Convert each V1 agent to .md format
  - [ ] Generate YAML frontmatter with id, name, description, version
  - [ ] Convert system_prompt string to .md content
  - [ ] Replace V1 placeholders with V2 template variables ({{input}}, {{context_folder}})
  - [ ] Save .md files with kebab-case filenames (e.g., "diagnostic-agent.md" → "diagnostic-agent.md")

- [ ] Implement workspace creation (AC: #3)
  - [ ] Create default workspace from V1 config
  - [ ] Set workspace.folder from V1 context_folder
  - [ ] Add all migrated agents to workspace.agents list
  - [ ] Generate workspace YAML structure
  - [ ] Save to `config/workspaces.yaml`

- [ ] Implement backup mechanism (AC: #4)
  - [ ] Copy V1 config to `{filename}.json.backup`
  - [ ] Add timestamp to backup filename
  - [ ] Verify backup was created successfully
  - [ ] Abort migration if backup fails

- [ ] Implement rollback mechanism (AC: #5)
  - [ ] Implement restore_from_backup() method
  - [ ] Delete V2 files (workspaces.yaml, .md files)
  - [ ] Restore V1 config from backup
  - [ ] Verify rollback success
  - [ ] Provide rollback CLI command

- [ ] Create migration CLI (AC: #1-5)
  - [ ] Create `migration/migrate.py` script
  - [ ] Add CLI arguments: --migrate, --rollback, --dry-run, --verbose
  - [ ] Implement dry-run mode (preview changes without executing)
  - [ ] Show migration progress with detailed output
  - [ ] Handle errors gracefully with helpful messages

- [ ] Write User Guide (AC: #6)
  - [ ] Create `docs/USER_GUIDE.md`
  - [ ] Document installation steps (prerequisites, setup)
  - [ ] Document workspace creation and management
  - [ ] Document agent creation (commands, skills, agents)
  - [ ] Document template configuration
  - [ ] Document hotkeys and usage
  - [ ] Add screenshots and examples
  - [ ] Document troubleshooting common issues

- [ ] Write Migration Guide (AC: #7)
  - [ ] Create `docs/MIGRATION_GUIDE.md`
  - [ ] Document V1 → V2 changes overview
  - [ ] Document step-by-step migration process
  - [ ] Document migration script usage
  - [ ] Document manual migration (if script fails)
  - [ ] Document rollback procedure
  - [ ] Document breaking changes and migration tips
  - [ ] Add FAQ section

- [ ] Update main README (AC: #6)
  - [ ] Update project README for V2
  - [ ] Add V2 features overview
  - [ ] Link to User Guide and Migration Guide
  - [ ] Add quick start guide

- [ ] Add migration tests (Quality assurance)
  - [ ] Create test fixtures for V1 config
  - [ ] Test agent conversion to .md
  - [ ] Test workspace creation
  - [ ] Test backup and rollback
  - [ ] Test edge cases (missing config, malformed JSON, etc.)

## Dev Notes

### Technical Requirements
- **Libraries:** json (V1 config parsing), PyYAML (V2 config creation), pathlib (file operations), shutil (backup/restore), argparse (CLI)
- **Key Features:** JSON to YAML conversion, .md file generation, backup/restore, CLI interface
- **Configuration:** V1: config/agent_config.json, V2: config/workspaces.yaml, .claude/commands/

### Architecture Alignment
- **File Locations:**
  - `migration/v1_to_v2_migrator.py` - Migration logic
  - `migration/migrate.py` - CLI interface
  - `docs/USER_GUIDE.md` - User documentation
  - `docs/MIGRATION_GUIDE.md` - Migration documentation
  - `README.md` - Updated main README
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Workspace Manager (uses migrated workspaces.yaml), Dynamic Agent Loader (scans migrated .md files)

### V1 Config Format Example
```json
{
  "diagnostic_agent": {
    "name": "Diagnostic Agent",
    "system_prompt": "You are a diagnostic agent. Analyze: {input}",
    "enabled": true,
    "context_folder": "C:/projects"
  },
  "code_reviewer": {
    "name": "Code Reviewer",
    "system_prompt": "Review the following code:\n{input}",
    "enabled": true,
    "context_folder": "C:/projects"
  }
}
```

### V2 .md File Format (Generated)
```markdown
---
id: diagnostic-agent
name: Diagnostic Agent
description: Migrated from V1
version: "2.0"
---

You are a diagnostic agent. Analyze: {{input}}
Context: {{context_folder}}
```

### V2 Workspace YAML (Generated)
```yaml
version: "2.0"
workspaces:
  default:
    name: "Default Workspace (Migrated from V1)"
    folder: "C:/projects"
    emoji: "🔧"
    color: "#0078d4"
    agents:
      - type: command
        id: diagnostic-agent
        enabled: true
      - type: command
        id: code-reviewer
        enabled: true
```

### Migration Flow
```python
async def migrate():
    # 1. Backup V1 config
    backup_path = backup_v1_config()

    try:
        # 2. Load V1 config
        v1_config = load_v1_config()

        # 3. Convert agents to .md
        for agent_name, agent_config in v1_config.items():
            md_content = convert_agent_to_md(agent_name, agent_config)
            save_md_file(agent_name, md_content)

        # 4. Create workspaces.yaml
        create_workspaces_yaml(v1_config)

        # 5. Verify migration
        verify_migration()

        print("✅ Migration complete!")

    except Exception as e:
        # Rollback on error
        rollback_migration(backup_path)
        print(f"❌ Migration failed: {e}")
        print("Rollback complete. V1 config restored.")
```

### CLI Interface
```bash
# Dry run (preview changes)
python migration/migrate.py --dry-run

# Migrate
python migration/migrate.py --migrate

# Rollback
python migration/migrate.py --rollback

# Verbose output
python migration/migrate.py --migrate --verbose
```

### Anti-Patterns to Avoid
- ❌ Don't proceed with migration without backup (always backup first)
- ❌ Don't overwrite existing V2 configs without warning (check and confirm)
- ❌ Don't use hardcoded paths - make paths configurable
- ❌ Don't ignore V1 config errors - validate and report them
- ❌ Don't forget to document breaking changes clearly
- ❌ Don't make migration irreversible without rollback (always provide rollback)
- ❌ Don't assume V1 config exists - handle fresh install case

### Error Handling Strategy
- **Missing V1 config:** Inform user this is a fresh install, no migration needed
- **Malformed V1 config:** Show specific error, suggest manual migration
- **Backup failure:** Abort migration, show error
- **Migration failure:** Rollback automatically, restore from backup
- **Rollback failure:** Show emergency manual rollback steps

### Documentation Structure

**User Guide Sections:**
1. Introduction to AgentClick V2
2. Installation (prerequisites, setup)
3. Quick Start (first-time users)
4. Workspaces (create, manage, switch)
5. Agents (commands, skills, agents)
6. Templates (configure, customize)
7. Hotkeys & Usage
8. Troubleshooting
9. FAQ

**Migration Guide Sections:**
1. What's New in V2
2. Breaking Changes from V1
3. Pre-Migration Checklist
4. Automated Migration (using script)
5. Manual Migration (step-by-step)
6. Post-Migration Steps
7. Rollback Procedure
8. Common Migration Issues
9. FAQ

### References
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 8: Estratégia de Migração V1 → V2]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Apêndice B: Exemplo Completo de Migration]
- [Related: Story 1 (Core Models), Story 2 (Workspace Manager), Story 3 (Dynamic Agent Loader)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
