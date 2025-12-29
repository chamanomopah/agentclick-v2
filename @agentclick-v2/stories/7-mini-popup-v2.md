# Story 7: Mini Popup V2 (Workspace + Agent Display)

Status: backlog

## Story

As a user,
I want to see current workspace and agent in a mini popup,
so that I can quickly understand my current context.

## Acceptance Criteria

1. Mini popup displays workspace emoji (e.g., 🐍 for Python, 🌐 for Web-Dev, 📚 for Docs) on the left side
2. Mini popup displays current agent name in the center (e.g., "verify-python", "ux-ui-improver")
3. Mini popup displays agent type icon on the right (📝 for command, 🎯 for skill, 🤖 for agent)
4. Mini popup background color matches workspace color (e.g., #0078d4 for Python workspace)
5. Mini popup size is 80x60px (slightly larger than V1's 60x40px to fit all information)

## Tasks / Subtasks

- [ ] Implement MiniPopupV2 class (AC: #1, #2, #3, #4, #5)
  - [ ] Create `ui/mini_popup_v2.py`
  - [ ] Inherit from QWidget or QLabel
  - [ ] Set fixed size to 80x60px
  - [ ] Implement update_display(workspace, agent) method
  - [ ] Implement set_workspace_color(color) method

- [ ] Design mini popup layout (AC: #1, #2, #3)
  - [ ] Use QHBoxLayout for horizontal arrangement
  - [ ] Add QLabel for workspace emoji (left)
  - [ ] Add QLabel for agent name (center)
  - [ ] Add QLabel for agent type icon (right)
  - [ ] Set proper font sizes and spacing

- [ ] Implement workspace color theming (AC: #4)
  - [ ] Apply background color from workspace.color
  - [ ] Use QWidget.setStyleSheet() for dynamic styling
  - [ ] Ensure text contrast (white text on dark backgrounds)
  - [ ] Update color when workspace switches

- [ ] Implement emoji rendering (AC: #1)
  - [ ] Use QLabel with unicode emoji support
  - [ ] Ensure emoji displays correctly on all platforms
  - [ ] Scale emoji size appropriately (16-20px)

- [ ] Implement agent name display (AC: #2)
  - [ ] Truncate long names to fit width (max 10-12 chars)
  - [ ] Use ellipsis (...) for truncated names
  - [ ] Use compact font (8-10pt)

- [ ] Implement agent type icon display (AC: #3)
  - [ ] Map agent type to emoji: command→📝, skill→🎯, agent→🤖
  - [ ] Use QLabel with proper emoji rendering
  - [ ] Scale icon size to match workspace emoji

- [ ] Add hover tooltip (UX enhancement)
  - [ ] Show tooltip on hover with full details
  - [ ] Format: "{workspace_name} - {agent_name} ({agent_type})"
  - [ ] Include hotkey hints: "Press Pause to execute, Ctrl+Pause for next agent"

- [ ] Implement click handlers (UX enhancement)
  - [ ] Single-click: Open Detailed Popup
  - [ ] Double-click: Switch workspace (Story 8)

- [ ] Create mini popup examples for testing (AC: #1-5)
  - [ ] Test with Python workspace (🐍, #0078d4)
  - [ ] Test with Web-Dev workspace (🌐, #107c10)
  - [ ] Test with Docs workspace (📚, #d83b01)

## Dev Notes

### Technical Requirements
- **Libraries:** PyQt6 (QWidget, QLabel, QHBoxLayout, QToolTip)
- **Key Features:** Dynamic styling, emoji rendering, layout management
- **Configuration:** Size 80x60px, horizontal layout with 3 elements

### Architecture Alignment
- **File Locations:**
  - `ui/mini_popup_v2.py` - MiniPopupV2 class
  - `ui/popup_window_v2.py` - Detailed Popup (opened on click)
  - `core/workspace_manager.py` - Provides current workspace and agent
- **Naming Conventions:** PascalCase for class, snake_case for methods
- **Integration Points:** Workspace Manager, Detailed Popup, Hotkey Processor

### Visual Layout
```
┌────────────────────────────┐
│ 🐍 │ verify-python │ 📝     │  ← 80x60px
└────────────────────────────┘
 ↑      ↑              ↑
 |      |              └─ Agent type icon
 |      └──────────────── Agent name (truncated if needed)
 └───────────────────────── Workspace emoji
```

### Color Examples
| Workspace | Emoji | Color | Example |
|-----------|-------|-------|---------|
| Python | 🐍 | #0078d4 | Blue |
| Web-Dev | 🌐 | #107c10 | Green |
| Docs | 📚 | #d83b01 | Orange |

### Styling Example
```python
self.setStyleSheet(f"""
    MiniPopupV2 {{
        background-color: {workspace_color};
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }}
    QLabel {{
        color: white;
        font-size: 9pt;
    }}
""")
```

### Anti-Patterns to Avoid
- ❌ Don't hardcode colors - use workspace.color
- ❌ Don't make the popup too large (max 80x60px)
- ❌ Don't use small fonts that are hard to read (min 8pt)
- ❌ Don't let agent names overflow without truncation
- ❌ Don't forget to handle color contrast for readability
- ❌ Don't use fixed emoji - must be dynamic based on workspace
- ❌ Don't use complex layouts - keep it simple with QHBoxLayout

### Performance Targets
- Update display in < 10ms (workspace/agent switch)
- Render emoji without lag
- No flickering on updates

### Platform Considerations
- Windows: Emoji render correctly natively
- Linux: May need font fallback for emoji
- macOS: Emoji render correctly natively

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: UX/UI Design - Mini Popup (V2)]
- [Related: Story 2 (Workspace Manager), Story 8 (Detailed Popup)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
