# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hrungnir is an MCP (Model Context Protocol) server built with FastMCP that leverages Large Language Models (LLMs) to assist software engineers with RHEL packaging workflows.

## Development Setup

```bash
# Set up development environment
uv sync -U
source .venv/bin/activate
```

## Common Development Commands

### Code Quality and Testing

```bash
# Linting and formatting (required before commits)
uv run ruff format     # Format code
uv run ruff check      # Lint code

# Type checking
uv run basedpyright    # Type checking

# Testing
uv run pytest         # Run tests

# Pre-commit (automatically runs on commit)
 pre-commit run --all-files  # Manual run
```

**Important**: Always use `uv run` prefix for consistency, even when in virtual environment.

### Running the MCP Server

```bash
# Inside virtual environment
hrungnir

# Without virtual environment setup
uvx .
```

## Architecture Overview

### Directory Structure

```
src/hrungnir/
├── models/           # Pydantic data models
├── resources/        # FastMCP resources
├── tools/            # FastMCP tool implementations
├── prompts/          # FastMCP prompt templates
├── utils/            # Utility functions
└── server.py         # FastMCP server entry point
```

## Basic Memory MCP Integration

This project integrates with basic-memory MCP tools for knowledge management:

### Required Reading Before Any Note Edits

**ALWAYS** read the `ai-assistant-guide` note first using the `read_note` tool before editing any basic-memory notes.

### Knowledge Structure

- **Single basic-memory project** with knowledge organized in separate directories:
  - `rhel-dev-guide/` - Source of truth documentation (generally READ-ONLY, avoid edits)
  - `hrungnir/` - Project-specific documentation supplementing rhel-dev-guide
  - `fastmcp/` - FastMCP upstream documentation (critical for implementation steps)

### Development Workflow Integration

When working on specific components, read relevant FastMCP documentation first:

- **Writing tests**: Read `fastmcp/testing` note via basic-memory before implementing tests
- **Writing tools**: Read `fastmcp/tools` note via basic-memory before implementing MCP tools
- **General FastMCP patterns**: Consult appropriate `fastmcp/*` notes for implementation guidance

## Code Style and Standards

- **Python 3.12+** with modern syntax and type hints:
  - Use built-in `list`, `dict` types (NOT `List`, `Dict` from typing module)
  - Leverage modern Python features and best practices
- **Pydantic models** for all data structures
- **Async/await** patterns for concurrent operations
- **Line length**: 100 characters (configured in pyproject.toml)
- **Documentation**: Google-style docstrings
- **Type checking**: basedpyright in "standard" mode

### Code Quality Workflow

After making any code changes, ALWAYS run these commands in order:

```bash
uv run ruff format    # Format code first
uv run ruff check     # Then lint
uv run basedpyright   # Finally type check
```

## FastMCP Tool Implementation Patterns

### Critical FastMCP Tool Architecture

**IMPORTANT**: FastMCP tools MUST use `@mcp.tool()` decorator pattern, not standalone `@tool()` imports.

### Tool Organization Best Practices

- **Separate tool interface from implementation**: Keep `@mcp.tool()` decorators in `/tools` directory
