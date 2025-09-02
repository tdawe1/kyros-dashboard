"""
Tools Registry

This module provides dynamic tool discovery and registration for the Kyros Dashboard.
It allows the system to automatically discover and register tool routers.
"""

import importlib
import logging
from typing import List, Dict, Any, Tuple
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Registry of available tools
TOOLS = [
    {
        "name": "repurposer",
        "module": "tools.repurposer",
        "router": "router",
        "title": "Content Repurposer",
        "description": "Transform content into multiple channel formats",
        "version": "1.0.0",
        "enabled": True,
    },
    # Future tools will be added here
    # {
    #     "name": "hello",
    #     "module": "tools.hello",
    #     "router": "router",
    #     "title": "Hello World",
    #     "description": "A simple demo tool",
    #     "version": "1.0.0",
    #     "enabled": True,
    # },
]


def load_tool_routers() -> List[Tuple[str, APIRouter]]:
    """
    Dynamically load and return all enabled tool routers.

    Returns:
        List of tuples containing (tool_name, router) for each enabled tool.
    """
    routers = []

    for tool in TOOLS:
        if not tool.get("enabled", True):
            logger.info(f"Tool {tool['name']} is disabled, skipping")
            continue

        try:
            # Import the tool module
            module_path = f"{tool['module']}.{tool['router']}"
            module = importlib.import_module(module_path)

            # Get the router from the module
            router = getattr(module, tool["router"])

            if not isinstance(router, APIRouter):
                logger.error(f"Tool {tool['name']} router is not an APIRouter instance")
                continue

            routers.append((tool["name"], router))
            logger.info(f"Successfully loaded tool: {tool['name']}")

        except ImportError as e:
            logger.error(f"Failed to import tool {tool['name']}: {e}")
        except AttributeError as e:
            logger.error(f"Failed to get router from tool {tool['name']}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading tool {tool['name']}: {e}")

    logger.info(f"Loaded {len(routers)} tool routers")
    return routers


def get_tools_metadata() -> List[Dict[str, Any]]:
    """
    Get metadata for all tools.

    Returns:
        List of tool metadata dictionaries.
    """
    return [
        {
            "name": tool["name"],
            "title": tool["title"],
            "description": tool["description"],
            "version": tool["version"],
            "enabled": tool.get("enabled", True),
            "endpoints": {
                "base": f"/api/tools/{tool['name']}",
                "config": f"/api/tools/{tool['name']}/config",
            },
        }
        for tool in TOOLS
        if tool.get("enabled", True)
    ]


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """
    Get metadata for a specific tool.

    Args:
        tool_name: Name of the tool to get metadata for.

    Returns:
        Tool metadata dictionary or None if not found.
    """
    tool = next((t for t in TOOLS if t["name"] == tool_name), None)
    if not tool:
        return None

    return {
        "name": tool["name"],
        "title": tool["title"],
        "description": tool["description"],
        "version": tool["version"],
        "enabled": tool.get("enabled", True),
        "endpoints": {
            "base": f"/api/tools/{tool['name']}",
            "config": f"/api/tools/{tool['name']}/config",
        },
    }


def is_tool_enabled(tool_name: str) -> bool:
    """
    Check if a tool is enabled.

    Args:
        tool_name: Name of the tool to check.

    Returns:
        True if tool is enabled, False otherwise.
    """
    tool = next((t for t in TOOLS if t["name"] == tool_name), None)
    return tool.get("enabled", True) if tool else False


def enable_tool(tool_name: str) -> bool:
    """
    Enable a tool.

    Args:
        tool_name: Name of the tool to enable.

    Returns:
        True if tool was enabled, False if tool not found.
    """
    tool = next((t for t in TOOLS if t["name"] == tool_name), None)
    if tool:
        tool["enabled"] = True
        logger.info(f"Enabled tool: {tool_name}")
        return True
    return False


def disable_tool(tool_name: str) -> bool:
    """
    Disable a tool.

    Args:
        tool_name: Name of the tool to disable.

    Returns:
        True if tool was disabled, False if tool not found.
    """
    tool = next((t for t in TOOLS if t["name"] == tool_name), None)
    if tool:
        tool["enabled"] = False
        logger.info(f"Disabled tool: {tool_name}")
        return True
    return False


def add_tool(tool_config: Dict[str, Any]) -> bool:
    """
    Add a new tool to the registry.

    Args:
        tool_config: Tool configuration dictionary.

    Returns:
        True if tool was added, False if tool already exists.
    """
    tool_name = tool_config.get("name")
    if not tool_name:
        logger.error("Tool name is required")
        return False

    # Check if tool already exists
    if any(t["name"] == tool_name for t in TOOLS):
        logger.error(f"Tool {tool_name} already exists")
        return False

    # Add default values
    tool_config.setdefault("enabled", True)
    tool_config.setdefault("version", "1.0.0")

    TOOLS.append(tool_config)
    logger.info(f"Added new tool: {tool_name}")
    return True


def remove_tool(tool_name: str) -> bool:
    """
    Remove a tool from the registry.

    Args:
        tool_name: Name of the tool to remove.

    Returns:
        True if tool was removed, False if tool not found.
    """
    global TOOLS
    original_count = len(TOOLS)
    TOOLS = [t for t in TOOLS if t["name"] != tool_name]

    if len(TOOLS) < original_count:
        logger.info(f"Removed tool: {tool_name}")
        return True
    return False
