# Story 4: Template Engine

Status: backlog

## Story

As a user,
I want to customize input templates with variables,
so that I can format inputs consistently for each agent.

## Acceptance Criteria

1. TemplateEngine loads templates from `config/input_templates.yaml` with proper YAML parsing
2. TemplateEngine applies templates by replacing variables: {{input}}, {{context_folder}}, {{focus_file}}
3. TemplateEngine validates template syntax before saving (detects unclosed brackets, unknown variables)
4. TemplateEngine provides preview of rendered template with sample data
5. TemplateEngine gracefully handles missing templates (returns input unchanged without error)

## Tasks / Subtasks

- [ ] Implement TemplateEngine class (AC: #1, #5)
  - [ ] Create `core/template_engine.py`
  - [ ] Implement __init__ with templates_config_path parameter
  - [ ] Implement load_templates() method
  - [ ] Implement get_template(agent_id) method
  - [ ] Implement has_template(agent_id) method
  - [ ] Implement save_template(agent_id, template) method

- [ ] Implement template rendering (AC: #2)
  - [ ] Implement apply_template(agent_id, input_text, variables) method
  - [ ] Use string.Template or Jinja2 for variable substitution
  - [ ] Handle missing variables gracefully (leave as-is or replace with empty string)
  - [ ] Return original input if template not found (AC: #5)

- [ ] Implement template validation (AC: #3)
  - [ ] Create validate_template(template) method
  - [ ] Check for unclosed {{ }} brackets
  - [ ] Check for unknown variable names
  - [ ] Return ValidationResult with errors/warnings
  - [ ] Provide helpful error messages

- [ ] Implement template preview (AC: #4)
  - [ ] Implement preview_template(agent_id, sample_vars) method
  - [ ] Use sample data: input="<sample input>", context_folder="C:/example", focus_file="main.py"
  - [ ] Return rendered preview string

- [ ] Add template caching (Performance optimization)
  - [ ] Compile templates and cache compiled version
  - [ ] Implement cache_key based on agent_id
  - [ ] Invalidate cache on template change

- [ ] Create default input_templates.yaml (AC: #1)
  - [ ] Create `config/input_templates.yaml`
  - [ ] Define templates for common agents: verify-python, diagnose, ux-ui-improver
  - [ ] Set version "2.0"

- [ ] Create template exceptions
  - [ ] Define TemplateError base exception
  - [ ] Define TemplateSyntaxError exception
  - [ ] Define TemplateValidationError exception

## Dev Notes

### Technical Requirements
- **Libraries:** string.Template (stdlib) or Jinja2 (optional), re (for validation)
- **Key Features:** Variable substitution, template validation, caching
- **Configuration:** config/input_templates.yaml with version "2.0"

### Architecture Alignment
- **File Locations:**
  - `core/template_engine.py` - TemplateEngine class
  - `config/input_templates.yaml` - Template definitions
  - `core/exceptions.py` - Template exceptions
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Virtual Agent Executor (applies templates before execution), Config UI (template editor)

### Template Format
```yaml
version: "2.0"
templates:
  verify-python:
    template: |
      Arquivo: {{input}}
      Contexto: {{context_folder}}
      Focus: {{focus_file}}
    enabled: true

  diagnose:
    template: |
      Problema: {{input}}
      Analisar: {{context_folder}}
    enabled: true
```

### Built-in Variables
- `{{input}}` - User input (text, file content, URL content, etc.)
- `{{context_folder}}` - Current workspace folder path
- `{{focus_file}}` - Currently focused file (optional, may be empty)

### Anti-Patterns to Avoid
- ❌ Don't use complex logic in templates (keep them simple)
- ❌ Don't crash on missing variables - handle gracefully
- ❌ Don't allow template injection attacks (sanitize if needed)
- ❌ Don't forget to cache compiled templates for performance
- ❌ Don't use Jinja2 unless absolutely necessary (string.Template is simpler and safer)
- ❌ Don't hardcode variable names - make them extensible

### Performance Targets
- Template rendering in < 10ms
- Template validation in < 5ms
- Cache hit rate > 90%

### References
- [Source: AGENTCLICK_V2_PRD.md#Section: Input Templates]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 4.4: Template Engine API]
- [Related: Story 1 (Core Models), Story 5 (Virtual Agent Executor)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
