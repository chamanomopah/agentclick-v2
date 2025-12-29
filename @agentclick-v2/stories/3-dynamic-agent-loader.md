# Story 3: Dynamic Agent Loader

Status: review

## Story

As a system,
I want to automatically discover and load agents from `.claude/` structure,
so that users don't need to manually configure agents.

## Acceptance Criteria

1. DynamicAgentLoader scans `.claude/commands/*.md` and creates VirtualAgent(type="command") with emoji "📝"
2. DynamicAgentLoader scans `.claude/skills/*/SKILL.md` and creates VirtualAgent(type="skill") with emoji "🎯"
3. DynamicAgentLoader scans `.claude/agents/*.md` and creates VirtualAgent(type="agent") with emoji "🤖"
4. Loader extracts YAML frontmatter metadata from .md files (id, name, description, version, tools, etc.)
5. Loader assigns correct emoji based on type and caches metadata for performance

## Tasks / Subtasks

- [x] Implement DynamicAgentLoader class (AC: #1, #2, #3, #5)
  - [x] Create `core/agent_loader.py`
  - [x] Implement __init__ with commands_dir, skills_dir, agents_dir parameters
  - [x] Implement scan_all() async method
  - [x] Implement scan_commands() async method
  - [x] Implement scan_skills() async method
  - [x] Implement scan_custom_agents() async method
  - [x] Implement create_virtual_agent() helper method

- [x] Implement YAML frontmatter extraction (AC: #4)
  - [x] Create extract_frontmatter() function
  - [x] Parse YAML between --- delimiters
  - [x] Handle missing frontmatter gracefully
  - [x] Extract common metadata fields (id, name, description, version, type, tools)

- [x] Implement metadata caching (AC: #5)
  - [x] Add _metadata_cache dict to store parsed metadata
  - [x] Implement cache invalidation on file modification
  - [x] Implement get_cached_metadata() method
  - [x] Add cache size limits to prevent memory bloat

- [x] Implement lazy loading optimization (AC: #5)
  - [x] Load only metadata initially
  - [x] Load full .md content on first access
  - [x] Implement load_content() in VirtualAgent to read on demand

- [x] Create example .claude structure (AC: #1, #2, #3)
  - [x] Create `.claude/commands/` directory
  - [x] Create `.claude/skills/` directory
  - [x] Create `.claude/agents/` directory
  - [x] Create example commands: diagnose.md, verify-python.md, review-code.md
  - [x] Create example skill: ux-ui-improver/SKILL.md

- [x] Implement agent reload functionality (AC: #1, #2, #3)
  - [x] Implement reload_agent(agent_id) method
  - [x] Implement watch_changes() async method for hot-reload
  - [x] Emit signals on agent add/remove/update

## Dev Notes

### Technical Requirements
- **Libraries:** pathlib, aiofiles (for async file I/O), ruamel.yaml or PyYAML
- **Key Features:** File system scanning, YAML parsing, lazy loading, caching
- **Configuration:** .claude/ directory structure at project root

### Architecture Alignment
- **File Locations:**
  - `core/agent_loader.py` - DynamicAgentLoader class
  - `.claude/commands/` - Command .md files
  - `.claude/skills/` - Skill directories with SKILL.md
  - `.claude/agents/` - Agent .md files
- **Naming Conventions:** snake_case for methods, kebab-case for .md filenames
- **Integration Points:** Workspace Manager (assigns agents to workspaces), Virtual Agent Executor (uses loaded agents)

### Example .md File Format
```markdown
---
id: verify-python
name: Verify Python Script
description: Validates and verifies Python scripts
version: "1.0"
tools:
  - Read
  - Write
  - Edit
---

You are a Python verification specialist. Analyze the following script:

{{input}}

Context: {{context_folder}}
```

### Anti-Patterns to Avoid
- ❌ Don't scan the entire file system - limit to .claude/ directories only
- ❌ Don't load all file contents into memory at once (lazy load)
- ❌ Don't crash on invalid .md files - log and skip them
- ❌ Don't forget to set the correct emoji based on agent type
- ❌ Don't use synchronous file operations in async methods
- ❌ Don't cache indefinitely - implement TTL or size limits

### Performance Targets
- Scan 50 agents in < 2 seconds
- Load metadata in < 100ms per agent
- Hot-reload detection in < 500ms

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Dynamic Agent Loader]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 4.2: Dynamic Agent Loader API]
- [Related: Story 1 (Core Models), Story 2 (Workspace Manager)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
✅ Story 3 Implementation Complete

**Summary:**
Successfully implemented DynamicAgentLoader following TDD principles with comprehensive test coverage.

**Implementation Highlights:**
- Created DynamicAgentLoader class with async scanning methods for commands, skills, and agents
- Implemented YAML frontmatter extraction with robust error handling
- Added metadata caching with file modification time-based invalidation
- Lazy loading implemented - only metadata loaded initially, full content on demand
- Created example .claude structure with 5 sample agents (3 commands, 1 skill, 1 agent)
- Agent reload functionality with cache invalidation

**Technical Achievements:**
- Followed TDD cycle: Red (32 tests written) → Green (all tests passing) → Refactor (code quality verified)
- All 157 tests passing (unit + integration + existing tests)
- Performance targets met: 50 agents scanned in < 0.4s (target: < 2s)
- Cache size limits implemented (1000 entries default)
- Proper async/await patterns used throughout
- Comprehensive error handling for invalid files, missing directories, etc.

**Test Coverage:**
- 32 unit tests for agent_loader.py
- 8 integration tests for end-to-end workflows
- All existing tests still passing (no regressions)
- Tests cover happy paths, edge cases, error conditions, and performance

**Acceptance Criteria Validation:**
✅ AC1: Commands scanned from .claude/commands/*.md with type="command" and emoji="📝"
✅ AC2: Skills scanned from .claude/skills/*/SKILL.md with type="skill" and emoji="🎯"
✅ AC3: Agents scanned from .claude/agents/*.md with type="agent" and emoji="🤖"
✅ AC4: YAML frontmatter extraction working (id, name, description, version, tools, etc.)
✅ AC5: Correct emoji assignment and metadata caching implemented

**Files Modified/Created:**
- core/agent_loader.py (created) - 505 lines
- tests/test_agent_loader.py (created) - 758 lines
- tests/test_agent_loader_integration.py (created) - 274 lines
- .claude/commands/diagnose.md (created)
- .claude/commands/verify-python.md (created)
- .claude/commands/review-code.md (created)
- .claude/skills/ux-ui-improver/SKILL.md (created)
- .claude/agents/code-architect.md (created)

**Anti-Patterns Avoided:**
✅ Scanning limited to .claude/ directories only
✅ Lazy loading - content loaded on demand via VirtualAgent.load_content()
✅ Invalid files handled gracefully with logging
✅ Correct emoji assignment based on agent type
✅ Async file operations used throughout
✅ Cache size limits implemented (FIFO eviction)

**Next Steps:**
- Story is ready for review
- All acceptance criteria satisfied
- Comprehensive test coverage
- Ready for integration with Virtual Agent Executor (future story)

### File List
**Core Implementation:**
- core/agent_loader.py (created, 505 lines)

**Test Files:**
- tests/test_agent_loader.py (created, 758 lines)
- tests/test_agent_loader_integration.py (created, 274 lines)

**Example Agents:**
- .claude/commands/diagnose.md (created)
- .claude/commands/verify-python.md (created)
- .claude/commands/review-code.md (created)
- .claude/skills/ux-ui-improver/SKILL.md (created)
- .claude/agents/code-architect.md (created)

**Story File:**
- @agentclick-v2/stories/3-dynamic-agent-loader.md (updated)

