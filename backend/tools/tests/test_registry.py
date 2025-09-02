from unittest.mock import patch, MagicMock
from ..registry import (
    load_tool_routers,
    get_tools_metadata,
    get_tool_metadata,
    is_tool_enabled,
    enable_tool,
    disable_tool,
    add_tool,
    remove_tool,
    TOOLS,
)


class TestToolsRegistry:
    """Test cases for the tools registry module."""

    def test_get_tools_metadata(self):
        """Test getting metadata for all tools."""
        metadata = get_tools_metadata()

        assert isinstance(metadata, list)
        assert len(metadata) > 0

        # Check structure of metadata
        for tool in metadata:
            assert "name" in tool
            assert "title" in tool
            assert "description" in tool
            assert "version" in tool
            assert "enabled" in tool
            assert "endpoints" in tool
            assert "base" in tool["endpoints"]
            assert "config" in tool["endpoints"]

    def test_get_tool_metadata_existing(self):
        """Test getting metadata for an existing tool."""
        metadata = get_tool_metadata("hello")

        assert metadata is not None
        assert metadata["name"] == "hello"
        assert metadata["title"] == "Hello World"
        assert metadata["enabled"] is True

    def test_get_tool_metadata_nonexistent(self):
        """Test getting metadata for a non-existent tool."""
        metadata = get_tool_metadata("nonexistent")
        assert metadata is None

    def test_is_tool_enabled_existing(self):
        """Test checking if an existing tool is enabled."""
        assert is_tool_enabled("hello") is True

    def test_is_tool_enabled_nonexistent(self):
        """Test checking if a non-existent tool is enabled."""
        assert is_tool_enabled("nonexistent") is False

    def test_enable_tool_existing(self):
        """Test enabling an existing tool."""
        # First disable it
        disable_tool("hello")
        assert is_tool_enabled("hello") is False

        # Then enable it
        result = enable_tool("hello")
        assert result is True
        assert is_tool_enabled("hello") is True

    def test_enable_tool_nonexistent(self):
        """Test enabling a non-existent tool."""
        result = enable_tool("nonexistent")
        assert result is False

    def test_disable_tool_existing(self):
        """Test disabling an existing tool."""
        result = disable_tool("hello")
        assert result is True
        assert is_tool_enabled("hello") is False

        # Re-enable for other tests
        enable_tool("hello")

    def test_disable_tool_nonexistent(self):
        """Test disabling a non-existent tool."""
        result = disable_tool("nonexistent")
        assert result is False

    def test_add_tool_valid(self):
        """Test adding a valid new tool."""
        tool_config = {
            "name": "test_tool",
            "module": "tools.test_tool",
            "router": "router",
            "title": "Test Tool",
            "description": "A test tool",
        }

        result = add_tool(tool_config)
        assert result is True

        # Check that tool was added
        assert is_tool_enabled("test_tool") is True
        metadata = get_tool_metadata("test_tool")
        assert metadata is not None
        assert metadata["name"] == "test_tool"

        # Clean up
        remove_tool("test_tool")

    def test_add_tool_duplicate(self):
        """Test adding a tool that already exists."""
        tool_config = {
            "name": "hello",  # Already exists
            "module": "tools.hello",
            "router": "router",
            "title": "Duplicate Hello",
            "description": "A duplicate tool",
        }

        result = add_tool(tool_config)
        assert result is False

    def test_add_tool_missing_name(self):
        """Test adding a tool without a name."""
        tool_config = {
            "module": "tools.test_tool",
            "router": "router",
            "title": "Test Tool",
            "description": "A test tool",
        }

        result = add_tool(tool_config)
        assert result is False

    def test_remove_tool_existing(self):
        """Test removing an existing tool."""
        # First add a tool
        tool_config = {
            "name": "temp_tool",
            "module": "tools.temp_tool",
            "router": "router",
            "title": "Temporary Tool",
            "description": "A temporary tool",
        }
        add_tool(tool_config)

        # Then remove it
        result = remove_tool("temp_tool")
        assert result is True

        # Check that tool was removed
        assert is_tool_enabled("temp_tool") is False
        metadata = get_tool_metadata("temp_tool")
        assert metadata is None

    def test_remove_tool_nonexistent(self):
        """Test removing a non-existent tool."""
        result = remove_tool("nonexistent")
        assert result is False

    @patch("tools.registry.importlib.import_module")
    def test_load_tool_routers_success(self, mock_import):
        """Test successful loading of tool routers."""
        # Mock the import and router
        from fastapi import APIRouter

        mock_module = MagicMock()
        mock_router = APIRouter()  # Use real APIRouter instance
        mock_module.router = mock_router
        mock_import.return_value = mock_module

        routers = load_tool_routers()

        assert isinstance(routers, list)
        assert len(routers) > 0

        # Check that import was called
        mock_import.assert_called()

    @patch("tools.registry.importlib.import_module")
    def test_load_tool_routers_import_error(self, mock_import):
        """Test handling of import errors when loading tool routers."""
        mock_import.side_effect = ImportError("Module not found")

        routers = load_tool_routers()

        # Should still return a list (empty or with other tools)
        assert isinstance(routers, list)

    @patch("tools.registry.importlib.import_module")
    def test_load_tool_routers_disabled_tool(self, mock_import):
        """Test that disabled tools are not loaded."""
        # Disable hello tool
        disable_tool("hello")

        routers = load_tool_routers()

        # Check that hello router is not in the list
        router_names = [name for name, _ in routers]
        assert "hello" not in router_names

        # Re-enable for other tests
        enable_tool("hello")

    def test_tools_constant_structure(self):
        """Test that TOOLS constant has the expected structure."""
        assert isinstance(TOOLS, list)
        assert len(TOOLS) > 0

        for tool in TOOLS:
            assert "name" in tool
            assert "module" in tool
            assert "router" in tool
            assert "title" in tool
            assert "description" in tool
            assert "version" in tool
