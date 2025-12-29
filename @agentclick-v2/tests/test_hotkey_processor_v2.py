"""
Tests for HotkeyProcessorV2 (Story 9)

Test coverage:
- HotkeyProcessorV2 class initialization
- Hotkey registration
- Agent execution flow
- Agent switching logic
- Workspace switching logic
- Clipboard integration
- Error handling
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from pathlib import Path
import asyncio

# Mock pynput before importing HotkeyProcessorV2
with patch('core.hotkey_processor.PYNPUT_AVAILABLE', True):
    from core.hotkey_processor import HotkeyProcessorV2
    from core.hotkey_processor import HOTKEY_PAUSE, HOTKEY_CTRL_PAUSE, HOTKEY_CTRL_SHIFT_PAUSE

from models.workspace import Workspace
from models.virtual_agent import VirtualAgent
from models.execution_result import ExecutionResult


@pytest.fixture
def mock_workspace_manager():
    """Mock workspace manager."""
    manager = Mock()
    manager.current_workspace_id = "test-workspace"

    # Create mock workspace
    workspace = Mock(spec=Workspace)
    workspace.id = "test-workspace"
    workspace.name = "Test Workspace"
    workspace.emoji = "🧪"
    workspace.color = "#0078d4"
    workspace.folder = Path("/test/folder")

    # Create second workspace for switching tests
    workspace2 = Mock(spec=Workspace)
    workspace2.id = "test-workspace-2"
    workspace2.name = "Test Workspace 2"
    workspace2.emoji = "🧪🧪"
    workspace2.color = "#ff0000"
    workspace2.folder = Path("/test/folder2")
    workspace2.current_agent_index = 0

    # Create mock agents
    agent1 = Mock(spec=VirtualAgent)
    agent1.id = "agent-1"
    agent1.name = "test-agent"
    agent1.type = "command"
    agent1.enabled = True

    agent2 = Mock(spec=VirtualAgent)
    agent2.id = "agent-2"
    agent2.name = "another-agent"
    agent2.type = "skill"
    agent2.enabled = True

    workspace.agents = [agent1, agent2]
    workspace.current_agent_index = 0
    workspace2.agents = [agent1]

    manager.get_current_workspace.return_value = workspace
    manager.list_workspaces.return_value = [workspace, workspace2]
    manager.switch_workspace = Mock()
    manager.switch_to_next_workspace = Mock()

    return manager


@pytest.fixture
def mock_agent_executor():
    """Mock agent executor."""
    executor = Mock()
    executor.execute = AsyncMock(return_value=ExecutionResult(
        output="Test result",
        status="success",
        metadata={}
    ))
    return executor


@pytest.fixture
def mock_input_processor():
    """Mock input processor."""
    from core.input_processor import InputType

    processor = Mock()
    processor.detect_input_type = AsyncMock(return_value=InputType.TEXT)
    processor.process_text = Mock(return_value="test input")
    processor.process_file = Mock(return_value="file content")
    processor.process_empty = Mock(return_value="manual input")
    processor.process_url = AsyncMock(return_value="downloaded content")
    return processor


@pytest.fixture
def mock_mini_popup():
    """Mock mini popup."""
    popup = Mock()
    popup.update_display = Mock()
    popup.set_workspace_color = Mock()
    return popup


@pytest.fixture
def mock_clipboard():
    """Mock clipboard."""
    clipboard = Mock()
    clipboard.setText = Mock()
    return clipboard


@pytest.fixture
def hotkey_processor(mock_workspace_manager, mock_agent_executor,
                     mock_input_processor, mock_mini_popup):
    """Create HotkeyProcessorV2 instance with mocks."""
    return HotkeyProcessorV2(
        workspace_manager=mock_workspace_manager,
        agent_executor=mock_agent_executor,
        input_processor=mock_input_processor,
        mini_popup=mock_mini_popup
    )


class TestHotkeyProcessorInitialization:
    """Tests for HotkeyProcessorV2 initialization (AC: #1, #2, #3, #5)."""

    def test_init_with_all_dependencies(self, mock_workspace_manager,
                                       mock_agent_executor, mock_input_processor,
                                       mock_mini_popup):
        """Test HotkeyProcessorV2 initialization with all dependencies."""
        processor = HotkeyProcessorV2(
            workspace_manager=mock_workspace_manager,
            agent_executor=mock_agent_executor,
            input_processor=mock_input_processor,
            mini_popup=mock_mini_popup
        )

        assert processor.workspace_manager == mock_workspace_manager
        assert processor.agent_executor == mock_agent_executor
        assert processor.input_processor == mock_input_processor
        assert processor.mini_popup == mock_mini_popup

    def test_init_stores_dependencies_correctly(self, hotkey_processor):
        """Test that all dependencies are stored correctly."""
        assert hotkey_processor.workspace_manager is not None
        assert hotkey_processor.agent_executor is not None
        assert hotkey_processor.input_processor is not None
        assert hotkey_processor.mini_popup is not None

    def test_hotkey_constants_defined(self):
        """Test that hotkey constants are defined (AC: #1, #2, #3)."""
        # Check that hotkey constants are defined
        assert HOTKEY_PAUSE == 'pause'
        assert HOTKEY_CTRL_PAUSE == 'ctrl+pause'
        assert HOTKEY_CTRL_SHIFT_PAUSE == 'ctrl+shift+pause'


class TestHotkeyRegistration:
    """Tests for hotkey registration (AC: #1, #2, #3)."""

    def test_setup_hotkeys_method_exists(self, hotkey_processor):
        """Test that setup_hotkeys method exists."""
        assert hasattr(hotkey_processor, 'setup_hotkeys')
        assert callable(hotkey_processor.setup_hotkeys)

    @patch('core.hotkey_processor.PYNPUT_AVAILABLE', True)
    @patch('core.hotkey_processor.keyboard')
    def test_setup_hotkeys_registers_pause_key(self, mock_keyboard, hotkey_processor):
        """Test that setup_hotkeys registers Pause key (AC: #1)."""
        mock_keyboard.add_hotkey = Mock()
        mock_keyboard.hook = Mock()
        mock_keyboard.GlobalHotKeys = Mock(return_value=Mock(start=Mock()))

        hotkey_processor.setup_hotkeys()

        # Verify hotkey was registered
        assert mock_keyboard.GlobalHotKeys.called

    @patch('core.hotkey_processor.PYNPUT_AVAILABLE', True)
    @patch('core.hotkey_processor.keyboard')
    def test_setup_hotkeys_registers_ctrl_pause(self, mock_keyboard, hotkey_processor):
        """Test that setup_hotkeys registers Ctrl+Pause (AC: #2)."""
        mock_keyboard.add_hotkey = Mock()
        mock_keyboard.GlobalHotKeys = Mock(return_value=Mock(start=Mock()))

        hotkey_processor.setup_hotkeys()

        # Should register hotkeys
        assert mock_keyboard.GlobalHotKeys.called

    @patch('core.hotkey_processor.PYNPUT_AVAILABLE', True)
    @patch('core.hotkey_processor.keyboard')
    def test_setup_hotkeys_registers_ctrl_shift_pause(self, mock_keyboard, hotkey_processor):
        """Test that setup_hotkeys registers Ctrl+Shift+Pause (AC: #3)."""
        mock_keyboard.GlobalHotKeys = Mock(return_value=Mock(start=Mock()))

        hotkey_processor.setup_hotkeys()

        # Should register hotkeys
        assert mock_keyboard.GlobalHotKeys.called


class TestHotkeyHandlers:
    """Tests for hotkey handler methods."""

    def test_on_pause_handler_exists(self, hotkey_processor):
        """Test that on_pause handler exists (AC: #1)."""
        assert hasattr(hotkey_processor, 'on_pause')
        assert callable(hotkey_processor.on_pause)

    def test_on_ctrl_pause_handler_exists(self, hotkey_processor):
        """Test that on_ctrl_pause handler exists (AC: #2)."""
        assert hasattr(hotkey_processor, 'on_ctrl_pause')
        assert callable(hotkey_processor.on_ctrl_pause)

    def test_on_ctrl_shift_pause_handler_exists(self, hotkey_processor):
        """Test that on_ctrl_shift_pause handler exists (AC: #3)."""
        assert hasattr(hotkey_processor, 'on_ctrl_shift_pause')
        assert callable(hotkey_processor.on_ctrl_shift_pause)


class TestAgentExecutionFlow:
    """Tests for agent execution flow (AC: #1, #4, #6)."""

    @pytest.mark.asyncio
    async def test_execute_agent_detects_input_type(self, hotkey_processor, mock_input_processor):
        """Test that execute_agent detects input type (AC: #4)."""
        # Execute agent
        await hotkey_processor.execute_agent()

        # Verify input type detection was called
        mock_input_processor.detect_input_type.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_processes_input(self, hotkey_processor, mock_input_processor):
        """Test that execute_agent processes input based on type (AC: #4)."""
        mock_input_processor.detect_input_type.return_value = "text"

        await hotkey_processor.execute_agent()

        # Verify input was processed
        mock_input_processor.process_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_gets_current_workspace(self, hotkey_processor,
                                                         mock_workspace_manager):
        """Test that execute_agent gets current workspace (AC: #1)."""
        await hotkey_processor.execute_agent()

        # Verify workspace was retrieved
        mock_workspace_manager.get_current_workspace.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_executes_agent(self, hotkey_processor,
                                                mock_agent_executor,
                                                mock_workspace_manager):
        """Test that execute_agent executes agent (AC: #1)."""
        await hotkey_processor.execute_agent()

        # Verify agent was executed
        workspace = mock_workspace_manager.get_current_workspace.return_value
        assert mock_agent_executor.execute.called

        # Get the call arguments
        call_args = mock_agent_executor.execute.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_execute_agent_copies_to_clipboard(self, hotkey_processor):
        """Test that execute_agent copies result to clipboard (AC: #6)."""
        with patch.object(hotkey_processor, '_copy_to_clipboard') as mock_copy:
            await hotkey_processor.execute_agent()

            # Verify clipboard copy was called
            mock_copy.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_handles_text_input(self, hotkey_processor,
                                                    mock_input_processor):
        """Test execute_agent with text input type."""
        from core.input_processor import InputType

        mock_input_processor.detect_input_type.return_value = InputType.TEXT
        mock_input_processor.process_text.return_value = "test text"

        await hotkey_processor.execute_agent()

        mock_input_processor.process_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_handles_url_input(self, hotkey_processor,
                                                   mock_input_processor):
        """Test execute_agent with URL input type."""
        from core.input_processor import InputType

        mock_input_processor.detect_input_type.return_value = InputType.URL
        mock_input_processor.process_url = AsyncMock(return_value="downloaded content")
        mock_input_processor.process_text.return_value = "http://example.com"

        await hotkey_processor.execute_agent()

        mock_input_processor.process_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_handles_empty_input(self, hotkey_processor,
                                                     mock_input_processor,
                                                     mock_workspace_manager):
        """Test execute_agent with empty input type."""
        from core.input_processor import InputType

        mock_input_processor.detect_input_type.return_value = InputType.EMPTY
        mock_input_processor.process_empty.return_value = "manual input"
        workspace = mock_workspace_manager.get_current_workspace.return_value
        agent = workspace.agents[0]

        await hotkey_processor.execute_agent()

        mock_input_processor.process_empty.assert_called_once()


class TestAgentSwitching:
    """Tests for agent switching logic (AC: #2)."""

    def test_switch_to_next_agent_exists(self, hotkey_processor):
        """Test that switch_to_next_agent method exists."""
        assert hasattr(hotkey_processor, 'switch_to_next_agent')
        assert callable(hotkey_processor.switch_to_next_agent)

    def test_switch_to_next_agent_gets_workspace(self, hotkey_processor,
                                                 mock_workspace_manager):
        """Test that switch_to_next_agent gets current workspace."""
        hotkey_processor.switch_to_next_agent()

        mock_workspace_manager.get_current_workspace.assert_called_once()

    def test_switch_to_next_agent_wraps_around(self, hotkey_processor,
                                              mock_workspace_manager):
        """Test that switch_to_next_agent wraps to beginning (AC: #2)."""
        workspace = mock_workspace_manager.get_current_workspace.return_value

        # Start at index 0
        workspace.current_agent_index = 0

        # Switch twice - should wrap around
        hotkey_processor.switch_to_next_agent()
        hotkey_processor.switch_to_next_agent()

        # Should wrap back to first agent
        # Index should be 0 again after 2 switches (0 -> 1 -> 0)
        assert workspace.current_agent_index == 0

    def test_switch_to_next_agent_updates_mini_popup(self, hotkey_processor,
                                                     mock_mini_popup):
        """Test that switch_to_next_agent updates mini popup (AC: #2, #5)."""
        hotkey_processor.switch_to_next_agent()

        # Verify mini popup was updated
        mock_mini_popup.update_display.assert_called()

    def test_switch_to_next_agent_handles_single_agent(self, hotkey_processor,
                                                       mock_workspace_manager):
        """Test that switch_to_next_agent handles single agent workspace."""
        workspace = mock_workspace_manager.get_current_workspace.return_value
        workspace.agents = [workspace.agents[0]]  # Only one agent

        # Should not crash or show notification for single agent
        hotkey_processor.switch_to_next_agent()

        # Index should stay at 0
        assert workspace.current_agent_index == 0


class TestWorkspaceSwitching:
    """Tests for workspace switching logic (AC: #3)."""

    def test_switch_to_next_workspace_exists(self, hotkey_processor):
        """Test that switch_to_next_workspace method exists."""
        assert hasattr(hotkey_processor, 'switch_to_next_workspace')
        assert callable(hotkey_processor.switch_to_next_workspace)

    def test_switch_to_next_workspace_calls_manager(self, hotkey_processor,
                                                    mock_workspace_manager):
        """Test that switch_to_next_workspace calls workspace manager."""
        hotkey_processor.switch_to_next_workspace()

        mock_workspace_manager.switch_to_next_workspace.assert_called_once()

    def test_switch_to_next_workspace_updates_mini_popup(self, hotkey_processor,
                                                         mock_mini_popup):
        """Test that switch_to_next_workspace updates mini popup (AC: #3, #5)."""
        hotkey_processor.switch_to_next_workspace()

        mock_mini_popup.update_display.assert_called()

    def test_switch_to_next_workspace_handles_single_workspace(self, hotkey_processor,
                                                               mock_workspace_manager):
        """Test that switch_to_next_workspace handles single workspace."""
        mock_workspace_manager.list_workspaces.return_value = [
            mock_workspace_manager.get_current_workspace.return_value
        ]

        # Should not crash for single workspace
        hotkey_processor.switch_to_next_workspace()


class TestClipboardIntegration:
    """Tests for clipboard integration (AC: #6)."""

    def test_copy_to_clipboard_method_exists(self, hotkey_processor):
        """Test that _copy_to_clipboard method exists."""
        assert hasattr(hotkey_processor, '_copy_to_clipboard')
        assert callable(hotkey_processor._copy_to_clipboard)

    @patch('core.hotkey_processor.QT_AVAILABLE', True)
    @patch('core.hotkey_processor.QApplication')
    def test_copy_to_clipboard_uses_qclipboard(self, mock_qt_app, hotkey_processor):
        """Test that clipboard uses QApplication.clipboard() (AC: #6)."""
        mock_clipboard = Mock()
        mock_qt_app.instance.return_value.clipboard.return_value = mock_clipboard

        hotkey_processor._copy_to_clipboard("test result")

        # Verify clipboard.setText was called
        mock_clipboard.setText.assert_called_once_with("test result")

    @patch('core.hotkey_processor.QT_AVAILABLE', True)
    @patch('core.hotkey_processor.QApplication')
    def test_copy_to_clipboard_handles_empty_result(self, mock_qt_app, hotkey_processor):
        """Test that clipboard handles empty results gracefully (AC: #6)."""
        mock_clipboard = Mock()
        mock_qt_app.instance.return_value.clipboard.return_value = mock_clipboard

        # Should not crash with empty string
        hotkey_processor._copy_to_clipboard("")

        mock_clipboard.setText.assert_called_once_with("")


class TestErrorHandling:
    """Tests for error handling (AC: #1)."""

    @pytest.mark.asyncio
    async def test_execute_agent_catches_exceptions(self, hotkey_processor,
                                                    mock_agent_executor):
        """Test that execute_agent catches exceptions during execution."""
        # Make executor raise an exception
        mock_agent_executor.execute.side_effect = Exception("Test error")

        # Should not crash
        result = await hotkey_processor.execute_agent()

        # Should return error result
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_agent_handles_execution_failure(self, hotkey_processor,
                                                          mock_agent_executor):
        """Test that execute_agent handles execution failures."""
        # Return error result
        mock_agent_executor.execute.return_value = ExecutionResult(
            output="Error occurred",
            status="error",
            metadata={"error": "Test error"}
        )

        # Should handle error gracefully
        result = await hotkey_processor.execute_agent()

        assert result.status == "error"

    def test_handlers_catch_exceptions(self, hotkey_processor):
        """Test that hotkey handlers catch exceptions."""
        # Should not crash when called
        try:
            hotkey_processor.on_ctrl_pause()
            hotkey_processor.on_ctrl_shift_pause()
        except Exception as e:
            pytest.fail(f"Handler raised exception: {e}")
