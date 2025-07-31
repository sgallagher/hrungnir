"""Basic model validation tests."""

from hrungnir.models.build import BuildConfiguration, BuildEstimate, BuildResult
from hrungnir.models.chain_build import BuildGroup, ChainBuildExecution, ChainBuildPlan
from hrungnir.models.package import DependencyRelation, Package, PackageGraph, PackageInfo


class TestBuildModels:
    """Test build-related models."""

    def test_build_configuration_creation(self):
        """Test BuildConfiguration can be created with minimal data."""
        config = BuildConfiguration(target="c10s-build", build_type="official", timeout=60)
        assert config.target == "c10s-build"
        assert config.scratch is False
        assert config.enable_draft_builds is False
        assert config.additional_repos == []

    def test_build_result_creation(self):
        """Test BuildResult can be created."""
        config = BuildConfiguration(target="c10s-build", build_type="official", timeout=60)
        result = BuildResult(
            package_name="test-package",
            status="success",
            config=config,
            build_id=123,
            start_time=None,
            end_time=None,
            duration_seconds=None,
            log_url=None,
            error_message=None,
            koji_task_id=None,
            copr_build_id=None,
            rog_pipeline_id=None,
        )
        assert result.package_name == "test-package"
        assert result.status == "success"
        assert result.artifacts == []

    def test_build_estimate_creation(self):
        """Test BuildEstimate can be created."""
        estimate = BuildEstimate(
            package_name="test-package",
            estimated_duration_minutes=30,
            estimated_queue_time_minutes=5,
            memory_gb=4,
            disk_gb=10,
            cpu_cores=2,
            confidence_score=0.8,
        )
        assert estimate.package_name == "test-package"
        assert estimate.estimated_duration_minutes == 30
        assert estimate.is_large_package is False
        assert estimate.confidence_score == 0.8


class TestChainBuildModels:
    """Test chain build models."""

    def test_build_group_creation(self):
        """Test BuildGroup can be created."""
        group = BuildGroup(
            group_id=1,
            packages=["pkg1", "pkg2"],
            estimated_duration_minutes=45,
            risk_level="low",
            max_parallel_jobs=2,
        )
        assert group.group_id == 1
        assert group.packages == ["pkg1", "pkg2"]
        assert group.can_run_in_parallel is True
        assert group.requires_special_target is False

    def test_chain_build_plan_creation(self):
        """Test ChainBuildPlan can be created."""
        group = BuildGroup(
            group_id=1,
            packages=["pkg1"],
            estimated_duration_minutes=30,
            risk_level="low",
            max_parallel_jobs=1,
        )
        plan = ChainBuildPlan(
            plan_id="test-plan-123",
            root_packages=["pkg1"],
            target_tag="c10s-build",
            build_groups=[group],
            estimated_total_duration_minutes=30,
            critical_path_packages=["pkg1"],
            overall_risk_level="low",
            strategy="parallel_groups",
            estimated_queue_time_minutes=0,
            default_build_config=None,
            created_by="test-user",
        )
        assert plan.plan_id == "test-plan-123"
        assert plan.total_packages == 1
        assert plan.strategy == "parallel_groups"  # default

    def test_chain_build_execution_creation(self):
        """Test ChainBuildExecution can be created."""
        group = BuildGroup(
            group_id=1,
            packages=["pkg1"],
            estimated_duration_minutes=30,
            risk_level="low",
            max_parallel_jobs=1,
        )
        plan = ChainBuildPlan(
            plan_id="test-plan-123",
            root_packages=["pkg1"],
            target_tag="c10s-build",
            build_groups=[group],
            estimated_total_duration_minutes=30,
            critical_path_packages=["pkg1"],
            overall_risk_level="low",
            strategy="parallel_groups",
            estimated_queue_time_minutes=0,
            default_build_config=None,
            created_by="test-user",
        )
        execution = ChainBuildExecution(
            execution_id="exec-123",
            plan=plan,
            current_status="pending",
            started_at=None,
            completed_at=None,
            error_message=None,
            retry_count=0,
        )
        assert execution.execution_id == "exec-123"
        assert execution.current_status == "pending"
        assert execution.progress_percentage == 0.0
        assert not execution.is_complete


class TestPackageModels:
    """Test package-related models."""

    def test_package_info_creation(self):
        """Test PackageInfo can be created."""
        info = PackageInfo(
            name="test-package",
            version="1.0.0",
            release="1",
            epoch="0",
            summary="Test package",
            description="A test package for unit tests",
        )
        assert info.name == "test-package"
        assert info.version == "1.0.0"

    def test_package_creation(self):
        """Test Package can be created."""
        info = PackageInfo(
            name="test-package",
            version="1.0.0",
            release="1",
            epoch="0",
            summary="Test package",
            description="A test package for unit tests",
        )
        package = Package(
            info=info,
            source_package="test-source",
            current_tag="build",
            dist_git_url="https://git.example.com/test-package",
            spec_file_path="/SPECS/test-package.spec",
            last_build_time="2025-01-01T00:00:00Z",
            status="success",
        )
        assert package.info.name == "test-package"
        assert package.has_packit_config is False
        assert package.build_requires == []
        assert package.status == "success"

    def test_dependency_relation_creation(self):
        """Test DependencyRelation can be created."""
        dep = DependencyRelation(
            dependent="pkg-a", dependency="pkg-b", relation_type="BuildRequires", depth=1
        )
        assert dep.dependent == "pkg-a"
        assert dep.dependency == "pkg-b"
        assert dep.is_direct is True
        assert dep.depth == 1

    def test_package_graph_creation(self):
        """Test PackageGraph can be created."""
        info = PackageInfo(
            name="test-package",
            version="1.0.0",
            release="1",
            epoch="0",
            summary="Test package",
            description="A test package for unit tests",
        )
        package = Package(
            info=info,
            source_package="test-source",
            current_tag="build",
            dist_git_url="https://git.example.com/test-package",
            spec_file_path="/SPECS/test-package.spec",
            last_build_time="2025-01-01T00:00:00Z",
            status="success",
        )
        dep = DependencyRelation(
            dependent="pkg-a", dependency="pkg-b", relation_type="BuildRequires", depth=1
        )
        graph = PackageGraph(packages={"test-package": package}, dependencies=[dep])
        assert "test-package" in graph.packages
        assert len(graph.dependencies) == 1
