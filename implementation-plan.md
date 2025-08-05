# (DRAFT) Hrungnir MCP Server Implementation Plan

## Executive Summary

Hrungnir(name subject to change) is a MCP (Model Context Protocol) server using FastMCP framework aimed at assisting software engineers working with RHEL, CentOS Stream packaging workflows.

## CentOS Stream Build Process Understanding

### Build Tags and Lifecycle

From the CentOS Stream 10 documentation, packages follow this progression:

1. `c10s-gate` - Initial landing after build
1. `c10s-candidate` - Passed gating tests
1. `c10s-pending` - Passed all processes, ready for signing
1. `c10s-pending-signed` - Signed and ready for release
1. `c10s-build` - Buildroot (inherits from pending)
1. `c10s-released` - Released to mirrors

### Source Management

- **Dist-Git**: GitLab repos at `https://gitlab.com/redhat/centos-stream/rpms/`
- **Source-Git**: Available for some packages with upstream git history
- **DistGit Lookaside Cache**: Binary assets referenced by SHA in `sources` file
- **Packit Integration**: Automated synchronization between source-git and dist-git
- **RoG Pipeline Integration**: RHEL-on-GitLab CI/CD with dynamic test generation

### RHEL-on-GitLab (RoG) Pipeline Architecture Integration

Hrungnir integrates deeply with the RoG pipeline's 7-stage architecture to provide intelligent build orchestration:

#### RoG Pipeline Stages (Integration Points)

1. **merge_check** - Rebase validation and ticket checking
1. **pre_build** - Pipeline initialization and test discovery *(Chain build planning integration)*
1. **build** - RPM building with intelligent target selection *(Core optimization target)*
1. **build_failure_analysis** - Log Detective integration *(Failure prediction)*
1. **test** - Dynamic test pipeline generation *(Risk assessment)*
1. **summary** - Result aggregation and MR approval *(Chain coordination)*
1. **promote** - Build tagging and downstream synchronization *(Timeline estimation)*

#### RoG-Specific Features Leveraged

- **Draft vs Scratch Builds**: Faster draft builds for development workflows
- **Label-Controlled Workflows**: `feature::draft-builds::enabled`, `feature::konflux::enabled`
- **Resource Allocation**: Large packages (kernel, systemd) get 768Mi memory allocation
- **Side Tag Management**: Complex dependency builds across multiple packages
- **Multi-token Authentication**: Namespace-specific GitLab token management

#### Enhanced Build Target Intelligence

```yaml
# RoG build-targets.yml integration
default:
  ystream: -candidate     # Standard builds
  zstream: -z-candidate   # Z-stream builds

kernel:
  ystream: -candidate-pesign  # Signed kernel builds requiring special handling

java-11-openjdk:
  rhel-9: java-openjdk-rhel-9-build  # Java-specific targets per RHEL version

# Draft build target mangling: removes -candidate, adds -draft
```

## Architecture Decision Analysis

### Phase 0: Architecture Evaluation

Before implementing the MCP server, we need to evaluate different architectural approaches:

#### Option 1: Pure Python MCP Server

**Pros**:

- Simpler deployment via `uv tool install` / `uvx`
- Direct FastMCP integration
- Easier debugging and development
- Lower resource overhead
- Better performance for Python-native operations

**Cons**:

- Manual dependency management for external tools
- Limited access to specialized CLI tools
- Requires separate installation of rpm-python, koji, etc.
- Complex SSL certificate handling for CentOS authentication

#### Option 2: Container-Based MCP Server

**Pros**:

- **Pre-built tooling**: Leverage existing containers like:
  - `registry.fedoraproject.org/fedora-toolbox:latest` (includes fedpkg, koji)
  - `quay.io/centos/centos:stream9-development` (CentOS development tools)
  - Custom images with centpkg, koji, rpmbuild pre-installed
- **Consistent environment**: Same tools as developers use
- **SSL certificates**: Easier management in container
- **CLI tool access**: Direct access to centpkg, fedpkg, koji CLI
- **Isolation**: Better security and dependency isolation

**Cons**:

- More complex deployment (Docker/Podman required)
- Higher resource usage
- Container orchestration complexity
- Potential performance overhead for frequent operations
- More complex development workflow

##### Existing Container Images for CentOS/Fedora Developers

1. **Fedora Toolbox**: `registry.fedoraproject.org/fedora-toolbox:42`

   - Includes: fedpkg, koji, rpm-build, git
   - Pre-configured for Fedora development

1. **CentOS Stream Development**: `quay.io/centos/centos:stream10-development`

   - Includes: centpkg, git, rpm-build
   - CentOS Stream specific tooling

1. **RHEL Developer toolbox**: `quay.io/rhel-devel-tools/rhel-developer-toolbox:latest`

   - Includes: beaker, centpkg, fedpkg, odcs, osh-cli (formerly covscan), rhcopr, rhelbz-components, rhel-repoquery, rhpkg, scl-utils, tmt

1. **Toolbx**: [containers/toolbox](https://github.com/containers/toolbox)

   - Provides consistent development environments
   - Could be extended with MCP server capabilities?

#### Selected Architecture: Python-Only MCP Server (IMPLEMENTED)

**Rationale**:

- Simpler deployment and development workflow, suitable for rapid prototyping and testing
- Easy integration with existing and future agentic workflow tools and platforms

## Tool Specifications (Prototype Concepts)

*Note: These are conceptual specifications for prototype development. Implementation details will be refined based on integration testing and library evaluation results.*

### Chain Build Optimizer Tool (in-progress)

**Concept**: Intelligent chain build orchestration for RoG pipeline workflows. Serve as proof-of-concept for other tools.

**Proposed Interface**:

```python
@tool
async def suggest_chain_build_order(
    packages: List[str],
    target_tag: str = "c10s",
    # Additional parameters to be determined during prototyping
) -> ChainBuildPlan:
    """
    Analyzes package dependencies and suggests optimal build order for chain builds.
    Integrates with RoG pipeline architecture for intelligent scheduling.

    Implementation approach will be determined based on:
    - Library evaluation results (packitos, specfile, etc.)
    - RoG pipeline integration capabilities
    - Performance and accuracy testing
    """
```

**Conceptual Features (Subject to Prototyping Validation)**:

- **RoG Pipeline Intelligence**: Integration with RHEL-on-GitLab build target selection and timing
- **Dependency Analysis**: Leveraging existing libraries to avoid reinventing dependency resolution
- **Build Type Optimization**: Draft vs scratch build selection based on RoG pipeline features
- **Side Tag Coordination**: Management of complex dependency builds across multiple packages
- **Risk Assessment**: Based on historical data and RoG pipeline reliability patterns
- **Resource Awareness**: Consideration of RoG resource allocation (memory, architecture)

### Smart Build Label Advisor Tool (Concept)

**Concept**: Intelligent RoG pipeline label selection

**Proposed Interface**:

```python
@tool
async def suggest_build_labels(
    package: str, changed_files: List[str], mr_description: str = ""
) -> BuildLabelRecommendation:
    """
    Analyzes package changes and suggests optimal RoG pipeline labels for faster builds.

    Prototype evaluation will determine best approach for change analysis and impact estimation.
    """
```

**Conceptual Intelligence**:

- Change pattern detection (spec-only vs source changes)
- Architecture compatibility analysis
- Container vs RPM build detection
- Time savings estimation per label combination?

### Build Readiness Checker Tool (Concept)

**Concept**: Comprehensive pre-flight validation with gating intelligence and failure prediction

**Proposed Interface**:

```python
@tool
async def check_build_readiness(
    package: str,
    target_branch: str = "c10s",
    check_dependencies: bool = True,
    include_gating_analysis: bool = True,
    historical_lookback_days: int = 30,
) -> BuildReadinessReport:
    """
    Comprehensive pre-flight validation to avoid build failures.
    Includes gating status monitoring and failure prediction based on historical patterns.

    Integration points:
    - RHEL CI + CentOS Stream CI gating systems
    - PackitAPI for automation status
    - Koji build system for dependency analysis
    - Historical gating data for failure prediction
    """
```

**Conceptual Validation Areas**:

#### Core Validation

- Package configuration syntax and completeness
- Build target compatibility with RoG pipeline
- Spec file validation using selected parsing library
- Source availability and dependency resolution
- Branch-specific requirements analysis

#### Gating Integration & Intelligence

- **Gating Status Monitoring**: Real-time status of packages in gating pipeline

  - Current position in c10s-gate → c10s-candidate → c10s-pending progression
  - RHEL CI test results and pending/failed tests identification
  - CentOS Stream CI status and known environmental issues
  - Estimated time to complete gating based on current queue depth

- **Historical Gating Pattern Analysis**:

  - Package-specific gating failure rates over configurable time periods
  - Common failure patterns by package type (kernel, Java, systemd, etc.)
  - Correlation analysis between dependency changes and gating failures
  - Time-of-day and day-of-week failure pattern recognition
  - Maintainer response time patterns for gating failures

- **Predictive Failure Assessment**:

  - Risk scoring based on recent upstream changes and their gating impact
  - Dependency chain risk propagation (if dep A fails gating, packages B, C at risk)
  - Architecture-specific failure prediction (x86_64 vs aarch64 vs s390x patterns)
  - Integration with RoG pipeline resource allocation patterns

#### Advanced Risk Mitigation

- **Proactive Dependency Validation**:

  - Cross-reference with packages currently failing in gating
  - Identify potentially problematic dependencies before build submission
  - Suggest alternative build timing based on dependency gating status

- **Build Coordination Intelligence**:

  - Detection of conflicting chain builds that might interfere
  - Side tag conflict prediction and resolution suggestions
  - Resource contention analysis (large package builds competing for resources)

- **Automated Fallback Recommendations**:

  - Alternative build targets if primary target shows high failure risk
  - Draft build suggestions for faster iteration during development
  - Suggested test subset execution for faster feedback loops

#### Gating Data Sources & Integration

- **RHEL CI Pipeline**: Test execution status, failure logs, environmental issues
- **CentOS Stream CI**: Stream-specific test results and known issues
- **Koji Build System**: Build dependency status, buildroot package availability
- **PackitAPI Integration**: Automation status, PR synchronization delays
- **Historical Build Database**: Pattern analysis from past builds and outcomes
- **RoG Pipeline Metrics**: Resource usage, timing patterns, success rates

*Additional tools to be added to this section*

## Project Structure (Conceptual Design)

```
hrungnir/
├── src/hrungnir/
│   ├── models/           # Pydantic data models
│   │   ├── build/        # Build-related models
│   │   ├── package/      # Package and dependency models
│   │   └── chain_build/  # Chain build orchestration models
│   ├── tools/            # MCP tool implementations
│   │   └── chain_build/  # Chain build optimization tools
│   ├── services/         # External service integrations
│   │   ├── rog/          # RoG pipeline integration
│   │   ├── packit/       # Packit API integration (if selected)
│   │   └── koji/         # Koji build system integration
│   ├── utils/            # Utility functions and helpers
│   │   └── graph/        # Dependency graph utilities
│   ├── config/           # Configuration management
│   │   └── rog/          # RoG-specific configurations
│   └── server.py         # FastMCP server entry point
├── tests/                # Test suite
│   ├── models/           # Model validation tests
│   ├── tools/            # Tool integration tests
│   └── services/         # Service integration tests
├── basic-memory/         # Documentation and architecture notes
├── pyproject.toml        # Project configuration
└── README.md            # Development setup instructions
```

*Note: This structure represents the conceptual design approach. Actual implementation may vary based on prototyping discoveries and integration requirements. The focus is on clear separation of concerns between data models, MCP tools, external service integrations, and utility functions.*

## Development Roadmap

### Phase 0: Foundation (COMPLETED)

- ✅ Architecture decision: Python-only MCP server
- ✅ Project structure and dependency setup
- ✅ Draft Pydantic data models
- ✅ Development environment with uv, ruff, basedpyright
- ✅ Basic pytest test framework

### Phase 1: MCP Tools Prototyping (IN PROGRESS)

### Current Implementation Status

- **Models**: ✅ Pydantic models for all core entities
- **Testing**: ✅ Type-checked model validation tests
- **Dependencies**: ✅ Modern Python toolchain with latest libraries
- **RoG Integration**: 🔄 Architecture documented, implementation planned

## Dependencies (Prototype Evaluation Phase)

### Core Framework Dependencies

- **fastmcp**: MCP protocol implementation - established choice
- **pydantic**: Data validation and serialization - established choice
- **httpx**: Modern async HTTP client - established choice

### Packaging Ecosystem Libraries (Under Evaluation)

The following libraries are being evaluated to avoid reinventing existing packaging workflow tools:

- **packitos**: Potential primary interface to Packit APIs and dist-git operations
- **specfile**: Spec file parsing and manipulation
- **pygit2** / **GitPython**: Git operations
- **ogr**: Unified interface for GitLab/GitHub operations
- **python-rpm**: Direct RPM metadata access
- **koji**: Build system integration options
- **atlassian-python-api**: Jira integration

### Development Toolchain

- **uv**: Package management and build system
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **basedpyright**: Type checking

### Evaluation Criteria

- **Avoid Reinvention**: Leverage battle-tested libraries where possible
- **RoG Integration**: Compatibility with RHEL-on-GitLab pipeline architecture
- **API Stability**: Mature libraries with stable APIs
- **Performance**: Async-compatible and efficient operations
- **Maintenance**: Active development and community support

## Implementation Status and Disclaimers

**Current Status**: Prototype/Concept Development Phase

**Important Notes**:

- This plan represents conceptual design and prototype intentions
- Tool specifications are preliminary concepts subject to refinement during implementation
- Library selections (packitos, specfile, etc.) are targets for evaluation, not final decisions
- Focus on avoiding reinvention by leveraging existing, battle-tested libraries
- Implementation details will evolve based on integration testing and performance evaluation
