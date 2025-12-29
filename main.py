"""
AgentClick V2 - Main Entry Point

This is the primary entry point for the AgentClick V2 application.
It initializes and integrates all system components following the startup flow.

Usage:
    python main.py
    python -m agentclick_v2

Story: 0-Integration & Bootstrap
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to Python path
# The core modules are in @agentclick-v2 directory
project_root = Path(__file__).parent / '@agentclick-v2'
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add parent directory to path for imports
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

# PyQt6 imports
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QApplication = None
    QMessageBox = None

# Core system imports
from core.workspace_manager import WorkspaceManager
from core.agent_loader import DynamicAgentLoader
from core.hotkey_processor import HotkeyProcessorV2
from core.input_processor import InputProcessor
from core.agent_executor import VirtualAgentExecutor
from core.template_engine import TemplateEngine

# UI imports
from ui.mini_popup_v2 import MiniPopupV2
from ui.popup_window_v2 import DetailedPopupV2

# Utility imports
from utils.logger_v2 import LoggerV2, LogLevel, LogCategory
from utils.notification_manager import NotificationManager, NotificationType

# Project metadata
PROJECT_NAME = "AgentClick V2"
PROJECT_VERSION = "2.0.0"
PROJECT_ORGANIZATION = "AgentClick"


def _show_critical_error(message: str, details: Optional[str] = None) -> None:
    """
    Show a critical error dialog to the user.

    Args:
        message: The main error message
        details: Optional detailed error information
    """
    if PYQT6_AVAILABLE and QMessageBox:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(f"{PROJECT_NAME} - Startup Error")
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    else:
        print(f"ERROR: {message}", file=sys.stderr)
        if details:
            print(f"Details: {details}", file=sys.stderr)


def _create_default_workspace(workspace_manager: WorkspaceManager) -> None:
    """
    Create a default workspace for first-time setup.
    Uses atomic file creation to prevent race conditions.

    Args:
        workspace_manager: WorkspaceManager instance to create workspace in
    """
    import tempfile
    import os

    try:
        from models.workspace import Workspace
        import yaml
        from datetime import datetime

        # Create config directory if it doesn't exist
        config_dir = workspace_manager.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create default workspace
        default_workspace = Workspace(
            id="default",
            name="Default Workspace",
            folder=Path.cwd(),
            emoji="🚀",
            color="#0078d4",
            agents=[]  # Empty list, will be populated by scan
        )

        # Save to config file
        workspaces_data = {
            'version': '2.0',
            'current_workspace': default_workspace.id,
            'workspaces': {
                default_workspace.id: {
                    'name': default_workspace.name,
                    'folder': str(default_workspace.folder),
                    'emoji': default_workspace.emoji,
                    'color': default_workspace.color,
                    'agents': []
                }
            }
        }

        # Use atomic file creation to prevent race conditions
        # Create temp file first
        temp_fd, temp_path = tempfile.mkstemp(
            prefix='.workspace_tmp_',
            suffix='.yaml',
            dir=config_dir
        )

        try:
            # Write to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(workspaces_data, f, allow_unicode=True, default_flow_style=False)

            # Atomic rename (will fail if another process created it first)
            try:
                os.replace(temp_path, workspace_manager.config_path)
                print(f"✅ Created default workspace at {workspace_manager.config_path}")
            except FileExistsError:
                # Another process created the file first - clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                print(f"ℹ️  Workspace config already created by another process")
        except Exception as e:
            # Clean up temp file if write failed
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            raise

    except Exception as e:
        print(f"⚠️  Failed to create default workspace: {e}", file=sys.stderr)
        raise


async def _initialize_core_systems(logger: LoggerV2) -> tuple:
    """
    Initialize core systems (WorkspaceManager, DynamicAgentLoader).

    Args:
        logger: Logger instance for logging initialization progress

    Returns:
        Tuple of (workspace_manager, agent_loader)

    Raises:
        Exception: If initialization fails critically
    """
    logger.add_log_entry(
        category=LogCategory.INFO,
        message="Initializing core systems..."
    )

    # Initialize WorkspaceManager
    workspace_manager = WorkspaceManager()

    try:
        await workspace_manager.load_workspaces()
        logger.add_log_entry(
            category=LogCategory.SUCCESS,
            message=f"Loaded {len(workspace_manager.workspaces)} workspace(s)"
        )
    except FileNotFoundError:
        # First-run scenario - create default workspace
        logger.add_log_entry(
            category=LogCategory.INFO,
            message="No workspaces config found - creating default workspace"
        )
        _create_default_workspace(workspace_manager)
        await workspace_manager.load_workspaces()
        logger.add_log_entry(
            category=LogCategory.SUCCESS,
            message="Default workspace created and loaded"
        )
    except Exception as e:
        logger.add_log_entry(
            category=LogCategory.ERROR,
            message=f"Failed to load workspaces: {e}"
        )
        raise

    # Initialize DynamicAgentLoader
    agent_loader = DynamicAgentLoader()
    try:
        agents = await agent_loader.scan_all()
        logger.add_log_entry(
            category=LogCategory.SUCCESS,
            message=f"Loaded {len(agents)} agent(s) from .claude/"
        )
    except Exception as e:
        logger.add_log_entry(
            category=LogCategory.WARNING,
            message=f"Failed to load agents: {e}"
        )
        # Continue anyway - agents can be scanned from UI

    return workspace_manager, agent_loader


def _initialize_ui_components(workspace_manager, agent_loader, logger: LoggerV2) -> tuple:
    """
    Initialize UI components (MiniPopupV2, PopupWindowV2).

    Args:
        workspace_manager: WorkspaceManager instance
        agent_loader: DynamicAgentLoader instance
        logger: Logger instance

    Returns:
        Tuple of (mini_popup, popup_window)
    """
    logger.add_log_entry(
        category=LogCategory.INFO,
        message="Initializing UI components..."
    )

    # Create MiniPopupV2
    mini_popup = MiniPopupV2()

    # Create DetailedPopupV2
    popup_window = DetailedPopupV2()
    popup_window.workspace_manager = workspace_manager
    popup_window.agent_loader = agent_loader

    logger.add_log_entry(
        category=LogCategory.SUCCESS,
        message="UI components initialized"
    )

    return mini_popup, popup_window


def _initialize_hotkey_system(
    workspace_manager,
    agent_loader,
    mini_popup,
    popup_window,
    logger: LoggerV2
) -> HotkeyProcessorV2:
    """
    Initialize hotkey system (HotkeyProcessor).

    Args:
        workspace_manager: WorkspaceManager instance
        agent_loader: DynamicAgentLoader instance
        mini_popup: MiniPopupV2 instance
        popup_window: PopupWindowV2 instance
        logger: Logger instance

    Returns:
        HotkeyProcessorV2 instance
    """
    logger.add_log_entry(
        category=LogCategory.INFO,
        message="Initializing hotkey system..."
    )

    # Create InputProcessor
    input_processor = InputProcessor()

    # Create TemplateEngine
    template_engine = TemplateEngine()

    # Create VirtualAgentExecutor
    agent_executor = VirtualAgentExecutor(template_engine=template_engine)

    # Create HotkeyProcessor
    hotkey_processor = HotkeyProcessorV2(
        workspace_manager=workspace_manager,
        agent_executor=agent_executor,
        input_processor=input_processor,
        mini_popup=mini_popup,
        activity_logger=logger,
        notification_manager=None  # Will create if needed
    )

    logger.add_log_entry(
        category=LogCategory.SUCCESS,
        message="Hotkey system initialized"
    )

    return hotkey_processor


def main() -> int:
    """
    Main entry point for AgentClick V2 application.

    This function follows the initialization sequence:
    1. Create QApplication
    2. Initialize LoggerV2
    3. Load WorkspaceManager and DynamicAgentLoader
    4. Create UI components
    5. Initialize HotkeyProcessor
    6. Start hotkey listener
    7. Enter Qt event loop

    Returns:
        Exit code (0 for success, non-zero for error)

    Raises:
        SystemExit: On application exit
    """
    # Check if PyQt6 is available
    if not PYQT6_AVAILABLE:
        _show_critical_error(
            "PyQt6 is not installed",
            "Please install PyQt6 to run AgentClick V2:\n\npip install PyQt6"
        )
        sys.exit(1)

    # Check for existing QApplication instance
    existing_app = QApplication.instance()
    if existing_app is None:
        # Create QApplication instance
        app = QApplication(sys.argv)
    else:
        app = existing_app

    # Set application metadata
    app.setApplicationName(PROJECT_NAME)
    app.setApplicationVersion(PROJECT_VERSION)
    app.setOrganizationName(PROJECT_ORGANIZATION)

    # Initialize logger
    logger = LoggerV2()
    logger.add_log_entry(
        category=LogCategory.INFO,
        message=f"Starting {PROJECT_NAME} v{PROJECT_VERSION}"
    )

    # Initialize core systems (async) using asyncio.run for proper lifecycle
    try:
        workspace_manager, agent_loader = asyncio.run(
            _initialize_core_systems(logger)
        )
    except Exception as e:
        error_msg = f"Failed to initialize core systems: {e}"
        logger.add_log_entry(
            category=LogCategory.ERROR,
            message=error_msg
        )
        _show_critical_error(error_msg, str(e))
        sys.exit(1)

    # Validate workspace loading succeeded
    if not workspace_manager.workspaces:
        logger.add_log_entry(
            category=LogCategory.ERROR,
            message="No workspaces loaded - cannot start"
        )
        _show_critical_error(
            "Failed to load workspaces",
            "Please check config/workspaces.yaml exists and is valid"
        )
        sys.exit(1)

    if workspace_manager.get_current_workspace() is None:
        logger.add_log_entry(
            category=LogCategory.WARNING,
            message="No current workspace set - using first available"
        )
        workspace_manager.switch_workspace(workspace_manager.list_workspaces()[0].id)

    try:
        # Initialize UI components
        mini_popup, popup_window = _initialize_ui_components(
            workspace_manager, agent_loader, logger
        )

        # Initialize hotkey system
        hotkey_processor = _initialize_hotkey_system(
            workspace_manager, agent_loader,
            mini_popup, popup_window, logger
        )

        # Start hotkey listener (drives the system) with validation
        try:
            hotkey_processor.setup_hotkeys()

            # Verify hotkeys registered successfully
            if hasattr(hotkey_processor, '_listener') and hotkey_processor._listener is None:
                logger.add_log_entry(
                    category=LogCategory.WARNING,
                    message="Hotkey processor failed to start - running in UI-only mode"
                )
                notification_mgr = NotificationManager()
                notification_mgr.show_notification(
                    type=NotificationType.WARNING,
                    title="Global Hotkeys Unavailable",
                    message="Hotkey registration failed. Use the UI to execute agents."
                )
            else:
                logger.add_log_entry(
                    category=LogCategory.SUCCESS,
                    message="Hotkey system started successfully"
                )
        except Exception as e:
            logger.add_log_entry(
                category=LogCategory.WARNING,
                message=f"Failed to start hotkey processor: {e} - continuing in UI-only mode"
            )
            notification_mgr = NotificationManager()
            notification_mgr.show_notification(
                type=NotificationType.WARNING,
                title="Global Hotkeys Unavailable",
                message=f"Hotkey registration failed: {e}\n\nUse the UI to execute agents."
            )

        logger.add_log_entry(
            category=LogCategory.SUCCESS,
            message="Application initialized successfully"
        )
        logger.add_log_entry(
            category=LogCategory.INFO,
            message="Press Pause to execute current agent"
        )

        # Show welcome notification for first run
        if len(workspace_manager.workspaces) == 1:
            notification_mgr = NotificationManager()
            notification_mgr.show_notification(
                type=NotificationType.INFO,
                title="Welcome to AgentClick V2!",
                message="Press Pause to execute agents, Ctrl+Pause to switch agents"
            )

        # Enter Qt event loop (blocks until app quits)
        exit_code = app.exec()

        # Cleanup on exit
        logger.add_log_entry(
            category=LogCategory.INFO,
            message="Shutting down..."
        )

        # Stop hotkey processor
        try:
            hotkey_processor.stop()
        except Exception as e:
            logger.add_log_entry(
                category=LogCategory.WARNING,
                message=f"Error stopping hotkey processor: {e}"
            )

        # Save workspace state if modified
        # (workspace_manager handles this automatically)

        logger.add_log_entry(
            category=LogCategory.SUCCESS,
            message="Shutdown complete"
        )

        sys.exit(exit_code)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully with proper cleanup
        logger.add_log_entry(
            category=LogCategory.INFO,
            message="Interrupted by user"
        )

        # Cleanup before exit
        try:
            if 'hotkey_processor' in locals():
                hotkey_processor.stop()
        except Exception as e:
            logger.add_log_entry(
                category=LogCategory.WARNING,
                message=f"Error stopping hotkey processor: {e}"
            )

        sys.exit(0)

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Failed to initialize application: {e}"
        logger.add_log_entry(
            category=LogCategory.ERROR,
            message=error_msg
        )
        _show_critical_error(error_msg, str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
