# Story 2: Workspace Manager

Status: backlog

## Story

As a system,
I want to manage multiple workspaces with isolated contexts,
so that users can switch between different project environments seamlessly.

## Acceptance Criteria

1. WorkspaceManager can load workspaces from `config/workspaces.yaml` with proper YAML parsing
2. WorkspaceManager can switch current workspace and persist state to YAML
3. WorkspaceManager can add, update, and remove workspaces with validation
4. WorkspaceManager validates workspace configurations (ID alphanumeric check, folder existence check, color hex format #RRGGBB)
5. WorkspaceManager raises WorkspaceNotFoundError when accessing non-existent workspace

## Tasks / Subtasks

- [ ] Implement WorkspaceManager class (AC: #1, #2, #3)
  - [ ] Create `core/workspace_manager.py`
  - [ ] Implement __init__ with config_path parameter
  - [ ] Implement load_workspaces() async method
  - [ ] Implement switch_workspace(workspace_id) method
  - [ ] Implement get_current_workspace() method
  - [ ] Implement list_workspaces() method
  - [ ] Implement add_workspace(config) method
  - [ ] Implement update_workspace(workspace_id, updates) method
  - [ ] Implement remove_workspace(workspace_id) method

- [ ] Implement workspace validation (AC: #4)
  - [ ] Create WorkspaceValidator class
  - [ ] Implement validate_workspace_id() - alphanumeric + underscore only
  - [ ] Implement validate_workspace_folder() - folder must exist
  - [ ] Implement validate_workspace_color() - must match #RRGGBB format
  - [ ] Implement validate_workspace() - comprehensive validation

- [ ] Create workspace exceptions (AC: #5)
  - [ ] Create `core/exceptions.py`
  - [ ] Define WorkspaceError base exception
  - [ ] Define WorkspaceNotFoundError exception
  - [ ] Define WorkspaceLoadError exception
  - [ ] Define WorkspaceValidationError exception

- [ ] Implement YAML persistence (AC: #1, #2)
  - [ ] Create `utils/yaml_helpers.py`
  - [ ] Implement load_yaml() helper
  - [ ] Implement save_yaml() helper
  - [ ] Handle YAML version "2.0" format

- [ ] Add workspace agent management (AC: #1)
  - [ ] Implement get_workspace_agents(workspace_id) method
  - [ ] Implement assign_agent_to_workspace() method
  - [ ] Implement remove_agent_from_workspace() method

- [ ] Create default workspaces.yaml (AC: #1)
  - [ ] Create `config/workspaces.yaml`
  - [ ] Define 3 example workspaces (python, web-dev, docs)
  - [ ] Set proper structure with workspaces key

## Dev Notes

### Technical Requirements
- **Libraries:** PyYAML (yaml), pathlib, asyncio (for async methods)
- **Key Features:** Singleton pattern, YAML load/save, async I/O
- **Configuration:** config/workspaces.yaml with version "2.0"

### Architecture Alignment
- **File Locations:**
  - `core/workspace_manager.py` - Main WorkspaceManager class
  - `core/exceptions.py` - Custom exceptions
  - `utils/yaml_helpers.py` - YAML utilities
  - `config/workspaces.yaml` - Workspace configuration
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Used by UI components, Hotkey Processor, Agent Executor

### YAML Format Example
```yaml
version: "2.0"
workspaces:
  python:
    name: "Python Projects"
    folder: "C:/python-projects"
    emoji: "🐍"
    color: "#0078d4"
    agents:
      - type: command
        id: verify-python
        enabled: true
```

### Anti-Patterns to Avoid
- ❌ Don't allow removing the last workspace (must have at least 1)
- ❌ Don't switch to non-existent workspace without validation
- ❌ Don't allow workspace IDs with spaces or special characters
- ❌ Don't forget to persist state after workspace switch
- ❌ Don't use synchronous I/O for file operations (use async/await)
- ❌ Don't hardcode workspace paths - use YAML only

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Sistema de Workspaces]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 4.1: Workspace Manager API]
- [Related: Story 1 (Core Models), Story 3 (Dynamic Agent Loader)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
