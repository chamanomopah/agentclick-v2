"""
Test suite for MiniPopupV2 class.

This module tests the MiniPopupV2 widget which displays workspace and agent
information in a compact popup format.
"""
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.mini_popup_v2 import MiniPopupV2
from models.workspace import Workspace
from models.virtual_agent import VirtualAgent


# Fixtures
@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_workspace():
    """Create a sample workspace for testing."""
    return Workspace(
        id="python",
        name="Python Projects",
        folder=Path("/python"),
        emoji="🐍",
        color="#0078d4"
    )


@pytest.fixture
def sample_agent():
    """Create a sample virtual agent for testing."""
    return VirtualAgent(
        id="verify-python",
        type="command",
        name="verify-python",
        description="Verify Python code",
        source_file=Path("/agents/verify_python.py"),
        emoji="✓",
        color="#0078d4",
        enabled=True
    )


@pytest.fixture
def mini_popup(qapp):
    """Create MiniPopupV2 instance for testing."""
    return MiniPopupV2()


# Test: Basic Widget Properties (AC: #5)
class TestMiniPopupBasicProperties:
    """Test basic widget properties and initialization."""

    def test_initial_size(self, mini_popup):
        """Test that mini popup has correct initial size (80x60px)."""
        assert mini_popup.width() == 80, f"Expected width 80, got {mini_popup.width()}"
        assert mini_popup.height() == 60, f"Expected height 60, got {mini_popup.height()}"

    def test_fixed_size(self, mini_popup):
        """Test that mini popup has fixed size (cannot be resized)."""
        assert mini_popup.minimumWidth() == 80
        assert mini_popup.maximumWidth() == 80
        assert mini_popup.minimumHeight() == 60
        assert mini_popup.maximumHeight() == 60

    def test_widget_type(self, mini_popup):
        """Test that mini_popup is a QWidget."""
        from PyQt6.QtWidgets import QWidget
        assert isinstance(mini_popup, QWidget)


# Test: Layout and Components (AC: #1, #2, #3)
class TestMiniPopupLayout:
    """Test horizontal layout with three components."""

    def test_has_horizontal_layout(self, mini_popup):
        """Test that mini popup uses QHBoxLayout."""
        from PyQt6.QtWidgets import QHBoxLayout
        layout = mini_popup.layout()
        assert layout is not None, "Layout should not be None"
        assert isinstance(layout, QHBoxLayout), "Layout should be QHBoxLayout"

    def test_has_workspace_emoji_label(self, mini_popup):
        """Test that workspace emoji label exists."""
        assert hasattr(mini_popup, '_workspace_emoji_label')
        assert mini_popup._workspace_emoji_label is not None

    def test_has_agent_name_label(self, mini_popup):
        """Test that agent name label exists."""
        assert hasattr(mini_popup, '_agent_name_label')
        assert mini_popup._agent_name_label is not None

    def test_has_agent_type_icon_label(self, mini_popup):
        """Test that agent type icon label exists."""
        assert hasattr(mini_popup, '_agent_type_icon_label')
        assert mini_popup._agent_type_icon_label is not None


# Test: Update Display Method (AC: #1, #2, #3)
class TestMiniPopupUpdateDisplay:
    """Test update_display method with workspace and agent."""

    def test_update_workspace_emoji(self, mini_popup, sample_workspace):
        """Test that workspace emoji is displayed correctly."""
        mini_popup.update_display(sample_workspace, None)
        assert mini_popup._workspace_emoji_label.text() == "🐍"

    def test_update_agent_name(self, mini_popup, sample_agent):
        """Test that agent name is displayed correctly (may be truncated)."""
        mini_popup.update_display(None, sample_agent)
        # Agent name may be truncated, so check if it contains key part or is truncated properly
        text = mini_popup._agent_name_label.text()
        if len(sample_agent.name) <= mini_popup.MAX_AGENT_NAME_LENGTH:
            assert text == sample_agent.name, f"Expected '{sample_agent.name}', got '{text}'"
        else:
            assert text.endswith("..."), f"Truncated name should end with '...', got '{text}'"
            assert text.startswith(sample_agent.name[:9]), f"Truncated name should start with first 9 chars"

    def test_update_agent_type_icon_command(self, mini_popup, sample_agent):
        """Test that command agent shows 📝 icon."""
        sample_agent.type = "command"
        mini_popup.update_display(None, sample_agent)
        assert mini_popup._agent_type_icon_label.text() == "📝"

    def test_update_agent_type_icon_skill(self, mini_popup):
        """Test that skill agent shows 🎯 icon."""
        agent = VirtualAgent(
            id="ux-ui-improver",
            type="skill",
            name="ux-ui-improver",
            description="Improve UI/UX",
            source_file=Path("/agents/ux_ui.py"),
            emoji="🎨",
            color="#FF5733",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        assert mini_popup._agent_type_icon_label.text() == "🎯"

    def test_update_agent_type_icon_agent(self, mini_popup):
        """Test that agent type shows 🤖 icon."""
        agent = VirtualAgent(
            id="auto-agent",
            type="agent",
            name="Auto Agent",
            description="Autonomous agent",
            source_file=Path("/agents/auto.py"),
            emoji="🤖",
            color="#987654",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        assert mini_popup._agent_type_icon_label.text() == "🤖"


# Test: Workspace Color Theming (AC: #4)
class TestMiniPopupColorTheming:
    """Test workspace color theming functionality."""

    def test_default_background_color(self, mini_popup):
        """Test that widget has default background color."""
        style = mini_popup.styleSheet()
        assert "background-color" in style

    def test_set_workspace_color_python(self, mini_popup):
        """Test setting Python workspace color (#0078d4)."""
        mini_popup.set_workspace_color("#0078d4")
        style = mini_popup.styleSheet()
        assert "#0078d4" in style

    def test_set_workspace_color_web_dev(self, mini_popup):
        """Test setting Web-Dev workspace color (#107c10)."""
        mini_popup.set_workspace_color("#107c10")
        style = mini_popup.styleSheet()
        assert "#107c10" in style

    def test_set_workspace_color_docs(self, mini_popup):
        """Test setting Docs workspace color (#d83b01)."""
        mini_popup.set_workspace_color("#d83b01")
        style = mini_popup.styleSheet()
        assert "#d83b01" in style

    def test_text_color_contrast(self, mini_popup):
        """Test that text color is white for contrast on dark backgrounds."""
        mini_popup.set_workspace_color("#0078d4")
        style = mini_popup.styleSheet()
        assert "color: white" in style


# Test: Agent Name Truncation (AC: #2)
class TestAgentNameTruncation:
    """Test agent name truncation for long names."""

    def test_short_name_not_truncated(self, mini_popup):
        """Test that short names are not truncated."""
        agent = VirtualAgent(
            id="test",
            type="command",
            name="test",
            description="Test agent",
            source_file=Path("/test.py"),
            emoji="✓",
            color="#000",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        assert mini_popup._agent_name_label.text() == "test"

    def test_long_name_truncated_with_ellipsis(self, mini_popup):
        """Test that long names are truncated with ellipsis."""
        agent = VirtualAgent(
            id="very-long-agent-name",
            type="command",
            name="very-long-agent-name-that-exceeds-limit",
            description="Test agent",
            source_file=Path("/test.py"),
            emoji="✓",
            color="#000",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        text = mini_popup._agent_name_label.text()
        assert "..." in text or len(text) < len(agent.name)

    def test_max_length_approx_12_chars(self, mini_popup):
        """Test that max length is approximately 10-12 characters."""
        agent = VirtualAgent(
            id="test",
            type="command",
            name="twelve-char",  # 12 chars
            description="Test agent",
            source_file=Path("/test.py"),
            emoji="✓",
            color="#000",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        # 12 chars should fit without truncation
        text = mini_popup._agent_name_label.text()
        assert len(text) <= 12, f"Expected max 12 chars, got {len(text)}"


# Test: Emoji Rendering (AC: #1)
class TestEmojiRendering:
    """Test emoji rendering and scaling."""

    def test_workspace_emoji_renders(self, mini_popup, sample_workspace):
        """Test that workspace emoji renders without error."""
        mini_popup.update_display(sample_workspace, None)
        emoji = mini_popup._workspace_emoji_label.text()
        assert emoji == "🐍"
        assert len(emoji) > 0

    def test_multiple_workspace_emojis(self, mini_popup):
        """Test rendering different workspace emojis."""
        workspaces = [
            Workspace(id="python", name="Python", folder=Path("/py"), emoji="🐍", color="#0078d4"),
            Workspace(id="web", name="Web-Dev", folder=Path("/web"), emoji="🌐", color="#107c10"),
            Workspace(id="docs", name="Docs", folder=Path("/docs"), emoji="📚", color="#d83b01"),
        ]
        for ws in workspaces:
            mini_popup.update_display(ws, None)
            assert mini_popup._workspace_emoji_label.text() == ws.emoji

    def test_emoji_font_size(self, mini_popup, sample_workspace):
        """Test that emoji has appropriate font size (16-20px)."""
        mini_popup.update_display(sample_workspace, None)
        font = mini_popup._workspace_emoji_label.font()
        assert 14 <= font.pointSize() <= 22  # Allow some flexibility


# Test: Hover Tooltip (UX Enhancement)
class TestHoverTooltip:
    """Test hover tooltip functionality."""

    def test_tooltip_on_hover(self, mini_popup, sample_workspace, sample_agent):
        """Test that tooltip shows full details."""
        mini_popup.update_display(sample_workspace, sample_agent)
        tooltip = mini_popup.toolTip()
        assert sample_workspace.name in tooltip
        assert sample_agent.name in tooltip
        assert sample_agent.type in tooltip

    def test_tooltip_format(self, mini_popup, sample_workspace, sample_agent):
        """Test tooltip format: 'Workspace - Agent (type)'."""
        mini_popup.update_display(sample_workspace, sample_agent)
        tooltip = mini_popup.toolTip()
        # Check that tooltip contains the key information
        assert sample_workspace.name in tooltip
        assert sample_agent.name in tooltip
        assert sample_agent.type in tooltip

    def test_tooltip_includes_hotkey_hints(self, mini_popup, sample_workspace, sample_agent):
        """Test that tooltip includes hotkey hints."""
        mini_popup.update_display(sample_workspace, sample_agent)
        tooltip = mini_popup.toolTip()
        assert "Pause" in tooltip or "hotkey" in tooltip.lower()


# Test: Integration Examples (AC: #1-5)
class TestMiniPopupExamples:
    """Test real-world workspace examples from acceptance criteria."""

    def test_python_workspace_example(self, mini_popup):
        """Test Python workspace example (🐍, #0078d4, verify-python)."""
        workspace = Workspace(
            id="python",
            name="Python",
            folder=Path("/python"),
            emoji="🐍",
            color="#0078d4"
        )
        agent = VirtualAgent(
            id="verify-python",
            type="command",
            name="verify-python",
            description="Verify Python scripts",
            source_file=Path("/agents/verify_python.py"),
            emoji="✓",
            color="#0078d4",
            enabled=True
        )
        mini_popup.update_display(workspace, agent)

        # Verify all components
        assert mini_popup._workspace_emoji_label.text() == "🐍"
        # Agent name may be displayed fully or truncated
        text = mini_popup._agent_name_label.text()
        assert "verify-python" == text or text.startswith("verify-p")
        assert mini_popup._agent_type_icon_label.text() == "📝"
        assert "#0078d4" in mini_popup.styleSheet()

    def test_web_dev_workspace_example(self, mini_popup):
        """Test Web-Dev workspace example (🌐, #107c10)."""
        workspace = Workspace(
            id="web-dev",
            name="Web-Dev",
            folder=Path("/web"),
            emoji="🌐",
            color="#107c10"
        )
        mini_popup.update_display(workspace, None)
        assert mini_popup._workspace_emoji_label.text() == "🌐"
        assert "#107c10" in mini_popup.styleSheet()

    def test_docs_workspace_example(self, mini_popup):
        """Test Docs workspace example (📚, #d83b01)."""
        workspace = Workspace(
            id="docs",
            name="Docs",
            folder=Path("/docs"),
            emoji="📚",
            color="#d83b01"
        )
        mini_popup.update_display(workspace, None)
        assert mini_popup._workspace_emoji_label.text() == "📚"
        assert "#d83b01" in mini_popup.styleSheet()


# Test: Performance (Performance Targets)
class TestMiniPopupPerformance:
    """Test performance requirements."""

    def test_update_display_performance(self, mini_popup, sample_workspace, sample_agent):
        """Test that update_display completes in < 10ms on average."""
        import time
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            mini_popup.update_display(sample_workspace, sample_agent)
        elapsed = (time.perf_counter() - start) / iterations * 1000  # Average in ms
        assert elapsed < 10, f"Average update took {elapsed:.2f}ms, expected < 10ms"


# Test: Edge Cases
class TestMiniPopupEdgeCases:
    """Test edge cases and error handling."""

    def test_none_workspace(self, mini_popup):
        """Test handling None workspace."""
        mini_popup.update_display(None, None)
        # Should not crash
        assert mini_popup is not None

    def test_none_agent(self, mini_popup, sample_workspace):
        """Test handling None agent."""
        mini_popup.update_display(sample_workspace, None)
        # Should show workspace but no agent
        assert mini_popup._workspace_emoji_label.text() == sample_workspace.emoji

    def test_empty_agent_name(self, mini_popup):
        """Test handling empty agent name."""
        agent = VirtualAgent(
            id="empty",
            type="command",
            name="",
            description="Empty name",
            source_file=Path("/empty.py"),
            emoji="",
            color="#000",
            enabled=True
        )
        mini_popup.update_display(None, agent)
        # Should not crash
        assert mini_popup is not None

    def test_invalid_agent_name_none(self, mini_popup):
        """Test that None agent name raises ValueError."""
        with pytest.raises(ValueError, match="must be a non-null string"):
            mini_popup._truncate_agent_name(None)

    def test_invalid_agent_name_type(self, mini_popup):
        """Test that non-string agent name raises ValueError."""
        with pytest.raises(ValueError, match="must be a non-null string"):
            mini_popup._truncate_agent_name(123)

    def test_invalid_color_format(self, mini_popup):
        """Test handling invalid color format."""
        # Should handle gracefully
        mini_popup.set_workspace_color("invalid")
        # Widget should still be functional
        assert mini_popup is not None
