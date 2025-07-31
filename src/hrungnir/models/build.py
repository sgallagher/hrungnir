"""Build-related data models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

type BuildType = Literal["scratch", "draft", "official", "chain"]

type BuildStatus = Literal["pending", "running", "success", "failed", "canceled", "skipped"]

type BuildTarget = Literal[
    # CentOS Stream 10
    "c10s-candidate",
    "c10s-pending",
    "c10s-build",
    # CentOS Stream 9
    "c9s-candidate",
    "c9s-pending",
    "c9s-build",
    # Special targets
    "c10s-candidate-pesign",  # For kernel builds
    "java-openjdk-rhel-9-build",  # For Java builds
]

type Architecture = Literal["x86_64", "aarch64", "ppc64le", "s390x", "i686", "noarch"]


class BuildConfiguration(BaseModel):
    """Build configuration settings."""

    target: BuildTarget = Field(description="Build target")
    architectures: list[Architecture] = Field(
        default=["x86_64", "i686"], description="Target architectures"
    )
    build_type: BuildType = Field("official", description="Type of build")
    scratch: bool = Field(default=False, description="Whether this is a scratch build")
    timeout: int | None = Field(None, description="Build timeout in minutes")

    # RoG pipeline specific
    enable_draft_builds: bool = Field(
        default=False, description="Enable draft builds for faster iteration"
    )
    enable_konflux: bool = Field(
        default=False, description="Enable Konflux integration for container builds"
    )
    signing_required: bool = Field(
        default=False, description="Whether signing is required (e.g., kernel)"
    )

    # Additional options
    additional_repos: list[str] = Field(default_factory=list, description="Additional repositories")
    additional_packages: list[str] = Field(default_factory=list, description="Additional packages")


class BuildResult(BaseModel):
    """Result of a build operation."""

    build_id: int | None = Field(None, description="Build ID from build system")
    package_name: str = Field(description="Package name")
    status: BuildStatus = Field(description="Build status")
    config: BuildConfiguration = Field(description="Build configuration used")

    # Timing information
    start_time: datetime | None = Field(None, description="Build start time")
    end_time: datetime | None = Field(None, description="Build end time")
    duration_seconds: int | None = Field(None, description="Build duration in seconds")

    # Results
    artifacts: list[str] = Field(
        default_factory=list, description="Built artifacts (RPMs, logs, etc.)"
    )
    log_url: str | None = Field(None, description="URL to build logs")
    error_message: str | None = Field(None, description="Error message if build failed")

    # Integration details
    koji_task_id: int | None = Field(None, description="Koji task ID")
    copr_build_id: int | None = Field(None, description="COPR build ID")
    rog_pipeline_id: str | None = Field(None, description="RoG pipeline ID")


class BuildEstimate(BaseModel):
    """Estimated build time and resource requirements."""

    package_name: str = Field(description="Package name")
    estimated_duration_minutes: int = Field(description="Estimated build duration in minutes")
    estimated_queue_time_minutes: int = Field(0, description="Estimated queue time in minutes")

    # Factors affecting build time
    is_large_package: bool = Field(
        default=False, description="Whether this is a large package (kernel, systemd, etc.)"
    )
    requires_signing: bool = Field(default=False, description="Whether package requires signing")
    is_java_package: bool = Field(default=False, description="Whether this is a Java package")
    has_konflux_integration: bool = Field(default=False, description="Whether package uses Konflux")

    # Resource requirements
    memory_gb: int | None = Field(None, description="Estimated memory requirement in GB")
    disk_gb: int | None = Field(None, description="Estimated disk space requirement in GB")
    cpu_cores: int | None = Field(None, description="Estimated CPU cores needed")

    confidence_score: float = Field(0.7, description="Confidence in the estimate (0.0-1.0)")


class GatingResult(BaseModel):
    """Gating test results."""

    package_name: str = Field(description="Package name")
    build_id: int = Field(description="Build ID")
    overall_status: BuildStatus = Field(description="Overall gating status")

    # Test results
    test_results: dict[str, str] = Field(
        default_factory=dict, description="Individual test results"
    )
    gating_yaml_url: str | None = Field(None, description="URL to gating.yaml configuration")
    resultsdb_url: str | None = Field(None, description="URL to ResultsDB results")

    # Timing
    start_time: datetime | None = Field(None, description="Gating start time")
    end_time: datetime | None = Field(None, description="Gating end time")

    # Failure analysis
    failure_reason: str | None = Field(None, description="Reason for gating failure")
    known_issues: list[str] = Field(
        default_factory=list, description="Known issues affecting gating"
    )
