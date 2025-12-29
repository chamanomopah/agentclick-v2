---
description: Implement BMAD story following TDD red-green-refactor cycle with comprehensive testing
argument-hint: [story-number] [story-path]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Develop BMAD Story (TDD Cycle)

You are implementing a BMAD story following **Test-Driven Development** with strict quality gates.

## Mission Critical

- **TDD CYCLE MANDATORY:** Red → Green → Refactor (NO skipping!)
- **NEVER LIE ABOUT COMPLETION:** Only mark tasks [x] when 100% complete and tested
- **CONTINUOUS EXECUTION:** Don't stop for "milestones" - continue until ALL tasks complete
- **VALIDATION GATES:** Tests MUST pass before marking task complete
- **FOLLOW STORY EXACTLY:** Only implement what's specified in story tasks

## Input Parameters

- **{{STORY_NUMBER}}:** Story number to develop (e.g., "1", "2", "3")
- **{{STORY_PATH}}:** Full path to story file (overrides auto-discovery)

If neither provided: Auto-discover next ready-for-dev story from @project-name/stories/status.yaml

## Phase 1: Story Discovery & Loading

### Step 1: Find Story to Develop

**Option A: Story Path Provided**
```
If {{STORY_PATH}} is provided:
  → Use that path directly
  → Extract story_key from filename
  → Go to Step 2
```

**Option B: Story Number Provided**
```
If {{STORY_NUMBER}} is provided:
  → Search for story file matching pattern: {story_dir}/{{STORY_NUMBER}}-*.md
  → If found, use that file
  → If not found, error and halt
```

**Option C: Auto-Discovery (default)**
```
If no input provided:
  → Detect project name (package.json or directory name)
  → Load @{{PROJECT_NAME}}/stories/status.yaml
  → Read COMPLETE file (all lines, in order)
  → Find FIRST story where:
    - Key pattern: number-name (e.g., "1-user-auth")
    - Status == "ready-for-dev" or "in-progress"
  → If none found, prompt user for story path
  → Extract story_key and load story file
```

**Story File Location:**
```
Default: @{{PROJECT_NAME}}/stories/{{story_key}}.md

Where {{PROJECT_NAME}} is auto-detected from:
  1. package.json → "name" field
  2. README.md → title
  3. Current directory name
```

### Step 2: Load Story Context

**Load COMPLETE story file and extract:**

```markdown
# Story {{num}}: {{title}}

Status: {{current_status}}

## Story
As a {{role}}, I want {{action}}, so that {{benefit}}

## Acceptance Criteria
1. {{BDD_criterion_1}}
2. {{BDD_criterion_2}}
...

## Tasks / Subtasks
- [ ] Task 1 (AC: #1)
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2 (AC: #2)
  - [ ] Subtask 2.1
...

## Dev Notes
### Technical Requirements
- {{libraries, frameworks, versions}}

### Architecture Alignment
- {{file_locations, naming_conventions}}

### Previous Story Context
- {{learnings_from_previous_stories}}

### Anti-Patterns to Avoid
- ❌ {{common_mistakes}}

### References
- {{source_documents}}

## Dev Agent Record
### Agent Model Used
{{model}}

### Completion Notes
[Will be filled during implementation]

### File List
[Will track all changed files]
```

**Critical: Extract Dev Notes completely** - This is your implementation blueprint!

### Step 3: Detect Review Continuation

**Check if resuming after code review:**

```
Does story have "Senior Developer Review (AI)" section?
  YES:
    → Extract review outcome, action items
    → Count unchecked review follow-up tasks
    → Prioritize [AI-Review] marked tasks first
    → Output: "⏯️ Resuming after code review - {{count}} items to address"

  NO:
    → Fresh implementation
    → Output: "🚀 Starting fresh implementation of {{story_key}}"
```

## Phase 2: Sprint Status Update

### Step 4: Mark Story In-Progress

**If @{{PROJECT_NAME}}/stories/status.yaml exists:**

```bash
# Detect project name if not already done
Detect {{PROJECT_NAME}} from package.json or directory

# Load story status
Load @{{PROJECT_NAME}}/stories/status.yaml

# Find story status
Find stories[{{story_key}}]

# Update if needed
If status == "ready-for-dev":
  Update to "in-progress"
  Output: "🚀 Story {{story_key}} status: ready-for-dev → in-progress"

If status == "in-progress":
  Output: "⏯️ Resuming work on {{story_key}}"

Else:
  Output: "⚠️ Unexpected status: {{status}} - continuing anyway"
```

**If no status.yaml:**
```
Output: "ℹ️ No status tracking - tracking in story file only"
```

## Phase 3: TDD Implementation Cycle

### Step 5: Implement Tasks (Red-Green-Refactor)

**For EACH incomplete task/subtask in order:**

```
FOLLOW THE STORY TASKS SEQUENCE EXACTLY - NO DEVIATION
```

#### **RED Phase (Write Failing Tests)**

```bash
# 1. Write tests FIRST (before implementation)
Create test file(s) for the task functionality
Write test cases for:
  - Happy path (expected behavior)
  - Edge cases
  - Error conditions
  - Boundary conditions

# 2. Confirm tests FAIL
Run tests
Verify they fail (validates test correctness)
```

**Test Structure:**
```javascript
// Example: Jest/React
describe('Task Feature', () => {
  it('should handle happy path', () => {
    // Test expected behavior
  })

  it('should handle edge case', () => {
    // Test edge conditions
  })

  it('should throw error for invalid input', () => {
    // Test error handling
  })
})
```

#### **GREEN Phase (Make Tests Pass)**

```bash
# 3. Implement MINIMAL code
Write just enough code to make tests pass
DO NOT add extra features
DO NOT over-engineer

# 4. Run tests - confirm they PASS
Run tests
All tests must pass
```

**Implementation Principles:**
- Follow Dev Notes technical requirements EXACTLY
- Use specified libraries/frameworks/versions
- Follow file structure from Dev Notes
- Adhere to naming conventions
- Avoid anti-patterns listed in Dev Notes

#### **REFACTOR Phase (Improve Code)**

```bash
# 5. Improve code structure (while tests stay green)
Extract reusable functions
Improve naming
Reduce duplication
Enhance readability

# 6. Verify tests still pass
Run full test suite
Ensure no regressions
```

#### **Document Decisions**

```bash
# Add to Dev Agent Record → Implementation Plan:
"Task {{num}}: {{description}}
  Approach: {{technical_approach}}
  Decisions: {{key_decisions}}
  Files: {{files_created/modified}}"
```

### Step 6: Comprehensive Testing

**After implementation, ensure:**

**Unit Tests:**
```bash
✅ Test all business logic
✅ Test all core functionality
✅ Cover edge cases from Dev Notes
✅ Test error conditions
```

**Integration Tests:**
```bash
✅ Test component interactions
✅ Test data flow
✅ Test API integrations (if applicable)
```

**End-to-End Tests:**
```bash
✅ Test critical user flows
✅ Test acceptance criteria scenarios
✅ Test real-world usage patterns
```

**Test Coverage:**
```bash
Run coverage tool
Verify acceptable coverage percentage (check project-context.md for standards)
```

### Step 7: Validation Gates

**Before marking task complete, verify:**

```bash
# 1. Tests exist and pass
Run test suite
All tests MUST pass (100%)

# 2. No regressions
Run full test suite
All existing tests MUST pass

# 3. Code quality
Run linter (if configured)
Run type checker (if configured)
All checks MUST pass

# 4. Acceptance criteria
Verify implementation satisfies ALL AC related to this task
Quantitative thresholds MUST be met (e.g., "response time < 200ms")

# 5. Dev Notes compliance
Followed technical requirements
Used correct libraries/versions
Followed architecture patterns
Avoided anti-patterns
```

**IF ANY VALIDATION FAILS:**
```bash
→ DO NOT mark task complete
→ Fix the issue
→ Re-run validations
→ Only proceed when ALL pass
```

### Step 8: Mark Task Complete

**ONLY when ALL validation gates pass:**

```bash
# 1. Mark task checkboxes [x] in story file
Update Tasks/Subtasks section:
  - [x] Task (AC: #)
    - [x] Subtask 1
    - [x] Subtask 2

# 2. Update File List
Add ALL new/modified/deleted files:
  File List:
    - src/components/AuthForm.tsx (created)
    - src/lib/auth/utils.ts (created)
    - src/app/api/auth/route.ts (modified)

# 3. Add completion notes
Dev Agent Record → Completion Notes:
  "✅ Task {{num}} complete:
   - Implemented {{feature}}
   - Tests: {{test_count}} passing
   - Files: {{files_count}} changed
   - AC satisfied: #1, #2"

# 4. Handle review follow-ups (if applicable)
If task has [AI-Review] prefix:
  → Mark in "Review Follow-ups (AI)" section
  → Mark corresponding item in "Senior Developer Review (AI)" section
  → Add to resolution notes

# 5. Save story file
# 6. Check if more tasks remain
If yes:
  → Go to Step 5 (next task)
If no:
  → Go to Step 9 (completion)
```

**CRITICAL: NEVER mark task complete unless:**
✅ All tests exist and pass
✅ No regressions
✅ Code quality checks pass
✅ Acceptance criteria satisfied
✅ File list updated
✅ Completion notes added

## Phase 4: Story Completion

### Step 9: Definition of Done Validation

**When all tasks are complete:**

```bash
# Verify completion
Re-scan story file - ALL tasks must be [x]

# Run full test suite
Execute ALL tests - must pass 100%

# Validate Definition of Done checklist:
```

**DoD Checklist:**

```
## ✅ Context & Requirements
- [ ] Dev Notes contain all technical requirements
- [ ] Architecture compliance verified
- [ ] Technical specifications met
- [ ] Previous story learnings applied

## ✅ Implementation
- [ ] ALL tasks marked [x]
- [ ] ALL acceptance criteria satisfied
- [ ] No ambiguous implementations
- [ ] Edge cases handled
- [ ] Only specified dependencies used

## ✅ Testing
- [ ] Unit tests added for all core functionality
- [ ] Integration tests added for component interactions
- [ ] End-to-end tests added for critical flows
- [ ] Test coverage meets requirements
- [ ] ALL tests pass (no regressions)
- [ ] Code quality checks pass
- [ ] Test framework compliance verified

## ✅ Documentation
- [ ] File list complete (all changed files)
- [ ] Dev Agent Record updated
- [ ] Change Log updated
- [ ] Only permitted sections modified

## ✅ Final Status
- [ ] Story Status set to "review"
- [ ] Sprint Status updated to "review"
- [ ] Quality gates passed
- [ ] No blocking issues
- [ ] User communication ready
```

**IF ANY DoD ITEM FAILS:**
```bash
→ HALT - Do not mark story complete
→ Fix the issue
→ Re-validate
→ Only proceed when DoD 100% satisfied
```

### Step 10: Mark Story Ready for Review

**When DoD validation passes:**

```bash
# 1. Update story Status
Change: Status: in-progress → Status: review

# 2. Update @project-name/stories/status.yaml (if exists)
Load @project-name/stories/status.yaml
Update development_status[{{story_key}}] = "review"
Save file

# 3. Verify all artifacts
Story file has all sections complete
File list includes every changed file
Dev Agent Record has completion notes
```

## Phase 5: Completion Report

### Step 11: Communicate Completion

```bash
Output completion summary:

**✅ STORY IMPLEMENTATION COMPLETE**

**Story:** {{story_num}} - {{title}}
**Status:** ready-for-review
**File:** {{story_file_path}}

**Implementation Summary:**
- Tasks completed: {{count}}
- Acceptance criteria satisfied: {{count}}/{{total}}
- Tests added: {{count}}
- Files modified: {{count}}
- Lines of code: {{count}}

**Changed Files:**
{{list all files from File List section}}

**Test Results:**
✅ All tests passing ({{count}}/{{count}})
✅ No regressions
✅ Code quality checks passed

**Next Steps:**
1. Review implemented story and test changes
2. Verify all acceptance criteria are met
3. Run code-review workflow for peer review
4. Deploy when ready

**Story file:** {{story_file_path}}
**Story status:** @{{PROJECT_NAME}}/stories/status.yaml
```

### Step 12: User Support

**Ask user if they need explanations:**

```bash
Based on user skill level, offer explanations about:
  - What was implemented and how it works
  - Why certain technical decisions were made
  - How to test or verify the changes
  - Patterns, libraries, or approaches used
  - Anything else they'd like clarified
```

**Provide recommendations:**

```bash
**Recommended Next Steps:**
1. Test the implemented features
2. Review the story file for completeness
3. Run code-review workflow (use different LLM for best results)
4. Check @project-name/stories/status.yaml for project progress
5. Deploy to staging/production when ready
```

## Critical Rules

### **MUST DO:**
✅ Follow TDD: Red → Green → Refactor (every task)
✅ Write tests BEFORE implementation
✅ Only mark tasks [x] when 100% complete
✅ Run full test suite after each task
✅ Follow Dev Notes exactly
✅ Update File List with all changes
✅ Document decisions in Dev Agent Record
✅ Continue until ALL tasks complete

### **MUST NOT DO:**
❌ Skip tests or write them after implementation
❌ Mark tasks complete before validation passes
❌ Implement features not in story tasks
❌ Stop at "milestones" - continue until done
❌ Lie about completion or fake task completion
❌ Modify story sections outside permitted areas
❌ Ignore Dev Notes requirements

### **Permitted Story File Modifications:**
- Tasks/Subtasks checkboxes ([ ] → [x])
- Dev Agent Record sections
- File List section
- Change Log section
- Status field (in-progress → review)

### **HALT Conditions:**
```bash
→ 3 consecutive implementation failures
→ Required configuration missing
→ New dependencies needed (beyond story spec)
→ Unable to fix validation failures
→ User intervention required
```

## Example Usage

```bash
# Auto-discover next ready-for-dev story
/dev-story

# Develop specific story by number
/dev-story 1

# Develop specific story by path
/dev-story "@my-project/stories/1-user-auth.md"
```

## Testing Commands Reference

**Common test frameworks:**

```bash
# JavaScript/TypeScript
npm test                    # Jest
npm run test                # Mocha/Jasmine
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:coverage       # With coverage report

# Python
pytest                      # Pytest
python -m pytest            # Pytest
python -m unittest          # unittest
coverage run -m pytest      # With coverage

# Run linting
npm run lint                # ESLint
npm run lint:fix            # Auto-fix
ruff check .                # Python ruff
black .                     # Python formatter

# Type checking
npm run type-check          # TypeScript
mypy .                      # Python mypy
```

## Workflow Summary

```
1. Discover story (auto or explicit)
2. Load story context and Dev Notes
3. Detect if resuming after review
4. Mark story in-progress
5. FOR EACH TASK:
   a. RED: Write failing tests
   b. GREEN: Implement minimal code
   c. REFACTOR: Improve structure
   d. Validate: Tests pass, no regressions
   e. Mark task [x] (only when 100% done)
6. When all tasks complete: Validate DoD
7. Mark story ready for review
8. Report completion to user
9. Provide next steps
```

---

**End of dev-story workflow**

Remember: Quality over speed. Never cut corners on testing or validation.
