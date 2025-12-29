"""
YAML helper utilities for loading and saving configuration files.

This module provides utility functions for reading and writing YAML files
with proper error handling and directory creation.
"""
from pathlib import Path
from typing import Any, Optional
import yaml
import asyncio


async def load_yaml_async(file_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Load a YAML file asynchronously and return its contents as a dictionary.

    This function reads a YAML file from disk asynchronously using
    run_in_executor to avoid blocking the event loop.

    Args:
        file_path: Path to the YAML file (string or Path object)

    Returns:
        Dictionary containing the YAML data, or None if file is empty

    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the YAML syntax is invalid

    Example:
        >>> data = await load_yaml_async('config/workspaces.yaml')
        >>> print(data['version'])
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, load_yaml, file_path)


async def save_yaml_async(file_path: str | Path, data: dict[str, Any]) -> None:
    """
    Save a dictionary to a YAML file asynchronously.

    This function writes a Python dictionary to a YAML file asynchronously
    using run_in_executor to avoid blocking the event loop.

    Args:
        file_path: Path where the YAML file should be saved
        data: Dictionary to save as YAML

    Raises:
        IOError: If the file cannot be written
        yaml.YAMLError: If the data cannot be serialized to YAML

    Example:
        >>> config = {'version': '2.0', 'workspaces': {}}
        >>> await save_yaml_async('config/workspaces.yaml', config)
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, save_yaml, file_path, data)


def load_yaml(file_path: str | Path) -> Optional[dict[str, Any]]:
    """
    Load a YAML file and return its contents as a dictionary.

    This function reads a YAML file from disk and parses it into a Python
    dictionary. It raises FileNotFoundError if the file doesn't exist.

    Args:
        file_path: Path to the YAML file (string or Path object)

    Returns:
        Dictionary containing the YAML data, or None if file is empty

    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the YAML syntax is invalid

    Example:
        >>> data = load_yaml('config/workspaces.yaml')
        >>> print(data['version'])
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        return None

    return yaml.safe_load(content)


def save_yaml(file_path: str | Path, data: dict[str, Any]) -> None:
    """
    Save a dictionary to a YAML file.

    This function writes a Python dictionary to a YAML file with proper
    formatting. Parent directories are created if they don't exist.

    Args:
        file_path: Path where the YAML file should be saved
        data: Dictionary to save as YAML

    Raises:
        IOError: If the file cannot be written
        yaml.YAMLError: If the data cannot be serialized to YAML

    Example:
        >>> config = {'version': '2.0', 'workspaces': {}}
        >>> save_yaml('config/workspaces.yaml', config)
    """
    path = Path(file_path)

    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
