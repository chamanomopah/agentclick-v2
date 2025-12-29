# Story 9: Hotkey Processor V2

Status: backlog

## Story

As a user,
I want to use hotkeys to execute agents and switch workspaces,
so that I can control the system without navigating menus.

## Acceptance Criteria

1. Pause key executes current agent with detected input using InputProcessor and VirtualAgentExecutor
2. Ctrl+Pause cycles to next agent in current workspace (updates mini popup display)
3. Ctrl+Shift+Pause switches to next workspace (updates mini popup color and emoji)
4. Hotkey processor detects input type and calls InputProcessor.detect_input_type()
5. Hotkey processor updates mini popup after workspace/agent switch (calls update_display)
6. Hotkey processor copies result to clipboard after execution using QClipboard

## Tasks / Subtasks

- [ ] Implement HotkeyProcessorV2 class (AC: #1, #2, #3, #5)
  - [ ] Create `core/hotkey_processor.py`
  - [ ] Implement __init__ with workspace_manager, agent_executor, input_processor, mini_popup references
  - [ ] Implement setup_hotkeys() method to register global hotkeys
  - [ ] Implement on_pause() handler (execute agent)
  - [ ] Implement on_ctrl_pause() handler (next agent)
  - [ ] Implement on_ctrl_shift_pause() handler (next workspace)

- [ ] Implement hotkey registration (AC: #1, #2, #3)
  - [ ] Use pynput or keyboard library for global hotkeys
  - [ ] Register Pause key → on_pause()
  - [ ] Register Ctrl+Pause → on_ctrl_pause()
  - [ ] Register Ctrl+Shift+Pause → on_ctrl_shift_pause()
  - [ ] Handle hotkey conflicts gracefully
  - [ ] Provide option to customize hotkeys (future enhancement)

- [ ] Implement agent execution flow (AC: #1, #4, #6)
  - [ ] Detect input type using input_processor.detect_input_type()
  - [ ] Process input based on type (text, file, empty, multiple, url)
  - [ ] Get current workspace and agent from workspace_manager
  - [ ] Execute agent using agent_executor.execute()
  - [ ] Copy result to clipboard using QApplication.clipboard()
  - [ ] Show success notification

- [ ] Implement agent switching (AC: #2)
  - [ ] Get current workspace from workspace_manager
  - [ ] Get list of enabled agents in workspace
  - [ ] Find index of current agent
  - [ ] Move to next agent (wrap around to beginning if at end)
  - [ ] Update workspace_manager.current_agent_index
  - [ ] Call mini_popup.update_display()

- [ ] Implement workspace switching (AC: #3)
  - [ ] Get list of all workspaces from workspace_manager
  - [ ] Find index of current workspace
  - [ ] Move to next workspace (wrap around to beginning if at end)
  - [ ] Call workspace_manager.switch_workspace(next_workspace_id)
  - [ ] Call mini_popup.update_display()

- [ ] Implement clipboard integration (AC: #6)
  - [ ] Use QApplication.clipboard()
  - [ ] Set text with clipboard.setText(result)
  - [ ] Handle empty results gracefully
  - [ ] Support rich text if needed (future)

- [ ] Add error handling (AC: #1)
  - [ ] Catch exceptions during execution
  - [ ] Show error notification on failures
  - [ ] Log errors for debugging
  - [ ] Allow user to retry on error

- [ ] Implement execution feedback (UX enhancement)
  - [ ] Show "Processing..." notification before execution
  - [ ] Update Activity Log with execution start
  - [ ] Show success/failure notification after execution
  - [ ] Update Activity Log with completion

- [ ] Create hotkey configuration (AC: #1, #2, #3)
  - [ ] Define hotkey constants (HOTKEY_PAUSE, HOTKEY_CTRL_PAUSE, etc.)
  - [ ] Make hotkeys configurable in future (via config file)
  - [ ] Document hotkey conflicts with other applications

## Dev Notes

### Technical Requirements
- **Libraries:** pynput or keyboard (global hotkeys), PyQt6 (clipboard, notifications), asyncio (async execution)
- **Key Features:** Global hotkey registration, async execution, clipboard integration, UI updates
- **Configuration:** Hotkeys: Pause, Ctrl+Pause, Ctrl+Shift+Pause

### Architecture Alignment
- **File Locations:**
  - `core/hotkey_processor.py` - HotkeyProcessorV2 class
  - `core/input_processor.py` - Input detection
  - `core/agent_executor.py` - Agent execution
  - `core/workspace_manager.py` - Workspace/agent switching
  - `ui/mini_popup_v2.py` - Display updates
- **Naming Conventions:** PascalCase for class, snake_case for methods
- **Integration Points:** All core components (Workspace Manager, Input Processor, Agent Executor, Mini Popup)

### Hotkey Mapping

| Hotkey | Action | Method Called | UI Update |
|--------|--------|---------------|-----------|
| **Pause** | Execute agent | on_pause() → execute_agent() | Success notification |
| **Ctrl+Pause** | Next agent | on_ctrl_pause() → switch_agent() | Mini popup agent name |
| **Ctrl+Shift+Pause** | Next workspace | on_ctrl_shift_pause() → switch_workspace() | Mini popup color + emoji |

### Execution Flow (Pause Key)
```python
async def on_pause():
    # 1. Detect input type
    input_type = await input_processor.detect_input_type()

    # 2. Process input
    processed_input = await input_processor.process(input_type)

    # 3. Get context
    workspace = workspace_manager.get_current_workspace()
    agent = workspace.get_current_agent()

    # 4. Execute agent
    result = await agent_executor.execute(agent, processed_input, workspace)

    # 5. Copy to clipboard
    clipboard.setText(result.output)

    # 6. Show notification
    show_notification("Agent executed successfully")
```

### Agent Switching Logic
```python
def switch_to_next_agent():
    workspace = workspace_manager.get_current_workspace()
    agents = workspace.get_enabled_agents()

    current_index = workspace.current_agent_index
    next_index = (current_index + 1) % len(agents)

    workspace.current_agent_index = next_index
    mini_popup.update_display(workspace, agents[next_index])
```

### Workspace Switching Logic
```python
def switch_to_next_workspace():
    workspaces = workspace_manager.list_workspaces()
    current_id = workspace_manager.current_workspace_id

    current_index = find_index(workspaces, current_id)
    next_index = (current_index + 1) % len(workspaces)

    next_workspace = workspaces[next_index]
    workspace_manager.switch_workspace(next_workspace.id)
    mini_popup.update_display(next_workspace, next_workspace.get_current_agent())
```

### Anti-Patterns to Avoid
- ❌ Don't use blocking operations in hotkey handlers (use async/await)
- ❌ Don't forget to handle exceptions (hotkey errors shouldn't crash system)
- ❌ Don't allow rapid-fire hotkey presses without debouncing (add 100-200ms delay)
- ❌ Don't switch agents if workspace has only 1 agent (show notification instead)
- ❌ Don't switch workspaces if only 1 workspace exists (show notification instead)
- ❌ Don't copy empty clipboard without notification (inform user)
- ❌ Don't forget to update mini popup after switches (visual feedback)
- ❌ Don't use keyboard library if it requires root/admin (use pynput instead)

### Error Handling Strategy
- **No agents enabled:** Show notification "No agents enabled in current workspace"
- **Execution failed:** Show error notification with details, log error
- **Clipboard error:** Log error, show notification "Failed to copy to clipboard"
- **Hotkey conflict:** Log warning, allow user to reconfigure hotkeys
- **Workspace/agent switch failed:** Log error, keep current state

### Performance Targets
- Hotkey response in < 50ms (UI update)
- Agent execution time varies (depends on SDK)
- Workspace switch in < 1 second (as per spec)
- Agent switch in < 100ms

### Platform Considerations
- **Windows:** pynput works well, Pause key available
- **Linux:** May need keyboard permissions, Pause key may not work on all keyboards
- **macOS:** May need accessibility permissions, Pause key may not exist (use F15 or custom)

### Security Considerations
- Global hotkeys can interfere with other applications
- Provide option to disable global hotkeys
- Allow hotkey customization to avoid conflicts

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Hotkeys & Interações]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 5.1: Fluxo Principal: Executar Agent]
- [Related: Story 2 (Workspace Manager), Story 5 (Virtual Agent Executor), Story 6 (Input Processor), Story 7 (Mini Popup)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
