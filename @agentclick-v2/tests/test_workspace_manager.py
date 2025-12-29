"""
Tests for WorkspaceManager.

This module tests the main workspace management functionality including
loading, switching, adding, updating, and removing workspaces.
"""
import pytest
from pathlib import Path
import tempfile
import yaml

from core.workspace_manager import WorkspaceManager
from core.exceptions import (
    WorkspaceNotFoundError,
    WorkspaceLoadError,
    WorkspaceValidationError
)
from models.workspace import Workspace


class TestWorkspaceManagerInit:
    """Test WorkspaceManager initialization."""

    def test_init_with_default_path(self):
        """Should initialize with default config path."""
        manager = WorkspaceManager()
        assert manager.config_path is not None

    def test_init_with_custom_path(self):
        """Should initialize with custom config path."""
        custom_path = "/custom/path/workspaces.yaml"
        manager = WorkspaceManager(config_path=custom_path)
        assert manager.config_path == Path(custom_path)

    def test_workspaces_dict_initially_empty(self):
        """Workspaces dictionary should be initially empty."""
        manager = WorkspaceManager()
        assert manager.workspaces == {}
        assert manager.current_workspace_id is None


class TestLoadWorkspaces:
    """Test loading workspaces from YAML file."""

    @pytest.fixture
    def valid_config_file(self):
        """Create a valid workspace config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('version: "2.0"\n')
            f.write('current_workspace: "python"\n')
            f.write('workspaces:\n')
            f.write('  python:\n')
            f.write('    name: "Python Projects"\n')
            f.write('    folder: "/python"\n')
            f.write('    emoji: "🐍"\n')
            f.write('    color: "#0078d4"\n')
            f.write('  web:\n')
            f.write('    name: "Web Development"\n')
            f.write('    folder: "/web"\n')
            f.write('    emoji: "🌐"\n')
            f.write('    color: "#ff6600"\n')
            temp_path = f.name

        # Create the folders so validation passes
        Path("/python").mkdir(exist_ok=True) if Path("/python").exists() else None
        Path("/web").mkdir(exist_ok=True) if Path("/web").exists() else None

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_load_valid_config(self, valid_config_file):
        """Should load workspaces from valid config file."""
        # Create temp directories for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Modify the config to use temp directory
            config_data = {
                'version': '2.0',
                'current_workspace': 'python',
                'workspaces': {
                    'python': {
                        'name': 'Python Projects',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    },
                    'web': {
                        'name': 'Web Development',
                        'folder': temp_dir,
                        'emoji': '🌐',
                        'color': '#ff6600'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                assert len(manager.workspaces) == 2
                assert 'python' in manager.workspaces
                assert 'web' in manager.workspaces
                assert manager.current_workspace_id == 'python'
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self):
        """Should raise WorkspaceLoadError for non-existent file."""
        manager = WorkspaceManager(config_path="/nonexistent/workspaces.yaml")

        with pytest.raises(WorkspaceLoadError):
            await manager.load_workspaces()

    @pytest.mark.asyncio
    async def test_load_invalid_yaml(self):
        """Should raise WorkspaceLoadError for invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write('invalid: yaml: content:')
            temp_path = f.name

        try:
            manager = WorkspaceManager(config_path=temp_path)
            with pytest.raises(WorkspaceLoadError):
                await manager.load_workspaces()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_load_empty_workspaces(self):
        """Should handle empty workspaces section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'current_workspace': None,
                'workspaces': {}
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                assert manager.workspaces == {}
                assert manager.current_workspace_id is None
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestSwitchWorkspace:
    """Test switching between workspaces."""

    @pytest.mark.asyncio
    async def test_switch_to_existing_workspace(self):
        """Should switch to existing workspace and persist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'current_workspace': 'python',
                'workspaces': {
                    'python': {
                        'name': 'Python Projects',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    },
                    'web': {
                        'name': 'Web Development',
                        'folder': temp_dir,
                        'emoji': '🌐',
                        'color': '#ff6600'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                # Switch to web workspace
                manager.switch_workspace('web')

                assert manager.current_workspace_id == 'web'

                # Verify it was persisted
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_data = yaml.safe_load(f)
                    assert saved_data['current_workspace'] == 'web'
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_switch_to_nonexistent_workspace(self):
        """Should raise WorkspaceNotFoundError for non-existent workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                with pytest.raises(WorkspaceNotFoundError, match='nonexistent'):
                    manager.switch_workspace('nonexistent')
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestGetWorkspace:
    """Test retrieving workspaces."""

    @pytest.mark.asyncio
    async def test_get_current_workspace(self):
        """Should return the current workspace object."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'current_workspace': 'python',
                'workspaces': {
                    'python': {
                        'name': 'Python Projects',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                current = manager.get_current_workspace()
                assert current is not None
                assert current.id == 'python'
                assert current.name == 'Python Projects'
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_get_current_workspace_when_none_set(self):
        """Should return None when no current workspace is set."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'current_workspace': None,
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                current = manager.get_current_workspace()
                assert current is None
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestListWorkspaces:
    """Test listing workspaces."""

    @pytest.mark.asyncio
    async def test_list_workspaces(self):
        """Should return list of all workspaces."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    },
                    'web': {
                        'name': 'Web',
                        'folder': temp_dir,
                        'emoji': '🌐',
                        'color': '#ff6600'
                    },
                    'docs': {
                        'name': 'Docs',
                        'folder': temp_dir,
                        'emoji': '📚',
                        'color': '#00ff00'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                workspaces = manager.list_workspaces()
                assert len(workspaces) == 3
                assert all(isinstance(ws, Workspace) for ws in workspaces)
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestAddWorkspace:
    """Test adding new workspaces."""

    @pytest.mark.asyncio
    async def test_add_valid_workspace(self):
        """Should add valid workspace and persist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'workspaces': {}
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                new_workspace_config = {
                    'id': 'python',
                    'name': 'Python Projects',
                    'folder': temp_dir,
                    'emoji': '🐍',
                    'color': '#0078d4'
                }

                manager.add_workspace(new_workspace_config)

                assert 'python' in manager.workspaces
                assert manager.workspaces['python'].name == 'Python Projects'

                # Verify persisted
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_data = yaml.safe_load(f)
                    assert 'python' in saved_data['workspaces']
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_add_invalid_workspace(self):
        """Should raise WorkspaceValidationError for invalid config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {'version': '2.0', 'workspaces': {}}

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                invalid_config = {
                    'id': 'python with spaces',  # Invalid ID
                    'name': 'Python',
                    'folder': temp_dir,
                    'emoji': '🐍',
                    'color': '#0078d4'
                }

                with pytest.raises(WorkspaceValidationError):
                    manager.add_workspace(invalid_config)
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestUpdateWorkspace:
    """Test updating existing workspaces."""

    @pytest.mark.asyncio
    async def test_update_existing_workspace(self):
        """Should update existing workspace and persist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                updates = {
                    'name': 'Python Projects (Updated)',
                    'emoji': '🐍🚀'
                }

                manager.update_workspace('python', updates)

                assert manager.workspaces['python'].name == 'Python Projects (Updated)'
                assert manager.workspaces['python'].emoji == '🐍🚀'
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_update_nonexistent_workspace(self):
        """Should raise WorkspaceNotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {'version': '2.0', 'workspaces': {}}

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                with pytest.raises(WorkspaceNotFoundError):
                    manager.update_workspace('nonexistent', {'name': 'New Name'})
            finally:
                Path(temp_path).unlink(missing_ok=True)


class TestRemoveWorkspace:
    """Test removing workspaces."""

    @pytest.mark.asyncio
    async def test_remove_existing_workspace(self):
        """Should remove workspace and persist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'current_workspace': 'python',
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    },
                    'web': {
                        'name': 'Web',
                        'folder': temp_dir,
                        'emoji': '🌐',
                        'color': '#ff6600'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                manager.remove_workspace('python')

                assert 'python' not in manager.workspaces
                assert len(manager.workspaces) == 1
            finally:
                Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_prevent_removing_last_workspace(self):
        """Should not allow removing the last workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_data = {
                'version': '2.0',
                'workspaces': {
                    'python': {
                        'name': 'Python',
                        'folder': temp_dir,
                        'emoji': '🐍',
                        'color': '#0078d4'
                    }
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config_data, f)
                temp_path = f.name

            try:
                manager = WorkspaceManager(config_path=temp_path)
                await manager.load_workspaces()

                with pytest.raises(ValueError, match="Cannot remove the last workspace"):
                    manager.remove_workspace('python')
            finally:
                Path(temp_path).unlink(missing_ok=True)
