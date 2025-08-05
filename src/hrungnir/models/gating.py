"""Gating intelligence and analysis data models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

type GatingStage = Literal[
    "c10s-gate",
    "c10s-candidate",
    "c10s-pending",
    "c10s-pending-signed",
    "c10s-build",
    "c10s-released",
]

type TestResult = Literal["pending", "running", "passed", "failed", "skipped", "error"]

type TestType = Literal["rhel_ci", "centos_stream_ci", "integration", "beaker", "tmt"]

type RiskLevel = Literal["low", "medium", "high", "critical"]

type RecommendedAction = Literal["proceed", "wait", "modify", "abort"]


class GatingTestStatus(BaseModel):
    """Individual test status within gating pipeline."""

    test_name: str = Field(description="Name of the test")
    test_type: TestType = Field(description="Type of gating test")
    status: TestResult = Field(description="Current test status")
    started_at: datetime | None = Field(None, description="Test start time")
    completed_at: datetime | None = Field(None, description="Test completion time")
    failure_reason: str | None = Field(None, description="Reason for test failure")
    log_url: str | None = Field(None, description="URL to test logs")
    architecture: str | None = Field(None, description="Architecture being tested")
    duration_minutes: int | None = Field(None, description="Test duration in minutes")


class PackageGatingStatus(BaseModel):
    """Current gating status for a specific package."""

    package_name: str = Field(description="Package name")
    nvr: str = Field(description="Name-Version-Release")
    current_stage: GatingStage = Field(description="Current stage in gating pipeline")
    stage_entered_at: datetime = Field(description="When package entered current stage")
    estimated_completion: datetime | None = Field(None, description="Estimated completion time")

    # Test execution details
    rhel_ci_tests: list[GatingTestStatus] = Field(
        default_factory=list, description="RHEL CI test results"
    )
    centos_stream_tests: list[GatingTestStatus] = Field(
        default_factory=list, description="CentOS Stream CI test results"
    )

    # Queue information
    queue_position: int | None = Field(None, description="Position in gating queue")
    queue_depth: int | None = Field(None, description="Total packages in queue")

    # Blocking information
    blocked_by: list[str] = Field(
        default_factory=list, description="Package NVRs blocking this package"
    )
    blocking: list[str] = Field(
        default_factory=list, description="Package NVRs blocked by this package"
    )

    # URLs and references
    koji_build_url: str | None = Field(None, description="Koji build URL")
    gating_yaml_url: str | None = Field(None, description="Gating configuration URL")
    resultsdb_url: str | None = Field(None, description="ResultsDB results URL")


class HistoricalGatingPattern(BaseModel):
    """Historical analysis of gating patterns for a package."""

    package_name: str = Field(description="Package name")
    analysis_period_days: int = Field(description="Number of days analyzed")

    # Failure statistics
    total_builds: int = Field(description="Total builds analyzed")
    gating_failures: int = Field(description="Number of gating failures")
    failure_rate: float = Field(ge=0.0, le=1.0, description="Gating failure rate")

    # Timing patterns
    average_gating_time_minutes: float = Field(description="Average time to complete gating")
    p95_gating_time_minutes: float = Field(description="95th percentile gating time")
    median_gating_time_minutes: float = Field(description="Median gating time")

    # Common failure patterns
    common_failure_reasons: dict[str, int] = Field(
        default_factory=dict, description="Failure reason -> count mapping"
    )
    failure_by_architecture: dict[str, float] = Field(
        default_factory=dict, description="Architecture -> failure rate mapping"
    )
    failure_by_time_of_day: dict[int, float] = Field(
        default_factory=dict, description="Hour -> failure rate mapping"
    )
    failure_by_day_of_week: dict[int, float] = Field(
        default_factory=dict, description="Day of week -> failure rate mapping"
    )

    # Dependency correlation
    dependency_failure_correlation: dict[str, float] = Field(
        default_factory=dict, description="Dependency package -> correlation score"
    )

    # Maintainer patterns
    average_maintainer_response_hours: float | None = Field(
        None, description="Average response time for gating failures"
    )


class GatingEnvironmentStatus(BaseModel):
    """Current status of gating infrastructure."""

    timestamp: datetime = Field(description="Status timestamp")
    rhel_ci_operational: bool = Field(description="RHEL CI system operational status")
    centos_stream_ci_operational: bool = Field(description="CentOS Stream CI operational status")
    known_issues: list[str] = Field(default_factory=list, description="Known infrastructure issues")
    estimated_delay_minutes: int | None = Field(None, description="Estimated delay due to issues")
    resource_contention_level: Literal["low", "normal", "high", "critical"] = Field(
        default="normal", description="Current resource contention level"
    )

    # Queue metrics
    total_packages_in_gating: int = Field(0, description="Total packages currently in gating")
    average_queue_time_minutes: float = Field(
        0.0, description="Average time packages spend in queue"
    )

    # System load indicators
    rhel_ci_queue_depth: int = Field(0, description="RHEL CI queue depth")
    centos_stream_ci_queue_depth: int = Field(0, description="CentOS Stream CI queue depth")


class BuildReadinessAssessment(BaseModel):
    """Comprehensive build readiness assessment with gating intelligence."""

    package_name: str = Field(description="Package name being assessed")
    target_branch: str = Field(description="Target branch for build")
    assessment_timestamp: datetime = Field(description="When assessment was performed")

    # Overall readiness
    overall_risk_score: float = Field(
        ge=0.0, le=1.0, description="Overall risk score (0=low risk, 1=high risk)"
    )
    risk_level: RiskLevel = Field(description="Categorized risk level")
    recommended_action: RecommendedAction = Field(description="Recommended action")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the assessment")

    # Core validation results
    spec_file_valid: bool = Field(description="Spec file syntax validation")
    dependencies_available: bool = Field(description="All dependencies available")
    build_target_compatible: bool = Field(description="Build target compatibility")
    source_accessible: bool = Field(description="Source code accessibility")
    packit_config_valid: bool = Field(default=True, description="Packit configuration validity")

    # Gating intelligence
    current_gating_status: PackageGatingStatus | None = Field(
        None, description="Current gating status if applicable"
    )
    historical_patterns: HistoricalGatingPattern | None = Field(
        None, description="Historical gating patterns"
    )
    environment_status: GatingEnvironmentStatus | None = Field(
        None, description="Current gating environment status"
    )

    # Risk factors and dependencies
    dependency_gating_risks: list[str] = Field(
        default_factory=list, description="Dependencies with gating risks"
    )
    conflicting_builds: list[str] = Field(
        default_factory=list, description="Potentially conflicting builds"
    )
    resource_conflicts: list[str] = Field(
        default_factory=list, description="Resource contention risks"
    )

    # Identified issues and suggestions
    identified_risks: list[str] = Field(
        default_factory=list, description="Specific risks identified"
    )
    mitigation_suggestions: list[str] = Field(
        default_factory=list, description="Risk mitigation suggestions"
    )
    blocking_issues: list[str] = Field(
        default_factory=list, description="Issues that would block the build"
    )

    # Alternative recommendations
    alternative_build_targets: list[str] = Field(
        default_factory=list, description="Alternative build targets"
    )
    suggested_wait_time_minutes: int | None = Field(
        None, description="Suggested wait time before proceeding"
    )
    draft_build_eligible: bool = Field(
        default=False, description="Whether package is eligible for draft builds"
    )
    optimal_build_timing: datetime | None = Field(None, description="Optimal time to submit build")


class GatingFailurePrediction(BaseModel):
    """Prediction model for gating failure likelihood."""

    package_name: str = Field(description="Package name")
    prediction_timestamp: datetime = Field(description="When prediction was made")

    # Prediction results
    failure_probability: float = Field(
        ge=0.0, le=1.0, description="Predicted probability of gating failure"
    )
    confidence_interval: tuple[float, float] = Field(
        description="95% confidence interval for prediction"
    )
    model_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the prediction model"
    )

    # Contributing factors
    risk_factors: dict[str, float] = Field(
        default_factory=dict, description="Risk factor -> impact score mapping"
    )
    protective_factors: dict[str, float] = Field(
        default_factory=dict, description="Protective factor -> impact score mapping"
    )

    # Dependency chain impact
    dependency_risk_propagation: dict[str, float] = Field(
        default_factory=dict, description="Dependency -> risk propagation score"
    )

    # Timing factors
    optimal_submission_window: tuple[datetime, datetime] | None = Field(
        None, description="Optimal time window for submission"
    )
    peak_risk_periods: list[tuple[datetime, datetime]] = Field(
        default_factory=list, description="High-risk time periods"
    )

    # Model metadata
    model_version: str = Field(description="Version of prediction model used")
    training_data_period: tuple[datetime, datetime] = Field(
        description="Period of training data used"
    )
    feature_importance: dict[str, float] = Field(
        default_factory=dict, description="Feature -> importance score mapping"
    )
