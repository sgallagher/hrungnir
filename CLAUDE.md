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

# With MCP inspector GUI for testing
npx @modelcontextprotocol/inspector uvx .
```

## Architecture Overview

### Core Architecture Pattern

The project follows a 5-phase chain build optimization architecture:

1. **Phase 1: Concurrent Data Gathering** - PackitAPI status + dependency analysis
1. **Phase 2: RoG Pipeline Intelligence** - Build target optimization
1. **Phase 3: Optimization Algorithm** - Dependency-aware parallelization
1. **Phase 4: Risk Assessment** - Gating intelligence and failure prediction
1. **Phase 5: Plan Generation** - Build groups with timing estimates

### Directory Structure

```
src/hrungnir/
├── models/           # Pydantic data models
├── services/         # Logic and external integrations
├── tools/            # FastMCP tool implementations
├── prompts/          # FastMCP prompt templates
├── utils/            # Utility functions
└── server.py         # FastMCP server entry point
```

### Key Services

- **ChainBuildOptimizerService**: Main orchestration logic coordinating all optimization phases
- **PackitService**: Integration with PackitAPI for package status and automation
- **DependencyAnalyzer**: Analyzes package dependencies using spec files
- **RogPipelineService**: Optimizes build targets for RHEL-on-GitLab pipeline
- **GatingIntelligenceService**: Risk assessment and failure prediction for CI gating

### Integration Points

- **RoG Pipeline**: RHEL-on-GitLab 7-stage CI/CD architecture
- **PackitAPI**: Automation between source-git and dist-git repositories
- **OSCI Pipeline**: CentOS Stream CI integration patterns
- **Koji Build System**: RPM build dependency resolution

## Key Concepts

### Chain Build Optimization

The core feature optimizes building multiple related packages by:

- Analyzing dependencies to determine build order
- Grouping independent packages for parallel execution
- Selecting optimal build targets (draft vs production)
- Assessing risk factors and failure probability

### Package-Specific Intelligence

- **Kernel packages**: Special handling for signing requirements (`-pesign` targets)
- **Java packages**: Custom toolchain handling and longer build estimates
- **System packages**: Higher risk assessment for critical components (systemd, glibc)

### Mock vs Real Integration

Current implementation uses mock services structured for easy replacement:

- PackitAPI calls → Real PackitAPI integration ready
- Spec file parsing → python-specfile integration ready
- Gating data → RHEL CI/CentOS Stream CI integration ready

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
uv run pytest        # Run tests to ensure functionality
```

### Common Type Error Fixes

**Pydantic Model Constructor Issues**: When adding new fields to existing models, update ALL constructor calls:

```python
# If you add a new required field to a model
class MyModel(BaseModel):
    existing_field: str
    new_required_field: str  # Added this


# Update ALL constructor calls throughout the codebase
MyModel(
    existing_field="value",
    new_required_field="new_value",  # Add this everywhere
)
```

**FastMCP Tool Parameter Types**: Use proper types for tool parameters:

- `tags` parameter MUST be `set[str]`, not `list[str]`
- Import `from typing import Literal` for constrained string parameters

## FastMCP Tool Implementation Patterns

### Critical FastMCP Tool Architecture

**IMPORTANT**: FastMCP tools MUST use `@mcp.tool()` decorator pattern, not standalone `@tool()` imports.

```python
# CORRECT: Tool registration pattern
from fastmcp import FastMCP


def register_chain_build_tools(mcp: FastMCP) -> None:
    """Register tools with the FastMCP server."""

    @mcp.tool(
        name="tool_name",
        description="Tool description",
        tags={"tag1", "tag2"},  # Note: set, not list
    )
    async def tool_function(param: str) -> dict:
        return await implementation_function(param)


# WRONG: Do not use standalone @tool decorator
# from fastmcp import tool  # This doesn't exist!
# @tool(name="...", description="...")  # This will cause type errors
```

### Tool Organization Best Practices

- **Separate tool interface from implementation**: Keep `@mcp.tool()` decorators in `/tools` directory
- **Use registration functions**: Group related tools in `register_*_tools(mcp)` functions
- **Import and register in server.py**: `from tools.module import register_tools; register_tools(mcp)`
- **Clean separation**: Tool decorators should call separate implementation functions

## Important Implementation Notes

### Current Status

- Core optimization logic implemented with mock services
- FastMCP tool interface functional
- Ready for real API integration (PackitAPI, python-specfile, gating systems)
- Type-safe with comprehensive Pydantic models

### Future Integration Areas

- Replace mock PackitService with real PackitAPI calls
- Integrate python-specfile for actual spec parsing
- Connect to RHEL CI/CentOS Stream CI for historical gating data
- Add machine learning models for enhanced failure prediction

### Error Handling Patterns

- Graceful degradation when external services are unavailable
- Comprehensive retry logic for API calls
- Fallback mechanisms maintain core functionality
