"""Package-related data models."""

from typing import Literal

from pydantic import BaseModel, Field

type PackageStatus = Literal["unknown", "building", "success", "failed", "pending"]

type CentOSStreamTag = Literal[
    "gate", "candidate", "pending", "pending-signed", "build", "released"
]


class PackageInfo(BaseModel):
    """Basic package information."""

    name: str = Field(description="Package name")
    version: str | None = Field(None, description="Package version")
    release: str | None = Field(None, description="Package release")
    epoch: str | None = Field(None, description="Package epoch")
    summary: str | None = Field(None, description="Package summary")
    description: str | None = Field(None, description="Package description")


class BuildRequirement(BaseModel):
    """Package build requirement."""

    name: str = Field(description="Required package name")
    version_spec: str | None = Field(None, description="Version specification (e.g., '>= 1.0')")
    conditional: str | None = Field(None, description="Conditional requirement expression")


class Package(BaseModel):
    """Represents a package in the packaging workflow."""

    info: PackageInfo = Field(description="Basic package information")
    source_package: str | None = Field(None, description="Source package name if binary package")
    build_requires: list[BuildRequirement] = Field(
        default_factory=list, description="Build dependencies"
    )
    requires: list[BuildRequirement] = Field(
        default_factory=list, description="Runtime dependencies"
    )

    # CentOS Stream specific
    current_tag: CentOSStreamTag | None = Field(None, description="Current CentOS Stream tag")
    dist_git_url: str | None = Field(None, description="Dist-git repository URL")
    spec_file_path: str | None = Field(None, description="Path to spec file")

    # Packit integration
    has_packit_config: bool = Field(
        default=False, description="Whether package has Packit configuration"
    )
    packit_job_types: list[str] = Field(
        default_factory=list, description="Configured Packit job types"
    )

    # Metadata
    last_build_time: str | None = Field(None, description="Last successful build timestamp")
    status: PackageStatus = Field("unknown", description="Current package status")


class DependencyRelation(BaseModel):
    """Represents a dependency relationship between packages."""

    dependent: str = Field(description="Package that depends on another")
    dependency: str = Field(description="Package being depended upon")
    relation_type: str = Field(description="Type of dependency (BuildRequires, Requires, etc.)")
    is_direct: bool = Field(default=True, description="Whether this is a direct dependency")
    depth: int = Field(1, description="Dependency depth (1 = direct, 2+ = transitive)")


class PackageGraph(BaseModel):
    """Graph of package dependencies."""

    packages: dict[str, Package] = Field(description="Map of package name to Package object")
    dependencies: list[DependencyRelation] = Field(description="List of dependency relationships")
