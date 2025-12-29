#!/usr/bin/env python3
"""
Mini Popup V2 Demo - Test different workspace configurations.

This script demonstrates the MiniPopupV2 widget with various workspace
and agent configurations to verify visual appearance and functionality.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

from ui.mini_popup_v2 import MiniPopupV2
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent


class MiniPopupDemoWindow(QMainWindow):
    """Demo window showing multiple MiniPopupV2 instances."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Popup V2 Demo")
        self.setGeometry(100, 100, 400, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Setup layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create test workspaces and agents
        self.create_test_examples(layout)

    def create_test_examples(self, layout):
        """Create various test examples of MiniPopupV2."""

        # Example 1: Python Workspace with command agent
        python_workspace = Workspace(
            id="python",
            name="Python Projects",
            folder=Path("/python"),
            emoji="🐍",
            color="#0078d4"
        )
        python_agent = VirtualAgent(
            id="verify-python",
            type="command",
            name="verify-python",
            description="Verify Python scripts",
            source_file=Path("/agents/verify_python.py"),
            emoji="✓",
            color="#0078d4",
            enabled=True
        )
        popup1 = self.create_popup("Python Workspace - verify-python (command)", python_workspace, python_agent)
        layout.addWidget(popup1)

        # Example 2: Web-Dev Workspace with skill agent
        web_workspace = Workspace(
            id="web-dev",
            name="Web-Dev",
            folder=Path("/web"),
            emoji="🌐",
            color="#107c10"
        )
        web_agent = VirtualAgent(
            id="ux-ui-improver",
            type="skill",
            name="ux-ui-improver",
            description="Improve UI/UX design",
            source_file=Path("/agents/ux_ui.py"),
            emoji="🎨",
            color="#FF5733",
            enabled=True
        )
        popup2 = self.create_popup("Web-Dev Workspace - ux-ui-improver (skill)", web_workspace, web_agent)
        layout.addWidget(popup2)

        # Example 3: Docs Workspace with agent type
        docs_workspace = Workspace(
            id="docs",
            name="Docs",
            folder=Path("/docs"),
            emoji="📚",
            color="#d83b01"
        )
        docs_agent = VirtualAgent(
            id="doc-writer",
            type="agent",
            name="doc-writer",
            description="Write documentation",
            source_file=Path("/agents/doc_writer.py"),
            emoji="📝",
            color="#d83b01",
            enabled=True
        )
        popup3 = self.create_popup("Docs Workspace - doc-writer (agent)", docs_workspace, docs_agent)
        layout.addWidget(popup3)

        # Example 4: Long agent name (truncation test)
        long_agent = VirtualAgent(
            id="very-long-agent-name",
            type="command",
            name="very-long-agent-name-test",
            description="Test truncation",
            source_file=Path("/test.py"),
            emoji="✓",
            color="#0078d4",
            enabled=True
        )
        popup4 = self.create_popup("Python Workspace - Long name truncation", python_workspace, long_agent)
        layout.addWidget(popup4)

        # Add stretch to push items to top
        layout.addStretch()

    def create_popup(self, label_text: str, workspace: Workspace, agent: VirtualAgent) -> QWidget:
        """Create a container widget with label and popup."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(5)

        # Create description label
        from PyQt6.QtWidgets import QLabel
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 10pt; color: #333;")
        container_layout.addWidget(label)

        # Create mini popup
        popup = MiniPopupV2()
        popup.update_display(workspace, agent)
        container_layout.addWidget(popup)

        return container


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)

    window = MiniPopupDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
