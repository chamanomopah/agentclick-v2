"""
Tests for the TemplateEngine class.

This test module follows TDD principles and validates:
- Template loading from YAML configuration
- Template retrieval and existence checking
- Template saving and persistence
- Graceful handling of missing templates
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from core.template_engine import TemplateEngine, TemplateError


class TestTemplateEngineInitialization:
    """Test TemplateEngine initialization and configuration loading."""

    def test_init_with_valid_config_path(self):
        """Test initialization with a valid config path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            assert engine is not None
            assert engine.templates_config_path == config_path
        finally:
            os.unlink(config_path)

    def test_init_with_default_config_path(self):
        """Test initialization with default config path."""
        # Test with config/input_templates.yaml
        engine = TemplateEngine()
        assert engine is not None
        assert 'input_templates.yaml' in engine.templates_config_path

    def test_init_loads_templates_on_creation(self):
        """Test that templates are loaded automatically on initialization."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Test: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            assert 'test-agent' in engine._templates
            assert engine._templates['test-agent']['template'] == 'Test: {{input}}'
        finally:
            os.unlink(config_path)

    def test_init_handles_missing_config_file(self):
        """Test graceful handling when config file doesn't exist."""
        engine = TemplateEngine(templates_config_path='nonexistent.yaml')
        assert engine._templates == {}


class TestLoadTemplates:
    """Test template loading from YAML configuration."""

    def test_load_templates_from_valid_yaml(self):
        """Test loading templates from a valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'agent1': {'template': 'Template 1: {{input}}', 'enabled': True},
                    'agent2': {'template': 'Template 2: {{context_folder}}', 'enabled': False}
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            templates = engine._templates
            assert len(templates) == 2
            assert 'agent1' in templates
            assert 'agent2' in templates
            assert templates['agent1']['enabled'] is True
            assert templates['agent2']['enabled'] is False
        finally:
            os.unlink(config_path)

    def test_load_templates_handles_invalid_yaml(self):
        """Test graceful handling of invalid YAML format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            # Should handle gracefully and return empty templates
            assert engine._templates == {}
        finally:
            os.unlink(config_path)

    def test_load_templates_handles_missing_version(self):
        """Test handling of templates without version field."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'templates': {
                    'agent1': {'template': 'Test: {{input}}', 'enabled': True}
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            # Should still load templates even without version
            assert 'agent1' in engine._templates
        finally:
            os.unlink(config_path)

    def test_load_templates_can_be_called_multiple_times(self):
        """Test that load_templates can be called to reload configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'agent1': {'template': 'Test: {{input}}', 'enabled': True}
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)

            # Modify the file
            with open(config_path, 'w') as f:
                config_data['templates']['agent2'] = {'template': 'New: {{input}}', 'enabled': True}
                yaml.dump(config_data, f)

            # Reload templates
            engine.load_templates()
            assert 'agent1' in engine._templates
            assert 'agent2' in engine._templates
        finally:
            os.unlink(config_path)


class TestGetTemplate:
    """Test template retrieval by agent ID."""

    def test_get_template_returns_template_string(self):
        """Test retrieving a template string for a valid agent ID."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Test Template: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            template = engine.get_template('test-agent')
            assert template == 'Test Template: {{input}}'
        finally:
            os.unlink(config_path)

    def test_get_template_returns_none_for_missing_agent(self):
        """Test that get_template returns None for non-existent agent."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            template = engine.get_template('non-existent')
            assert template is None
        finally:
            os.unlink(config_path)

    def test_get_template_returns_none_for_disabled_template(self):
        """Test that get_template returns None for disabled templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'disabled-agent': {
                        'template': 'Test: {{input}}',
                        'enabled': False
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            template = engine.get_template('disabled-agent')
            # Should return None even if template exists but is disabled
            assert template is None
        finally:
            os.unlink(config_path)


class TestHasTemplate:
    """Test template existence checking."""

    def test_has_template_returns_true_for_existing_enabled_template(self):
        """Test that has_template returns True for existing enabled templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Test: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            assert engine.has_template('test-agent') is True
        finally:
            os.unlink(config_path)

    def test_has_template_returns_false_for_missing_template(self):
        """Test that has_template returns False for non-existent templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            assert engine.has_template('non-existent') is False
        finally:
            os.unlink(config_path)

    def test_has_template_returns_false_for_disabled_template(self):
        """Test that has_template returns False for disabled templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'disabled-agent': {
                        'template': 'Test: {{input}}',
                        'enabled': False
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            assert engine.has_template('disabled-agent') is False
        finally:
            os.unlink(config_path)


class TestSaveTemplate:
    """Test template saving and persistence."""

    def test_save_template_adds_new_template(self):
        """Test saving a new template."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            engine.save_template('new-agent', 'New Template: {{input}}')

            # Verify it was added
            assert 'new-agent' in engine._templates
            assert engine._templates['new-agent']['template'] == 'New Template: {{input}}'
            assert engine._templates['new-agent']['enabled'] is True

            # Verify it was persisted to file
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                assert 'new-agent' in config['templates']
        finally:
            os.unlink(config_path)

    def test_save_template_updates_existing_template(self):
        """Test updating an existing template."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Old Template: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            engine.save_template('test-agent', 'Updated Template: {{input}}')

            # Verify it was updated
            assert engine._templates['test-agent']['template'] == 'Updated Template: {{input}}'

            # Verify it was persisted to file
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                assert config['templates']['test-agent']['template'] == 'Updated Template: {{input}}'
        finally:
            os.unlink(config_path)

    def test_save_template_invalidates_cache(self, tmp_path):
        """Test that saving a template invalidates the cache."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)

            # Create template to populate cache
            engine.save_template('test-agent', 'Original: {{input}}')
            engine.apply_template('test-agent', 'input')  # Creates cache entry

            # Verify cache entry exists
            assert 'test-agent' in engine._compiled_cache

            # Save should invalidate cache
            engine.save_template('test-agent', 'Updated: {{input}}')

            # Verify cache was invalidated
            assert 'test-agent' not in engine._compiled_cache

            # Apply again creates new cache entry
            engine.apply_template('test-agent', 'input')
            assert 'test-agent' in engine._compiled_cache
        finally:
            os.unlink(config_path)

    def test_save_template_creates_config_directory_if_needed(self, tmp_path):
        """Test that save_template creates directory if it doesn't exist."""
        non_existent_dir = tmp_path / "subdir" / "input_templates.yaml"
        engine = TemplateEngine(templates_config_path=str(non_existent_dir))

        engine.save_template('test-agent', 'Test: {{input}}')

        # Verify file was created
        assert Path(non_existent_dir).exists()
        assert 'test-agent' in engine._templates


class TestGracefulHandling:
    """Test graceful handling of edge cases (AC: #5)."""

    def test_get_template_returns_none_for_missing_config(self):
        """Test that missing config file is handled gracefully."""
        engine = TemplateEngine(templates_config_path='nonexistent.yaml')
        template = engine.get_template('any-agent')
        assert template is None

    def test_has_template_returns_false_for_missing_config(self):
        """Test that missing config file is handled gracefully."""
        engine = TemplateEngine(templates_config_path='nonexistent.yaml')
        assert engine.has_template('any-agent') is False

    def test_save_template_creates_file_if_missing(self, tmp_path):
        """Test that save_template creates config file if missing."""
        non_existent_file = tmp_path / "new_config.yaml"
        engine = TemplateEngine(templates_config_path=str(non_existent_file))

        engine.save_template('test-agent', 'Test: {{input}}')

        # Verify file was created
        assert Path(non_existent_file).exists()
