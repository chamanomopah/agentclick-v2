# Story 5: Virtual Agent Executor

Status: backlog

## Story

As a system,
I want to execute virtual agents using Claude SDK,
so that agents defined in .md files can process user inputs.

## Acceptance Criteria

1. VirtualAgentExecutor creates ClaudeAgentOptions dynamically from VirtualAgent (system_prompt, tools, MCP servers)
2. Executor applies input template before execution via TemplateEngine
3. Executor sets system_prompt from .md file content loaded by VirtualAgent
4. Executor configures allowed_tools based on agent type (command: basic tools, skill: +custom tools, agent: configurable)
5. Executor returns ExecutionResult with output (str), status (success/error/partial), and metadata (dict)

## Tasks / Subtasks

- [ ] Implement VirtualAgentExecutor class (AC: #1, #2, #3, #5)
  - [ ] Create `core/agent_executor.py`
  - [ ] Implement __init__ with template_engine and default_options parameters
  - [ ] Implement execute(agent, input_text, workspace, focus_file) async method
  - [ ] Return ExecutionResult with proper status

- [ ] Implement SDK options factory (AC: #1, #3, #4)
  - [ ] Implement create_sdk_options(agent, workspace, input_text, focus_file) method
  - [ ] Set system_prompt from agent.load_content()
  - [ ] Set cwd from workspace.folder
  - [ ] Configure allowed_tools based on agent type
  - [ ] Set permission_mode to "acceptEdits"
  - [ ] Configure mcp_servers if agent has custom tools

- [ ] Implement tool mapping logic (AC: #4)
  - [ ] Implement _get_tools_for_agent(agent) method
  - [ ] Define BASE_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob"]
  - [ ] Return BASE_TOOLS for command type
  - [ ] Return BASE_TOOLS + custom tools for skill type
  - [ ] Return configurable tools from metadata for agent type

- [ ] Implement MCP server creation (AC: #1)
  - [ ] Implement _get_mcp_servers(agent) method
  - [ ] Return None for command and agent types (no MCP)
  - [ ] Create MCP server for skill type if custom_tools in metadata
  - [ ] Use create_sdk_mcp_server() from SDK

- [ ] Integrate TemplateEngine (AC: #2)
  - [ ] Call template_engine.apply_template() before execution
  - [ ] Pass input_text, context_folder, focus_file to template engine
  - [ ] Use rendered template as final input for SDK

- [ ] Implement error handling (AC: #5)
  - [ ] Catch SDKConnectionError and set status to "error"
  - [ ] Catch AgentExecutionError and set status to "error"
  - [ ] Set status to "partial" on partial success
  - [ ] Set status to "success" on complete success
  - [ ] Include error details in metadata

- [ ] Create SDK config factory helper (AC: #1)
  - [ ] Create `config/sdk_config_factory.py`
  - [ ] Implement SDKOptionsBuilder class (Builder pattern)
  - [ ] Add with_system_prompt() method
  - [ ] Add with_working_directory() method
  - [ ] Add with_tools() method
  - [ ] Add with_mcp_servers() method
  - [ ] Add build() method returning ClaudeAgentOptions

## Dev Notes

### Technical Requirements
- **Libraries:** claude-agent-sdk, asyncio, typing
- **Key Features:** Factory pattern, Builder pattern, async execution, MCP integration
- **Configuration:** SDK options created dynamically from VirtualAgent

### Architecture Alignment
- **File Locations:**
  - `core/agent_executor.py` - VirtualAgentExecutor class
  - `config/sdk_config_factory.py` - SDKOptionsBuilder helper
  - `models/execution_result.py` - ExecutionResult dataclass
- **Naming Conventions:** snake_case for methods, PascalCase for classes
- **Integration Points:** Template Engine, Dynamic Agent Loader, Workspace Manager

### SDK Options Mapping

| Agent Type | System Prompt | Allowed Tools | MCP Servers |
|------------|---------------|---------------|-------------|
| **Command** | .md content | BASE_TOOLS only | ❌ No |
| **Skill** | .md content | BASE_TOOLS + custom | ✅ Yes (if custom_tools) |
| **Agent** | .md content | Configurable in metadata | ✅ Yes (if specified) |

### Factory Pattern Example
```python
def create_sdk_options(agent, workspace, input_text, focus_file):
    builder = SDKOptionsBuilder()
    builder.with_system_prompt(agent.load_content())
    builder.with_working_directory(workspace.folder)
    builder.with_tools(self._get_tools_for_agent(agent))
    builder.with_mcp_servers(self._get_mcp_servers(agent))
    builder.with_permission_mode("acceptEdits")
    return builder.build()
```

### Anti-Patterns to Avoid
- ❌ Don't hardcode SDK options - create dynamically from agent
- ❌ Don't forget to apply template before execution
- ❌ Don't use synchronous SDK calls - use async/await
- ❌ Don't ignore SDK errors - catch and handle them properly
- ❌ Don't create MCP servers for command types (unnecessary overhead)
- ❌ Don't modify agent metadata during execution (keep it read-only)
- ❌ Don't use deprecated SDK methods - check latest SDK docs

### Performance Targets
- SDK options creation in < 50ms
- Agent execution time depends on SDK (no additional overhead)
- Memory usage should not leak between executions

### Error Handling Strategy
- **SDKConnectionError:** Retry up to 3 times with exponential backoff
- **AgentExecutionError:** Log error and return ExecutionResult(status="error")
- **TemplateError:** Fall back to raw input without template
- **FileNotFoundError:** Log and return error in ExecutionResult

### References
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 4.3: Virtual Agent Executor API]
- [Source: AGENTCLICK_V2_TECHNICAL_SPEC.md#Section 7: Integração com Claude SDK]
- [Related: Story 1 (Core Models), Story 3 (Dynamic Agent Loader), Story 4 (Template Engine)]

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-5-20250929

### Completion Notes
[To be filled during implementation]

### File List
[To be filled during implementation]
