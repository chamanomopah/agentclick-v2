# Story 8: Detailed Popup V2 - Workspaces Tab

Status: backlog

## Story

As a user,
I want to manage workspaces through a dedicated UI tab,
so that I can create, edit, and switch workspaces visually.

## Acceptance Criteria

1. Detailed Popup has 3 tabs: Activity (📋), Config (⚙️), Workspaces (💼) using QTabWidget
2. Workspaces tab shows current workspace with emoji, name, folder path, color, and agent count in a highlighted section
3. Workspaces tab lists all workspaces in a table/list with checkboxes for enabled/disabled state
4. Workspaces tab has 4 action buttons: Add Workspace, Edit Workspace, Switch Workspace, Delete Workspace
5. Double-clicking mini popup switches workspace using WorkspaceManager

## Tasks / Subtasks

- [ ] Implement DetailedPopupV2 class (AC: #1)
  - [ ] Create `ui/popup_window_v2.py`
  - [ ] Inherit from QMainWindow or QWidget
  - [ ] Set size to 600x500px (larger than V1)
  - [ ] Add header showing "AgentClick V2 - {workspace_name}"
  - [ ] Create QTabWidget with 3 tabs

- [ ] Implement Workspaces tab layout (AC: #2, #3)
  - [ ] Create QVBoxLayout for tab content
  - [ ] Add "Current Workspace" section at top with QGroupBox
  - [ ] Display workspace details: emoji, name, folder, color, agent count
  - [ ] Add "All Workspaces" section below with QTableWidget or QListWidget
  - [ ] Show workspace emoji, name, agent count in list
  - [ ] Add checkbox column for enabled state (optional, for future use)

- [ ] Implement workspace action buttons (AC: #4)
  - [ ] Create QHBoxLayout for buttons at bottom
  - [ ] Add "Add Workspace" button → opens WorkspaceDialog (create mode)
  - [ ] Add "Edit Workspace" button → opens WorkspaceDialog (edit mode)
  - [ ] Add "Switch Workspace" button → calls workspace_manager.switch_workspace()
  - [ ] Add "Delete Workspace" button → calls workspace_manager.remove_workspace()
  - [ ] Disable "Delete" if only one workspace exists

- [ ] Implement WorkspaceDialog (AC: #4)
  - [ ] Create `ui/workspace_dialog.py`
  - [ ] Inherit from QDialog
  - [ ] Add form fields: ID (QLineEdit), Name (QLineEdit), Folder (QFileDialog), Emoji (QComboBox or QLineEdit), Color (QColorDialog button)
  - [ ] Add OK and Cancel buttons
  - [ ] Validate inputs before accepting (ID format, folder exists, color format)
  - [ ] Support both create and edit modes (constructor parameter)

- [ ] Implement workspace list refresh (AC: #3)
  - [ ] Connect to workspace manager signals
  - [ ] Refresh list when workspaces change
  - [ ] Update current workspace display on switch
  - [ ] Highlight current workspace in list

- [ ] Implement double-click workspace switch (AC: #5)
  - [ ] In MiniPopupV2, override mouseDoubleClickEvent()
  - [ ] Call workspace_manager.switch_workspace() to next workspace
  - [ ] Emit signal to update UI

- [ ] Add workspace validation UI feedback (AC: #4)
  - [ ] Show error message for invalid workspace ID
  - [ ] Show error message if folder doesn't exist
  - [ ] Show error message if color format is invalid
  - [ ] Use QMessageBox for errors

- [ ] Implement Activity and Config tab placeholders (AC: #1)
  - [ ] Create Activity tab with placeholder (implement in Story 11)
  - [ ] Create Config tab with placeholder (implement in Story 10)
  - [ ] Add tab icons: 📋 Activity, ⚙️ Config, 💼 Workspaces

## Dev Notes

### Technical Requirements
- **Libraries:** PyQt6 (QMainWindow, QTabWidget, QTableWidget, QDialog, QFormLayout, QMessageBox, QColorDialog, QFileDialog)
- **Key Features:** Tab widget, form validation, dialog management, list/table display
- **Configuration:** Popup size 600x500px

### Architecture Alignment
- **File Locations:**
  - `ui/popup_window_v2.py` - DetailedPopupV2 class
  - `ui/workspace_dialog.py` - WorkspaceDialog class
  - `ui/mini_popup_v2.py` - Double-click handler
  - `core/workspace_manager.py` - Workspace management
- **Naming Conventions:** PascalCase for classes, snake_case for methods
- **Integration Points:** Workspace Manager, Mini Popup, Activity Tab (Story 11), Config Tab (Story 10)

### Workspaces Tab Layout
```
┌─────────────────────────────────────────┐
│ AgentClick V2 - Python Projects         │ ← Header
├─────────────────────────────────────────┤
│ [📋 Activity] [⚙️ Config] [💼 Workspaces] ← Tabs
├─────────────────────────────────────────┤
│ **Current Workspace**:                  │
│ ┌─────────────────────────────────────┐ │
│ │ 🐍 Python Projects                  │ │
│ │ Folder: C:\python-projects          │ │
│ │ Agents: 2 active                    │ │
│ │ Color: #0078d4                      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ **All Workspaces**:                     │
│ ☑ 🐍 Python Projects (2 agents)        │
│ ☑ 🌐 Web Development (1 agent)         │
│ ☐ 📚 Documentation (1 agent)           │
│                                         │
│ [Add] [Edit] [Switch] [Delete]          │
└─────────────────────────────────────────┘
```

### WorkspaceDialog Fields
| Field | Type | Validation | Example |
|-------|------|------------|---------|
| ID | QLineEdit | Alphanumeric + underscore | "python-projects" |
| Name | QLineEdit | Required | "Python Projects" |
| Folder | QFileDialog | Must exist | "C:/python-projects" |
| Emoji | QLineEdit/QComboBox | Optional, default based on ID | "🐍" |
| Color | QColorDialog | Hex format | "#0078d4" |

### Anti-Patterns to Avoid
- ❌ Don't allow deleting the last workspace (must have at least 1)
- ❌ Don't allow workspace ID conflicts (must be unique)
- ❌ Don't forget to refresh UI after workspace operations
- ❌ Don't use blocking operations in UI thread (use async for file I/O)
- ❌ Don't hardcode workspace list - load from WorkspaceManager
- ❌ Don't allow switching to non-existent workspace without validation
- ❌ Don't forget to persist workspace changes to YAML

### Error Handling Strategy
- **Invalid ID:** Show QMessageBox with error, keep dialog open
- **Folder doesn't exist:** Show error, prompt user to select existing folder
- **Duplicate ID:** Show error, suggest unique ID
- **Delete last workspace:** Disable "Delete" button, show tooltip "Cannot delete last workspace"
- **Switch failed:** Log error, show notification, keep current workspace

### Performance Targets
- Open popup in < 100ms
- Switch workspace in < 1 second (as per spec)
- Refresh workspace list in < 50ms
- Open WorkspaceDialog in < 50ms

### User Experience Considerations
- Highlight current workspace clearly in list
- Show emoji and color in workspace list for visual identification
- Use color picker dialog for easy color selection
- Provide emoji picker or predefined emoji list
- Show folder path as clickable link (opens in file explorer)

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: UX/UI Design - Detailed Popup (V2)]
- [Source: AGENTCLICK_V2_PRD.md#Section: Aba 3: Workspaces (NOVA)]
- [Related: Story 2 (Workspace Manager), Story 7 (Mini Popup), Story 10 (Config Tab)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
