"""Hrungnir MCP Server."""

from fastmcp import FastMCP

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
