"""FastMCP tools.

See https://gofastmcp.com/servers/tools.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

from hrungnir.tools.specfile import get_upstream_url


def register_tools(mcp: "FastMCP") -> None:
    """Register all tools with the FastMCP instance."""
    mcp.tool(get_upstream_url)
