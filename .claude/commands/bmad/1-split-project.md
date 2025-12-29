---
description: Split large project into BMAD stories to avoid LLM context overload
argument-hint: [context-type] [source-path]
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

# Split Project into BMAD Stories

You are analyzing a large project and splitting it into **independent BMAD stories** to prevent LLM context overload during implementation.

## Mission Critical

- **ZERO USER INTERVENTION:** Process should be fully automated
- **EXHAUSTIVE ANALYSIS:** Thoroughly analyze ALL provided context - do NOT be lazy!
- **CONTEXT OVERLOAD PREVENTION:** Each story must be implementable in ~2000 tokens
- **INDEPENDENT STORIES:** Stories should have minimal coupling and clear dependencies
- **BMAD COMPLIANCE:** Follow BMAD story structure and conventions

## Input Parameters

- **{{CONTEXT_TYPE}}:** `codebase` | `prd` | `prompt` | `auto` (default)
- **{{SOURCE_PATH}}:** Path to analyze (default: current directory)

## Phase 1: Context Discovery & Analysis

### Step 1: Identify Input Type

**If {{CONTEXT_TYPE}} == "codebase" or {{SOURCE_PATH}} contains code:**
- Use `Glob` to discover all source files: `**/*.ts`, `**/*.tsx`, `**/*.js`, `**/*.py`, etc.
- Use `Grep` to find key patterns: imports, class definitions, API routes
- Read critical files to understand functionality:
  - `package.json` or `requirements.txt` (dependencies)
  - `README.md` (project overview)
  - Main entry points (index files, app files)
  - Configuration files

**If {{CONTEXT_TYPE}} == "prd" or {{SOURCE_PATH}} is a document:**
- Load the PRD/document file
- Use `Grep` to find section headers, feature descriptions
- Extract all features, requirements, technical specifications

**If {{CONTEXT_TYPE}} == "prompt":**
- Use the user's descriptive prompt as primary context
- Ask clarifying questions ONLY if absolutely necessary for story breakdown

**If {{CONTEXT_TYPE}} == "auto" or not provided:**
- Auto-detect: Check if {{SOURCE_PATH}} is codebase, PRD, or needs prompt input
- Default to analyzing current git repository if no path provided

### Step 2: Understand Project Scope

Analyze the discovered content and identify:

**Functional Areas:**
- Authentication & authorization
- Database & data models
- API endpoints & services
- UI components & pages
- Business logic & features
- Integrations (external APIs, services)
- Configuration & infrastructure

**Technical Stack:**
- Languages & frameworks with versions
- Key libraries & dependencies
- Database technologies
- Deployment & environment setup

**Complexity Factors:**
- Real-time features (WebSocket, streaming)
- State management complexity
- Security requirements
- Performance considerations
- Testing requirements

**Output Summary:**
```
**Project Analysis Complete**

**Project:** {{detected_name}}
**Type:** {{codebase/prd/prompt}}
**Stack:** {{main_technologies}}
**Complexity:** {{estimated_size}}
**Functional Areas:** {{count}} areas identified
```

## Phase 2: Story Breakdown Strategy

### Step 3: Determine Story Count & Size

**Calculate optimal story breakdown:**

**Small Project** (< 5000 LOC, 1-3 features):
- Target: 3-5 stories
- Story size: ~1000-1500 tokens implementation context

**Medium Project** (5000-20000 LOC, 3-10 features):
- Target: 6-12 stories
- Story size: ~1500-2000 tokens implementation context

**Large Project** (> 20000 LOC, 10+ features):
- Target: 15+ stories
- Story size: ~2000 tokens implementation context
- Consider grouping related features into single stories

### Step 4: Create Story List

**Break down project into stories following these principles:**

1. **Foundation First:** Setup, configuration, base architecture
2. **Independent Features:** Each major feature as separate story
3. **Integration Points:** Connecting features together
4. **Dependencies Clearly Marked:** Story B depends on Story A

**For each story, define:**
- **Story Number:** Sequential (1, 2, 3...)
- **Title:** Clear, descriptive (e.g., "user-authentication", "database-setup")
- **User Story:** As a [role], I want [action], so that [benefit]
- **Acceptance Criteria:** 2-5 BDD-formatted criteria
- **Dependencies:** Which stories must be completed first (if any)
- **Estimated Complexity:** small/medium/large
- **Technical Context:** Key requirements, libraries, file locations

**Example Story Breakdown:**

```
Story 1: project-setup
- User Story: As a developer, I want project structure initialized, so that I can build features
- Dependencies: None
- Complexity: small

Story 2: database-schema
- User Story: As a system, I need database models defined, so that data can be persisted
- Dependencies: Story 1
- Complexity: medium

Story 3: user-authentication
- User Story: As a user, I want to login securely, so that I can access my account
- Dependencies: Story 2
- Complexity: large

Story 4: api-endpoints
- User Story: As a client, I want REST API endpoints, so that I can interact with the system
- Dependencies: Story 2, Story 3
- Complexity: large
```

## Phase 3: Generate BMAD Artifacts

### Step 5: Detect Project Name

**Auto-detect project name from:**

```bash
1. Try package.json → extract "name" field
2. Try README.md title or first heading
3. Fallback: current directory name
4. Fallback: "project" if nothing found

Set {{PROJECT_NAME}} = detected name (slugified: lowercase, hyphens for spaces)
```

**Examples:**
- `package.json` name: "my-awesome-app" → `@my-awesome-app/stories`
- Directory name: "AgentClick" → `@agentclick/stories`
- README title: "My API" → `@my-api/stories`

### Step 6: Create Output Directory Structure

```
@{{PROJECT_NAME}}/
  stories/
    README.md              <- Overview of all stories (was stories.md)
    status.yaml            <- Story tracking (was sprint-status.yaml)
    1-project-setup.md     <- Story file 1
    2-database-schema.md   <- Story file 2
    3-user-authentication.md
    ...
```

**Create directories if needed:**
```bash
# Create stories directory at project root
mkdir -p "@{{PROJECT_NAME}}/stories"
```

### Step 7: Generate `README.md`

Create `@{{PROJECT_NAME}}/stories/README.md`:

```markdown
# Project Stories

**Project:** {{project_name}}
**Total Stories:** {{total_count}}
**Created:** {{current_date}}
**Status:** backlog

---

## Overview

This document contains all stories for the {{project_name}} project. Stories are numbered in dependency order.

**Implementation Order:** Start with Story 1 and proceed sequentially unless dependencies allow parallel work.

---

## Story 1: {{story_1_title}}

**User Story:**
As a {{role}},
I want {{action}},
so that {{benefit}}.

**Acceptance Criteria:**
1. {{BDD_criterion_1}}
2. {{BDD_criterion_2}}
3. {{BDD_criterion_3}}

**Dependencies:** None

**Estimated Complexity:** {{complexity}}

**Technical Context:**
{{technical_requirements_summary}}

---

## Story 2: {{story_2_title}}

**User Story:**
...

**Dependencies:** Story 1

**Estimated Complexity:** {{complexity}}

**Technical Context:**
...

---

[Continue for all stories]
```

### Step 8: Generate `status.yaml`

Create `@{{PROJECT_NAME}}/stories/status.yaml`:

```yaml
project:
  name: "{{project_name}}"
  total_stories: {{total_count}}
  created_at: {{timestamp}}
  current_story: null

stories:
  1-{{story_1_slug}}: backlog
  2-{{story_2_slug}}: backlog
  3-{{story_3_slug}}: backlog
  # ... continue for all stories

# STATUS DEFINITIONS:
# backlog - Story created, not started
# ready-for-dev - Story context generated, ready for implementation
# in-dev - Currently being implemented
# ready-for-review - Implementation complete, pending review
# done - Story completed and verified
```

### Step 9: Generate Individual Story Files

For each story, create `@{{PROJECT_NAME}}/stories/{num}-{slug}.md`:

```markdown
# Story {{num}}: {{title}}

Status: ready-for-dev

## Story

As a {{role}},
I want {{action}},
so that {{benefit}}.

## Acceptance Criteria

1. {{BDD_criterion_1}}
2. {{BDD_criterion_2}}
3. {{BDD_criterion_3}}

## Tasks / Subtasks

- [ ] Task 1 (AC: #1, #2)
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2 (AC: #3)
  - [ ] Subtask 2.1

## Dev Notes

### Technical Requirements
- **Frameworks/Libraries:** {{list with versions}}
- **Key Features:** {{main functionality}}
- **Configuration:** {{setup requirements}}

### Architecture Alignment
- **File Locations:**
  - {{file_path_1}}
  - {{file_path_2}}
- **Naming Conventions:** {{conventions}}
- **Integration Points:** {{other systems/components}}

### Anti-Patterns to Avoid
- ❌ Don't {{common_mistake_1}}
- ❌ Don't {{common_mistake_2}}
- ❌ Don't reinvent {{existing_solution}}

### References
- [Source: {{document_or_file}}#{{section}}]
- [Related: Story {{related_story_num}}]

## Dev Agent Record

### Agent Model Used
{{model_name_version}}

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
```

**Repeat for each story**, customizing technical details based on project analysis.

## Phase 4: Validation & Quality Check

### Step 9: Verify Story Quality

**Checklist for each story:**

- [ ] **User Story:** Clear "As a, I want, so that" format
- [ ] **Acceptance Criteria:** BDD format (GIVEN/WHEN/THEN implied), testable
- [ ] **Tasks:** Break down into implementable subtasks
- [ ] **Technical Requirements:** Specific libraries, versions, file locations
- [ ] **Dependencies:** Clearly marked, no circular dependencies
- [ ] **Size Estimate:** Implementable in ~2000 tokens of context
- [ ] **Anti-Patterns:** Listed common mistakes to avoid
- [ ] **References:** Linked to source documents or related stories

**Global checks:**

- [ ] All stories numbered sequentially (1, 2, 3...)
- [ ] Dependencies are acyclic (no A→B→A)
- [ ] Foundation stories come first (setup, database, auth)
- [ ] Total story count matches project complexity
- [ ] All files created in correct locations
- [ ] status.yaml formatted correctly

## Phase 5: Output Report

### Step 10: Present Results

```
**🎯 PROJECT SUCCESSFULLY SPLIT INTO BMAD STORIES**

**Project:** {{project_name}}
**Type:** {{codebase/prd/prompt}}
**Total Stories:** {{count}}
**Location:** @{{PROJECT_NAME}}/stories/

---

**📊 Story Breakdown:**

{{#each story}}
{{num}}. **{{title}}**
   - Complexity: {{complexity}}
   - Dependencies: {{dependencies}}
   - Status: backlog

{{/each}}

---

**📁 Generated Files:**

✓ **@{{PROJECT_NAME}}/stories/README.md**
  - Overview of all {{count}} stories
  - User stories and acceptance criteria
  - Dependency graph

✓ **@{{PROJECT_NAME}}/stories/status.yaml**
  - Story tracking and status management
  - Progress monitoring

✓ **@{{PROJECT_NAME}}/stories/{{num}}-{{slug}}.md** ({{count}} files)
  - Detailed implementation guides
  - Technical requirements
  - Anti-patterns and references

---

**🚀 Next Steps:**

1. **Review Stories:**
   - Open `@{{PROJECT_NAME}}/stories/README.md` to review all stories
   - Adjust priorities or dependencies if needed
   - Verify technical requirements are accurate

2. **Start Implementation:**
   - Run `/dev-story 1` to start first story
   - Follow dependency order (Story 1 → Story 2 → Story 3...)
   - Track progress in `@{{PROJECT_NAME}}/stories/status.yaml`

3. **Iterative Development:**
   - Each story is independently implementable
   - Status updates automatically in status.yaml
   - Move to next story when current is marked "done"

**Implementation Commands:**
```bash
# Start first story
/dev-story 1

# Check story status
cat @{{PROJECT_NAME}}/stories/status.yaml

# View all stories
cat @{{PROJECT_NAME}}/stories/README.md
```

---

**💡 Tips:**

- Stories are sized to avoid LLM context overload (~2000 tokens each)
- Each story file contains everything needed for implementation
- Dependencies ensure proper implementation order
- `@{{PROJECT_NAME}}/stories/status.yaml` tracks progress across all stories
- Use `@project-name/stories` pattern for easy navigation
```

## Examples

### Example 1: Analyze Current Codebase
```bash
/split-project codebase .
```

**Output:**
- Scans current directory
- Identifies all source files
- Creates stories based on discovered functionality

### Example 2: Analyze PRD Document
```bash
/split-project prd ./docs/PRD.md
```

**Output:**
- Loads PRD and extracts requirements
- Creates stories for each feature/requirement
- Preserves technical specifications from PRD

### Example 3: From Prompt Description
```bash
/split-project prompt "Create a todo app with user authentication, real-time sync, and mobile app"
```

**Output:**
- Analyzes prompt and extracts implied features
- Creates stories for auth, database, API, mobile, etc.
- Asks clarifying questions if needed

### Example 4: Auto-Detect
```bash
/split-project
```

**Output:**
- Auto-detects project type from current directory
- Falls back to prompting user if unclear
- Creates appropriate stories based on findings

## Important Notes

**Story Size Management:**
- Target ~2000 tokens of implementation context per story
- If a story is too large, split it further
- If a story is too small, consider merging with related story

**Dependency Management:**
- Always mark dependencies explicitly
- Avoid circular dependencies
- Foundation stories (setup, database, auth) typically have no dependencies

**Technical Detail Level:**
- Include specific library versions when known
- Reference actual file paths when analyzing codebase
- List anti-patterns to prevent common mistakes

**BMAD Compliance:**
- Follow BMAD story structure (Story, AC, Tasks, Dev Notes)
- Use `@{{PROJECT_NAME}}/stories/status.yaml` for tracking
- Stories should be ready for `/dev-story` command

---

**End of split-project workflow**
