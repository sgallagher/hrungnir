"""Package graph utilities and operations."""

from hrungnir.models.package import PackageGraph


class PackageGraphUtils:
    """Utilities for working with package dependency graphs."""

    @staticmethod
    def get_dependents(
        graph: PackageGraph, package_name: str, max_depth: int | None = None
    ) -> list[str]:
        """Get all packages that depend on the given package."""
        dependents = []
        for dep in graph.dependencies:
            if dep.dependency == package_name and (max_depth is None or dep.depth <= max_depth):
                dependents.append(dep.dependent)
        return list(set(dependents))

    @staticmethod
    def get_dependencies(
        graph: PackageGraph, package_name: str, max_depth: int | None = None
    ) -> list[str]:
        """Get all packages that the given package depends on."""
        dependencies = []
        for dep in graph.dependencies:
            if dep.dependent == package_name and (max_depth is None or dep.depth <= max_depth):
                dependencies.append(dep.dependency)
        return list(set(dependencies))
