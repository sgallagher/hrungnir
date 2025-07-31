# 🚧 Hrungnir - work in progress 🚧

## Development Setup

Install uv: `dnf install uv` or follow the [installation guide](https://docs.astral.sh/uv/getting-started/installation)

```bash
uv sync
source .venv/bin/activate
```

## Linting, Formatting, Testing, and Type Checking

```bash
# Linting and formatting
ruff format
ruff check

# Testing and type checking
pytest
basedpyright
```

*Note: Prepend `uv run` to commands if not in the virtual environment.*

## Running the MCP Server

To run the server locally:

```bash
# Inside virtual environment
hrungnir

# Without setting virtual environment
uvx .

# With MCP inspector GUI
npx @modelcontextprotocol/inspector uvx .
```
