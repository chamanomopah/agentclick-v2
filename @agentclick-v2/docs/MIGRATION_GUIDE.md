# AgentClick V2 - Migration Guide (V1 → V2)

This guide helps you migrate from AgentClick V1 to V2 seamlessly.

## Table of Contents

1. [What's New in V2](#whats-new-in-v2)
2. [Breaking Changes from V1](#breaking-changes-from-v1)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Automated Migration](#automated-migration)
5. [Manual Migration](#manual-migration)
6. [Post-Migration Steps](#post-migration-steps)
7. [Rollback Procedure](#rollback-procedure)
8. [Common Migration Issues](#common-migration-issues)
9. [FAQ](#faq)

---

## What's New in V2

### Major Improvements

- **Modular Agent System**: Agents are now defined as `.md` files instead of hardcoded JSON
- **Multiple Workspaces**: Support for multiple project workspaces with different contexts
- **Enhanced Templates**: More powerful template engine with custom variables
- **Better Performance**: Improved agent execution and resource management
- **Activity Logging**: Built-in logging of all agent executions
- **Hotkey Support**: Customizable hotkeys for quick agent access

### Architecture Changes

| V1 | V2 |
|----|----|
| `config/agent_config.json` (single file) | `config/workspaces.yaml` + `.claude/commands/*.md` |
| Hardcoded agents in Python | Agent definitions in markdown files |
| Single workspace | Multiple workspaces |
| No templates | Template engine with variables |
| Basic execution tracking | Full activity logging |

---

## Breaking Changes from V1

### 1. Configuration Format

**V1 Format** (`config/agent_config.json`):
```json
{
  "diagnostic_agent": {
    "name": "Diagnostic Agent",
    "system_prompt": "Analyze: {input}",
    "enabled": true,
    "context_folder": "C:/projects"
  }
}
```

**V2 Format** (`config/workspaces.yaml` + `.claude/commands/*.md`):

`config/workspaces.yaml`:
```yaml
version: "2.0"
current_workspace: default

workspaces:
  default:
    name: "Default Workspace"
    folder: "C:/projects"
    emoji: "🔧"
    color: "#0078d4"
    agents:
      - type: command
        id: diagnostic-agent
        enabled: true
```

`.claude/commands/diagnostic-agent.md`:
```markdown
---
id: diagnostic-agent
name: Diagnostic Agent
description: Migrated from V1
version: "2.0"
---

Analyze: {{input}}
Context: {{context_folder}}
```

### 2. Template Variables

**V1**: Used single braces `{input}`, `{context_folder}`

**V2**: Uses double braces `{{input}}`, `{{context_folder}}`

### 3. Agent Loading

**V1**: Agents loaded from JSON config on startup

**V2**: Agents dynamically loaded from `.md` files in `.claude/commands/`

### 4. Workspace Structure

**V1**: Single workspace with `context_folder`

**V2**: Multiple workspaces, each with its own folder, agents, and settings

---

## Pre-Migration Checklist

### ✅ Before You Start

1. **Backup Your Data**
   ```bash
   # Create backup directory
   mkdir agentclick-backup

   # Backup V1 config
   cp config/agent_config.json agentclick-backup/

   # Backup any custom agents or scripts
   cp -r custom/ agentclick-backup/  # if you have this
   ```

2. **Check V1 Configuration**
   - Verify `config/agent_config.json` exists and is valid JSON
   - Note down any custom agents you've created
   - Document your current `context_folder` path

3. **Install V2 Dependencies**
   ```bash
   cd agentclick-v2
   pip install -r requirements.txt
   ```

4. **Verify Python Version**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

5. **Review V2 Features**
   - Read [User Guide](USER_GUIDE.md) for new features
   - Understand workspace concept
   - Plan your workspace structure

### 📋 Migration Planning

Decide your migration approach:

- **Automated Migration**: Use migration script (recommended)
- **Manual Migration**: Manually convert configuration (advanced users)

Most users should use the automated migration script.

---

## Automated Migration

The automated migration script converts your V1 configuration to V2 format automatically.

### Step 1: Preview Migration (Dry Run)

See what will change without modifying any files:

```bash
python migration/migrate.py --dry-run
```

**Expected Output**:
```
============================================================
DRY RUN MODE - Preview of migration changes
============================================================

📋 Migration Summary:
   V1 Config: config/agent_config.json
   V2 Config: config/workspaces.yaml
   Commands Dir: .claude/commands
   Agents to migrate: 5

📝 Agents to be converted:
   - diagnostic_agent
     Name: Diagnostic Agent
     Enabled: True
     Context Folder: C:/projects

   - code_reviewer
     Name: Code Reviewer
     Enabled: True
     Context Folder: C:/projects

🏠 Workspace to be created:
   ID: default
   Name: Default Workspace (Migrated from V1)
   Folder: C:/projects
   Emoji: 🔧
   Color: #0078d4

📄 Files to be created:
   - config/workspaces.yaml
   - .claude/commands/diagnostic-agent.md
   - .claude/commands/code-reviewer.md

💾 Backup to be created:
   - config/agent_config_20251229_143000.backup

============================================================
✅ Dry run complete. No changes were made.
============================================================

💡 To perform migration, run:
   python migration/migrate.py --migrate
```

### Step 2: Perform Migration

When ready, execute the actual migration:

```bash
python migration/migrate.py --migrate
```

**Expected Output**:
```
============================================================
AgentClick V1 → V2 Migration
============================================================

🚀 Starting V1 → V2 migration...

📦 Step 1: Backing up V1 config...
✅ Backup created: config/agent_config_20251229_143000.backup

📖 Step 2: Loading V1 config...
✅ Loaded V1 config with 5 agents

🔄 Step 3: Converting agents to .md format...
✅ Created commands directory: .claude/commands
✅ Created agent file: diagnostic-agent.md
✅ Created agent file: code-reviewer.md

🏠 Step 4: Creating workspace configuration...
✅ Created workspace config: config/workspaces.yaml
   - 5 agents migrated to default workspace

✅ Step 5: Verifying migration...
✅ Verification passed: 5 agent files created

============================================================
✅ MIGRATION COMPLETE!
============================================================

📝 Summary:
   - V1 config backed up to: config/agent_config_20251229_143000.backup
   - V2 workspace config: config/workspaces.yaml
   - Agent .md files: .claude/commands
   - Total agents migrated: 5

💡 You can now use AgentClick V2!
   To rollback, run: python migration/migrate.py --rollback
```

### Step 3: Verify Migration

Check that migration was successful:

```bash
# Check V2 workspace config exists
ls config/workspaces.yaml

# Check agent files were created
ls .claude/commands/

# Verify workspace config is valid YAML
python -c "import yaml; print(yaml.safe_load(open('config/workspaces.yaml')))"

# Check backup was created
ls config/*.backup
```

### Step 4: Test V2

Run tests to ensure everything works:

```bash
python -m pytest tests/ -v
```

All tests should pass.

### Step 5: Start Using V2

Now you can use AgentClick V2:

```python
from agentclick_v2 import WorkspaceManager, AgentExecutor

# Load workspaces
manager = WorkspaceManager()
await manager.load_workspaces()

# Execute migrated agent
executor = AgentExecutor()
workspace = manager.get_current_workspace()
result = await executor.execute("diagnostic-agent", "Analyze this code", workspace)

print(result.output)
```

---

## Manual Migration

If the automated script fails or you prefer manual control, follow these steps:

### Step 1: Backup V1 Config

```bash
cp config/agent_config.json config/agent_config.json.backup
```

### Step 2: Create Agent .md Files

For each agent in V1 config, create a corresponding `.md` file:

**V1 Config** (`config/agent_config.json`):
```json
{
  "diagnostic_agent": {
    "name": "Diagnostic Agent",
    "system_prompt": "Analyze: {input}",
    "enabled": true,
    "context_folder": "C:/projects"
  }
}
```

**V2 Agent** (`.claude/commands/diagnostic-agent.md`):
```markdown
---
id: diagnostic-agent
name: Diagnostic Agent
description: Migrated from V1
version: "2.0"
---

Analyze: {{input}}
Context: {{context_folder}}
```

**Conversion Rules**:
1. Convert `snake_case` IDs to `kebab-case` (e.g., `diagnostic_agent` → `diagnostic-agent`)
2. Replace `{input}` with `{{input}}`
3. Replace `{context_folder}` with `{{context_folder}}`
4. Add YAML frontmatter with `id`, `name`, `description`, `version`

### Step 3: Create Workspace Config

Create `config/workspaces.yaml`:

```yaml
version: "2.0"
current_workspace: default

workspaces:
  default:
    name: "Default Workspace (Migrated from V1)"
    folder: "C:/projects"  # Use context_folder from V1
    emoji: "🔧"
    color: "#0078d4"
    agents:
      - type: command
        id: diagnostic-agent  # Use kebab-case ID
        enabled: true
      - type: command
        id: code-reviewer
        enabled: true
```

### Step 4: Verify Manual Migration

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('config/workspaces.yaml'))"

# Check agent files
ls .claude/commands/*.md

# Run tests
python -m pytest tests/ -v
```

---

## Post-Migration Steps

### 1. Organize Workspaces (Optional)

If you have multiple projects, create separate workspaces:

```yaml
workspaces:
  default:
    name: "Personal Projects"
    folder: "C:/Projects/personal"
    emoji: "🏠"
    color: "#0078d4"
    agents:
      - id: diagnostic-agent
        enabled: true

  work:
    name: "Work Projects"
    folder: "C:/Projects/work"
    emoji: "💼"
    color: "#0078d4"
    agents:
      - id: code-reviewer
        enabled: true
      - id: productivity-agent
        enabled: true
```

### 2. Customize Templates (Optional)

Create `config/templates.yaml`:

```yaml
version: "2.0"

templates:
  default:
    variables:
      max_tokens: 2000
      temperature: 0.7

  code-review:
    variables:
      focus_areas:
        - security
        - performance
```

### 3. Update Scripts

Update any scripts that use AgentClick:

**V1**:
```python
from v1_agent_system import Agent

agent = Agent("diagnostic_agent")
result = agent.execute("Analyze this")
```

**V2**:
```python
from agentclick_v2 import AgentExecutor, WorkspaceManager

manager = WorkspaceManager()
await manager.load_workspaces()
workspace = manager.get_current_workspace()

executor = AgentExecutor()
result = await executor.execute("diagnostic-agent", "Analyze this", workspace)
```

### 4. Delete V1 Config (Optional)

Once you're satisfied with V2:

```bash
# Move V1 config to archive (don't delete yet!)
mv config/agent_config.json config/archive/agent_config_v1.json
```

Keep the backup for at least a week before deleting.

---

## Rollback Procedure

If you need to rollback to V1, use the automated rollback:

### Automated Rollback

```bash
python migration/migrate.py --rollback
```

**Expected Output**:
```
============================================================
Rolling Back Migration
============================================================

⚠️  This will:
   - Delete V2 workspace configuration
   - Delete converted agent .md files
   - Restore V1 configuration from backup

📂 Most recent backup: agent_config_20251229_143000.backup

⚠️  Are you sure you want to rollback? (yes/no): yes

✅ Deleted: config/workspaces.yaml
✅ Deleted: .claude/commands
✅ Restored V1 config from: config/agent_config_20251229_143000.backup
✅ Rollback complete

============================================================
✅ Rollback completed successfully!
============================================================

💡 Your V1 configuration has been restored.
```

### Manual Rollback

If automated rollback fails:

```bash
# 1. Delete V2 files
rm config/workspaces.yaml
rm -rf .claude/commands

# 2. Restore V1 config from backup
cp config/agent_config_20251229_143000.backup config/agent_config.json

# 3. Verify V1 config
cat config/agent_config.json
```

---

## Common Migration Issues

### Issue 1: Malformed V1 Config

**Error**: `MigrationError: Malformed V1 config JSON`

**Solution**:
1. Validate V1 config JSON:
   ```bash
   python -c "import json; json.load(open('config/agent_config.json'))"
   ```
2. Fix JSON syntax errors
3. Re-run migration

### Issue 2: Missing V1 Config

**Error**: `No V1 config found. This appears to be a fresh install.`

**Solution**:
- This is normal if you didn't have V1 installed
- No migration needed
- Start using V2 directly

### Issue 3: Backup Creation Failed

**Error**: `Failed to create backup`

**Solution**:
1. Check disk space
2. Verify write permissions on `config/` directory
3. Manually create backup:
   ```bash
   cp config/agent_config.json config/agent_config.json.manual_backup
   ```

### Issue 4: Agent Conversion Failed

**Error**: `Failed to convert agent 'xyz'`

**Solution**:
1. Check V1 agent has all required fields: `name`, `system_prompt`, `enabled`, `context_folder`
2. Manually create `.md` file for that agent
3. Re-run migration

### Issue 5: YAML Validation Error

**Error**: `WorkspaceLoadError: Invalid YAML`

**Solution**:
1. Validate YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/workspaces.yaml'))"
   ```
2. Check indentation (use spaces, not tabs)
3. Ensure proper YAML syntax

---

## FAQ

### Q: Will I lose my V1 agents during migration?

**A**: No! The migration script creates a backup before making any changes. Your original V1 config is preserved.

### Q: Can I keep using V1 after migration?

**A**: Yes, you can rollback at any time using:
```bash
python migration/migrate.py --rollback
```

### Q: Do I need to rewrite all my agents?

**A**: No! The migration script automatically converts V1 agents to V2 `.md` format. You only need to manually update agents if you want to add V2-specific features.

### Q: What if I have custom V1 agents not in the standard format?

**A**: The migration script handles standard V1 format. For custom agents, you can:
1. Run automated migration for standard agents
2. Manually create `.md` files for custom agents
3. Add them to `workspaces.yaml`

### Q: Can I migrate multiple times?

**A**: Yes, but it's not recommended. If you need to remigrate:
1. Rollback to V1
2. Fix any issues
3. Migrate again

### Q: How long does migration take?

**A**: Typically less than 10 seconds for 10-20 agents. Large installations (100+ agents) may take 30-60 seconds.

### Q: What happens to my V1 activity logs?

**A**: V1 activity logs are not migrated. V2 has its own logging system. You can archive V1 logs manually if needed.

### Q: Can I use V1 and V2 side-by-side?

**A**: It's possible but not recommended. They use different configuration formats and may conflict. Complete migration is better.

---

## Next Steps

After successful migration:

1. **Read the User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
2. **Explore V2 Features**: Multiple workspaces, templates, hotkeys
3. **Customize Your Setup**: Create workspaces for different projects
4. **Create New Agents**: Take advantage of modular `.md` agent files
5. **Configure Hotkeys**: Set up quick access to favorite agents

---

## Need Help?

If you encounter issues not covered in this guide:

1. Check the [User Guide](USER_GUIDE.md) troubleshooting section
2. Review error messages carefully
3. Open an issue on GitHub with:
   - Migration command used
   - Full error message
   - V1 config (sanitized)
   - Steps to reproduce

---

**Good luck with your migration to AgentClick V2!** 🚀
