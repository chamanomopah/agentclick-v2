# AgentClick V2

AgentClick V2 is a virtual agent automation framework for task execution and workspace management with a modular, extensible architecture.

## 🚀 What's New in V2

- **📝 Modular Agent System**: Agents defined as `.md` files instead of hardcoded
- **🏢 Multiple Workspaces**: Manage multiple projects with different contexts
- **🎨 Enhanced Templates**: Powerful template engine with custom variables
- **⚡ Better Performance**: Improved agent execution and resource management
- **📊 Activity Logging**: Built-in logging of all agent executions
- **⌨️ Hotkey Support**: Customizable hotkeys for quick agent access
- **🔄 Easy Migration**: Automated migration from V1 with rollback support

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Migration from V1](#migration-from-v1)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Virtual Agents
- Create intelligent agents for specific tasks
- Three agent types: Commands, Skills, and Virtual Agents
- Dynamic agent loading from `.md` files
- Template variable support for flexible prompts

### Workspace Management
- Organize projects into separate workspaces
- Each workspace has its own agents, folder, and settings
- Easy workspace switching and management
- Visual identification with emojis and colors

### Template Engine
- Configure agent behavior with variables
- Custom templates for different use cases
- Variable substitution in agent prompts
- Workspace-specific template configurations

### Activity Logging
- Track all agent executions
- Store execution results and metadata
- Searchable activity history
- Performance metrics

## 📁 Project Structure

```
agentclick-v2/
├── config/              # System configurations
│   ├── workspaces.yaml  # Workspace configuration (V2)
│   └── templates.yaml   # Template configurations
├── core/                # Core functionality
│   ├── agent_executor.py      # Agent execution engine
│   ├── agent_loader.py        # Dynamic agent loading
│   ├── workspace_manager.py   # Workspace management
│   ├── template_engine.py     # Template processing
│   ├── input_processor.py     # Input handling
│   └── hotkey_processor.py    # Hotkey management
├── migration/           # Migration scripts
│   ├── v1_to_v2_migrator.py   # V1 → V2 migration logic
│   └── migrate.py             # Migration CLI
├── models/              # Data models
│   ├── virtual_agent.py
│   ├── workspace.py
│   ├── template_config.py
│   └── execution_result.py
├── docs/                # Documentation
│   ├── USER_GUIDE.md         # Complete user guide
│   └── MIGRATION_GUIDE.md    # V1 → V2 migration guide
├── tests/               # Unit and integration tests
├── ui/                  # User interface components
├── utils/               # Utilities and helpers
├── .claude/             # Claude-specific configurations
│   └── commands/        # Agent definitions (.md files)
├── main.py              # 🆕 Primary entry point
└── @agentclick-v2/
    ├── __main__.py      # 🆕 Module entry point
    └── __init__.py      # Package initialization
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/agentclick-v2.git
cd agentclick-v2
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -m pytest tests/ -v
```

All tests should pass.

## 🎯 Quick Start

### For New Users

1. **Initialize Your Workspace**

   AgentClick V2 will create default configuration files on first run.

2. **Start the Application**

   ```bash
   # Recommended: Run from project root using main.py
   python main.py
   ```

   The application will:
   - Create default workspace configuration
   - Scan for agents in `.claude/commands/`
   - Start the hotkey system
   - Show welcome notification

   **Note:** The `python -m agentclick_v2` option is available for development but requires proper package installation.

3. **Create Your First Agent**

   Create a file `.claude/commands/my-agent.md`:

   ```markdown
   ---
   id: my-agent
   name: My First Agent
   description: A simple agent
   version: "2.0"
   ---

   Hello! You are a helpful assistant. Process this: {{input}}
   ```

3. **Add Agent to Workspace**

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
           id: my-agent
           enabled: true
   ```

4. **Use the Agent**

   ```python
   from agentclick_v2 import WorkspaceManager, AgentExecutor

   # Load workspace
   manager = WorkspaceManager()
   await manager.load_workspaces()

   # Execute agent
   executor = AgentExecutor()
   workspace = manager.get_current_workspace()
   result = await executor.execute("my-agent", "Hello, Agent!", workspace)

   print(result.output)
   ```

### For V1 Users

If you're upgrading from V1, use the automated migration script:

```bash
# Preview migration (safe, no changes)
python migration/migrate.py --dry-run

# Perform migration
python migration/migrate.py --migrate

# If needed, rollback
python migration/migrate.py --rollback
```

See [Migration Guide](docs/MIGRATION_GUIDE.md) for detailed instructions.

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide with examples
  - Installation and setup
  - Workspace management
  - Creating and using agents
  - Template configuration
  - Hotkeys and usage
  - Troubleshooting

- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - V1 to V2 migration
  - What's new in V2
  - Breaking changes
  - Automated migration
  - Manual migration
  - Rollback procedure
  - Common issues

## 🔄 Migration from V1

Upgrading from AgentClick V1? The automated migration script makes it easy:

```bash
# Preview what will change
python migration/migrate.py --dry-run

# Migrate with backup
python migration/migrate.py --migrate

# Verify migration
python -m pytest tests/ -v
```

The migration script:
- ✅ Backs up your V1 config automatically
- ✅ Converts V1 agents to V2 `.md` files
- ✅ Creates workspace configuration
- ✅ Provides rollback if anything goes wrong

See [Migration Guide](docs/MIGRATION_GUIDE.md) for details.

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_workspace_manager.py
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_agent_executor.py::TestAgentExecutor::test_execute_agent
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/agentclick-v2.git
cd agentclick-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 📝 Examples

Check the `examples/` directory for sample implementations:

- **Mini Popup V2** - Minimal popup interface example
- **Workspace Manager Demo** - Workspace management example
- **Agent Executor Demo** - Agent execution example

## ❓ FAQ

### How is V2 different from V1?

See [Migration Guide](docs/MIGRATION_GUIDE.md#whats-new-in-v2) for a complete list of changes.

### Can I use V1 and V2 side-by-side?

It's possible but not recommended. Complete migration is better.

### What if migration fails?

The migration script creates automatic backups and can rollback. See [Migration Guide](docs/MIGRATION_GUIDE.md#rollback-procedure).

### Where can I get help?

- Check [User Guide](docs/USER_GUIDE.md#troubleshooting)
- Review [Migration Guide](docs/MIGRATION_GUIDE.md#common-migration-issues)
- Open an issue on GitHub

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built for Claude Code and Anthropic's Claude SDK
- Inspired by modern agent-based automation frameworks
- Community contributions and feedback

---

**Happy automating with AgentClick V2!** 🚀

For questions or issues, please visit:
- GitHub: [https://github.com/your-username/agentclick-v2](https://github.com/your-username/agentclick-v2)
- Documentation: [docs/](docs/)
