"""
Hotkey Processor V2 - Global hotkey handling for agent execution and workspace switching (Story 9)

This module provides the HotkeyProcessorV2 class which handles global hotkeys for:
- Executing the current agent with detected input (AC: #1)
- Switching to the next agent in the current workspace (AC: #2)
- Switching to the next workspace (AC: #3)
- Copying execution results to clipboard (AC: #6)

Hotkeys:
- Pause: Execute current agent
- Ctrl+Pause: Switch to next agent
- Ctrl+Shift+Pause: Switch to next workspace

Acceptance Criteria:
1. Pause key executes current agent with detected input using InputProcessor and VirtualAgentExecutor
2. Ctrl+Pause cycles to next agent in current workspace (updates mini popup display)
3. Ctrl+Shift+Pause switches to next workspace (updates mini popup color and emoji)
4. Hotkey processor detects input type and calls InputProcessor.detect_input_type()
5. Hotkey processor updates mini popup after workspace/agent switch (calls update_display)
6. Hotkey processor copies result to clipboard after execution using QClipboard
"""

import logging
import asyncio
from typing import Optional
from pathlib import Path

# Try to import pynput for global hotkeys
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    keyboard = None
    Key = None
    KeyCode = None

# Try to import PyQt6 for clipboard
try:
    from PyQt6.QtWidgets import QApplication
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QApplication = None

from core.workspace_manager import WorkspaceManager
from core.agent_executor import VirtualAgentExecutor
from core.input_processor import InputProcessor, InputType
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent
from models.execution_result import ExecutionResult


logger = logging.getLogger(__name__)

# Hotkey constants (AC: #1, #2, #3)
HOTKEY_PAUSE = 'pause'
HOTKEY_CTRL_PAUSE = 'ctrl+pause'
HOTKEY_CTRL_SHIFT_PAUSE = 'ctrl+shift+pause'


class HotkeyProcessorV2:
    """
    Global hotkey processor for agent execution and workspace switching.

    This class handles global hotkeys using pynput library:
    - Pause key: Execute current agent with detected input
    - Ctrl+Pause: Switch to next agent in workspace
    - Ctrl+Shift+Pause: Switch to next workspace

    The processor integrates with:
    - WorkspaceManager: For workspace/agent switching
    - VirtualAgentExecutor: For agent execution
    - InputProcessor: For input type detection
    - MiniPopupV2: For display updates

    Attributes:
        workspace_manager: WorkspaceManager instance for workspace/agent management
        agent_executor: VirtualAgentExecutor instance for executing agents
        input_processor: InputProcessor instance for input detection
        mini_popup: MiniPopupV2 instance for display updates
        _debounce_timer: Timestamp for debouncing rapid hotkey presses

    Example:
        >>> processor = HotkeyProcessorV2(
        ...     workspace_manager=manager,
        ...     agent_executor=executor,
        ...     input_processor=input_proc,
        ...     mini_popup=popup
        ... )
        >>> processor.setup_hotkeys()
        >>> # Hotkeys are now active
    """

    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        agent_executor: VirtualAgentExecutor,
        input_processor: InputProcessor,
        mini_popup
    ):
        """
        Initialize HotkeyProcessorV2 with required dependencies (AC: #1, #2, #3, #5).

        Args:
            workspace_manager: WorkspaceManager instance for workspace/agent switching
            agent_executor: VirtualAgentExecutor instance for agent execution
            input_processor: InputProcessor instance for input detection and processing
            mini_popup: MiniPopupV2 instance for display updates

        Raises:
            RuntimeError: If pynput is not available

        Example:
            >>> processor = HotkeyProcessorV2(
            ...     workspace_manager=manager,
            ...     agent_executor=executor,
            ...     input_processor=input_proc,
            ...     mini_popup=popup
            ... )
        """
        self.workspace_manager = workspace_manager
        self.agent_executor = agent_executor
        self.input_processor = input_processor
        self.mini_popup = mini_popup

        # Debounce timer to prevent rapid-fire hotkey presses
        self._debounce_timer: float = 0
        self._debounce_delay: float = 0.2  # 200ms debounce delay

        # Hotkey listener (will be initialized in setup_hotkeys)
        self._listener: Optional[keyboard.Listener] = None

        # Check for pynput availability
        if not PYNPUT_AVAILABLE:
            logger.warning(
                "pynput library not available. "
                "Global hotkeys will not work. Install with: pip install pynput"
            )

        logger.info("HotkeyProcessorV2 initialized")

    def setup_hotkeys(self) -> None:
        """
        Register global hotkeys for agent execution and workspace switching (AC: #1, #2, #3).

        This method sets up the following hotkeys:
        - Pause key: Execute current agent
        - Ctrl+Pause: Switch to next agent
        - Ctrl+Shift+Pause: Switch to next workspace

        Hotkey conflicts are handled gracefully - if a hotkey fails to register,
        a warning is logged but the system continues to function.

        Returns:
            None

        Raises:
            RuntimeError: If pynput is not available

        Note:
            This method uses pynput's keyboard.Listener with hotkey support.
            The listener runs in a separate thread and processes hotkeys globally.

        Example:
            >>> processor.setup_hotkeys()
            >>> # Hotkeys are now registered and active
        """
        if not PYNPUT_AVAILABLE:
            raise RuntimeError("pynput library not available for global hotkeys")

        try:
            # Create a mapping of hotkeys to handlers
            hotkeys = {
                HOTKEY_PAUSE: self._on_pause_wrapper,
                HOTKEY_CTRL_PAUSE: self._on_ctrl_pause_wrapper,
                HOTKEY_CTRL_SHIFT_PAUSE: self._on_ctrl_shift_pause_wrapper
            }

            # Create and start the listener
            self._listener = keyboard.GlobalHotKeys(hotkeys)
            self._listener.start()

            logger.info(f"Global hotkeys registered: {list(hotkeys.keys())}")

        except Exception as e:
            logger.error(f"Failed to register global hotkeys: {e}")
            # Cleanup listener if it was partially created
            if self._listener:
                try:
                    self._listener.stop()
                except:
                    pass
                self._listener = None
            raise

    def _on_pause_wrapper(self) -> None:
        """
        Wrapper for Pause key handler with debouncing.

        This wrapper ensures rapid-fire hotkey presses are debounced
        to prevent accidental multiple executions.
        """
        self._debounce_and_execute("on_pause", self.on_pause)

    def _on_ctrl_pause_wrapper(self) -> None:
        """
        Wrapper for Ctrl+Pause handler with debouncing.
        """
        self._debounce_and_execute("on_ctrl_pause", self.on_ctrl_pause)

    def _on_ctrl_shift_pause_wrapper(self) -> None:
        """
        Wrapper for Ctrl+Shift+Pause handler with debouncing.
        """
        self._debounce_and_execute("on_ctrl_shift_pause", self.on_ctrl_shift_pause)

    def _debounce_and_execute(self, handler_name: str, handler_func) -> None:
        """
        Execute handler with debouncing to prevent rapid-fire presses.

        Updates debounce timer AFTER handler execution to prevent overlapping
        executions when handlers take longer than debounce delay.

        Args:
            handler_name: Name of the handler (for logging)
            handler_func: Handler function to execute

        Returns:
            None

        Raises:
            Exceptions from handler_func are caught and logged
        """
        import time

        current_time = time.time()

        # Check if enough time has passed since last hotkey
        if current_time - self._debounce_timer < self._debounce_delay:
            logger.debug(f"Debounced {handler_name} - too soon")
            return

        # Execute handler
        try:
            logger.debug(f"Executing {handler_name}")
            handler_func()
            # Update debounce timer AFTER successful execution
            self._debounce_timer = current_time
        except Exception as e:
            logger.error(f"Error in {handler_name}: {e}", exc_info=True)
            # Still update timer on error to prevent error spam
            self._debounce_timer = current_time

    def on_pause(self) -> None:
        """
        Handle Pause key press - execute current agent (AC: #1).

        This method:
        1. Detects input type using InputProcessor
        2. Processes input based on type
        3. Gets current workspace and agent
        4. Executes agent
        5. Copies result to clipboard
        6. Shows success notification

        The method executes asynchronously and handles errors gracefully.

        Note:
            This method is called from the hotkey handler thread.
            Execution happens asynchronously to avoid blocking the hotkey thread.
            Handles both running event loops and creates new one if needed.

        Example:
            >>> When Pause key is pressed, this handler executes the current agent
        """
        try:
            # Try to get running event loop
            try:
                loop = asyncio.get_running_loop()
                # Create task in running loop
                loop.create_task(self.execute_agent())
                logger.debug("Scheduled agent execution in running event loop")
            except RuntimeError:
                # No running loop, create new one
                asyncio.run(self.execute_agent())
                logger.debug("Created new event loop for agent execution")
        except Exception as e:
            logger.error(f"Error executing agent on Pause: {e}", exc_info=True)

    def on_ctrl_pause(self) -> None:
        """
        Handle Ctrl+Pause key press - switch to next agent (AC: #2).

        This method:
        1. Gets current workspace
        2. Gets list of enabled agents
        3. Moves to next agent (wraps to beginning if at end)
        4. Updates workspace_manager.current_agent_index
        5. Calls mini_popup.update_display()

        If workspace has only 1 agent, shows notification instead.

        Note:
            This method is called from the hotkey handler thread.

        Example:
            >>> When Ctrl+Pause is pressed, switches to next agent in workspace
        """
        try:
            self.switch_to_next_agent()
        except Exception as e:
            logger.error(f"Error switching agent on Ctrl+Pause: {e}", exc_info=True)
            self._show_notification(f"Failed to switch agent: {e}", success=False)

    def on_ctrl_shift_pause(self) -> None:
        """
        Handle Ctrl+Shift+Pause key press - switch to next workspace (AC: #3).

        This method:
        1. Gets list of all workspaces
        2. Finds index of current workspace
        3. Moves to next workspace (wraps to beginning if at end)
        4. Calls workspace_manager.switch_workspace()
        5. Calls mini_popup.update_display()

        If only 1 workspace exists, shows notification instead.

        Note:
            This method is called from the hotkey handler thread.

        Example:
            >>> When Ctrl+Shift+Pause is pressed, switches to next workspace
        """
        try:
            self.switch_to_next_workspace()
        except Exception as e:
            logger.error(f"Error switching workspace on Ctrl+Shift+Pause: {e}", exc_info=True)
            self._show_notification(f"Failed to switch workspace: {e}", success=False)

    async def execute_agent(self) -> ExecutionResult:
        """
        Execute current agent with detected input (AC: #1, #4, #6).

        This method implements the full execution flow:
        1. Detect input type using input_processor.detect_input_type()
        2. Process input based on type (text, file, empty, url)
        3. Get current workspace and agent
        4. Execute agent using agent_executor.execute()
        5. Copy result to clipboard
        6. Show notification

        Returns:
            ExecutionResult with output, status, and metadata

        Raises:
            Exception: If execution fails (caught and logged)

        Example:
            >>> result = await execute_agent()
            >>> if result.is_success():
            ...     print(result.output)
        """
        try:
            # Step 1: Detect input type (AC: #4)
            input_type = await self.input_processor.detect_input_type()
            logger.info(f"Detected input type: {input_type}")

            # Step 2: Process input based on type (AC: #4)
            processed_input = await self._process_input_by_type(input_type)

            if processed_input is None:
                logger.warning("No input available for processing")
                return ExecutionResult(
                    output="No input available",
                    status="error",
                    metadata={"error": "No input provided"}
                )

            # Step 3: Get current workspace and agent (AC: #1)
            workspace = self.workspace_manager.get_current_workspace()
            if workspace is None:
                logger.error("No current workspace")
                return ExecutionResult(
                    output="No workspace selected",
                    status="error",
                    metadata={"error": "No current workspace"}
                )

            agent = workspace.agents[workspace.current_agent_index] if workspace.agents else None
            if agent is None:
                logger.error(f"No agents in workspace {workspace.id}")
                return ExecutionResult(
                    output=f"No agents enabled in workspace {workspace.name}",
                    status="error",
                    metadata={"error": "No agents available"}
                )

            # Step 4: Execute agent (AC: #1)
            logger.info(f"Executing agent {agent.id} with input type {input_type}")
            result = await self.agent_executor.execute(
                agent=agent,
                input_text=processed_input,
                workspace=workspace
            )

            # Step 5: Copy result to clipboard (AC: #6)
            if result.output:
                self._copy_to_clipboard(result.output)
                logger.info(f"Copied result to clipboard ({len(result.output)} chars)")

            # Step 6: Show notification
            self._show_notification(
                f"Agent {agent.name} executed",
                success=(result.status == "success")
            )

            return result

        except Exception as e:
            logger.error(f"Error executing agent: {e}", exc_info=True)
            self._show_notification(f"Agent execution failed: {e}", success=False)
            return ExecutionResult(
                output=f"Execution error: {e}",
                status="error",
                metadata={"error": str(e)}
            )

    async def _process_input_by_type(self, input_type: InputType) -> Optional[str]:
        """
        Process input based on detected type.

        Args:
            input_type: Detected input type from InputProcessor

        Returns:
            Processed input string, or None if input is not available

        Example:
            >>> input_text = await _process_input_by_type(InputType.TEXT)
        """
        try:
            # Handle both enum and string values for compatibility
            if isinstance(input_type, str):
                # Legacy support for string input types
                logger.debug(f"Processing input type (string): {input_type}")
                if input_type == "text":
                    return self.input_processor.process_text()
                elif input_type == "url":
                    url = self.input_processor.process_text()
                    if url:
                        return await self.input_processor.process_url(url)
                    return None
                elif input_type == "empty":
                    workspace = self.workspace_manager.get_current_workspace()
                    if workspace and workspace.agents:
                        agent = workspace.agents[workspace.current_agent_index]
                        return self.input_processor.process_empty(agent.name)
                    return None
                else:
                    logger.warning(f"Unhandled input type (string): {input_type}")
                    return None

            # Handle enum values (preferred)
            logger.debug(f"Processing input type (enum): {input_type}")
            if input_type == InputType.TEXT:
                return self.input_processor.process_text()

            elif input_type == InputType.URL:
                # For URL, get the URL from clipboard first
                url = self.input_processor.process_text()
                if url:
                    return await self.input_processor.process_url(url)
                return None

            elif input_type == InputType.EMPTY:
                # Get agent name for prompt
                workspace = self.workspace_manager.get_current_workspace()
                if workspace and workspace.agents:
                    agent = workspace.agents[workspace.current_agent_index]
                    return self.input_processor.process_empty(agent.name)
                return None

            else:
                logger.warning(f"Unhandled input type: {input_type}")
                return None

        except Exception as e:
            logger.error(f"Error processing input type {input_type}: {e}")
            return None

    def switch_to_next_agent(self) -> None:
        """
        Switch to the next agent in the current workspace (AC: #2).

        This method:
        1. Gets current workspace from workspace_manager
        2. Gets list of enabled agents in workspace
        3. Finds index of current agent
        4. Moves to next agent (wraps around to beginning if at end)
        5. Updates workspace.current_agent_index
        6. Calls mini_popup.update_display()

        If workspace has only 1 agent, shows notification instead of switching.

        Example:
            >>> processor.switch_to_next_agent()
            >>> # Mini popup updates with new agent name
        """
        try:
            # Get current workspace
            workspace = self.workspace_manager.get_current_workspace()
            if workspace is None:
                logger.warning("No current workspace for agent switch")
                return

            # Get enabled agents
            agents = [a for a in workspace.agents if a.enabled]

            if len(agents) <= 1:
                # Only one agent - show notification
                logger.info(f"Only {len(agents)} agent(s) in workspace, no switch needed")
                self._show_notification(f"Only {len(agents)} agent(s) in workspace")
                return

            # Get current agent index
            current_index = workspace.current_agent_index
            current_agent = workspace.agents[current_index] if current_index < len(workspace.agents) else None

            # Find current agent in enabled agents list
            enabled_index = -1
            if current_agent in agents:
                enabled_index = agents.index(current_agent)

            # Calculate next index (wrap to beginning)
            next_index = (enabled_index + 1) % len(agents)
            next_agent = agents[next_index]

            # Find next agent's index in all agents list
            new_index = workspace.agents.index(next_agent)

            # Update workspace
            workspace.current_agent_index = new_index

            # Update mini popup (AC: #2, #5)
            self.mini_popup.update_display(workspace, next_agent)

            logger.info(f"Switched to agent {next_agent.name} in workspace {workspace.name}")
            self._show_notification(f"Agent: {next_agent.name}")

        except Exception as e:
            logger.error(f"Error switching agent: {e}", exc_info=True)
            self._show_notification(f"Failed to switch agent: {e}", success=False)

    def switch_to_next_workspace(self) -> None:
        """
        Switch to the next workspace (AC: #3).

        This method:
        1. Gets list of all workspaces from workspace_manager
        2. Finds index of current workspace
        3. Moves to next workspace (wraps around to beginning if at end)
        4. Calls workspace_manager.switch_to_next_workspace()
        5. Calls mini_popup.update_display()

        If only 1 workspace exists, shows notification instead of switching.

        Example:
            >>> processor.switch_to_next_workspace()
            >>> # Mini popup updates with new workspace color and emoji
        """
        try:
            # Get list of workspaces
            workspaces = self.workspace_manager.list_workspaces()

            if len(workspaces) <= 1:
                # Only one workspace - show notification
                logger.info(f"Only {len(workspaces)} workspace(s), no switch needed")
                self._show_notification(f"Only {len(workspaces)} workspace(s)")
                return

            # Switch workspace
            self.workspace_manager.switch_to_next_workspace()

            # Get new workspace and agent
            new_workspace = self.workspace_manager.get_current_workspace()
            if new_workspace and new_workspace.agents:
                current_agent = new_workspace.agents[new_workspace.current_agent_index]

                # Update mini popup (AC: #3, #5)
                self.mini_popup.update_display(new_workspace, current_agent)

                logger.info(f"Switched to workspace {new_workspace.name}")
                self._show_notification(f"Workspace: {new_workspace.name} {new_workspace.emoji}")

        except Exception as e:
            logger.error(f"Error switching workspace: {e}", exc_info=True)
            self._show_notification(f"Failed to switch workspace: {e}", success=False)

    def _copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to clipboard using QClipboard (AC: #6).

        Args:
            text: Text to copy to clipboard

        Raises:
            RuntimeError: If QApplication is not available

        Note:
            Handles empty results gracefully - copies empty string without error.

        Example:
            >>> processor._copy_to_clipboard("Result text")
            >>> # Text is now in clipboard
        """
        if not QT_AVAILABLE:
            logger.warning("PyQt6 not available for clipboard operations")
            return

        try:
            app = QApplication.instance()
            if app is None:
                logger.warning("QApplication instance not found")
                return

            clipboard = app.clipboard()
            clipboard.setText(text)

            logger.debug(f"Copied {len(text)} characters to clipboard")

        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")

    def _show_notification(self, message: str, success: bool = True) -> None:
        """
        Show notification to user.

        Args:
            message: Notification message
            success: Whether operation was successful (affects notification style)

        Note:
            This is a placeholder for Story 11 (Activity Log & Notifications).
            For now, just log the message.

        Example:
            >>> processor._show_notification("Agent executed successfully")
        """
        # Placeholder for Story 11
        # For now, just log
        level = logger.info if success else logger.warning
        level(f"Notification: {message}")

    def stop(self) -> None:
        """
        Stop the hotkey listener and cleanup resources.

        This method stops the global hotkey listener and releases resources.

        Example:
            >>> processor.stop()
            >>> # Hotkeys are no longer active
        """
        if self._listener:
            self._listener.stop()
            logger.info("Hotkey listener stopped")
