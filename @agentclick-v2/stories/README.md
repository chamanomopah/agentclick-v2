# AgentClick V2 Stories

**Project:** AgentClick V2
**Total Stories:** 12
**Created:** 2025-12-29
**Status:** backlog

---

## Overview

AgentClick V2 transforms the system from 3 hardcoded Python agents into a dynamic, extensible platform supporting the Claude ecosystem structure (`.claude/commands`, `.claude/skills`, `.claude/agents`) with workspace-based context isolation.

**Implementation Order:** Start with Story 1 and proceed sequentially. Stories with no dependencies can be implemented in parallel.

---

## Story 1: Project Structure & Core Models

**User Story:**
As a developer,
I want the project structure and core data models defined,
so that I can build the rest of the system on a solid foundation.

**Acceptance Criteria:**
1. Project directory structure matches technical specification (core/, models/, ui/, config/, utils/, migration/)
2. VirtualAgent dataclass is defined with all required fields (id, type, name, description, source_file, emoji, color, enabled, workspace_id, metadata)
3. Workspace dataclass is defined with all required fields (id, name, folder, emoji, color, agents)
4. TemplateConfig dataclass is defined with all required fields (agent_id, template, enabled, variables)
5. ExecutionResult dataclass is defined for agent execution outputs

**Dependencies:** None

**Estimated Complexity:** small

**Technical Context:**
- Python 3.11+ with dataclasses
- Type hints throughout
- Pydantic-style validation
- File location: `models/virtual_agent.py`, `models/workspace.py`, `models/template_config.py`

---

## Story 2: Workspace Manager

**User Story:**
As a system,
I want to manage multiple workspaces with isolated contexts,
so that users can switch between different project environments seamlessly.

**Acceptance Criteria:**
1. WorkspaceManager can load workspaces from `config/workspaces.yaml`
2. WorkspaceManager can switch current workspace and persist state
3. WorkspaceManager can add, update, and remove workspaces
4. WorkspaceManager validates workspace configurations (ID format, folder existence, color format)
5. WorkspaceManager raises WorkspaceNotFoundError when workspace doesn't exist

**Dependencies:** Story 1

**Estimated Complexity:** medium

**Technical Context:**
- Singleton pattern for global workspace manager
- YAML load/save with PyYAML
- Workspace validation logic
- File location: `core/workspace_manager.py`
- Config file: `config/workspaces.yaml` with version "2.0"

---

## Story 3: Dynamic Agent Loader

**User Story:**
As a system,
I want to automatically discover and load agents from `.claude/` structure,
so that users don't need to manually configure agents.

**Acceptance Criteria:**
1. DynamicAgentLoader scans `.claude/commands/*.md` and creates VirtualAgent(type="command")
2. DynamicAgentLoader scans `.claude/skills/*/SKILL.md` and creates VirtualAgent(type="skill")
3. DynamicAgentLoader scans `.claude/agents/*.md` and creates VirtualAgent(type="agent")
4. Loader extracts YAML frontmatter metadata from .md files
5. Loader assigns correct emoji based on type (📝 command, 🎯 skill, 🤖 agent)

**Dependencies:** Story 1

**Estimated Complexity:** medium

**Technical Context:**
- File system scanning with pathlib
- YAML frontmatter extraction (ruamel.yaml or similar)
- Lazy loading for performance
- Metadata caching
- File location: `core/agent_loader.py`
- Directory structure: `.claude/commands/`, `.claude/skills/`, `.claude/agents/`

---

## Story 4: Template Engine

**User Story:**
As a user,
I want to customize input templates with variables,
so that I can format inputs consistently for each agent.

**Acceptance Criteria:**
1. TemplateEngine loads templates from `config/input_templates.yaml`
2. TemplateEngine applies templates by replacing {{input}}, {{context_folder}}, {{focus_file}}
3. TemplateEngine validates template syntax before saving
4. TemplateEngine provides preview of rendered template
5. TemplateEngine gracefully handles missing templates (returns input unchanged)

**Dependencies:** Story 1

**Estimated Complexity:** small

**Technical Context:**
- String.Template or Jinja2 for rendering
- Template compilation and caching
- Variable extraction and validation
- File location: `core/template_engine.py`
- Config file: `config/input_templates.yaml`

---

## Story 5: Virtual Agent Executor

**User Story:**
As a system,
I want to execute virtual agents using Claude SDK,
so that agents defined in .md files can process user inputs.

**Acceptance Criteria:**
1. VirtualAgentExecutor creates ClaudeAgentOptions dynamically from VirtualAgent
2. Executor applies input template before execution
3. Executor sets system_prompt from .md file content
4. Executor configures allowed_tools based on agent type (command: basic tools, skill: +custom tools)
5. Executor returns ExecutionResult with output, status, and metadata

**Dependencies:** Story 1, Story 3, Story 4

**Estimated Complexity:** large

**Technical Context:**
- Factory pattern for SDK options
- claude-agent-sdk integration
- MCP server creation for skills with custom tools
- Async execution
- File location: `core/agent_executor.py`
- SDK: ClaudeAgentOptions with system_prompt, allowed_tools, mcp_servers, permission_mode

---

## Story 6: Enhanced Input Processor

**User Story:**
As a user,
I want to use multiple input types (selected text, file, URL, multiple files),
so that I can process content from various sources seamlessly.

**Acceptance Criteria:**
1. InputProcessor detects input type automatically (text, file, empty, multiple, url)
2. InputProcessor processes selected text from clipboard
3. InputProcessor opens file dialog for file input
4. InputProcessor shows popup dialog for empty input
5. InputProcessor processes multiple files sequentially with progress notification
6. InputProcessor downloads content from URL (http/https)

**Dependencies:** Story 2 (for workspace context)

**Estimated Complexity:** medium

**Technical Context:**
- PyQt6 clipboard integration
- File dialog (QFileDialog)
- HTTP requests for URLs (aiohttp or requests)
- Sequential processing with async/await
- Progress notifications
- File location: `core/input_processor.py`

---

## Story 7: Mini Popup V2 (Workspace + Agent Display)

**User Story:**
As a user,
I want to see current workspace and agent in a mini popup,
so that I can quickly understand my current context.

**Acceptance Criteria:**
1. Mini popup displays workspace emoji (e.g., 🐍, 🌐, 📚)
2. Mini popup displays current agent name
3. Mini popup displays agent type icon (📝 command, 🎯 skill, 🤖 agent)
4. Mini popup background color matches workspace color
5. Mini popup size is 80x60px (slightly larger than V1)

**Dependencies:** Story 2, Story 3

**Estimated Complexity:** small

**Technical Context:**
- PyQt6 QLabel or QWidget
- Custom styling with QWidget.setStyleSheet()
- Workspace-based color theming
- Emoji rendering
- File location: `ui/mini_popup_v2.py`

---

## Story 8: Detailed Popup V2 - Workspaces Tab

**User Story:**
As a user,
I want to manage workspaces through a dedicated UI tab,
so that I can create, edit, and switch workspaces visually.

**Acceptance Criteria:**
1. Detailed Popup has 3 tabs: Activity, Config, Workspaces
2. Workspaces tab shows current workspace with emoji, name, folder, color, agent count
3. Workspaces tab lists all workspaces with checkboxes
4. Workspaces tab has buttons: Add Workspace, Edit Workspace, Switch Workspace, Delete Workspace
5. Double-clicking mini popup switches workspace

**Dependencies:** Story 2, Story 7

**Estimated Complexity:** medium

**Technical Context:**
- PyQt6 QTabWidget
- QTableWidget or QListWidget for workspace list
- Workspace creation/editing dialog (QDialog)
- Workspace validation UI
- File location: `ui/popup_window_v2.py`, `ui/workspace_dialog.py`

---

## Story 9: Hotkey Processor V2

**User Story:**
As a user,
I want to use hotkeys to execute agents and switch workspaces,
so that I can control the system without navigating menus.

**Acceptance Criteria:**
1. Pause key executes current agent with input
2. Ctrl+Pause cycles to next agent in current workspace
3. Ctrl+Shift+Pause switches to next workspace
4. Hotkey processor detects input type and calls InputProcessor
5. Hotkey processor updates mini popup after workspace/agent switch
6. Hotkey processor copies result to clipboard after execution

**Dependencies:** Story 2, Story 5, Story 6, Story 7

**Estimated Complexity:** medium

**Technical Context:**
- pynput or keyboard library for global hotkeys
- Integration with InputProcessor, VirtualAgentExecutor
- PyQt6 signals/slots for UI updates
- Clipboard operations (QClipboard)
- File location: `core/hotkey_processor.py`

---

## Story 10: Configuration UI & Templates Editor

**User Story:**
As a user,
I want to edit input templates and manage agents through the UI,
so that I can customize the system without editing YAML files manually.

**Acceptance Criteria:**
1. Config tab shows current workspace and current agent
2. Config tab has input template editor with preview
3. Config tab lists available agents in current workspace with checkboxes
4. Config tab has "Scan for New Agents" button
5. Config tab has "Save Template" button with validation
6. Template changes are saved to `config/input_templates.yaml`

**Dependencies:** Story 2, Story 3, Story 4, Story 8

**Estimated Complexity:** medium

**Technical Context:**
- QTextEdit for template editing
- Real-time template preview
- Agent list with QCheckBox
- YAML validation before save
- File location: `ui/popup_window_v2.py` (Config tab implementation)

---

## Story 11: Activity Log & Notifications

**User Story:**
As a user,
I want to see activity logs and notifications,
so that I can track what the system is doing and troubleshoot issues.

**Acceptance Criteria:**
1. Activity tab shows timestamped log entries (emoji + time + message)
2. Activity tab logs: Agent ready, Processing started, Complete, Copied to clipboard
3. Activity tab has "Clear Log" and "Export Log" buttons
4. System shows success notification after execution
5. System shows error notification on failures
6. Multiple file processing shows progress (Processing file 1/3...)

**Dependencies:** Story 5, Story 8, Story 9

**Estimated Complexity:** small

**Technical Context:**
- QTextEdit or QListWidget for activity log
- QSystemTrayIcon for notifications
- Structured logging format
- Log export to file
- File location: `ui/popup_window_v2.py` (Activity tab), `utils/logger_v2.py`

---

## Story 12: Migration Script & Documentation

**User Story:**
As a V1 user,
I want to migrate my configuration to V2 automatically,
so that I can upgrade without losing my settings.

**Acceptance Criteria:**
1. Migration script reads V1 `config/agent_config.json`
2. Migration script converts V1 agents to .md files in `.claude/commands/`
3. Migration script creates default workspace in `config/workspaces.yaml`
4. Migration script backs up V1 config before migration
5. Migration script provides rollback mechanism
6. User guide documents installation, configuration, and usage
7. Migration guide documents V1 → V2 upgrade process

**Dependencies:** Story 1, Story 2, Story 3 (all foundational components)

**Estimated Complexity:** medium

**Technical Context:**
- JSON to YAML conversion
- .md file generation from V1 agent configs
- Backup/restore logic
- Error handling and validation
- File location: `migration/v1_to_v2_migrator.py`
- Documentation: `README.md`, `MIGRATION_GUIDE.md`, `USER_GUIDE.md`

---

## Dependency Graph

```
Story 1 (Foundation)
  ├─→ Story 2 (Workspace Manager)
  │     ├─→ Story 7 (Mini Popup)
  │     │     ├─→ Story 8 (Workspaces Tab)
  │     │     └─→ Story 9 (Hotkey Processor)
  │     ├─→ Story 6 (Input Processor)
  │     └─→ Story 10 (Config UI)
  ├─→ Story 3 (Agent Loader)
  │     ├─→ Story 7 (Mini Popup)
  │     └─→ Story 5 (Agent Executor)
  ├─→ Story 4 (Template Engine)
  │     ├─→ Story 5 (Agent Executor)
  │     └─→ Story 10 (Config UI)
  └─→ Story 12 (Migration)

Story 5 (Agent Executor)
  ├─→ Story 9 (Hotkey Processor)
  └─→ Story 11 (Activity Log)

Story 8 (Workspaces Tab)
  ├─→ Story 10 (Config UI)
  └─→ Story 11 (Activity Log)

Story 9 (Hotkey Processor)
  └─→ Story 11 (Activity Log)
```

---

## Implementation Order

**Phase 1: Foundation (Stories 1-4)**
- Story 1: Project Structure & Core Models
- Story 2: Workspace Manager
- Story 3: Dynamic Agent Loader
- Story 4: Template Engine

**Phase 2: Execution Engine (Stories 5-6)**
- Story 5: Virtual Agent Executor
- Story 6: Enhanced Input Processor

**Phase 3: User Interface (Stories 7-8, 10)**
- Story 7: Mini Popup V2
- Story 8: Detailed Popup V2 - Workspaces Tab
- Story 10: Configuration UI & Templates Editor

**Phase 4: Integration & Polish (Stories 9, 11-12)**
- Story 9: Hotkey Processor V2
- Story 11: Activity Log & Notifications
- Story 12: Migration Script & Documentation

---

## Estimated Timeline

- **Phase 1:** 2 weeks (Foundation)
- **Phase 2:** 2 weeks (Execution Engine)
- **Phase 3:** 2 weeks (User Interface)
- **Phase 4:** 2 weeks (Integration & Polish)

**Total:** 8 weeks (as specified in PRD)

---

## Next Steps

1. **Review Stories:**
   - Read through all 12 stories
   - Verify dependencies are correct
   - Adjust complexity estimates if needed

2. **Start Implementation:**
   - Run `/bmad:2-dev-story 1` to begin Story 1
   - Follow the dependency order
   - Update status in `status.yaml` as you progress

3. **Track Progress:**
   - Mark stories as `ready-for-dev`, `in-dev`, `ready-for-review`, `done`
   - Use `status.yaml` for overall progress tracking
