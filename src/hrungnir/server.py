"""Hrungnir MCP Server."""

import logging

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create the FastMCP server instance
mcp = FastMCP(name="hrungnir")


@mcp.tool()
async def hello(name: str = "World") -> str:
    """Simple greeting tool to test the server.

    Args:
        name: Name to greet

    Returns:
        Greeting message
    """
    return f"Hello, {name}! Hrungnir is ready to help with your packaging needs."


if __name__ == "__main__":
    mcp.run()
