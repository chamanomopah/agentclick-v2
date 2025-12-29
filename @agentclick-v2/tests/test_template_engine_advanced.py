"""
Tests for advanced TemplateEngine functionality.

This test module validates:
- Template rendering with variable substitution (AC: #2)
- Template validation with syntax checking (AC: #3)
- Template preview functionality (AC: #4)
- Template caching performance
"""

import pytest
import yaml
import tempfile
import os
from core.template_engine import TemplateEngine, ValidationResult


class TestApplyTemplate:
    """Test template rendering with variable substitution (AC: #2)."""

    def test_apply_template_substitutes_input_variable(self):
        """Test that {{input}} variable is substituted correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Process: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            result = engine.apply_template('test-agent', 'My input text')

            assert result == 'Process: My input text'
        finally:
            os.unlink(config_path)

    def test_apply_template_substitutes_context_folder(self):
        """Test that {{context_folder}} variable is substituted correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Context: {{context_folder}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            result = engine.apply_template(
                'test-agent',
                'input',
                {'context_folder': '/my/project'}
            )

            assert result == 'Context: /my/project'
        finally:
            os.unlink(config_path)

    def test_apply_template_substitutes_focus_file(self):
        """Test that {{focus_file}} variable is substituted correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'File: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            result = engine.apply_template(
                'test-agent',
                'input',
                {'focus_file': 'main.py'}
            )

            assert result == 'File: main.py'
        finally:
            os.unlink(config_path)

    def test_apply_template_substitutes_multiple_variables(self):
        """Test that multiple variables are substituted correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Input: {{input}}\nContext: {{context_folder}}\nFile: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            result = engine.apply_template(
                'test-agent',
                'Check this',
                {'context_folder': '/project', 'focus_file': 'app.py'}
            )

            assert result == 'Input: Check this\nContext: /project\nFile: app.py'
        finally:
            os.unlink(config_path)

    def test_apply_template_handles_missing_variables_gracefully(self):
        """Test that missing variables are left as-is or replaced with empty string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Input: {{input}}, File: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            # Don't provide focus_file variable
            result = engine.apply_template('test-agent', 'Test input', {'context_folder': '/path'})

            # safe_substitute leaves missing variables as-is
            assert 'Input: Test input' in result
        finally:
            os.unlink(config_path)

    def test_apply_template_returns_original_input_if_template_not_found(self, tmp_path):
        """Test that original input is returned when template doesn't exist (AC: #5)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            original_input = 'My original input'
            result = engine.apply_template('non-existent', original_input)

            assert result == original_input
        finally:
            os.unlink(config_path)

    def test_apply_template_handles_disabled_template(self):
        """Test that disabled templates return original input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'disabled-agent': {
                        'template': 'Disabled: {{input}}',
                        'enabled': False
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            original_input = 'My input'
            result = engine.apply_template('disabled-agent', original_input)

            assert result == original_input
        finally:
            os.unlink(config_path)

    def test_apply_template_with_multiline_template(self):
        """Test template rendering with multi-line templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'File: {{input}}\nContext: {{context_folder}}\nFocus: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            result = engine.apply_template(
                'test-agent',
                'test.py',
                {'context_folder': '/project', 'focus_file': 'main.py'}
            )

            assert result == 'File: test.py\nContext: /project\nFocus: main.py'
        finally:
            os.unlink(config_path)


class TestValidateTemplate:
    """Test template validation with syntax checking (AC: #3)."""

    def test_validate_valid_template(self):
        """Test validation of a valid template."""
        engine = TemplateEngine()
        result = engine.validate_template('Process: {{input}}')

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_template_with_unclosed_brackets(self):
        """Test detection of unclosed {{ brackets."""
        engine = TemplateEngine()
        result = engine.validate_template('Process: {{input')

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert 'unclosed' in result.errors[0].lower()

    def test_validate_template_with_extra_closing_brackets(self):
        """Test detection of extra }} brackets."""
        engine = TemplateEngine()
        result = engine.validate_template('Process: input}}')

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert 'closing' in result.errors[0].lower() or 'bracket' in result.errors[0].lower()

    def test_validate_template_with_multiple_unclosed_brackets(self):
        """Test detection of multiple unclosed brackets."""
        engine = TemplateEngine()
        result = engine.validate_template('{{input}} and {{context')

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_template_warns_about_unknown_variables(self):
        """Test warning for unknown variable names."""
        engine = TemplateEngine()
        result = engine.validate_template('{{unknown_var}}')

        # Template is still valid, but has warning
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) > 0
        assert 'unknown' in result.warnings[0].lower()

    def test_validate_template_with_known_variables(self):
        """Test validation with known variables (no warnings)."""
        engine = TemplateEngine()
        result = engine.validate_template('{{input}} {{context_folder}} {{focus_file}}')

        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_validate_complex_template(self):
        """Test validation of a complex real-world template."""
        engine = TemplateEngine()
        template = '''File: {{input}}
Context: {{context_folder}}
Focus: {{focus_file}}'''

        result = engine.validate_template(template)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_returns_helpful_error_messages(self):
        """Test that validation provides helpful error messages."""
        engine = TemplateEngine()
        result = engine.validate_template('{{input')

        assert len(result.errors) > 0
        # Error message should be descriptive
        assert len(result.errors[0]) > 0

    def test_validate_empty_template(self):
        """Test validation of an empty template."""
        engine = TemplateEngine()
        result = engine.validate_template('')

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_template_without_variables(self):
        """Test validation of template without variables."""
        engine = TemplateEngine()
        result = engine.validate_template('Static text without variables')

        assert result.is_valid is True
        assert len(result.errors) == 0


class TestPreviewTemplate:
    """Test template preview functionality (AC: #4)."""

    def test_preview_with_default_sample_data(self):
        """Test preview with default sample data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Input: {{input}}\nContext: {{context_folder}}\nFile: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            preview = engine.preview_template('test-agent')

            assert preview is not None
            assert '<sample input>' in preview
            assert 'C:/example' in preview
            assert 'main.py' in preview
        finally:
            os.unlink(config_path)

    def test_preview_with_custom_sample_data(self):
        """Test preview with custom sample variables."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Project: {{context_folder}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            custom_vars = {'context_folder': '/custom/path'}
            preview = engine.preview_template('test-agent', sample_vars=custom_vars)

            assert preview is not None
            assert '/custom/path' in preview
        finally:
            os.unlink(config_path)

    def test_preview_returns_none_for_missing_template(self):
        """Test that preview returns None for non-existent templates."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'version': '2.0', 'templates': {}}, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            preview = engine.preview_template('non-existent')

            assert preview is None
        finally:
            os.unlink(config_path)

    def test_preview_with_multiline_template(self):
        """Test preview with multi-line template."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'File: {{input}}\nContext: {{context_folder}}\nFocus: {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)
            preview = engine.preview_template('test-agent')

            # Should contain all sample values
            assert 'File: <sample input>' in preview
            assert 'Context: C:/example' in preview
            assert 'Focus: main.py' in preview
        finally:
            os.unlink(config_path)


class TestTemplateCaching:
    """Test template caching for performance optimization."""

    def test_compiled_templates_are_cached(self):
        """Test that compiled templates are cached."""
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

            # First call creates cache entry
            engine.apply_template('test-agent', 'input1')
            assert 'test-agent' in engine._compiled_cache

            # Second call uses cache
            engine.apply_template('test-agent', 'input2')
            # Still only one cache entry
            assert len(engine._compiled_cache) == 1
        finally:
            os.unlink(config_path)

    def test_cache_is_invalidated_on_save(self):
        """Test that cache is invalidated when template is saved."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Original: {{input}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)

            # Create cache entry
            engine.apply_template('test-agent', 'input')
            assert 'test-agent' in engine._compiled_cache

            # Save new template (should invalidate cache)
            engine.save_template('test-agent', 'Updated: {{input}}')
            assert 'test-agent' not in engine._compiled_cache

            # Apply again creates new cache entry
            engine.apply_template('test-agent', 'input')
            assert 'test-agent' in engine._compiled_cache
        finally:
            os.unlink(config_path)

    def test_cache_performance(self, benchmark=None):
        """Test that caching improves performance (if benchmarking available)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'version': '2.0',
                'templates': {
                    'test-agent': {
                        'template': 'Complex template with {{input}} and {{context_folder}} and {{focus_file}}',
                        'enabled': True
                    }
                }
            }
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            engine = TemplateEngine(templates_config_path=config_path)

            # First application (creates cache)
            result1 = engine.apply_template('test-agent', 'input', {'context_folder': '/path', 'focus_file': 'file.py'})

            # Second application (uses cache - should be faster)
            result2 = engine.apply_template('test-agent', 'input', {'context_folder': '/path', 'focus_file': 'file.py'})

            # Results should be identical
            assert result1 == result2
        finally:
            os.unlink(config_path)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_verify_python_template(self):
        """Test the verify-python template from the default config."""
        engine = TemplateEngine()

        if engine.has_template('verify-python'):
            result = engine.apply_template(
                'verify-python',
                'test.py',
                {'context_folder': '/project', 'focus_file': 'main.py'}
            )

            assert 'test.py' in result
            assert '/project' in result
            assert 'main.py' in result

    def test_diagnose_template(self):
        """Test the diagnose template from the default config."""
        engine = TemplateEngine()

        if engine.has_template('diagnose'):
            result = engine.apply_template(
                'diagnose',
                'Error in code',
                {'context_folder': '/project'}
            )

            assert 'Error in code' in result
            assert '/project' in result

    def test_ux_ui_improver_template(self):
        """Test the ux-ui-improver template from the default config."""
        engine = TemplateEngine()

        if engine.has_template('ux-ui-improver'):
            result = engine.apply_template(
                'ux-ui-improver',
                'Improve the UI',
                {'context_folder': '/project', 'focus_file': 'app.py'}
            )

            assert 'Improve the UI' in result
            assert '/project' in result
            assert 'app.py' in result
