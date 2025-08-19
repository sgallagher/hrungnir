"""Prompts for setting up the upstream development environment for a package."""

from pathlib import Path


def setup_upstream_dev(dist_git_path: Path, package_name: str, branch: str) -> str:
    """Setup the upstream development environment."""
    return f"""
You are a helpful assistant that can help with setting up the upstream
development environment for a package.

The package should be located at {dist_git_path} and the package name is
{package_name}.

You are given a list of commands to run to set up the upstream development
environment.

Execute the following commands in order to set up the upstream development
environment.

1. Determine if the downstream dist-git repository exists in
{dist_git_path}/{package_name}. If it does not, use the dist_git_clone tool
from the hrungnir MCP server to clone the respository to that location. Also
pull the latest changes from the upstream remote "origin" for {branch}

2. Interrogate the specfile in the dist-git repository to determine the
upstream URL.

3. Clone the upstream repository to the dist-git repository at
{dist_git_path}/{package_name}/upstream.

4. Create a new branch in the upstream repository with the name
distgit-{branch} if that branch name does not already exist. if it does exist,
attempt to switch to that branch if the git repository contains uncommitted
changes. Create this branch based on the version of the RPM package, applying
any patches individually from the downstream dist-git repository, maintaining
the patch metadata. If possible, apply the patches using the git am tool.
"""
