"""
Tests for YAML helper utilities.

This module tests the YAML loading and saving utilities used by
the WorkspaceManager.
"""
import pytest
from pathlib import Path
import tempfile
import os

from utils.yaml_helpers import load_yaml, save_yaml


class TestLoadYaml:
    """Test the load_yaml function."""

    @pytest.fixture
    def temp_yaml_file(self):
        """Create a temporary YAML file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('version: "2.0"\n')
            f.write('key1: value1\n')
            f.write('key2: value2\n')
            temp_path = f.name
        yield temp_path
        # Cleanup
        os.unlink(temp_path)

    def test_load_existing_file(self, temp_yaml_file):
        """Should load YAML file and return dictionary."""
        result = load_yaml(temp_yaml_file)
        assert isinstance(result, dict)
        assert result['version'] == '2.0'
        assert result['key1'] == 'value1'
        assert result['key2'] == 'value2'

    def test_load_nonexistent_file(self):
        """Should raise FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_yaml('nonexistent_file.yaml')

    def test_load_invalid_yaml(self):
        """Should raise error for invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('invalid: yaml: content:\n  - broken')
            temp_path = f.name

        try:
            with pytest.raises(Exception):  # Could be yaml.YAMLError or similar
                load_yaml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_empty_file(self):
        """Should handle empty file gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            result = load_yaml(temp_path)
            assert result is None or result == {}
        finally:
            os.unlink(temp_path)

    def test_load_with_complex_structure(self, temp_yaml_file):
        """Should load complex nested structures."""
        # Create a more complex YAML file
        with open(temp_yaml_file, 'w') as f:
            f.write('version: "2.0"\n')
            f.write('workspaces:\n')
            f.write('  workspace1:\n')
            f.write('    name: "Workspace 1"\n')
            f.write('    settings:\n')
            f.write('      enabled: true\n')
            f.write('      count: 42\n')

        result = load_yaml(temp_yaml_file)
        assert result['workspaces']['workspace1']['name'] == 'Workspace 1'
        assert result['workspaces']['workspace1']['settings']['enabled'] is True
        assert result['workspaces']['workspace1']['settings']['count'] == 42


class TestSaveYaml:
    """Test the save_yaml function."""

    @pytest.fixture
    def temp_file_path(self):
        """Create a temporary file path for testing."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=True) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup if file exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_save_simple_dict(self, temp_file_path):
        """Should save dictionary to YAML file."""
        data = {
            'version': '2.0',
            'key1': 'value1',
            'key2': 'value2'
        }
        save_yaml(temp_file_path, data)

        # Verify file was created and contains correct data
        assert Path(temp_file_path).exists()
        loaded = load_yaml(temp_file_path)
        assert loaded == data

    def test_save_nested_dict(self, temp_file_path):
        """Should save nested dictionary structures."""
        data = {
            'version': '2.0',
            'workspaces': {
                'workspace1': {
                    'name': 'Workspace 1',
                    'agents': ['agent1', 'agent2']
                }
            }
        }
        save_yaml(temp_file_path, data)

        loaded = load_yaml(temp_file_path)
        assert loaded['workspaces']['workspace1']['name'] == 'Workspace 1'
        assert loaded['workspaces']['workspace1']['agents'] == ['agent1', 'agent2']

    def test_save_overwrites_existing(self, temp_file_path):
        """Should overwrite existing file."""
        # Create initial file
        initial_data = {'version': '1.0', 'old': 'data'}
        save_yaml(temp_file_path, initial_data)

        # Overwrite with new data
        new_data = {'version': '2.0', 'new': 'data'}
        save_yaml(temp_file_path, new_data)

        # Verify new data
        loaded = load_yaml(temp_file_path)
        assert loaded == new_data
        assert 'old' not in loaded

    def test_save_creates_directories(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / 'subdir' / 'nested' / 'config.yaml'

            data = {'version': '2.0', 'test': 'data'}
            save_yaml(nested_path, data)

            assert nested_path.exists()
            loaded = load_yaml(nested_path)
            assert loaded == data

    def test_save_preserves_data_types(self, temp_file_path):
        """Should preserve data types (strings, numbers, booleans, lists)."""
        data = {
            'version': '2.0',
            'string_val': 'hello',
            'int_val': 42,
            'float_val': 3.14,
            'bool_val': True,
            'list_val': [1, 2, 3],
            'none_val': None
        }
        save_yaml(temp_file_path, data)

        loaded = load_yaml(temp_file_path)
        assert loaded['string_val'] == 'hello'
        assert loaded['int_val'] == 42
        assert loaded['float_val'] == 3.14
        assert loaded['bool_val'] is True
        assert loaded['list_val'] == [1, 2, 3]
        assert loaded['none_val'] is None

    def test_save_with_path_object(self, temp_file_path):
        """Should accept Path objects as file path."""
        data = {'version': '2.0', 'test': 'data'}
        path_obj = Path(temp_file_path)

        save_yaml(path_obj, data)

        assert path_obj.exists()
        loaded = load_yaml(path_obj)
        assert loaded == data


class TestYamlRoundTrip:
    """Test save and load round-trip operations."""

    def test_round_trip_preserves_data(self):
        """Data should be identical after save/load cycle."""
        original_data = {
            'version': '2.0',
            'workspaces': {
                'python': {
                    'name': 'Python Projects',
                    'folder': 'C:/python-projects',
                    'emoji': '🐍',
                    'color': '#0078d4',
                    'agents': [
                        {'type': 'command', 'id': 'verify-python', 'enabled': True}
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            save_yaml(temp_path, original_data)
            loaded_data = load_yaml(temp_path)

            assert loaded_data == original_data
        finally:
            os.unlink(temp_path)

    def test_multiple_round_trips(self):
        """Data should survive multiple save/load cycles."""
        data = {'version': '2.0', 'counter': 0}

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            # Multiple cycles
            for i in range(5):
                data['counter'] = i
                save_yaml(temp_path, data)
                loaded = load_yaml(temp_path)
                assert loaded['counter'] == i
        finally:
            os.unlink(temp_path)
