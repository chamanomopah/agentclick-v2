# Story 3: Dynamic Agent Loader

Status: backlog

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

- [ ] Implement DynamicAgentLoader class (AC: #1, #2, #3, #5)
  - [ ] Create `core/agent_loader.py`
  - [ ] Implement __init__ with commands_dir, skills_dir, agents_dir parameters
  - [ ] Implement scan_all() async method
  - [ ] Implement scan_commands() async method
  - [ ] Implement scan_skills() async method
  - [ ] Implement scan_custom_agents() async method
  - [ ] Implement create_virtual_agent() helper method

- [ ] Implement YAML frontmatter extraction (AC: #4)
  - [ ] Create extract_frontmatter() function
  - [ ] Parse YAML between --- delimiters
  - [ ] Handle missing frontmatter gracefully
  - [ ] Extract common metadata fields (id, name, description, version, type, tools)

- [ ] Implement metadata caching (AC: #5)
  - [ ] Add _metadata_cache dict to store parsed metadata
  - [ ] Implement cache invalidation on file modification
  - [ ] Implement get_cached_metadata() method
  - [ ] Add cache size limits to prevent memory bloat

- [ ] Implement lazy loading optimization (AC: #5)
  - [ ] Load only metadata initially
  - [ ] Load full .md content on first access
  - [ ] Implement load_content() in VirtualAgent to read on demand

- [ ] Create example .claude structure (AC: #1, #2, #3)
  - [ ] Create `.claude/commands/` directory
  - [ ] Create `.claude/skills/` directory
  - [ ] Create `.claude/agents/` directory
  - [ ] Create example commands: diagnose.md, verify-python.md, review-code.md
  - [ ] Create example skill: ux-ui-improver/SKILL.md

- [ ] Implement agent reload functionality (AC: #1, #2, #3)
  - [ ] Implement reload_agent(agent_id) method
  - [ ] Implement watch_changes() async method for hot-reload
  - [ ] Emit signals on agent add/remove/update

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
[To be filled during implementation]

### File List
[To be filled during implementation]
