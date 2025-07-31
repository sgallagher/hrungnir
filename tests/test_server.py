"""Tests for the Hrungnir MCP server."""

import pytest
from fastmcp import Client


@pytest.fixture
def mcp_server():
    """Create a test instance of the Hrungnir MCP server."""
    from hrungnir.server import mcp

    return mcp


async def test_server_connectivity(mcp_server):
    """Test basic server connectivity."""
    async with Client(mcp_server) as client:
        # Test basic connectivity by listing tools
        tools = await client.list_tools()
        assert len(tools) > 0

        # Verify hello tool exists
        tool_names = [tool.name for tool in tools]
        assert "hello" in tool_names


async def test_hello_tool_default(mcp_server):
    """Test the hello tool with default parameter."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("hello")
        assert result.data == "Hello, World! Hrungnir is ready to help with your packaging needs."


async def test_hello_tool_custom_name(mcp_server):
    """Test the hello tool with custom name."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("hello", {"name": "Developer"})
        assert (
            result.data == "Hello, Developer! Hrungnir is ready to help with your packaging needs."
        )


async def test_server_capabilities(mcp_server):
    """Test server information and capabilities."""
    async with Client(mcp_server) as client:
        # Test that we can connect and get basic server info
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        # Should have at least the hello tool
        assert len(tools) >= 1
        # Currently no resources or prompts
        assert len(resources) == 0
        assert len(prompts) == 0
