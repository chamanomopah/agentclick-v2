"""
TemplateConfig dataclass for agent prompt templates.

This module defines the configuration for prompt templates used with virtual agents.
Templates allow customization of agent prompts with variables.
"""
from dataclasses import dataclass, field


@dataclass
class TemplateConfig:
    """
    Configuration for a prompt template associated with a virtual agent.

    Templates enable custom prompts with variable substitution. The template
    string can contain placeholders in {variable} format that will be replaced
    with actual values from the variables dictionary.

    Attributes:
        agent_id: ID of the agent this template is for
        template: Template string with {variable} placeholders
        enabled: Whether this template is currently active
        variables: Dictionary of variable names to values

    Built-in Variables:
        The following built-in variables are automatically available:
        - {workspace_name}: Name of the current workspace
        - {agent_name}: Name of the agent
        - {agent_type}: Type of the agent (command/skill/agent)
        - {agent_description}: Description of the agent
        - {user_input}: User's input text
        - {selected_text}: Currently selected text (if any)
        - {clipboard_content}: Content from clipboard (if available)

    Example:
        >>> config = TemplateConfig(
        ...     agent_id="git-commit",
        ...     template="You are {agent_name}. {agent_description}\\n\\nUser input: {user_input}",
        ...     enabled=True,
        ...     variables={"user_input": "Fix bug in login"}
        ... )
        >>> # Template can be rendered by substituting {variable} placeholders
    """
    agent_id: str
    template: str
    enabled: bool
    variables: dict = field(default_factory=dict)
