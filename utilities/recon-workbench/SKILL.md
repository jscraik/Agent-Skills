---
name: recon-workbench
description: Production-grade forensic evidence collection for software interrogation across macOS/iOS, web/React, and OSS repos. Use when running rwb CLI commands (doctor, authorize, plan, run, manifest, summarize, validate), designing probe catalogs or schemas, generating evidence-backed findings, inspecting targets under authorization guardrails, or configuring scope and compliance policies.
metadata:
  short-description: Forensic evidence collection for software interrogation
  schema_version: 2.0
  compatibility:
    requires:
      - Python 3.13+
      - Node.js 24+ (for web probes)
      - Xcode (optional, for iOS Simulator probes)
---
# Recon Workbench (rwb)

**Recon Workbench** is a production-grade forensic evidence collection platform with policy-driven authorization, comprehensive validation, and supply chain integrity.

Answer with sections titled exactly: **Outputs** and **Procedure** (include authorization notes).

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

- Check against GOLD Industry Standards guide in `~/.codex/AGENTS.override.md`
- All reconnaissance runs require explicit authorization
- Evidence-only claims: every finding must cite an artifact path

## Purpose

Create or evolve a unified, controlled interrogation workflow that: (1) authorizes targets, (2) plans probes, (3) collects deterministic artifacts, (4) generates evidence-backed findings, and (5) validates integrity with SHA256 manifests.

## Philosophy

- **Evidence over inference**: If you cannot cite an artifact, mark it as a hypothesis
- **Least privilege**: Start with static inventory, escalate only when justified
- **Safety first**: No circumvention, no DRM bypass, no private user data access
- **Decision-ready outputs**: Minimize noise, maximize traceability
- **Explain escalations**: Document the why behind each escalation step

## Pre-action Questions

Before building or inspecting, clarify:

1. **Authorization**: Do we have explicit permission to analyze the target?
2. **Target type**: macOS app, iOS Simulator/device, web app, or OSS repo?
3. **Goal**: Inventory, behavior map, API surface, regression diff, or patch plan?
4. **Evidence outputs**: What artifacts are required (JSON schemas, reports, traces)?
5. **Escalation limit**: Maximum allowed level (read_only < instrumentation < escalation)?

## When to Use

- Running `rwb` CLI commands for evidence collection
- Designing or updating probe catalogs, schemas, or validation pipelines
- Generating evidence-backed findings and reports
- Inspecting targets under strict legal/safety constraints
- Configuring scope policies and compliance guardrails
- If the target is a web app and source is unavailable, use `web-app-interrogate` for HAR/trace capture and endpoint mapping

## Core Constraints (Non-Negotiable)

- **No circumvention**: No DRM bypass, no cracking, no private data access
- **Evidence-only**: Every finding must cite an artifact path under `runs/...`
- **Observation-first**: Prefer static analysis; use dynamic only when authorized
- **Authorized tools only**: For deeper visibility, request debug builds and use LLDB/Instruments/logs
- **Web/React caution**: Component inspection only on authorized apps with documented permission
- **Redact by default**: Scrub secrets from logs, snapshots, and reports

## CLI Commands (rwb)

The `rwb` CLI is the primary interface via `uv run python -m rwb` or `recon` (from repo root):

| Command | Purpose |
|---------|---------|
| `rwb doctor` | Check toolchain readiness (Python, Node, Xcode, probe scripts) |
| `rwb authorize` | Create authorization artifact with target metadata |
| `rwb plan` | Generate or validate probe plan from catalog |
| `rwb run` | Execute probes with metadata capture |
| `rwb manifest` | Generate SHA256 integrity manifest |
| `rwb summarize` | Generate findings and report from run artifacts |
| `rwb validate` | Validate schemas and artifacts |

## Target Kinds

| Kind | Description | Example Locator |
|------|-------------|-----------------|
| `macos-app` | macOS applications (.app bundles) | `/Applications/MyApp.app` |
| `ios-sim` | iOS Simulator apps | `com.example.MyApp` (bundle ID) |
| `ios-device` | Physical iOS devices | `UDID` or device serial |
| `web-app` | Web applications | `https://example.com` |
| `oss-repo` | Open source repositories | `owner/repo` or git URL |

## Probe Sets

Predefined probe sets for common scenarios:

- `macos-baseline`: Bundle tree, codesign, Mach-O imports, metadata
- `macos-objc-static`: Static analysis including class dump and Swift demangling
- `macos-debug`: Baseline + LLDB backtrace + log capture
- `ios-baseline`: Bundle tree, setup, health, screenshot, metadata
- `ios-objc-static`: iOS static analysis
- `ios-debug`: Baseline + LLDB backtrace + log capture
- `ios-smoke`: Quick simulator validation
- `web-baseline`: Playwright trace + HAR capture
- `web-react`: Baseline + React Fiber component extraction
- `web-react-only`: React Fiber extraction only
- `oss-baseline`: Git hotspots + dependency tree
- `oss-full`: Baseline + Semgrep SAST scan

## Escalation Levels

- **read_only**: Static analysis, no code execution
- **instrumentation**: Log capture, tracing, non-invasive monitoring
- **escalation**: Debug builds, LLDB, dynamic analysis (requires explicit authorization)

## Scope Configuration

Create `scope.yaml` to set organizational defaults:

```yaml
# Disallow dangerous probes
disallowed_probes:
  - "debug.lldb_backtrace"
  - "ios.device_diagnose"

# Limit escalation level
max_escalation_level: "instrumentation"  # read_only < instrumentation < escalation

# Require authorization
require_authorization: true
```

## Inputs

- `target_id`: Unique identifier for the target
- `target_kind`: One of macos-app, ios-sim, ios-device, web-app, oss-repo
- `target_locator`: Path, URL, bundle ID, or repo identifier
- `authorization`: Authorization artifact (required)
- `probe_set`: Predefined probe set or custom probe list
- `run_dir`: Output directory for artifacts

## Outputs

**Structure**: `runs/<target>/<session>/<run>/`
- `raw/` - Probe artifacts (logs, dumps, traces, HARs)
- `manifest.json` - SHA256 hashes for integrity verification
- `derived/findings.json` - Schema-valid findings with evidence citations; include `schema_version` matching `schemas/findings.v2.schema.json`
- `derived/report.md` - Human-readable summary with artifact paths

## Procedure

### 1) Check Toolchain

```bash
uv run python -m rwb doctor --json
```

### 2) Create Authorization

```bash
uv run python -m rwb authorize \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --output authorization.json
```

### 3) Generate Probe Plan

```bash
uv run python -m rwb plan \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --probe-set macos-baseline \
  --authorization authorization.json
```

This creates `probe-plan.json` with all probes to execute.

### 4) Execute Probes

```bash
uv run python -m rwb run \
  --plan-file probe-plan.json \
  --run-dir runs/myapp/
```

### 5) Generate Findings

```bash
uv run python -m rwb summarize \
  --run-dir runs/myapp/
```

### 6) Generate Integrity Manifest

```bash
uv run python -m rwb manifest \
  --run-dir runs/myapp/ \
  --output runs/myapp/manifest.json
```

## Validation

Fail fast: stop at the first failed validation gate, fix the issue, and re-run the failed check before proceeding.

```bash
# Validate probe catalog
python scripts/validate_catalog.py --catalog probes/catalog.json

# Validate a manifest
python scripts/validate_manifest.py runs/myapp/manifest.json

# Validate evidence paths in findings
python scripts/validate_evidence.py runs/myapp/derived/findings.json runs/myapp/
```

## Escalation Ladder (Worst-Case Path)

1. **Static inventory** (safe, read-only)
2. **Baseline run** (minimal interaction)
3. **Stimulus run** (targeted action)
4. **Diff** (baseline vs stimulus)
5. **Advanced observation** (approved tools only; stop if protections block)

**Stop conditions**:
- Goals are met with evidence
- Further steps require circumvention or exceed authorization
- Signals flatten (no new findings across two successive probes)

## Evidence Discipline

- Every finding must cite one or more evidence paths
- Summaries must list commands used + artifact locations
- If evidence is insufficient, request additional probes rather than speculating
- Use `manifest.json` to verify artifact integrity

## Build Mode (Tooling Design)

When creating or evolving the workbench:

- Design schemas in `schemas/` with JSON Schema validation
- Add probes to `probes/catalog.json` with target kinds and timeouts
- Implement probe scripts in `scripts/probes/`
- Define probe sets for common workflows
- Update `AGENTS.md` with agent instructions
- Add validation scripts to `scripts/validate_*.py`

## Inspect Mode (Evidence Collection)

When analyzing a target:

1. Confirm authorization and target type
2. Select appropriate probe set
3. Execute probes and collect artifacts
4. Generate findings with evidence citations
5. Validate all artifacts and evidence paths
6. Produce report with artifact links

## Variation Rules

- Vary probe depth by authorization level and target risk profile
- Vary artifact collection based on target type (Apple, web, OSS) and goal
- Avoid repeating the same probe sequence across unrelated targets
- Prefer different variations when signals flatten

## Empowerment Principles

- **Operators**: Explicit stop conditions and safe rollback options
- **Teams**: Multiple probe paths when trade-offs exist
- **Stakeholders**: Clear evidence links and decision-ready summaries
- **Reviewers**: Direct artifact pointers for verification

## Anti-Patterns to Avoid

- Acting without explicit authorization or documented scope
- Skipping evidence capture while reporting conclusions
- Using intrusive probes when static inventory suffices
- Escalating by default instead of justifying each step
- Treating unknowns as confirmed facts
- Relying on inferred behavior without artifacts

## Example Prompts

- "Run a baseline reconnaissance on this macOS app and generate findings"
- "Design a probe set for React web app component inspection"
- "Validate the evidence paths in this findings.json"
- "Create an authorization artifact for this iOS Simulator target"
- "Generate a SHA256 manifest for this run directory"

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources

### Documentation

- `README.md` - Project overview and quickstart
- `docs/GOLD_STANDARD.md` - Gold Industry Standard compliance
- `AGENTS.md` - Agent instructions and workflows
- `SECURITY.md` - Security policy and vulnerability reporting
- `scope.example.yaml` - Scope configuration template

### Schemas

- `schemas/authorization.schema.json` - Authorization artifact structure
- `schemas/probe-plan.v2.schema.json` - Probe plan validation
- `schemas/findings.v2.schema.json` - Findings structure
- `schemas/manifest.v2.schema.json` - Integrity manifest structure

### Probe Catalog

- `probes/catalog.json` - All available probes and probe sets

### Validation Scripts

- `scripts/validate_catalog.py` - Validate probe catalog
- `scripts/validate_manifest.py` - Validate integrity manifest
- `scripts/validate_evidence.py` - Validate evidence paths in findings

### MCP Integration

- `scripts/mcp_server.py` - MCP server for AI agent integration

## Compliance Evidence

This skill meets Gold Industry Standards (baseline: January 31, 2026) for:

- **Security & Privacy**: Authorization enforcement, scope constraints, path traversal protection
- **Performance**: Timeouts, parallel execution, resource limits
- **Accessibility**: Structured JSON output, human-readable help text
- **Testing**: Lint (ruff), type check (mypy), tests (pytest), security scanning (Trivy, Semgrep)
- **Documentation**: Comprehensive docs, type hints, docstrings
- **Supply Chain**: Pinned dependencies, SBOM generation, provenance attestations

**Verification**: Run `uv run python -m rwb doctor` to check toolchain health.

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: recon-workbench
description: Production-grade forensic evidence collection for software interrogation across macOS/iOS, web/React, and OSS repos. Use when running rwb CLI commands (doctor, authorize, plan, run, manifest, summarize, validate), designing probe catalogs or schemas, generating evidence-backed findings, inspecting targets under authorization guardrails, or configuring scope and compliance policies.
metadata:
  short-description: Forensic evidence collection for software interrogation
  schema_version: 2.0
  compatibility:
    requires:
      - Python 3.13+
      - Node.js 24+ (for web probes)
      - Xcode (optional, for iOS Simulator probes)
---
```
Body:

# Recon Workbench (rwb)

**Recon Workbench** is a production-grade forensic evidence collection platform with policy-driven authorization, comprehensive validation, and supply chain integrity.

Answer with sections titled exactly: **Outputs** and **Procedure** (include authorization notes).

## Compliance

- Check against GOLD Industry Standards guide in `~/.codex/AGENTS.override.md`
- All reconnaissance runs require explicit authorization
- Evidence-only claims: every finding must cite an artifact path

## Purpose

Create or evolve a unified, controlled interrogation workflow that: (1) authorizes targets, (2) plans probes, (3) collects deterministic artifacts, (4) generates evidence-backed findings, and (5) validates integrity with SHA256 manifests.

## Philosophy

- **Evidence over inference**: If you cannot cite an artifact, mark it as a hypothesis
- **Least privilege**: Start with static inventory, escalate only when justified
- **Safety first**: No circumvention, no DRM bypass, no private user data access
- **Decision-ready outputs**: Minimize noise, maximize traceability
- **Explain escalations**: Document the why behind each escalation step

## Pre-action Questions

Before building or inspecting, clarify:

1. **Authorization**: Do we have explicit permission to analyze the target?
2. **Target type**: macOS app, iOS Simulator/device, web app, or OSS repo?
3. **Goal**: Inventory, behavior map, API surface, regression diff, or patch plan?
4. **Evidence outputs**: What artifacts are required (JSON schemas, reports, traces)?
5. **Escalation limit**: Maximum allowed level (read_only < instrumentation < escalation)?

## When to Use

- Running `rwb` CLI commands for evidence collection
- Designing or updating probe catalogs, schemas, or validation pipelines
- Generating evidence-backed findings and reports
- Inspecting targets under strict legal/safety constraints
- Configuring scope policies and compliance guardrails

## Core Constraints (Non-Negotiable)

- **No circumvention**: No DRM bypass, no cracking, no private data access
- **Evidence-only**: Every finding must cite an artifact path under `runs/...`
- **Observation-first**: Prefer static analysis; use dynamic only when authorized
- **Authorized tools only**: For deeper visibility, request debug builds and use LLDB/Instruments/logs
- **Web/React caution**: Component inspection only on authorized apps with documented permission
- **Redact by default**: Scrub secrets from logs, snapshots, and reports

## CLI Commands (rwb)

The `rwb` CLI is the primary interface via `uv run python -m rwb` or `./recon`:

| Command | Purpose |
|---------|---------|
| `rwb doctor` | Check toolchain readiness (Python, Node, Xcode, probe scripts) |
| `rwb authorize` | Create authorization artifact with target metadata |
| `rwb plan` | Generate or validate probe plan from catalog |
| `rwb run` | Execute probes with metadata capture |
| `rwb manifest` | Generate SHA256 integrity manifest |
| `rwb summarize` | Generate findings and report from run artifacts |
| `rwb validate` | Validate schemas and artifacts |

## Target Kinds

| Kind | Description | Example Locator |
|------|-------------|-----------------|
| `macos-app` | macOS applications (.app bundles) | `/Applications/MyApp.app` |
| `ios-sim` | iOS Simulator apps | `com.example.MyApp` (bundle ID) |
| `ios-device` | Physical iOS devices | `UDID` or device serial |
| `web-app` | Web applications | `https://example.com` |
| `oss-repo` | Open source repositories | `owner/repo` or git URL |

## Probe Sets

Predefined probe sets for common scenarios:

- `macos-baseline`: Bundle tree, codesign, Mach-O imports, metadata
- `macos-objc-static`: Static analysis including class dump and Swift demangling
- `macos-debug`: Baseline + LLDB backtrace + log capture
- `ios-baseline`: Bundle tree, setup, health, screenshot, metadata
- `ios-objc-static`: iOS static analysis
- `ios-debug`: Baseline + LLDB backtrace + log capture
- `ios-smoke`: Quick simulator validation
- `web-baseline`: Playwright trace + HAR capture
- `web-react`: Baseline + React Fiber component extraction
- `web-react-only`: React Fiber extraction only
- `oss-baseline`: Git hotspots + dependency tree
- `oss-full`: Baseline + Semgrep SAST scan

## Escalation Levels

- **read_only**: Static analysis, no code execution
- **instrumentation**: Log capture, tracing, non-invasive monitoring
- **escalation**: Debug builds, LLDB, dynamic analysis (requires explicit authorization)

## Scope Configuration

Create `scope.yaml` to set organizational defaults:

```yaml
# Disallow dangerous probes
disallowed_probes:
  - "debug.lldb_backtrace"
  - "ios.device_diagnose"

# Limit escalation level
max_escalation_level: "instrumentation"  # read_only < instrumentation < escalation

# Require authorization
require_authorization: true
```

## Inputs

- `target_id`: Unique identifier for the target
- `target_kind`: One of macos-app, ios-sim, ios-device, web-app, oss-repo
- `target_locator`: Path, URL, bundle ID, or repo identifier
- `authorization`: Authorization artifact (required)
- `probe_set`: Predefined probe set or custom probe list
- `run_dir`: Output directory for artifacts

## Outputs

**Structure**: `runs/<target>/<session>/<run>/`
- `raw/` - Probe artifacts (logs, dumps, traces, HARs)
- `manifest.json` - SHA256 hashes for integrity verification
- `derived/findings.json` - Schema-valid findings with evidence citations
- `derived/report.md` - Human-readable summary with artifact paths

## Procedure

### 1) Check Toolchain

```bash
uv run python -m rwb doctor --json
```

### 2) Create Authorization

```bash
uv run python -m rwb authorize \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --output authorization.json
```

### 3) Generate Probe Plan

```bash
uv run python -m rwb plan \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --probe-set macos-baseline \
  --authorization authorization.json
```

This creates `probe-plan.json` with all probes to execute.

### 4) Execute Probes

```bash
uv run python -m rwb run \
  --plan-file probe-plan.json \
  --run-dir runs/myapp/
```

### 5) Generate Findings

```bash
uv run python -m rwb summarize \
  --run-dir runs/myapp/
```

### 6) Generate Integrity Manifest

```bash
uv run python -m rwb manifest \
  --run-dir runs/myapp/ \
  --output runs/myapp/manifest.json
```

## Validation

```bash
# Validate probe catalog
python scripts/validate_catalog.py --catalog probes/catalog.json

# Validate a manifest
python scripts/validate_manifest.py runs/myapp/manifest.json

# Validate evidence paths in findings
python scripts/validate_evidence.py runs/myapp/derived/findings.json runs/myapp/
```

## Escalation Ladder (Worst-Case Path)

1. **Static inventory** (safe, read-only)
2. **Baseline run** (minimal interaction)
3. **Stimulus run** (targeted action)
4. **Diff** (baseline vs stimulus)
5. **Advanced observation** (approved tools only; stop if protections block)

**Stop conditions**:
- Goals are met with evidence
- Further steps require circumvention or exceed authorization
- Signals flatten (no new findings across two successive probes)

## Evidence Discipline

- Every finding must cite one or more evidence paths
- Summaries must list commands used + artifact locations
- If evidence is insufficient, request additional probes rather than speculating
- Use `manifest.json` to verify artifact integrity

## Build Mode (Tooling Design)

When creating or evolving the workbench:

- Design schemas in `schemas/` with JSON Schema validation
- Add probes to `probes/catalog.json` with target kinds and timeouts
- Implement probe scripts in `scripts/probes/`
- Define probe sets for common workflows
- Update `AGENTS.md` with agent instructions
- Add validation scripts to `scripts/validate_*.py`

## Inspect Mode (Evidence Collection)

When analyzing a target:

1. Confirm authorization and target type
2. Select appropriate probe set
3. Execute probes and collect artifacts
4. Generate findings with evidence citations
5. Validate all artifacts and evidence paths
6. Produce report with artifact links

## Variation Rules

- Vary probe depth by authorization level and target risk profile
- Vary artifact collection based on target type (Apple, web, OSS) and goal
- Avoid repeating the same probe sequence across unrelated targets
- Prefer different variations when signals flatten

## Empowerment Principles

- **Operators**: Explicit stop conditions and safe rollback options
- **Teams**: Multiple probe paths when trade-offs exist
- **Stakeholders**: Clear evidence links and decision-ready summaries
- **Reviewers**: Direct artifact pointers for verification

## Anti-Patterns to Avoid

- Acting without explicit authorization or documented scope
- Skipping evidence capture while reporting conclusions
- Using intrusive probes when static inventory suffices
- Escalating by default instead of justifying each step
- Treating unknowns as confirmed facts
- Relying on inferred behavior without artifacts

## Example Prompts

- "Run a baseline reconnaissance on this macOS app and generate findings"
- "Design a probe set for React web app component inspection"
- "Validate the evidence paths in this findings.json"
- "Create an authorization artifact for this iOS Simulator target"
- "Generate a SHA256 manifest for this run directory"

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources

### Documentation

- `README.md` - Project overview and quickstart
- `docs/GOLD_STANDARD.md` - Gold Industry Standard compliance
- `AGENTS.md` - Agent instructions and workflows
- `SECURITY.md` - Security policy and vulnerability reporting
- `scope.example.yaml` - Scope configuration template

### Schemas

- `schemas/authorization.schema.json` - Authorization artifact structure
- `schemas/probe-plan.v2.schema.json` - Probe plan validation
- `schemas/findings.v2.schema.json` - Findings structure
- `schemas/manifest.v2.schema.json` - Integrity manifest structure

### Probe Catalog

- `probes/catalog.json` - All available probes and probe sets

### Validation Scripts

- `scripts/validate_catalog.py` - Validate probe catalog
- `scripts/validate_manifest.py` - Validate integrity manifest
- `scripts/validate_evidence.py` - Validate evidence paths in findings

### MCP Integration

- `scripts/mcp_server.py` - MCP server for AI agent integration

## Compliance Evidence

This skill meets Gold Industry Standards (baseline: January 31, 2026) for:

- **Security & Privacy**: Authorization enforcement, scope constraints, path traversal protection
- **Performance**: Timeouts, parallel execution, resource limits
- **Accessibility**: Structured JSON output, human-readable help text
- **Testing**: Lint (ruff), type check (mypy), tests (pytest), security scanning (Trivy, Semgrep)
- **Documentation**: Comprehensive docs, type hints, docstrings
- **Supply Chain**: Pinned dependencies, SBOM generation, provenance attestations

**Verification**: Run `uv run python -m rwb doctor` to check toolchain health.
