"""Hrungnir MCP Server."""

import logging

from fastmcp import FastMCP

from hrungnir.prompts import register_prompts
from hrungnir.tools import register_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)

# Create the FastMCP server instance
mcp = FastMCP(name="hrungnir")
register_prompts(mcp)
register_tools(mcp)


if __name__ == "__main__":
    logger.info("Starting Hrungnir MCP server")
    mcp.run()
