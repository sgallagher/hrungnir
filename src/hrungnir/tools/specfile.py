"""Tools for interacting with specfiles."""

from pathlib import Path

from specfile import Specfile


def get_upstream_url(specfile_path: Path) -> str:
    """Parse a specfile and return the upstream URL."""
    specfile = Specfile(specfile_path)
    with specfile.tags() as tags:
        return tags.url.expanded_value or ""
