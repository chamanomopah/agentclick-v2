"""
Dynamic Agent Loader for AgentClick V2.

This module provides automatic discovery and loading of agents from .claude/
directory structure, including commands, skills, and custom agents.

Key features:
- Scan .claude/commands/*.md for command agents
- Scan .claude/skills/*/SKILL.md for skill agents
- Scan .claude/agents/*.md for custom agents
- Extract YAML frontmatter metadata
- Lazy loading optimization
- Metadata caching with invalidation
- Hot-reload support
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List, Literal, Any, Callable
from collections import OrderedDict
import yaml
import aiofiles
from models.virtual_agent import VirtualAgent


# Configure logging
logger = logging.getLogger(__name__)


class AgentChangeEvent:
    """
    Represents a change event for an agent.

    Attributes:
        event_type: Type of change - "added", "modified", "removed"
        agent_id: ID of the affected agent
        agent_type: Type of agent (command, skill, agent)
        source_file: Path to the agent's source file
    """
    def __init__(
        self,
        event_type: Literal["added", "modified", "removed"],
        agent_id: str,
        agent_type: Literal["command", "skill", "agent"],
        source_file: Path
    ):
        self.event_type = event_type
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.source_file = source_file

    def __repr__(self) -> str:
        return f"AgentChangeEvent({self.event_type}, {self.agent_id}, {self.agent_type})"


async def extract_frontmatter(content: str) -> Optional[dict]:
    """
    Extract YAML frontmatter from markdown content.

    Parses YAML metadata between --- delimiters at the start of a file.

    Args:
        content: The full markdown file content

    Returns:
        dict: Parsed YAML metadata, or None if no frontmatter found

    Example:
        >>> content = "---\\nid: test\\nname: Test\\n---\\nContent"
        >>> metadata = await extract_frontmatter(content)
        >>> metadata["id"]
        'test'
    """
    if not content.startswith("---"):
        return None

    # Find the end delimiter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    yaml_content = parts[1].strip()

    if not yaml_content:
        return None

    try:
        metadata = yaml.safe_load(yaml_content)
        return metadata if isinstance(metadata, dict) else None
    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse YAML frontmatter: {e}")
        return None


class DynamicAgentLoader:
    """
    Dynamically discovers and loads agents from .claude/ directory structure.

    This loader scans three types of directories:
    - commands/ - Markdown files defining command agents (emoji: 📝)
    - skills/ - Directories containing SKILL.md files (emoji: 🎯)
    - agents/ - Markdown files defining custom agents (emoji: 🤖)

    Attributes:
        commands_dir: Path to commands directory
        skills_dir: Path to skills directory
        agents_dir: Path to custom agents directory
        _metadata_cache: Cache for parsed file metadata
        _cache_max_size: Maximum number of items in cache

    Example:
        >>> loader = DynamicAgentLoader()
        >>> agents = await loader.scan_all()
        >>> for agent in agents:
        ...     print(f"{agent.emoji} {agent.name}: {agent.description}")
    """

    # Emoji mappings for agent types
    EMOJI_MAP = {
        "command": "📝",
        "skill": "🎯",
        "agent": "🤖"
    }

    def __init__(
        self,
        commands_dir: Optional[Path] = None,
        skills_dir: Optional[Path] = None,
        agents_dir: Optional[Path] = None,
        cache_max_size: int = 1000
    ):
        """
        Initialize the DynamicAgentLoader.

        Args:
            commands_dir: Path to .claude/commands/ (defaults to .claude/commands)
            skills_dir: Path to .claude/skills/ (defaults to .claude/skills)
            agents_dir: Path to .claude/agents/ (defaults to .claude/agents)
            cache_max_size: Maximum number of cached metadata entries
        """
        # Default to .claude subdirectories if not specified
        base_path = Path.cwd() / ".claude"

        self.commands_dir = commands_dir or (base_path / "commands")
        self.skills_dir = skills_dir or (base_path / "skills")
        self.agents_dir = agents_dir or (base_path / "agents")

        # Metadata cache for performance (OrderedDict for FIFO eviction)
        self._metadata_cache: OrderedDict[Path, dict] = OrderedDict()
        self._cache_max_size = cache_max_size

        # File modification time cache for invalidation
        self._mtime_cache: Dict[Path, float] = {}

        # Event callbacks for agent changes
        self._event_callbacks: List[Callable[[AgentChangeEvent], None]] = []

        logger.debug(
            f"DynamicAgentLoader initialized: "
            f"commands={self.commands_dir}, "
            f"skills={self.skills_dir}, "
            f"agents={self.agents_dir}"
        )

    def register_callback(self, callback: Callable[[AgentChangeEvent], None]) -> None:
        """
        Register a callback to be notified of agent changes.

        Args:
            callback: Async function that takes AgentChangeEvent parameter

        Example:
            >>> async def on_change(event: AgentChangeEvent):
            ...     print(f"Agent {event.agent_id} was {event.event_type}")
            >>> loader.register_callback(on_change)
        """
        self._event_callbacks.append(callback)
        logger.debug(f"Registered event callback, total callbacks: {len(self._event_callbacks)}")

    async def _emit_event(self, event: AgentChangeEvent) -> None:
        """
        Emit an event to all registered callbacks.

        Args:
            event: The agent change event to emit
        """
        if not self._event_callbacks:
            return

        logger.debug(f"Emitting event: {event}")
        for callback in self._event_callbacks:
            try:
                # Support both sync and async callbacks
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in event callback {callback.__name__}: {e}")

    async def scan_all(self) -> List[VirtualAgent]:
        """
        Scan all agent types and return combined list.

        Returns:
            List of all discovered VirtualAgent instances

        Example:
            >>> loader = DynamicAgentLoader()
            >>> all_agents = await loader.scan_all()
            >>> print(f"Found {len(all_agents)} agents")
        """
        results = await asyncio.gather(
            self.scan_commands(),
            self.scan_skills(),
            self.scan_custom_agents(),
            return_exceptions=True
        )

        all_agents = []
        for result in results:
            if isinstance(result, list):
                all_agents.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error during scan: {result}")

        logger.info(f"Scanned {len(all_agents)} total agents")
        return all_agents

    async def scan_commands(self) -> List[VirtualAgent]:
        """
        Scan commands directory for command agents.

        Discovers all .md files in commands/ and creates VirtualAgent
        instances with type="command" and emoji="📝".

        Returns:
            List of command VirtualAgent instances

        Example:
            >>> loader = DynamicAgentLoader()
            >>> commands = await loader.scan_commands()
            >>> for cmd in commands:
            ...     assert cmd.type == "command"
            ...     assert cmd.emoji == "📝"
        """
        if not self.commands_dir.exists():
            logger.debug(f"Commands directory does not exist: {self.commands_dir}")
            return []

        agents = []

        for md_file in self.commands_dir.glob("*.md"):
            try:
                agent = await self._load_agent_from_file(md_file, "command")
                if agent:
                    agents.append(agent)
            except Exception as e:
                logger.error(f"Error loading command from {md_file}: {e}")
                continue

        logger.debug(f"Scanned {len(agents)} commands from {self.commands_dir}")
        return agents

    async def scan_skills(self) -> List[VirtualAgent]:
        """
        Scan skills directory for skill agents.

        Discovers all subdirectories containing SKILL.md files and creates
        VirtualAgent instances with type="skill" and emoji="🎯".

        Returns:
            List of skill VirtualAgent instances

        Example:
            >>> loader = DynamicAgentLoader()
            >>> skills = await loader.scan_skills()
            >>> for skill in skills:
            ...     assert skill.type == "skill"
            ...     assert skill.emoji == "🎯"
        """
        if not self.skills_dir.exists():
            logger.debug(f"Skills directory does not exist: {self.skills_dir}")
            return []

        agents = []

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            try:
                agent = await self._load_agent_from_file(skill_file, "skill")
                if agent:
                    agents.append(agent)
            except Exception as e:
                logger.error(f"Error loading skill from {skill_file}: {e}")
                continue

        logger.debug(f"Scanned {len(agents)} skills from {self.skills_dir}")
        return agents

    async def scan_custom_agents(self) -> List[VirtualAgent]:
        """
        Scan agents directory for custom agents.

        Discovers all .md files in agents/ and creates VirtualAgent
        instances with type="agent" and emoji="🤖".

        Returns:
            List of custom agent VirtualAgent instances

        Example:
            >>> loader = DynamicAgentLoader()
            >>> agents = await loader.scan_custom_agents()
            >>> for agent in agents:
            ...     assert agent.type == "agent"
            ...     assert agent.emoji == "🤖"
        """
        if not self.agents_dir.exists():
            logger.debug(f"Agents directory does not exist: {self.agents_dir}")
            return []

        agents = []

        for md_file in self.agents_dir.glob("*.md"):
            try:
                agent = await self._load_agent_from_file(md_file, "agent")
                if agent:
                    agents.append(agent)
            except Exception as e:
                logger.error(f"Error loading agent from {md_file}: {e}")
                continue

        logger.debug(f"Scanned {len(agents)} agents from {self.agents_dir}")
        return agents

    async def _load_agent_from_file(
        self,
        file_path: Path,
        agent_type: Literal["command", "skill", "agent"],
        emit_event: bool = False
    ) -> Optional[VirtualAgent]:
        """
        Load a single agent from a markdown file.

        Args:
            file_path: Path to the .md file
            agent_type: Type of agent (command, skill, or agent)
            emit_event: Whether to emit agent change event

        Returns:
            VirtualAgent instance or None if loading fails
        """
        # Check if file was previously cached
        was_cached = file_path in self._metadata_cache
        metadata = await self.get_cached_metadata(file_path)

        if metadata is None:
            # Read file content asynchronously
            try:
                async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                    content = await f.read()
            except (FileNotFoundError, UnicodeDecodeError) as e:
                logger.error(f"Failed to read {file_path}: {e}")
                return None

            # Extract frontmatter
            metadata = await extract_frontmatter(content)

            if metadata is None:
                logger.warning(f"No frontmatter found in {file_path}, using defaults")
                metadata = {}

            # Cache metadata
            await self._cache_metadata(file_path, metadata)

        # Create VirtualAgent using metadata
        agent = await self.create_virtual_agent(
            agent_type=agent_type,
            id=metadata.get("id", file_path.stem),
            name=metadata.get("name", file_path.stem),
            description=metadata.get("description", ""),
            source_file=file_path,
            metadata=metadata
        )

        # Emit event if requested
        if emit_event and agent:
            event_type = "modified" if was_cached else "added"
            event = AgentChangeEvent(
                event_type=event_type,
                agent_id=agent.id,
                agent_type=agent_type,
                source_file=file_path
            )
            await self._emit_event(event)

        return agent

    async def create_virtual_agent(
        self,
        agent_type: Literal["command", "skill", "agent"],
        id: str,
        name: str,
        description: str,
        source_file: Path,
        metadata: dict
    ) -> VirtualAgent:
        """
        Create a VirtualAgent instance with correct type-specific settings.

        Args:
            agent_type: Type of agent (command, skill, or agent)
            id: Unique identifier for the agent (fallback)
            name: Human-readable name (fallback)
            description: What the agent does (fallback)
            source_file: Path to the agent's source file
            metadata: Additional metadata from frontmatter (takes priority)

        Returns:
            Configured VirtualAgent instance

        Example:
            >>> agent = await loader.create_virtual_agent(
            ...     agent_type="command",
            ...     id="test",
            ...     name="Test",
            ...     description="Test agent",
            ...     source_file=Path("/test.md"),
            ...     metadata={}
            ... )
            >>> assert agent.emoji == "📝"
        """
        # Validate and extract agent fields
        agent_id = metadata.get("id", id)
        if not agent_id or not isinstance(agent_id, str):
            logger.warning(
                f"Invalid or missing agent ID in {source_file}, using fallback: {id}"
            )
            agent_id = id

        agent_name = metadata.get("name", name)
        if not agent_name or not isinstance(agent_name, str):
            logger.warning(
                f"Invalid or missing agent name for {agent_id} in {source_file}, using fallback: {name}"
            )
            agent_name = name

        agent_description = metadata.get("description", description)
        if agent_description is None:
            agent_description = ""
        elif not isinstance(agent_description, str):
            logger.warning(f"Agent description for {agent_id} is not a string, using empty string")
            agent_description = ""

        emoji = self.EMOJI_MAP.get(agent_type, "🤖")
        color_map = {
            "command": "#3498db",  # Blue
            "skill": "#9b59b6",    # Purple
            "agent": "#2ecc71"     # Green
        }
        color = color_map.get(agent_type, "#95a5a6")

        return VirtualAgent(
            id=agent_id,
            type=agent_type,
            name=agent_name,
            description=agent_description,
            source_file=source_file,
            emoji=emoji,
            color=color,
            enabled=True,
            workspace_id=None,
            metadata=metadata
        )

    async def get_cached_metadata(self, file_path: Path) -> Optional[dict]:
        """
        Get cached metadata for a file, checking for invalidation.

        Args:
            file_path: Path to the file

        Returns:
            Cached metadata dict or None if not cached or invalidated

        Example:
            >>> metadata = await loader.get_cached_metadata(Path("/test.md"))
            >>> if metadata:
            ...     print(f"Cached: {metadata['id']}")
        """
        if file_path not in self._metadata_cache:
            return None

        # Check if file has been modified
        try:
            current_mtime = file_path.stat().st_mtime
            cached_mtime = self._mtime_cache.get(file_path, 0)

            if current_mtime > cached_mtime:
                # File was modified, invalidate cache
                logger.debug(f"Cache invalidated for {file_path}")
                del self._metadata_cache[file_path]
                del self._mtime_cache[file_path]
                return None
        except FileNotFoundError:
            # File was deleted
            if file_path in self._metadata_cache:
                del self._metadata_cache[file_path]
            if file_path in self._mtime_cache:
                del self._mtime_cache[file_path]
            return None

        return self._metadata_cache.get(file_path)

    async def _cache_metadata(self, file_path: Path, metadata: dict) -> None:
        """
        Cache metadata for a file with size limits.

        Uses FIFO eviction when cache is full - removes oldest entry first.

        Args:
            file_path: Path to the file
            metadata: Metadata to cache
        """
        # Enforce cache size limit with FIFO eviction
        if len(self._metadata_cache) >= self._cache_max_size:
            # Remove oldest entry (first inserted in OrderedDict)
            oldest_file, _ = self._metadata_cache.popitem(last=False)
            if oldest_file in self._mtime_cache:
                del self._mtime_cache[oldest_file]
            logger.debug(f"Cache full, evicted oldest entry: {oldest_file}")

        # Cache metadata (inserts at end of OrderedDict)
        self._metadata_cache[file_path] = metadata
        try:
            self._mtime_cache[file_path] = file_path.stat().st_mtime
        except FileNotFoundError:
            pass

        logger.debug(f"Cached metadata for {file_path}")

    async def reload_agent(self, agent_id: str) -> Optional[VirtualAgent]:
        """
        Reload a specific agent's metadata and configuration.

        Args:
            agent_id: ID of the agent to reload

        Returns:
            Updated VirtualAgent if reload succeeded, None otherwise

        Example:
            >>> agent = await loader.reload_agent("test-agent")
            >>> if agent:
            ...     print(f"Reloaded: {agent.name}")
        """
        # Search for agent file in all directories
        all_dirs = [self.commands_dir, self.skills_dir, self.agents_dir]

        for directory in all_dirs:
            if not directory.exists():
                continue

            # For skills, look in subdirectories
            if directory == self.skills_dir:
                for skill_dir in directory.iterdir():
                    if not skill_dir.is_dir():
                        continue
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        metadata = await self.get_cached_metadata(skill_file)
                        if metadata and metadata.get("id") == agent_id:
                            # Invalidate cache
                            if skill_file in self._metadata_cache:
                                del self._metadata_cache[skill_file]
                            if skill_file in self._mtime_cache:
                                del self._mtime_cache[skill_file]
                            # Reload and return updated agent
                            updated_agent = await self._load_agent_from_file(
                                skill_file, "skill", emit_event=True
                            )
                            if updated_agent:
                                logger.info(f"Reloaded agent: {agent_id}")
                                return updated_agent
            else:
                # For commands and agents, look for .md files
                for md_file in directory.glob("*.md"):
                    metadata = await self.get_cached_metadata(md_file)
                    if metadata and metadata.get("id") == agent_id:
                        # Invalidate cache
                        if md_file in self._metadata_cache:
                            del self._metadata_cache[md_file]
                        if md_file in self._mtime_cache:
                            del self._mtime_cache[md_file]
                        # Reload and return updated agent
                        agent_type = "command" if directory == self.commands_dir else "agent"
                        updated_agent = await self._load_agent_from_file(
                            md_file, agent_type, emit_event=True
                        )
                        if updated_agent:
                            logger.info(f"Reloaded agent: {agent_id}")
                            return updated_agent

        logger.warning(f"Agent not found for reload: {agent_id}")
        return None

    async def watch_changes(
        self,
        poll_interval: float = 1.0,
        stop_event: Optional[asyncio.Event] = None
    ) -> None:
        """
        Watch for file system changes and emit events on agent add/remove/update.

        Uses polling-based file system monitoring to detect changes without
        requiring external dependencies like watchdog.

        Args:
            poll_interval: Seconds between file system scans (default: 1.0)
            stop_event: Optional event to signal when to stop watching

        Example:
            >>> # Run in background
            >>> stop = asyncio.Event()
            >>> asyncio.create_task(loader.watch_changes(stop_event=stop))
            >>>
            >>> # Later, stop watching
            >>> stop.set()
        """
        logger.info(
            f"Starting file watcher with {poll_interval}s interval. "
            f"Monitoring: {self.commands_dir}, {self.skills_dir}, {self.agents_dir}"
        )

        # Track known files
        known_files: Dict[Path, float] = {}

        # Build initial file list
        for directory in [self.commands_dir, self.skills_dir, self.agents_dir]:
            if not directory.exists():
                continue

            if directory == self.skills_dir:
                # For skills, track SKILL.md files
                for skill_dir in directory.iterdir():
                    if skill_dir.is_dir():
                        skill_file = skill_dir / "SKILL.md"
                        if skill_file.exists():
                            known_files[skill_file] = skill_file.stat().st_mtime
            else:
                # For commands and agents, track .md files
                for md_file in directory.glob("*.md"):
                    known_files[md_file] = md_file.stat().st_mtime

        logger.debug(f"Initial watch list: {len(known_files)} files")

        try:
            while stop_event is None or not stop_event.is_set():
                # Scan for changes
                current_files: Dict[Path, float] = {}

                for directory in [self.commands_dir, self.skills_dir, self.agents_dir]:
                    if not directory.exists():
                        continue

                    if directory == self.skills_dir:
                        for skill_dir in directory.iterdir():
                            if not skill_dir.is_dir():
                                continue
                            skill_file = skill_dir / "SKILL.md"
                            if skill_file.exists():
                                current_files[skill_file] = skill_file.stat().st_mtime
                    else:
                        for md_file in directory.glob("*.md"):
                            current_files[md_file] = md_file.stat().st_mtime

                # Detect new files
                for file_path, mtime in current_files.items():
                    if file_path not in known_files:
                        # New file detected
                        logger.info(f"Detected new file: {file_path}")
                        # Determine agent type
                        if self.skills_dir in file_path.parents:
                            agent_type = "skill"
                        elif self.commands_dir in file_path.parents:
                            agent_type = "command"
                        else:
                            agent_type = "agent"

                        # Load agent and emit event
                        await self._load_agent_from_file(file_path, agent_type, emit_event=True)
                        known_files[file_path] = mtime

                # Detect modified files
                for file_path, mtime in current_files.items():
                    if file_path in known_files and mtime > known_files[file_path]:
                        # File modified
                        logger.info(f"Detected modified file: {file_path}")
                        # Determine agent type
                        if self.skills_dir in file_path.parents:
                            agent_type = "skill"
                        elif self.commands_dir in file_path.parents:
                            agent_type = "command"
                        else:
                            agent_type = "agent"

                        # Invalidate cache and reload
                        if file_path in self._metadata_cache:
                            del self._metadata_cache[file_path]
                        if file_path in self._mtime_cache:
                            del self._mtime_cache[file_path]

                        await self._load_agent_from_file(file_path, agent_type, emit_event=True)
                        known_files[file_path] = mtime

                # Detect removed files
                removed_files = set(known_files.keys()) - set(current_files.keys())
                for file_path in removed_files:
                    logger.info(f"Detected removed file: {file_path}")
                    # Determine agent type
                    if self.skills_dir in file_path.parents:
                        agent_type = "skill"
                    elif self.commands_dir in file_path.parents:
                        agent_type = "command"
                    else:
                        agent_type = "agent"

                    # Try to get agent ID from cache before removing
                    metadata = self._metadata_cache.get(file_path, {})
                    agent_id = metadata.get("id", file_path.stem) if metadata else file_path.stem

                    # Emit removal event
                    event = AgentChangeEvent(
                        event_type="removed",
                        agent_id=agent_id,
                        agent_type=agent_type,
                        source_file=file_path
                    )
                    await self._emit_event(event)

                    # Remove from tracking
                    del known_files[file_path]
                    if file_path in self._metadata_cache:
                        del self._metadata_cache[file_path]
                    if file_path in self._mtime_cache:
                        del self._mtime_cache[file_path]

                # Wait before next poll
                await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            logger.info("File watcher cancelled")
        except Exception as e:
            logger.error(f"Error in file watcher: {e}", exc_info=True)
        finally:
            logger.info("File watcher stopped")
