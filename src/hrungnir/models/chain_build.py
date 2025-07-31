"""Chain build planning and execution models."""

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field, computed_field

from .build import BuildConfiguration, BuildResult, BuildStatus

type ChainBuildStrategy = Literal[
    "sequential",  # Build one at a time
    "parallel_groups",  # Build independent packages in parallel
    "aggressive_parallel",  # Maximum parallelization
    "conservative",  # Safe approach with extra validation
]

type RiskLevel = Literal["low", "medium", "high", "critical"]


class BuildGroup(BaseModel):
    """A group of packages that can be built in parallel."""

    group_id: int = Field(description="Group sequence number")
    packages: list[str] = Field(description="Package names in this group")
    dependencies_satisfied: set[str] = Field(
        default_factory=set, description="Dependencies that must be completed before this group"
    )
    estimated_duration_minutes: int = Field(description="Estimated time for this group")
    risk_level: RiskLevel = Field("low", description="Risk assessment for this group")

    # Parallel execution details
    can_run_in_parallel: bool = Field(
        default=True, description="Whether packages in this group can run in parallel"
    )
    max_parallel_jobs: int | None = Field(None, description="Maximum parallel jobs for this group")

    # Special handling
    requires_special_target: bool = Field(
        default=False, description="Whether any package requires special build target"
    )
    signing_required: bool = Field(
        default=False, description="Whether any package in group requires signing"
    )


class ChainBuildPlan(BaseModel):
    """Complete plan for executing a chain build."""

    plan_id: str = Field(description="Unique identifier for this plan")
    root_packages: list[str] = Field(description="Root packages that triggered this chain build")
    target_tag: str = Field(description="Target build tag (e.g., c10s-build)")

    # Build strategy
    strategy: ChainBuildStrategy = Field("parallel_groups", description="Execution strategy")
    build_groups: list[BuildGroup] = Field(description="Ordered groups of packages to build")

    # Timing estimates
    estimated_total_duration_minutes: int = Field(description="Total estimated duration")
    estimated_queue_time_minutes: int = Field(0, description="Estimated time waiting in queues")
    critical_path_packages: list[str] = Field(description="Packages on the critical path")

    # Risk assessment
    overall_risk_level: RiskLevel = Field(description="Overall risk assessment")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")

    # Packit/RoG integration
    packit_automation_packages: list[str] = Field(
        default_factory=list, description="Packages with Packit automation"
    )
    rog_pipeline_coordination: bool = Field(
        default=False, description="Whether RoG pipeline coordination is enabled"
    )
    konflux_packages: list[str] = Field(
        default_factory=list, description="Packages requiring Konflux integration"
    )

    # Configuration
    default_build_config: BuildConfiguration | None = Field(
        None, description="Default build configuration"
    )
    package_specific_configs: dict[str, BuildConfiguration] = Field(
        default_factory=dict, description="Package-specific build configurations"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When this plan was created"
    )
    created_by: str | None = Field(None, description="Who created this plan")

    @computed_field
    @property
    def total_packages(self) -> int:
        """Total number of packages in the plan."""
        return sum(len(group.packages) for group in self.build_groups)

    @computed_field
    @property
    def estimated_completion_time(self) -> datetime:
        """Estimated completion time."""
        return self.created_at + timedelta(minutes=self.estimated_total_duration_minutes)


class ChainBuildExecution(BaseModel):
    """Tracks the execution of a chain build plan."""

    execution_id: str = Field(description="Unique identifier for this execution")
    plan: ChainBuildPlan = Field(description="The plan being executed")

    # Execution state
    current_status: BuildStatus = Field("pending", description="Overall execution status")
    completed_packages: set[str] = Field(
        default_factory=set, description="Packages that have completed successfully"
    )
    failed_packages: set[str] = Field(default_factory=set, description="Packages that have failed")
    running_packages: set[str] = Field(
        default_factory=set, description="Packages currently being built"
    )

    # Results
    build_results: dict[str, BuildResult] = Field(
        default_factory=dict, description="Build results by package name"
    )

    # Timing
    started_at: datetime | None = Field(None, description="When execution started")
    completed_at: datetime | None = Field(None, description="When execution completed")

    # Error handling
    error_message: str | None = Field(None, description="Error message if execution failed")
    retry_count: int = Field(0, description="Number of retry attempts")

    @computed_field
    @property
    def progress_percentage(self) -> float:
        """Execution progress as percentage."""
        total = self.plan.total_packages
        completed = len(self.completed_packages) + len(self.failed_packages)
        return (completed / total * 100) if total > 0 else 0.0

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Whether execution is complete (success or failure)."""
        return self.current_status in ["success", "failed", "canceled"]


class ChainBuildOptimization(BaseModel):
    """Optimization suggestions for chain builds."""

    suggested_strategy: ChainBuildStrategy = Field(description="Recommended build strategy")
    bottleneck_packages: list[str] = Field(description="Packages that are bottlenecks")
    optimization_suggestions: list[str] = Field(description="Specific optimization recommendations")

    # Parallel execution analysis
    max_parallelism: int = Field(description="Maximum safe parallelism level")
    parallel_groups_savings_minutes: int = Field(description="Time savings from parallel execution")

    # Risk mitigation
    high_risk_packages: list[str] = Field(description="Packages with high failure risk")
    mitigation_strategies: list[str] = Field(description="Risk mitigation strategies")

    # Alternative approaches
    alternative_orders: list[list[str]] = Field(
        default_factory=list, description="Alternative build orders"
    )
    incremental_build_candidates: list[str] = Field(
        default_factory=list, description="Packages suitable for incremental builds"
    )

    model_config = {"use_enum_values": True}
