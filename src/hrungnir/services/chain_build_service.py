"""Chain build business logic and orchestration."""

from datetime import UTC, datetime

from hrungnir.models.build import BuildResult
from hrungnir.models.chain_build import BuildGroup, ChainBuildExecution, ChainBuildPlan


class ChainBuildPlanService:
    """Service for chain build plan operations."""

    @staticmethod
    def get_package_group(plan: ChainBuildPlan, package_name: str) -> BuildGroup | None:
        """Get the build group containing the specified package."""
        for group in plan.build_groups:
            if package_name in group.packages:
                return group
        return None

    @staticmethod
    def get_packages_ready_to_build(
        plan: ChainBuildPlan, completed_packages: set[str]
    ) -> list[str]:
        """Get packages that are ready to build given completed packages."""
        ready_packages = []

        for group in plan.build_groups:
            # Check if all dependencies for this group are satisfied
            if group.dependencies_satisfied.issubset(completed_packages):
                # Add packages from this group that haven't been completed yet
                for pkg in group.packages:
                    if pkg not in completed_packages:
                        ready_packages.append(pkg)

        return ready_packages


class ChainBuildExecutionService:
    """Service for chain build execution operations."""

    @staticmethod
    def get_next_packages_to_build(execution: ChainBuildExecution) -> list[str]:
        """Get the next packages that should be built."""
        if execution.is_complete:
            return []

        ready_packages = ChainBuildPlanService.get_packages_ready_to_build(
            execution.plan, execution.completed_packages
        )

        # Filter out packages that are already running or have failed
        next_packages = []
        for pkg in ready_packages:
            if pkg not in execution.running_packages and pkg not in execution.failed_packages:
                next_packages.append(pkg)

        return next_packages

    @staticmethod
    def mark_package_started(execution: ChainBuildExecution, package_name: str) -> None:
        """Mark a package as started."""
        execution.running_packages.add(package_name)

    @staticmethod
    def mark_package_completed(
        execution: ChainBuildExecution, package_name: str, result: BuildResult
    ) -> None:
        """Mark a package as completed."""
        execution.running_packages.discard(package_name)

        if result.status == "success":
            execution.completed_packages.add(package_name)
        else:
            execution.failed_packages.add(package_name)

        execution.build_results[package_name] = result

        # Update overall status
        if len(execution.failed_packages) > 0:
            execution.current_status = "failed"
        elif len(execution.completed_packages) == execution.plan.total_packages:
            execution.current_status = "success"
            execution.completed_at = datetime.now(UTC)
