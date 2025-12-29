"""
Template Engine for Agent Input Formatting.

This module provides the TemplateEngine class which handles loading, validating,
and applying input templates for agent execution. Templates use variable
substitution with {{variable}} syntax.
"""

import yaml
import re
import logging
from pathlib import Path
from string import Template
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .exceptions import TemplateError, TemplateSyntaxError, TemplateValidationError


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of template validation.

    Attributes:
        is_valid: Whether the template passed validation
        errors: List of error messages
        warnings: List of warning messages
    """
    is_valid: bool
    errors: list[str]
    warnings: list[str]

    def __post_init__(self):
        """Initialize is_valid based on errors."""
        if self.errors:
            self.is_valid = False
        else:
            self.is_valid = True


class TemplateEngine:
    """
    Engine for managing and applying input templates.

    The TemplateEngine loads templates from a YAML configuration file,
    validates template syntax, and applies templates by substituting
    variables. It handles missing templates gracefully by returning
    the original input unchanged.

    Attributes:
        templates_config_path: Path to the YAML configuration file
        _templates: Internal cache of loaded templates
        _compiled_cache: Cache of compiled template objects

    Example:
        >>> engine = TemplateEngine()
        >>> rendered = engine.apply_template('verify-python', 'Check this code',
        ...                                  {'context_folder': '/path', 'focus_file': 'main.py'})
    """

    def __init__(self, templates_config_path: Optional[str] = None):
        """
        Initialize the TemplateEngine.

        Args:
            templates_config_path: Path to the YAML configuration file.
                                 If None, uses 'config/input_templates.yaml'.

        Example:
            >>> engine = TemplateEngine()
            >>> engine = TemplateEngine(templates_config_path='custom/path/templates.yaml')
        """
        if templates_config_path is None:
            # Use default path relative to current directory
            self.templates_config_path = 'config/input_templates.yaml'
        else:
            self.templates_config_path = templates_config_path

        self._templates: Dict[str, Dict[str, Any]] = {}
        self._compiled_cache: Dict[str, Template] = {}
        # Define allowed variables for extensibility
        self._known_vars = {'input', 'context_folder', 'focus_file'}

        # Load templates on initialization
        self.load_templates()

    def load_templates(self) -> None:
        """
        Load templates from the YAML configuration file.

        This method reads the YAML file and populates the internal templates
        dictionary. It handles missing files and invalid YAML gracefully.

        Example:
            >>> engine = TemplateEngine()
            >>> engine.load_templates()  # Reload templates from disk
        """
        config_path = Path(self.templates_config_path)

        # Handle missing config file gracefully
        if not config_path.exists():
            logger.debug(f"Template config file not found: {config_path}")
            self._templates = {}
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if config is None:
                logger.debug(f"Template config file is empty: {config_path}")
                self._templates = {}
                return

            # Extract templates from config
            templates = config.get('templates', {})
            self._templates = templates if templates else {}

            # Validate loaded templates
            for agent_id, template_config in templates.items():
                if isinstance(template_config, dict) and 'template' in template_config:
                    validation = self.validate_template(template_config['template'])
                    if not validation.is_valid:
                        logger.warning(f"Invalid template for {agent_id}: {validation.errors}")

        except (yaml.YAMLError, IOError) as e:
            # Handle YAML parsing errors gracefully
            logger.error(f"Failed to load templates from {config_path}: {e}")
            self._templates = {}

    def get_template(self, agent_id: str) -> Optional[str]:
        """
        Get the template string for a specific agent.

        Args:
            agent_id: The ID of the agent (e.g., 'verify-python', 'diagnose')

        Returns:
            The template string if found and enabled, None otherwise.

        Example:
            >>> engine = TemplateEngine()
            >>> template = engine.get_template('verify-python')
            >>> if template:
            ...     print(template)
        """
        template_config = self._templates.get(agent_id)

        if template_config is None:
            return None

        # Check if template is enabled
        if not template_config.get('enabled', True):
            return None

        # Return the template string
        return template_config.get('template')

    def has_template(self, agent_id: str) -> bool:
        """
        Check if a template exists for a specific agent.

        Args:
            agent_id: The ID of the agent

        Returns:
            True if the template exists and is enabled, False otherwise.

        Example:
            >>> engine = TemplateEngine()
            >>> if engine.has_template('verify-python'):
            ...     print("Template found")
        """
        template_config = self._templates.get(agent_id)

        if template_config is None:
            return False

        # Template must be enabled to be considered available
        return template_config.get('enabled', True)

    def save_template(self, agent_id: str, template: str, enabled: bool = True) -> None:
        """
        Save or update a template for an agent.

        This method updates the internal templates cache and persists
        the changes to the YAML configuration file. It creates the
        configuration file and directory if they don't exist.

        Args:
            agent_id: The ID of the agent
            template: The template string with {{variable}} placeholders
            enabled: Whether the template is enabled (default: True)

        Example:
            >>> engine = TemplateEngine()
            >>> engine.save_template('my-agent', 'Process: {{input}}', enabled=True)

        Raises:
            TemplateValidationError: If template syntax is invalid
            IOError: If unable to write to the configuration file
        """
        # Validate template before saving (AC: #3)
        validation_result = self.validate_template(template)
        if not validation_result.is_valid:
            raise TemplateValidationError(
                f"Invalid template for {agent_id}: " + "\n".join(validation_result.errors)
            )

        # Update internal cache
        self._templates[agent_id] = {
            'template': template,
            'enabled': enabled
        }

        # Invalidate compiled cache for this agent
        if agent_id in self._compiled_cache:
            del self._compiled_cache[agent_id]

        # Persist to file
        config_path = Path(self.templates_config_path)

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError):
                config = {}
        else:
            config = {}

        # Ensure structure
        if 'templates' not in config:
            config['templates'] = {}

        # Update config
        config['templates'][agent_id] = {
            'template': template,
            'enabled': enabled
        }

        # Write to file
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def apply_template(self, agent_id: str, input_text: str,
                      variables: Optional[Dict[str, str]] = None) -> str:
        """
        Apply a template to format input text with variable substitution.

        This method retrieves the template for the specified agent and
        substitutes {{variable}} placeholders with provided values.
        If the template is not found, it returns the original input unchanged.

        Args:
            agent_id: The ID of the agent
            input_text: The input text to format
            variables: Dictionary of variable names to values
                      (e.g., {'context_folder': '/path', 'focus_file': 'main.py'})

        Returns:
            The formatted input string with variables substituted.

        Example:
            >>> engine = TemplateEngine()
            >>> result = engine.apply_template(
            ...     'verify-python',
            ...     'Check this code',
            ...     {'context_folder': '/my/project', 'focus_file': 'main.py'}
            ... )
        """
        template_str = self.get_template(agent_id)

        # Return original input if template not found (AC: #5)
        if template_str is None:
            return input_text

        # Initialize variables dict if None
        if variables is None:
            variables = {}

        # Add input to variables
        template_vars = {'input': input_text}
        template_vars.update(variables)

        # Get or create compiled template (with caching)
        if agent_id not in self._compiled_cache:
            # Convert {{var}} to $var for string.Template
            template_str_converted = template_str.replace('{{', '$').replace('}}', '')
            self._compiled_cache[agent_id] = Template(template_str_converted)

        compiled_template = self._compiled_cache[agent_id]

        # Apply template with missing variable handling
        try:
            return compiled_template.safe_substitute(template_vars)
        except (KeyError, ValueError) as e:
            # Log warning and return original input
            logger.warning(f"Template substitution failed for {agent_id}: {e}")
            return input_text

    def validate_template(self, template: str) -> ValidationResult:
        """
        Validate template syntax and detect common errors.

        This method checks for:
        - Unclosed {{ }} brackets
        - Unknown variable names (optional)

        Args:
            template: The template string to validate

        Returns:
            ValidationResult with errors and warnings lists.

        Example:
            >>> engine = TemplateEngine()
            >>> result = engine.validate_template('Test: {{input}}')
            >>> if result.is_valid:
            ...     print("Template is valid")
        """
        errors = []
        warnings = []

        # Check for unclosed brackets
        open_count = template.count('{{')
        close_count = template.count('}}')

        if open_count != close_count:
            if open_count > close_count:
                errors.append(f"Unclosed brackets: {open_count - close_count} '{{{{' not matched with '}}}}'")
            else:
                errors.append(f"Extra closing brackets: {close_count - open_count} '}}}}' without matching '{{{{'")

        # Extract variable names
        var_pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(var_pattern, template)

        # Check for unknown variables (warning only)
        unknown_vars = set(variables) - self._known_vars

        if unknown_vars:
            warnings.append(f"Unknown variables: {', '.join(sorted(unknown_vars))}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def preview_template(self, agent_id: str, sample_vars: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Preview the rendered template with sample data.

        This method renders the template with sample variable values
        to show how the output will look.

        Args:
            agent_id: The ID of the agent
            sample_vars: Optional custom sample variables.
                        If not provided, uses default sample data.

        Returns:
            The rendered preview string, or None if template not found.

        Example:
            >>> engine = TemplateEngine()
            >>> preview = engine.preview_template('verify-python')
            >>> print(preview)
        """
        # Check if template exists first
        if not self.has_template(agent_id):
            return None

        # Use default sample data if not provided
        if sample_vars is None:
            sample_vars = {
                'input': '<sample input>',
                'context_folder': 'C:/example',
                'focus_file': 'main.py'
            }

        # Apply template with sample data
        return self.apply_template(agent_id, sample_vars.get('input', ''), sample_vars)
