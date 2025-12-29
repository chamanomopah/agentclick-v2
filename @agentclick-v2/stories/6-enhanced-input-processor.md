# Story 6: Enhanced Input Processor

Status: backlog

## Story

As a user,
I want to use multiple input types (selected text, file, URL, multiple files),
so that I can process content from various sources seamlessly.

## Acceptance Criteria

1. InputProcessor detects input type automatically: text (clipboard), file (dialog), empty (popup), multiple files (sequential), url (download)
2. InputProcessor processes selected text from clipboard using PyQt6 QClipboard
3. InputProcessor opens file dialog (QFileDialog) for file input and reads file content
4. InputProcessor shows popup dialog (QInputDialog) for empty input prompting user to enter text
5. InputProcessor processes multiple files sequentially with progress notifications (Processing file 1/3...)
6. InputProcessor downloads content from URL (http/https) using aiohttp or requests

## Tasks / Subtasks

- [ ] Implement InputProcessor class (AC: #1, #2, #3, #4, #6)
  - [ ] Create `core/input_processor.py`
  - [ ] Implement __init__ with clipboard reference
  - [ ] Implement detect_input_type() async method
  - [ ] Implement process_text() method (clipboard)
  - [ ] Implement process_file() method (file dialog)
  - [ ] Implement process_empty() method (popup dialog)
  - [ ] Implement process_multiple() method (sequential processing)
  - [ ] Implement process_url() method (download content)

- [ ] Implement input type detection (AC: #1)
  - [ ] Check if clipboard has text → INPUT_TYPE_TEXT
  - [ ] Check if user selected file in file dialog → INPUT_TYPE_FILE
  - [ ] Check if user selected multiple files → INPUT_TYPE_MULTIPLE
  - [ ] Check if text looks like URL (http:// or https://) → INPUT_TYPE_URL
  - [ ] Default → INPUT_TYPE_EMPTY

- [ ] Implement clipboard integration (AC: #2)
  - [ ] Use QApplication.clipboard()
  - [ ] Get text with clipboard.text()
  - [ ] Handle empty clipboard gracefully
  - [ ] Support Unicode and multilingual text

- [ ] Implement file dialog integration (AC: #3)
  - [ ] Create QFileDialog with proper filters
  - [ ] Allow single and multiple file selection
  - [ ] Read file content with pathlib
  - [ ] Handle file read errors gracefully

- [ ] Implement empty input popup (AC: #4)
  - [ ] Create QInputDialog with prompt text
  - [ ] Show "Enter input for {agent_name}" message
  - [ ] Handle Cancel button (abort execution)
  - [ ] Return user input or None

- [ ] Implement multiple file processing (AC: #5)
  - [ ] Process files sequentially (not in parallel)
  - [ ] Show progress notification for each file
  - [ ] Return list of results (one per file)
  - [ ] Handle errors per-file without stopping entire batch

- [ ] Implement URL download (AC: #6)
  - [ ] Use aiohttp for async HTTP requests
  - [ ] Support http and https protocols
  - [ ] Set reasonable timeout (10 seconds)
  - [ ] Handle download errors gracefully
  - [ ] Optionally use URL as text if download fails (configurable)

- [ ] Create InputType enum (AC: #1)
  - [ ] Define INPUT_TYPE_TEXT = "text"
  - [ ] Define INPUT_TYPE_FILE = "file"
  - [ ] Define INPUT_TYPE_EMPTY = "empty"
  - [ ] Define INPUT_TYPE_MULTIPLE = "multiple"
  - [ ] Define INPUT_TYPE_URL = "url"

## Dev Notes

### Technical Requirements
- **Libraries:** PyQt6 (clipboard, dialogs), aiohttp (URL download), pathlib (file I/O)
- **Key Features:** Automatic type detection, async operations, progress notifications
- **Configuration:** None required (uses system defaults)

### Architecture Alignment
- **File Locations:**
  - `core/input_processor.py` - InputProcessor class
  - `core/hotkey_processor.py` - Uses InputProcessor (Story 9)
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Hotkey Processor, Virtual Agent Executor

### Input Type Detection Logic
```python
async def detect_input_type():
    # 1. Check clipboard first
    clipboard_text = QApplication.clipboard().text()
    if clipboard_text.strip():
        # Check if it's a URL
        if clipboard_text.startswith(('http://', 'https://')):
            return InputType.URL
        return InputType.TEXT

    # 2. No clipboard content - show file dialog
    # 3. User can select single/multiple files or cancel
    # 4. If canceled - show empty input popup
```

### File Dialog Example
```python
file_path, _ = QFileDialog.getOpenFileName(
    None,
    "Select file to process",
    str(Path.home()),
    "All Files (*.*)"
)
```

### Progress Notification Format
```
Processing file 1/3...
✅ Complete: file1.py processed
Processing file 2/3...
✅ Complete: file2.py processed
Processing file 3/3...
✅ Complete: 3 files processed
```

### Anti-Patterns to Avoid
- ❌ Don't use blocking operations in async methods (use await)
- ❌ Don't download large files without size limits (add timeout and size check)
- ❌ Don't crash on invalid URLs - handle errors gracefully
- ❌ Don't process multiple files in parallel (causes confusion, do sequential)
- ❌ Don't forget to close file handles after reading
- ❌ Don't assume clipboard always has text (check for empty)
- ❌ Don't use synchronous requests library for URLs (use aiohttp)

### Performance Targets
- Type detection in < 50ms
- Clipboard read in < 10ms
- File read in < 100ms (for typical files)
- URL download in < 5 seconds (with 10s timeout)
- Multiple file processing: no more than 1s overhead per file

### Error Handling Strategy
- **File Read Error:** Log error, skip file, continue with next
- **URL Download Error:** Fall back to using URL as text (configurable)
- **Empty Input:** User cancels popup → abort execution gracefully
- **Clipboard Error:** Fall back to file dialog

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Sistema de Inputs]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 1.2: Componente E - Multi-Input Processor]
- [Related: Story 2 (Workspace Manager - for context), Story 9 (Hotkey Processor)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
