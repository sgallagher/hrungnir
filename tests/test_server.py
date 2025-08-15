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
        # resources = await client.list_resources()
        # prompts = await client.list_prompts()

        # Should have at least the hello tool
        assert len(tools) >= 1
        # TODO
        # assert len(resources) == 0
        # assert len(prompts) == 0
        # assert len(tools) > 0


async def test_hello_tool_default(mcp_server):
    """Test the hello tool with default parameter."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("hello")
        assert result.data == "Hello, World! Hrungnir is ready to help with your packaging needs."
