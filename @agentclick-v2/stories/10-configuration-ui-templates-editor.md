# Story 10: Configuration UI & Templates Editor

Status: backlog

## Story

As a user,
I want to edit input templates and manage agents through the UI,
so that I can customize the system without editing YAML files manually.

## Acceptance Criteria

1. Config tab shows current workspace name and current agent name in header section
2. Config tab has input template editor (QTextEdit) with live preview of rendered template
3. Config tab lists available agents in current workspace with enable/disable checkboxes
4. Config tab has "Scan for New Agents" button that triggers DynamicAgentLoader.scan_all()
5. Config tab has "Save Template" button that validates and saves template to input_templates.yaml
6. Template changes are immediately saved to `config/input_templates.yaml` with proper YAML formatting

## Tasks / Subtasks

- [ ] Implement Config tab in DetailedPopupV2 (AC: #1, #2, #3, #4, #5)
  - [ ] Add Config tab to QTabWidget in `ui/popup_window_v2.py`
  - [ ] Create QVBoxLayout for tab layout
  - [ ] Add "Current Workspace" and "Current Agent" labels at top
  - [ ] Create Input Template section with QTextEdit and preview
  - [ ] Create Available Agents section with QListWidget and checkboxes
  - [ ] Add buttons: "Scan for New Agents", "Save Template"

- [ ] Implement template editor (AC: #2)
  - [ ] Add QTextEdit for template editing
  - [ ] Add QLabel for live preview (read-only)
  - [ ] Implement preview update on text change
  - [ ] Use sample data for preview: input="<sample input>", context_folder="/example", focus_file="main.py"
  - [ ] Highlight template variables ({{input}}, etc.) with syntax highlighting

- [ ] Implement template validation (AC: #5)
  - [ ] Call TemplateEngine.validate_template() on save
  - [ ] Show validation errors in QMessageBox if invalid
  - [ ] Disable "Save" button if template is invalid
  - [ ] Show inline error messages below editor

- [ ] Implement template save functionality (AC: #5, #6)
  - [ ] Connect "Save Template" button to save handler
  - [ ] Call TemplateEngine.save_template(agent_id, template)
  - [ ] Show success notification on save
  - [ ] Update preview after save
  - [ ] Handle save errors gracefully

- [ ] Implement agent list with checkboxes (AC: #3)
  - [ ] Create QListWidget or QTableWidget for agent list
  - [ ] Add checkbox column for enable/disable state
  - [ ] Show agent type emoji (📝, 🎯, 🤖) next to agent name
  - [ ] Load agents from current workspace
  - [ ] Refresh list when workspace switches

- [ ] Implement agent enable/disable functionality (AC: #3)
  - [ ] Connect checkbox state changes to workspace manager
  - [ ] Update workspace.agents[].enabled based on checkbox
  - [ ] Persist changes to workspaces.yaml
  - [ ] Update agent list immediately on checkbox change

- [ ] Implement "Scan for New Agents" button (AC: #4)
  - [ ] Connect button to DynamicAgentLoader.scan_all()
  - [ ] Show progress dialog during scan
  - [ ] Update agent list after scan
  - [ ] Show notification with count of new agents found
  - [ ] Handle scan errors gracefully

- [ ] Implement agent selection for template editing (AC: #1, #2)
  - [ ] Add agent selector dropdown or list
  - [ ] Load current agent's template on selection
  - [ ] Update template editor when agent changes
  - [ ] Show which agent's template is being edited

- [ ] Add keyboard shortcuts (UX enhancement)
  - [ ] Ctrl+S: Save template
  - [ ] Ctrl+R: Refresh agent list
  - [ ] Ctrl+P: Update preview

## Dev Notes

### Technical Requirements
- **Libraries:** PyQt6 (QTextEdit, QListWidget, QCheckBox, QPushButton, QMessageBox), TemplateEngine, DynamicAgentLoader, WorkspaceManager
- **Key Features:** Live preview, template validation, agent management, YAML persistence
- **Configuration:** config/input_templates.yaml for templates, workspaces.yaml for agent enable/disable

### Architecture Alignment
- **File Locations:**
  - `ui/popup_window_v2.py` - Config tab implementation
  - `core/template_engine.py` - Template validation and save
  - `core/agent_loader.py` - Agent scanning
  - `core/workspace_manager.py` - Agent enable/disable persistence
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Template Engine, Dynamic Agent Loader, Workspace Manager

### Config Tab Layout
```
┌─────────────────────────────────────────┐
│ Configuration                           │
├─────────────────────────────────────────┤
│ **Current Workspace**: Python Projects  │
│ **Current Agent**: verify-python (📝)   │
│                                         │
│ Input Template:                        │
│ ┌───────────────────────────────────┐  │
│ │ Arquivo: {{input}}                │  │ ← QTextEdit (editable)
│ │ Contexto: {{context_folder}}      │  │
│ │ Focus: {{focus_file}}             │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Preview:                               │
│ ┌───────────────────────────────────┐  │
│ │ Arquivo: <sample input>           │  │ ← QLabel (read-only)
│ │ Contexto: /example                │  │
│ │ Focus: main.py                    │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Available Agents in Python Workspace:  │
│ ☑ 📝 verify-python                   │
│ ☑ 📝 diagnose                        │
│ ☐ 📝 review-code                     │
│ ☑ 🎯 ux-ui-improver                  │
│                                         │
│ [Scan for New Agents] [Save Template]   │
└─────────────────────────────────────────┘
```

### Template Validation Errors
```python
# Example validation feedback
if "{{unknown_var}}" in template:
    show_error("Unknown variable: {{unknown_var}}")

if "{{input" in template:  # Unclosed bracket
    show_error("Unclosed bracket: {{input")
```

### Anti-Patterns to Avoid
- ❌ Don't allow saving invalid templates (validate first)
- ❌ Don't use blocking scan operations (use async/await)
- ❌ Don't forget to refresh agent list after scan
- ❌ Don't allow editing system templates (make them read-only or add warning)
- ❌ Don't lose unsaved template changes (warn user on tab switch)
- ❌ Don't use raw YAML dump (use proper formatting with comments preserved)
- ❌ Don't forget to update preview in real-time (debounce if needed)

### Performance Targets
- Preview update in < 100ms (debounce to 500ms if heavy)
- Template validation in < 50ms
- Template save in < 200ms
- Agent scan in < 2 seconds (as per spec)
- Agent list refresh in < 100ms

### User Experience Considerations
- Show template variables in different color (syntax highlighting)
- Auto-focus template editor on tab open
- Warn user if template has unsaved changes on agent switch
- Show "New" badge next to newly discovered agents
- Sort agent list alphabetically or by type
- Allow filtering agents by type (command/skill/agent)

### Validation Error Messages
- **Unclosed bracket:** "Template has unclosed bracket: {{input"
- **Unknown variable:** "Unknown variable in template: {{unknown}}"
- **Missing variable:** "Required variable not used: {{input}}"
- **Syntax error:** "Template syntax error: {details}"

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Aba 2: Config]
- [Related: Story 2 (Workspace Manager), Story 3 (Dynamic Agent Loader), Story 4 (Template Engine)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
