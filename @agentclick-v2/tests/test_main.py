"""
Tests for main.py entry point.

Tests the integration and bootstrap of all AgentClick V2 systems.
Focuses on integration testing rather than unit testing implementation details.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add project root to sys.path to import main module
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def read_main_file():
    """Helper to read main.py with UTF-8 encoding."""
    return (project_root / 'main.py').read_text(encoding='utf-8')


class TestMainModuleStructure:
    """Test main.py module structure and imports."""

    def test_main_file_exists(self):
        """Test that main.py exists at project root."""
        main_path = project_root / 'main.py'
        assert main_path.exists(), f"main.py should exist at {main_path}"

    def test_main_module_imports(self):
        """Test that main module can be imported."""
        # Clear from cache if exists
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert main is not None

    def test_main_function_exists(self):
        """Test that main() function exists and is callable."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, 'main')
        assert callable(main.main)

    def test_main_has_correct_imports(self):
        """Test that main.py imports required components."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Check for PyQt6
        assert hasattr(main, 'QApplication') or hasattr(main, 'PYQT6_AVAILABLE')

        # Check for core imports
        assert hasattr(main, 'WorkspaceManager')
        assert hasattr(main, 'DynamicAgentLoader')
        assert hasattr(main, 'HotkeyProcessorV2')
        assert hasattr(main, 'InputProcessor')
        assert hasattr(main, 'VirtualAgentExecutor')

        # Check for UI imports
        assert hasattr(main, 'MiniPopupV2')
        assert hasattr(main, 'DetailedPopupV2')

        # Check for utility imports
        assert hasattr(main, 'LoggerV2')
        assert hasattr(main, 'NotificationManager')


class TestModuleExecution:
    """Test __main__.py module execution."""

    def test_main_module_exists(self):
        """Test that __main__.py exists in @agentclick-v2 package."""
        main_path = Path(__file__).parent.parent / '__main__.py'
        assert main_path.exists(), f"__main__.py should exist at {main_path}"

    def test_main_module_delegates_to_main(self):
        """Test that __main__.py delegates to main.main()."""
        main_path = Path(__file__).parent.parent / '__main__.py'
        if main_path.exists():
            content = main_path.read_text()
            assert 'main' in content or 'main()' in content


class TestApplicationMetadata:
    """Test application metadata setup."""

    def test_project_metadata_defined(self):
        """Test that project metadata constants are defined."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, 'PROJECT_NAME')
        assert hasattr(main, 'PROJECT_VERSION')
        assert hasattr(main, 'PROJECT_ORGANIZATION')

    def test_project_metadata_values(self):
        """Test that project metadata has correct values."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert main.PROJECT_NAME == "AgentClick V2"
        assert isinstance(main.PROJECT_VERSION, str)
        assert main.PROJECT_ORGANIZATION == "AgentClick"


class TestHelperFunctions:
    """Test helper functions in main.py."""

    def test_show_critical_error_function_exists(self):
        """Test that _show_critical_error function exists."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, '_show_critical_error')
        assert callable(main._show_critical_error)

    def test_create_default_workspace_function_exists(self):
        """Test that _create_default_workspace function exists."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, '_create_default_workspace')
        assert callable(main._create_default_workspace)

    def test_initialize_core_systems_function_exists(self):
        """Test that _initialize_core_systems function exists."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, '_initialize_core_systems')
        assert callable(main._initialize_core_systems)

    def test_initialize_ui_components_function_exists(self):
        """Test that _initialize_ui_components function exists."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, '_initialize_ui_components')
        assert callable(main._initialize_ui_components)

    def test_initialize_hotkey_system_function_exists(self):
        """Test that _initialize_hotkey_system function exists."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert hasattr(main, '_initialize_hotkey_system')
        assert callable(main._initialize_hotkey_system)


class TestAcceptanceCriteria:
    """Test acceptance criteria from Story 0."""

    def test_ac01_main_py_exists(self):
        """AC: #1 - A `main.py` file exists at the project root."""
        main_path = project_root / 'main.py'
        assert main_path.exists(), "main.py must exist at project root"

    def test_ac02_main_initializes_qapplication(self):
        """AC: #2 - main.py initializes QApplication and sets up Qt event loop."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Check that main() uses QApplication
        # (We can't actually run it without a display, but we can check the code)
        main_content = read_main_file()
        assert 'QApplication' in main_content
        assert 'app.exec()' in main_content

    def test_ac03_main_initializes_workspace_manager(self):
        """AC: #3 - main.py loads and initializes WorkspaceManager."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        main_content = read_main_file()

        assert 'WorkspaceManager' in main_content
        assert 'workspace_manager' in main_content

    def test_ac04_main_initializes_agent_loader(self):
        """AC: #4 - main.py initializes DynamicAgentLoader."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        main_content = read_main_file()

        assert 'DynamicAgentLoader' in main_content
        assert 'agent_loader' in main_content

    def test_ac05_main_initializes_hotkey_processor(self):
        """AC: #5 - main.py creates and starts HotkeyProcessor."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        main_content = read_main_file()

        assert 'HotkeyProcessorV2' in main_content
        assert 'hotkey_processor' in main_content
        assert '.start()' in main_content

    def test_ac06_main_creates_ui_components(self):
        """AC: #6 - main.py creates MiniPopupV2 and DetailedPopupV2 UI components."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        main_content = read_main_file()

        assert 'MiniPopupV2' in main_content
        assert 'DetailedPopupV2' in main_content
        assert 'mini_popup' in main_content
        assert 'popup_window' in main_content

    def test_ac07_main_enters_event_loop(self):
        """AC: #7 - main.py enters the Qt event loop."""
        main_content = read_main_file()

        assert 'app.exec()' in main_content

    def test_ac08_module_execution_works(self):
        """AC: #8 - The application can be started with `python main.py` or `python -m agentclick_v2`."""
        # Test main.py exists
        main_path = project_root / 'main.py'
        assert main_path.exists()

        # Test __main__.py exists
        main_module_path = Path(__file__).parent.parent / '__main__.py'
        assert main_module_path.exists()

        # Check that __main__.py imports main
        main_module_content = main_module_path.read_text()
        assert 'import main' in main_module_content
        assert 'main.main()' in main_module_content


class TestErrorHandling:
    """Test error handling in main.py."""

    def test_handles_missing_pyqt6(self):
        """Test that main.py handles missing PyQt6 gracefully."""
        main_content = read_main_file()

        # Check for ImportError handling
        assert 'PYQT6_AVAILABLE' in main_content
        assert 'ImportError' in main_content or 'except ImportError' in main_content

    def test_handles_first_run_scenario(self):
        """Test that main.py handles first-run (missing config) scenario."""
        main_content = read_main_file()

        # Check for FileNotFoundError handling
        assert 'FileNotFoundError' in main_content
        assert '_create_default_workspace' in main_content

    def test_handles_keyboard_interrupt(self):
        """Test that main.py handles KeyboardInterrupt (Ctrl+C)."""
        main_content = read_main_file()

        assert 'KeyboardInterrupt' in main_content

    def test_logs_initialization_progress(self):
        """Test that main.py logs initialization progress."""
        main_content = read_main_file()

        assert 'LoggerV2' in main_content
        assert 'add_log_entry' in main_content


class TestStartupFlow:
    """Test that main.py follows the specified startup flow."""

    def test_startup_flow_step1_create_qapplication(self):
        """Startup Flow #1 - Create Qt application."""
        main_content = read_main_file()
        assert 'app = QApplication(' in main_content or 'QApplication(sys.argv)' in main_content

    def test_startup_flow_step2_initialize_logging(self):
        """Startup Flow #2 - Initialize logging."""
        main_content = read_main_file()
        assert 'LoggerV2()' in main_content or 'logger = LoggerV2' in main_content

    def test_startup_flow_step3_load_workspace_manager(self):
        """Startup Flow #3 - Load workspace manager."""
        main_content = read_main_file()
        assert 'WorkspaceManager()' in main_content

    def test_startup_flow_step4_load_agents(self):
        """Startup Flow #4 - Load agents dynamically."""
        main_content = read_main_file()
        assert 'DynamicAgentLoader()' in main_content

    def test_startup_flow_step5_create_ui(self):
        """Startup Flow #5 - Create UI components."""
        main_content = read_main_file()
        assert 'MiniPopupV2(' in main_content
        assert 'DetailedPopupV2(' in main_content

    def test_startup_flow_step6_initialize_hotkey_processor(self):
        """Startup Flow #6 - Initialize hotkey processor (drives the system)."""
        main_content = read_main_file()
        assert 'HotkeyProcessorV2(' in main_content
        assert 'hotkey_processor.start()' in main_content

    def test_startup_flow_step7_enter_event_loop(self):
        """Startup Flow #7 - Enter event loop."""
        main_content = read_main_file()
        assert 'app.exec()' in main_content or 'sys.exit(app.exec())' in main_content


class TestAntiPatterns:
    """Test that main.py avoids specified anti-patterns."""

    def test_no_hardcoded_paths(self):
        """Anti-Pattern: Don't hardcode file paths."""
        main_content = read_main_file()

        # Check that pathlib Path is used
        assert 'Path(' in main_content or 'pathlib' in main_content

        # Check for config_path being dynamic
        assert 'config_path' in main_content

    def test_uses_relative_paths(self):
        """Test that relative paths are used where appropriate."""
        main_content = read_main_file()

        # Check for Path.cwd() or similar
        assert 'Path.cwd()' in main_content or '__file__' in main_content

    def test_logs_errors(self):
        """Anti-Pattern: Don't silently catch exceptions."""
        main_content = read_main_file()

        # Check for logging in error handlers
        assert 'logger' in main_content

    def test_checks_existing_qapplication(self):
        """Anti-Pattern: Don't create multiple QApplication instances."""
        main_content = read_main_file()

        # Check for existing instance check
        assert 'QApplication.instance()' in main_content


class TestCodeQuality:
    """Test code quality of main.py."""

    def test_main_py_has_docstring(self):
        """Test that main.py has a module docstring."""
        main_content = read_main_file()

        # Check for docstring at the start
        lines = main_content.split('\n')
        assert lines[0].startswith('"""') or lines[1].startswith('"""')

    def test_main_function_has_docstring(self):
        """Test that main() function has a docstring."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        assert main.main.__doc__ is not None
        assert len(main.main.__doc__) > 0

    def test_code_is_readably_structured(self):
        """Test that code follows structure from Dev Notes."""
        main_content = read_main_file()

        # Check for helper functions with _ prefix
        assert '_initialize_' in main_content
        assert '_show_' in main_content
        assert '_create_' in main_content


class TestIntegration:
    """Integration tests for main.py (with mocked dependencies)."""

    @pytest.mark.integration
    def test_main_can_be_imported_without_crashing(self):
        """Test that importing main module doesn't crash."""
        if 'main' in sys.modules:
            del sys.modules['main']

        # This should not raise any exceptions
        import main

        # Verify key components are accessible
        assert hasattr(main, 'main')
        assert hasattr(main, 'PROJECT_NAME')

    @pytest.mark.integration
    def test_all_required_components_importable(self):
        """Test that all components used by main can be imported."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # These imports should all work
        components = [
            'WorkspaceManager',
            'DynamicAgentLoader',
            'HotkeyProcessorV2',
            'InputProcessor',
            'VirtualAgentExecutor',
            'MiniPopupV2',
            'DetailedPopupV2',
            'LoggerV2',
            'NotificationManager',
        ]

        for component in components:
            assert hasattr(main, component), f"{component} should be imported in main"


class TestFunctionalBehavior:
    """Functional tests that verify actual behavior, not just structure."""

    @patch('main.sys.exit')
    @patch('main.QApplication')
    @patch('main.asyncio.run')
    @patch('main.LoggerV2')
    def test_main_exits_with_code_0_on_success(self, mock_logger, mock_asyncio_run, mock_qapp, mock_exit):
        """Test that main() calls sys.exit(0) when successful."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Setup mocks
        mock_app = MagicMock()
        mock_app.exec.return_value = 0
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = mock_app

        # Mock asyncio.run to return fake objects
        mock_workspace_manager = MagicMock()
        mock_workspace_manager.workspaces = [MagicMock()]
        mock_workspace_manager.current_workspace = MagicMock()
        mock_agent_loader = MagicMock()
        mock_asyncio_run.return_value = (mock_workspace_manager, mock_agent_loader)

        # Mock other components
        with patch('main._initialize_ui_components') as mock_init_ui, \
             patch('main._initialize_hotkey_system') as mock_init_hotkey, \
             patch('main.NotificationManager'):

            mock_init_ui.return_value = (MagicMock(), MagicMock())
            mock_hotkey_processor = MagicMock()
            mock_hotkey_processor.is_listening.return_value = True
            mock_init_hotkey.return_value = mock_hotkey_processor

            # Run main - should complete without exception
            main.main()

            # Verify sys.exit was called with 0
            mock_exit.assert_called_once_with(0)

    @patch('main.sys.exit')
    @patch('main.QApplication')
    @patch('main._show_critical_error')
    def test_main_shows_error_when_pyqt6_missing(self, mock_show_error, mock_qapp, mock_exit):
        """Test that main() shows error dialog when PyQt6 is not available."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Temporarily make PyQt6 unavailable
        original_pyqt6 = main.PYQT6_AVAILABLE
        main.PYQT6_AVAILABLE = False

        try:
            # Run main - should exit early
            main.main()

            # Verify error dialog was shown
            mock_show_error.assert_called_once()
            assert "PyQt6" in mock_show_error.call_args[0][0]

            # Verify sys.exit was called with error code
            mock_exit.assert_called_once_with(1)
        finally:
            main.PYQT6_AVAILABLE = original_pyqt6

    @patch('main.asyncio.run')
    def test_create_default_workspace_creates_valid_yaml(self, mock_asyncio_run):
        """Test that _create_default_workspace creates valid YAML structure."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main
        import tempfile
        import yaml

        # Create a temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock workspace manager with temp config path
            mock_workspace_manager = MagicMock()
            config_path = Path(temp_dir) / 'workspaces.yaml'
            mock_workspace_manager.config_path = config_path

            # Call the function
            main._create_default_workspace(mock_workspace_manager)

            # Verify file was created
            assert config_path.exists(), "Config file should be created"

            # Verify YAML is valid and has expected structure
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            assert 'current_workspace_id' in data
            assert data['current_workspace_id'] == 'default'
            assert 'workspaces' in data
            assert len(data['workspaces']) == 1
            assert data['workspaces'][0]['id'] == 'default'
            assert data['workspaces'][0]['name'] == 'Default Workspace'
            assert data['workspaces'][0]['emoji'] == '🚀'
            assert data['workspaces'][0]['color'] == '#0078d4'

    @patch('main.sys.exit')
    @patch('main.QApplication')
    @patch('main.asyncio.run')
    @patch('main.LoggerV2')
    @patch('main._show_critical_error')
    def test_main_exits_when_no_workspaces_loaded(self, mock_show_error, mock_logger, mock_asyncio_run, mock_qapp, mock_exit):
        """Test that main() exits gracefully when no workspaces loaded."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Setup mocks
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = MagicMock()

        # Mock asyncio.run to return empty workspaces
        mock_workspace_manager = MagicMock()
        mock_workspace_manager.workspaces = []  # Empty workspaces
        mock_agent_loader = MagicMock()
        mock_asyncio_run.return_value = (mock_workspace_manager, mock_agent_loader)

        # Run main - should exit with error
        main.main()

        # Verify error was shown
        mock_show_error.assert_called_once()
        assert "workspaces" in mock_show_error.call_args[0][0].lower()

        # Verify sys.exit was called with error code
        mock_exit.assert_called_with(1)

    @patch('main.QApplication')
    @patch('main.asyncio.run')
    @patch('main.LoggerV2')
    def test_initialization_functions_called_in_correct_order(self, mock_logger_class, mock_asyncio_run, mock_qapp):
        """Test that initialization functions are called in correct order."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Setup mocks
        mock_app = MagicMock()
        mock_app.exec.return_value = 0
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = mock_app

        mock_workspace_manager = MagicMock()
        mock_workspace_manager.workspaces = [MagicMock()]
        mock_workspace_manager.current_workspace = MagicMock()
        mock_agent_loader = MagicMock()
        mock_asyncio_run.return_value = (mock_workspace_manager, mock_agent_loader)

        mock_logger = MagicMock()
        mock_logger_class.return_value = mock_logger

        call_order = []

        with patch('main._initialize_ui_components') as mock_init_ui, \
             patch('main._initialize_hotkey_system') as mock_init_hotkey, \
             patch('main.NotificationManager'), \
             patch('main.sys.exit'):

            # Track call order
            mock_init_ui.side_effect = lambda *args, **kwargs: call_order.append('ui')
            mock_init_hotkey.side_effect = lambda *args, **kwargs: call_order.append('hotkey')

            mock_init_ui.return_value = (MagicMock(), MagicMock())
            mock_hotkey_processor = MagicMock()
            mock_hotkey_processor.is_listening.return_value = True
            mock_hotkey_processor.start.side_effect = lambda: call_order.append('start_hotkey')
            mock_init_hotkey.return_value = mock_hotkey_processor

            main.main()

            # Verify order: UI components → Hotkey system → Start hotkey
            assert call_order.index('ui') < call_order.index('hotkey')
            assert call_order.index('hotkey') < call_order.index('start_hotkey')

    @patch('main.QApplication')
    @patch('main.asyncio.run')
    @patch('main.LoggerV2')
    def test_keyboard_interrupt_performs_cleanup(self, mock_logger_class, mock_asyncio_run, mock_qapp):
        """Test that KeyboardInterrupt (Ctrl+C) performs cleanup."""
        if 'main' in sys.modules:
            del sys.modules['main']

        import main

        # Setup mocks
        mock_app = MagicMock()
        # Simulate KeyboardInterrupt during app.exec()
        mock_app.exec.side_effect = KeyboardInterrupt()
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = mock_app

        mock_workspace_manager = MagicMock()
        mock_workspace_manager.workspaces = [MagicMock()]
        mock_workspace_manager.current_workspace = MagicMock()
        mock_agent_loader = MagicMock()
        mock_asyncio_run.return_value = (mock_workspace_manager, mock_agent_loader)

        mock_logger = MagicMock()
        mock_logger_class.return_value = mock_logger

        with patch('main._initialize_ui_components') as mock_init_ui, \
             patch('main._initialize_hotkey_system') as mock_init_hotkey, \
             patch('main.NotificationManager'), \
             patch('main.sys.exit') as mock_exit:

            mock_init_ui.return_value = (MagicMock(), MagicMock())
            mock_hotkey_processor = MagicMock()
            mock_init_hotkey.return_value = mock_hotkey_processor

            # Run main - should handle KeyboardInterrupt
            main.main()

            # Verify hotkey processor was stopped during cleanup
            mock_hotkey_processor.stop.assert_called()

            # Verify exit was called with 0
            mock_exit.assert_called_with(0)
