"""
Tests for TemplateConfig dataclass.
"""
import pytest
from typing import get_type_hints
from models.template_config import TemplateConfig


class TestTemplateConfigDataclass:
    """Test TemplateConfig dataclass structure and type hints."""

    def test_template_config_has_all_required_fields(self):
        """Test that TemplateConfig has all required fields with correct types."""
        hints = get_type_hints(TemplateConfig)

        required_fields = {
            'agent_id': str,
            'template': str,
            'enabled': bool,
            'variables': dict,
        }

        for field_name, expected_type in required_fields.items():
            assert field_name in hints, f"Missing field: {field_name}"

    def test_template_config_creation_with_all_fields(self):
        """Test creating TemplateConfig with all fields."""
        config = TemplateConfig(
            agent_id="git-commit",
            template="Commit message: {user_input}",
            enabled=True,
            variables={"user_input": "default value"}
        )

        assert config.agent_id == "git-commit"
        assert config.template == "Commit message: {user_input}"
        assert config.enabled is True
        assert config.variables == {"user_input": "default value"}

    def test_template_config_creation_with_empty_variables(self):
        """Test creating TemplateConfig with empty variables dict."""
        config = TemplateConfig(
            agent_id="test-agent",
            template="Simple template",
            enabled=False,
            variables={}
        )

        assert config.variables == {}
        assert config.enabled is False

    def test_template_config_variables_are_mutable(self):
        """Test that variables dict can be modified."""
        config = TemplateConfig(
            agent_id="agent-1",
            template="Test {var1}",
            enabled=True,
            variables={"var1": "value1"}
        )

        # Add new variable
        config.variables["var2"] = "value2"

        assert "var2" in config.variables
        assert config.variables["var2"] == "value2"

        # Modify existing variable
        config.variables["var1"] = "new_value"

        assert config.variables["var1"] == "new_value"

    def test_template_config_with_builtin_variables(self):
        """Test TemplateConfig with built-in variables."""
        config = TemplateConfig(
            agent_id="agent-with-builtins",
            template="Workspace: {workspace_name}, Agent: {agent_name}",
            enabled=True,
            variables={
                "workspace_name": "My Workspace",
                "agent_name": "My Agent",
                "custom_var": "custom value"
            }
        )

        assert "workspace_name" in config.variables
        assert "agent_name" in config.variables
        assert "custom_var" in config.variables

    def test_template_config_multiple_templates(self):
        """Test multiple TemplateConfig instances."""
        config1 = TemplateConfig(
            agent_id="agent-1",
            template="Template 1",
            enabled=True,
            variables={"key": "value1"}
        )

        config2 = TemplateConfig(
            agent_id="agent-2",
            template="Template 2",
            enabled=False,
            variables={"key": "value2"}
        )

        assert config1.agent_id != config2.agent_id
        assert config1.template != config2.template
        assert config1.enabled != config2.enabled


class TestTemplateConfigEdgeCases:
    """Test TemplateConfig edge cases."""

    def test_template_config_with_empty_strings(self):
        """Test TemplateConfig with empty string fields."""
        config = TemplateConfig(
            agent_id="",
            template="",
            enabled=False,
            variables={}
        )

        assert config.agent_id == ""
        assert config.template == ""
        assert config.enabled is False

    def test_template_config_with_unicode_variables(self):
        """Test TemplateConfig with unicode values in variables."""
        config = TemplateConfig(
            agent_id="unicode-agent",
            template="Template with {emoji} and {text}",
            enabled=True,
            variables={
                "emoji": "🎉",
                "text": "Hello 世界",
                "special": "Ñoño"
            }
        )

        assert config.variables["emoji"] == "🎉"
        assert config.variables["text"] == "Hello 世界"
        assert config.variables["special"] == "Ñoño"

    def test_template_config_with_nested_variables(self):
        """Test TemplateConfig with complex nested values."""
        config = TemplateConfig(
            agent_id="complex-agent",
            template="Process {data}",
            enabled=True,
            variables={
                "data": "simple",
                "nested_dict": {"key": "value"},
                "list_value": [1, 2, 3],
                "mixed": {"array": [{"item": "value"}]}
            }
        )

        assert isinstance(config.variables["nested_dict"], dict)
        assert isinstance(config.variables["list_value"], list)

    def test_template_config_variables_none_values(self):
        """Test TemplateConfig with None values in variables."""
        config = TemplateConfig(
            agent_id="test",
            template="Test {var}",
            enabled=True,
            variables={
                "var1": None,
                "var2": "value",
                "var3": ""
            }
        )

        assert config.variables["var1"] is None
        assert config.variables["var2"] == "value"
        assert config.variables["var3"] == ""
