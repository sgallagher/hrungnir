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

*Note: Prepend `uv run ` to commands if not in the virtual environment.*
