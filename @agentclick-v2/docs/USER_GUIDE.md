# AgentClick V2 - User Guide

Welcome to AgentClick V2! This guide will help you install, configure, and use AgentClick V2 effectively.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Workspaces](#workspaces)
5. [Agents](#agents)
6. [Templates](#templates)
7. [Hotkeys & Usage](#hotkeys--usage)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

AgentClick V2 is a framework for automation based on virtual agents for task execution and workspace management. It provides:

- **Virtual Agents**: Create and manage intelligent agents for specific tasks
- **Workspace Management**: Organize your projects with workspaces
- **Template Configuration**: Flexible template system for agent prompts
- **Hotkey Support**: Quick access to agents with customizable hotkeys
- **Activity Logging**: Track agent executions and results

### What's New in V2

- **Modular Agent System**: Agents are now defined as `.md` files instead of hardcoded
- **Multiple Workspaces**: Manage multiple projects with different contexts
- **Enhanced Templates**: More powerful template engine with variables
- **Better Performance**: Improved agent execution and resource management
- **Migration Support**: Easy migration from V1 with automated migration script

---

## Installation

### Prerequisites

Before installing AgentClick V2, ensure you have:

- **Python 3.8 or higher**
  ```bash
  python --version
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/agentclick-v2.git
cd agentclick-v2
```

**Screenshot: Cloning the repository**
![Screenshot: Cloning repository](images/screenshots/clone-repo.png)
> **Note:** Replace the screenshot above with an actual screenshot showing the git clone command.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Screenshot: Installing dependencies**
![Screenshot: Installing dependencies](images/screenshots/install-dependencies.png)
> **Note:** Replace the screenshot above with an actual screenshot showing the pip install command.

### Step 3: Verify Installation

```bash
python -m pytest tests/ -v
```

**Screenshot: Running tests**
![Screenshot: Running tests](images/screenshots/running-tests.png)
> **Note:** Replace the screenshot above with an actual screenshot showing all tests passing.

All tests should pass.

### Step 4: Initial Configuration

If you're upgrading from V1, see the [Migration Guide](MIGRATION_GUIDE.md).

For new installations, AgentClick V2 will create default configuration files on first run:

- `config/workspaces.yaml` - Workspace configuration
- `.claude/commands/` - Agent definitions
- `config/templates.yaml` - Template configurations

---

## Quick Start

### Your First Agent

Let's create your first agent!

1. **Create an Agent File**

   Navigate to `.claude/commands/` and create a new file called `hello-agent.md`:

   **Screenshot: Creating agent file**
   ![Screenshot: Creating agent file](images/screenshots/create-agent-file.png)
   > **Note:** Replace the screenshot above with an actual screenshot showing the .claude/commands directory and the new hello-agent.md file.

   ```markdown
   ---
   id: hello-agent
   name: Hello Agent
   description: A friendly greeting agent
   version: "2.0"
   ---

   Hello! You are a friendly assistant. Please greet the user and say: {{input}}
   ```

2. **Add Agent to Workspace**

   Edit `config/workspaces.yaml`:

   ```yaml
   version: "2.0"
   current_workspace: default

   workspaces:
     default:
       name: "My Workspace"
       folder: "."
       emoji: "🚀"
       color: "#0078d4"
       agents:
         - type: command
           id: hello-agent
           enabled: true
   ```

   **Screenshot: Editing workspaces.yaml**
   ![Screenshot: Editing workspaces.yaml](images/screenshots/edit-workspaces.png)
   > **Note:** Replace the screenshot above with an actual screenshot showing the workspaces.yaml file with the hello-agent configuration.

3. **Run the Agent**

   ```python
   from agentclick_v2 import AgentExecutor, WorkspaceManager

   # Load workspace
   manager = WorkspaceManager()
   await manager.load_workspaces()

   # Execute agent
   executor = AgentExecutor()
   workspace = manager.get_current_workspace()
   result = await executor.execute("hello-agent", "Welcome to AgentClick!", workspace)

   print(result.output)
   ```

   **Screenshot: Running the agent**
   ![Screenshot: Running agent](images/screenshots/running-agent.png)
   > **Note:** Replace the screenshot above with an actual screenshot showing the agent execution and output.

Output:
```
Hello! You are a friendly assistant. Please greet the user and say: Welcome to AgentClick!
```

---

## Workspaces

### What are Workspaces?

Workspaces organize your agents and context by project. Each workspace has:

- **Folder**: Project directory path
- **Agents**: List of agents available in this workspace
- **Emoji & Color**: Visual identification
- **Templates**: Workspace-specific template configurations

### Creating Workspaces

#### Method 1: Edit Configuration File

Edit `config/workspaces.yaml`:

```yaml
version: "2.0"
current_workspace: default

workspaces:
  default:
    name: "Default Workspace"
    folder: "C:/Projects"
    emoji: "🏠"
    color: "#0078d4"
    agents:
      - type: command
        id: diagnostic-agent
        enabled: true

  python-project:
    name: "Python Development"
    folder: "C:/Projects/python-app"
    emoji: "🐍"
    color: "#3776ab"
    agents:
      - type: command
        id: code-reviewer
        enabled: true
      - type: command
        id: python-helper
        enabled: true
```

#### Method 2: Use WorkspaceManager

```python
from core.workspace_manager import WorkspaceManager

manager = WorkspaceManager()
await manager.load_workspaces()

# Add new workspace
new_workspace = {
    "name": "Web Development",
    "folder": "C:/Projects/web-app",
    "emoji": "🌐",
    "color": "#264de4",
    "agents": []
}

await manager.add_workspace("web-dev", new_workspace)
await manager.save_workspaces()
```

### Switching Workspaces

```python
# Switch to a different workspace
await manager.switch_workspace("python-project")

# Get current workspace
current = manager.get_current_workspace()
print(f"Current workspace: {current.name}")
```

### Managing Workspace Agents

Add agents to a workspace:

```python
# Add agent to workspace
await manager.add_agent_to_workspace(
    workspace_id="python-project",
    agent_type="command",
    agent_id="python-helper",
    enabled=True
)
```

Remove agents from workspace:

```python
await manager.remove_agent_from_workspace(
    workspace_id="python-project",
    agent_id="python-helper"
)
```

---

## Agents

### Agent Types

AgentClick V2 supports three types of agents:

#### 1. Commands

Commands are simple agents defined as markdown files in `.claude/commands/`.

**Example Command**: `diagnostic-agent.md`

```markdown
---
id: diagnostic-agent
name: Diagnostic Agent
description: Analyzes code issues and provides solutions
version: "2.0"
---

You are a diagnostic agent. Analyze the following code or issue:

{{input}}

Context folder: {{context_folder}}

Provide:
1. Problem identification
2. Root cause analysis
3. Recommended solutions
4. Code examples if applicable
```

#### 2. Skills

Skills are pre-built capabilities that can be invoked (e.g., UX/UI improvement, code review).

**Example Skill Usage**:

```python
# Invoke a skill
result = await executor.execute_skill("ux-ui-improver", "Improve this form", workspace)
```

#### 3. Virtual Agents

Virtual agents are programmable agents with custom logic.

**Example Virtual Agent**:

```python
from models.virtual_agent import VirtualAgent
from core.agent_executor import AgentExecutor

agent = VirtualAgent(
    id="custom-agent",
    name="Custom Agent",
    description="A custom virtual agent"
)

# Define execution logic
async def execute(input_text: str, workspace: Workspace):
    # Custom logic here
    return f"Processed: {input_text}"

agent.execute = execute
```

### Creating Custom Agents

#### Step 1: Create Agent File

Create a new `.md` file in `.claude/commands/`:

```markdown
---
id: my-custom-agent
name: My Custom Agent
description: Does something useful
version: "2.0"
---

You are a custom agent. Process this: {{input}}

Context: {{context_folder}}
```

#### Step 2: Add to Workspace

Edit `config/workspaces.yaml`:

```yaml
workspaces:
  default:
    agents:
      - type: command
        id: my-custom-agent
        enabled: true
```

#### Step 3: Use the Agent

```python
result = await executor.execute("my-custom-agent", "Hello", workspace)
```

### Template Variables

Agents can use template variables:

- `{{input}}` - User input text
- `{{context_folder}}` - Current workspace folder
- `{{workspace_name}}` - Current workspace name
- `{{timestamp}}` - Current timestamp
- Custom variables defined in templates

---

## Templates

### What are Templates?

Templates allow you to configure agent behavior with variables and customizations.

### Template Configuration

Edit `config/templates.yaml`:

```yaml
version: "2.0"

templates:
  default:
    variables:
      max_tokens: 2000
      temperature: 0.7
      model: "claude-sonnet-4-5"

  code-review:
    variables:
      max_tokens: 3000
      temperature: 0.3
      focus_areas:
        - security
        - performance
        - readability
```

### Using Templates in Agents

```markdown
---
id: code-reviewer
name: Code Reviewer
template: code-review
---

Review the following code with focus on {{focus_areas}}:

{{input}}

Context: {{context_folder}}
```

---

## Hotkeys & Usage

### Setting Up Hotkeys

AgentClick V2 supports customizable hotkeys for quick agent access.

Edit configuration (hotkey setup varies by platform):

```yaml
hotkeys:
  Ctrl+Shift+D:
    agent: diagnostic-agent
    description: "Run diagnostic agent"

  Ctrl+Shift+R:
    agent: code-reviewer
    description: "Run code reviewer"

  Ctrl+Shift+W:
    action: switch_workspace
    description: "Switch workspace"
```

### Basic Usage Workflow

1. **Select Workspace**
   ```python
   await manager.switch_workspace("my-project")
   ```

2. **Execute Agent**
   ```python
   result = await executor.execute("my-agent", "input text", workspace)
   ```

3. **View Results**
   ```python
   print(result.output)
   print(result.execution_time)
   ```

### Activity Log

AgentClick V2 maintains an activity log:

```python
from core.activity_logger import ActivityLogger

logger = ActivityLogger()
activities = await logger.get_recent_activities(limit=10)

for activity in activities:
    print(f"{activity.timestamp} - {activity.agent_id}: {activity.status}")
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Agent Not Found

**Error**: `AgentNotFoundError: Agent 'my-agent' not found`

**Solution**:
- Verify agent file exists in `.claude/commands/`
- Check agent is added to workspace in `workspaces.yaml`
- Confirm agent is enabled: `enabled: true`

#### Issue 2: Workspace Not Loading

**Error**: `WorkspaceLoadError: Failed to load workspaces`

**Solution**:
- Check `config/workspaces.yaml` syntax
- Validate YAML formatting
- Ensure file is not corrupted

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('config/workspaces.yaml'))"
```

#### Issue 3: Template Variables Not Replaced

**Issue**: Template variables appear as literal `{{variable}}` text

**Solution**:
- Ensure template engine is initialized
- Check variable names match template definition
- Verify template is applied before agent execution

#### Issue 4: Hotkeys Not Working

**Solution**:
- Check hotkey configuration format
- Verify no conflicts with system hotkeys
- Restart AgentClick after configuration changes

### Debug Mode

Enable debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run AgentClick
```

### Getting Help

If issues persist:

1. Check logs in `logs/agentclick.log`
2. Review [Migration Guide](MIGRATION_GUIDE.md) if upgrading from V1
3. Open an issue on GitHub with:
   - Error message
   - Configuration files
   - Steps to reproduce

---

## FAQ

### Q: Can I use multiple agents simultaneously?

**A**: Yes! You can execute multiple agents concurrently:

```python
import asyncio

results = await asyncio.gather(
    executor.execute("agent1", "input1", workspace),
    executor.execute("agent2", "input2", workspace),
    executor.execute("agent3", "input3", workspace)
)
```

### Q: How do I backup my configuration?

**A**: Backup these files:
- `config/workspaces.yaml`
- `config/templates.yaml`
- `.claude/commands/` directory

```bash
# Create backup
cp -r config/ config-backup/
cp -r .claude/ .claude-backup/
```

### Q: Can I share agents between workspaces?

**A**: Yes! Add the same agent ID to multiple workspaces:

```yaml
workspaces:
  project1:
    agents:
      - id: shared-agent
        enabled: true

  project2:
    agents:
      - id: shared-agent
        enabled: true
```

### Q: How do I update an agent?

**A**: Edit the `.md` file in `.claude/commands/`. Changes take effect immediately.

### Q: What's the maximum number of agents I can have?

**A**: There's no hard limit. However, for performance, we recommend:
- Small projects: 10-20 agents
- Medium projects: 20-50 agents
- Large projects: 50+ agents (organized in workspaces)

### Q: Can I use AgentClick V2 without Claude SDK?

**A**: AgentClick V2 requires the Claude SDK for agent execution. However, you can create mock agents for testing.

### Q: How do I migrate from V1?

**A**: Use the automated migration script:

```bash
# Preview migration
python migration/migrate.py --dry-run

# Perform migration
python migration/migrate.py --migrate

# If needed, rollback
python migration/migrate.py --rollback
```

See [Migration Guide](MIGRATION_GUIDE.md) for details.

---

## Next Steps

Congratulations! You're now ready to use AgentClick V2. Here are some next steps:

1. **Explore Examples**: Check `examples/` directory for sample agents
2. **Customize Workspaces**: Create workspaces for your projects
3. **Create Agents**: Build custom agents for your workflows
4. **Configure Hotkeys**: Set up quick access to favorite agents
5. **Review Templates**: Customize templates for better control

For more information:
- [Migration Guide](MIGRATION_GUIDE.md) - Upgrading from V1
- [GitHub Repository](https://github.com/your-username/agentclick-v2) - Source code and issues
- [API Documentation](docs/API.md) - Detailed API reference

---

**Happy automating with AgentClick V2!** 🚀
