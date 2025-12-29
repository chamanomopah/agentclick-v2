# Story 11: Activity Log & Notifications

Status: backlog

## Story

As a user,
I want to see activity logs and notifications,
so that I can track what the system is doing and troubleshoot issues.

## Acceptance Criteria

1. Activity tab shows timestamped log entries with emoji icons, time, and message in reverse chronological order (newest first)
2. Activity tab logs key events: Agent ready (✨), Processing started (📖), Complete (✅), Copied to clipboard (📋)
3. Activity tab has "Clear Log" and "Export Log" buttons for log management
4. System shows success notification (QSystemTrayIcon) after agent execution completes
5. System shows error notification on failures with error details
6. Multiple file processing shows progress notifications: "Processing file 1/3...", "Processing file 2/3..."

## Tasks / Subtasks

- [ ] Implement Activity tab in DetailedPopupV2 (AC: #1, #2, #3)
  - [ ] Add Activity tab to QTabWidget in `ui/popup_window_v2.py`
  - [ ] Create QVBoxLayout for tab layout
  - [ ] Add QListWidget or QTextEdit for log display
  - [ ] Add "Clear Log" and "Export Log" buttons at bottom
  - [ ] Implement log entry formatting with emoji + timestamp + message

- [ ] Implement logging system (AC: #1, #2)
  - [ ] Create `utils/logger_v2.py`
  - [ ] Define log levels: INFO, SUCCESS, ERROR, WARNING
  - [ ] Define log categories: AGENT_READY, PROCESSING_START, COMPLETE, CLIPBOARD_COPY
  - [ ] Implement add_log_entry(category, message) method
  - [ ] Connect logger to UI updates via signals/slots

- [ ] Implement log entry formatting (AC: #1, #2)
  - [ ] Use emoji icons: ✨ Agent ready, 📖 Processing, ✅ Complete, 📋 Copied, ❌ Error
  - [ ] Format timestamp as HH:MM:SS
  - [ ] Format entry as "{emoji} {time} - {message}"
  - [ ] Color-code entries (green for success, red for error, blue for info)

- [ ] Implement Clear Log functionality (AC: #3)
  - [ ] Connect "Clear Log" button to clear handler
  - [ ] Confirm clear action with QMessageBox
  - [ ] Clear log display widget
  - [ ] Clear internal log storage

- [ ] Implement Export Log functionality (AC: #3)
  - [ ] Connect "Export Log" button to export handler
  - [ ] Show QFileDialog for save location
  - [ ] Write log entries to file (TXT or JSON format)
  - [ ] Show success notification after export

- [ ] Implement system notifications (AC: #4, #5)
  - [ ] Create QSystemTrayIcon for notifications
  - [ ] Implement show_notification(title, message, type) method
  - [ ] Show success notification after agent execution
  - [ ] Show error notification on failures
  - [ ] Include error details in error notifications

- [ ] Integrate with HotkeyProcessor (AC: #2)
  - [ ] Log "Agent ready" on system startup
  - [ ] Log "Processing {agent_name}..." on execution start
  - [ ] Log "Complete ({char_count} chars)" on success
  - [ ] Log "Copied to clipboard" after copy
  - [ ] Log errors with details

- [ ] Implement multiple file progress notifications (AC: #6)
  - [ ] Show progress notification: "Processing file {current}/{total}..."
  - [ ] Update progress for each file in batch
  - [ ] Show final notification: "✅ Complete: {total} files processed"
  - [ ] Log each file processing in Activity Log

- [ ] Add log filtering (UX enhancement)
  - [ ] Add filter dropdown: All, Info, Success, Error, Warning
  - [ ] Filter log display based on selected category
  - [ ] Update filter in real-time

- [ ] Implement log persistence (Future enhancement)
  - [ ] Save logs to file on application close
  - [ ] Load logs from file on application start
  - [ ] Keep max 1000 log entries (rotate old ones)

## Dev Notes

### Technical Requirements
- **Libraries:** PyQt6 (QListWidget, QTextEdit, QSystemTrayIcon, QMessageBox, QFileDialog), Python logging (stdlib), datetime, json
- **Key Features:** Structured logging, UI notifications, log export, progress tracking
- **Configuration:** Log level set to INFO, max 1000 entries, auto-rotate old logs

### Architecture Alignment
- **File Locations:**
  - `ui/popup_window_v2.py` - Activity tab implementation
  - `utils/logger_v2.py` - Logger implementation
  - `core/hotkey_processor.py` - Integration point for logging
  - `core/agent_executor.py` - Log execution events
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Hotkey Processor, Virtual Agent Executor, Input Processor

### Activity Tab Layout
```
┌─────────────────────────────────────────┐
│ Activity Log                           │
├─────────────────────────────────────────┤
│ [Filter: All ▼]                        │
│                                         │
│ ✅ 10:35:42 - Complete (142 chars)      │
│ 📋 10:35:42 - Copied to clipboard      │
│ 📖 10:35:40 - Processing verify-python...│
│ ✨ 10:35:38 - Agent ready               │
│                                         │
│ ❌ 10:34:15 - Error: Connection timeout │
│ 📖 10:34:12 - Processing diagnose...   │
│ ✨ 10:34:10 - Agent ready               │
│                                         │
│ [Clear Log] [Export Log]                │
└─────────────────────────────────────────┘
```

### Log Entry Format
```python
# Log entry structure
{
    "timestamp": "2025-12-29T10:35:42Z",
    "level": "SUCCESS",
    "category": "COMPLETE",
    "message": "Complete (142 chars)",
    "emoji": "✅"
}
```

### Notification Examples
```python
# Success notification
show_notification(
    title="AgentClick V2",
    message="verify-python executed successfully",
    type="success"
)

# Error notification
show_notification(
    title="AgentClick V2 - Error",
    message="Failed to execute diagnose: Connection timeout",
    type="error"
)

# Progress notification
show_notification(
    title="Processing files",
    message="Processing file 2/3...",
    type="info"
)
```

### Anti-Patterns to Avoid
- ❌ Don't show too many notifications (batch them if rapid-fire)
- ❌ Don't log sensitive information (file contents, API keys, etc.)
- ❌ Don't let log grow infinitely (implement rotation)
- ❌ Don't use blocking operations in logging (use async/await)
- ❌ Don't show duplicate log entries (deduplicate if needed)
- ❌ Don't forget to handle missing QSystemTrayIcon support (some platforms)
- ❌ Don't use complex markdown in logs (keep it plain text)
- ❌ Don't log every tiny detail (only important events)

### Performance Targets
- Log entry add in < 10ms
- Log display update in < 50ms
- Notification show in < 100ms
- Log export in < 500ms (for 1000 entries)
- Clear log in < 100ms

### Log Categories & Emojis
| Category | Emoji | Example Message |
|----------|-------|-----------------|
| AGENT_READY | ✨ | "Agent ready: verify-python" |
| PROCESSING_START | 📖 | "Processing verify-python..." |
| COMPLETE | ✅ | "Complete (142 chars)" |
| CLIPBOARD_COPY | 📋 | "Copied to clipboard" |
| ERROR | ❌ | "Error: Connection timeout" |
| WORKSPACE_SWITCH | 🔄 | "Switched to Python workspace" |
| AGENT_SWITCH | 🔀 | "Switched to diagnose agent" |

### Export Formats
**Text Format:**
```
=== AgentClick V2 Activity Log ===
Generated: 2025-12-29 10:35:42

✅ 10:35:42 - Complete (142 chars)
📋 10:35:42 - Copied to clipboard
📖 10:35:40 - Processing verify-python...
✨ 10:35:38 - Agent ready
```

**JSON Format:**
```json
{
  "generated": "2025-12-29T10:35:42Z",
  "entries": [
    {"timestamp": "10:35:42", "level": "SUCCESS", "message": "Complete (142 chars)", "emoji": "✅"},
    {"timestamp": "10:35:42", "level": "INFO", "message": "Copied to clipboard", "emoji": "📋"}
  ]
}
```

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Aba 1: Activity]
- [Related: Story 9 (Hotkey Processor), Story 5 (Virtual Agent Executor)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
