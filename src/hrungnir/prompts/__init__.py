"""FastMCP prompts implementation.

See https://gofastmcp.com/servers/tools.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

from hrungnir.prompts.upstream import setup_upstream_dev

logger = logging.getLogger(__name__)


def register_prompts(mcp: "FastMCP") -> None:
    """Register all prompts with the FastMCP instance."""
    logger.info("Registering prompts")
    mcp.prompt(setup_upstream_dev)
