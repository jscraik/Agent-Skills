# Agent Skills

Canonical skill repository for Codex, Claude Code, and Gemini/Antigravity.

This repo gives you one place to author skills, validate quality, and sync runtime-ready projections.

## Table of Contents
- [Why teams use this repo](#why-teams-use-this-repo)
- [What is implemented today](#what-is-implemented-today)
- [Quickstart](#quickstart)
- [Common workflows](#common-workflows)
- [Why the claims are credible](#why-the-claims-are-credible)
- [Operational limits](#operational-limits)
- [Repository layout](#repository-layout)
- [Documentation](#documentation)

## Why teams use this repo

- **Single source of truth**: author a skill once, then project it to multiple agent runtimes with `just sync`.
- **Lower review risk**: every change can run through deterministic validation (`scripts/validate_all.sh`) with per-check logs.
- **Safer automation**: routing and recursive improvement workflows include explicit control files, promotion gates, and artifact verification.

## What is implemented today

- **Large skill catalog**: currently 100+ `SKILL.md` assets across domain folders and system skills.
- **Cross-runtime projection**: `scripts/sync_skills.sh` rebuilds projections with lock + timeout protections and path safety checks.
- **Deterministic skill router**: `utilities/skill-builder/scripts/skill_router.py` returns ranked candidates, confidence, rationale, and policy decisions.
- **Guarded recursive loop**: `scripts/run_skill_genome_loop.py` supports kill-switch/rollout controls, redaction filters, watermark-based processing, and bounded output.
- **Promotion governance**: `scripts/human_promote_recursive_run.sh` enforces reviewer policy signatures, allowlist checks, run-dir confinement, and write-once blockers.
- **Artifact parity checks**: `scripts/verify_recursive_skill_graph_artifacts.py` classifies run artifacts and can fail strict mode in CI.
- **CI coverage**: 13 GitHub workflows cover PR hygiene, skill quality, promotion validation, security scanning, and governance checks.

## Quickstart

```bash
# 1) Health check
just status

# 2) Validate repo state
just validate

# 3) Sync skills to runtime projections
just sync

# 4) Optional: sync MCP config into Antigravity format
python3 scripts/sync_mcp.py
```

## Common workflows

### 1) Add or update a skill

```bash
# scaffold from template
mkdir -p frontend/my-skill
cp templates/SKILL.md.template frontend/my-skill/SKILL.md

# run quality checks
just diagnose
just validate

# rebuild projections
just sync
```

### 2) Run CI-equivalent checks locally

```bash
# preflight + sync + validation bundle
bash scripts/verify-work.sh

# validation-only path
bash scripts/validate_all.sh
```

### 3) Route a task to likely skills

```bash
python3 utilities/skill-builder/scripts/skill_router.py \
  --query "fix failing GitHub Actions checks" \
  --top-k 3 \
  --json
```

### 4) Operate recursive improvement safely

```bash
# preview candidates
just genome-loop

# generate candidates
just genome-loop-live

# review and approve
python3 scripts/review_candidates.py --list
python3 scripts/review_candidates.py --approve <candidate_id>
```

## Why the claims are credible

- **Validation is deterministic and logged**: `scripts/validate_all.sh` runs required + warn checks and writes artifacts to `artifacts/validation/`.
- **Routing is policy-aware**: `skill_router.py` returns ranked candidates with confidence, uncertainty reasons, policy mode decisions, and guardrail outcomes.
- **Promotion is governance-hardened**: `human_promote_recursive_run.sh` enforces signed reviewer policy, allowlist checks, run-dir confinement, and write-once blockers.
- **Recursive artifacts are verifiable**: `verify_recursive_skill_graph_artifacts.py` classifies run states and supports strict CI failures.
- **MCP sync is tested for real drift**: `test_sync_mcp.py` covers stdio/HTTP mapping, env header injection, default injection, and corrupted JSON recovery.

## Operational limits

- Skill versioning is repo-level, not per-skill semver.
- Sync is local projection; cross-machine distribution is still git-based.
- Tier-2 eval paths require local CLI/model auth availability on the runner.
- Some helper commands may be policy-gated depending on your Codex runtime approval settings.

## Repository layout

```text
agent-skills/
├── auth/ backend/ frontend/ github/ interview/ ops/ product/ utilities/
├── skills-system/            # system-level skills
├── .agents/skills/           # flat projection surface
├── skills-antigravity/       # Antigravity projection
├── scripts/                  # sync, validation, genome loop, governance tools
├── artifacts/                # generated reports, telemetry, run outputs
├── docs/                     # runbooks, specs, governance docs
└── templates/                # skill and eval templates
```

## Documentation

- [Skills index](SKILL.md)
- [Contributor docs](docs/index.md)
- [Governed solutions](docs/solutions/README.md)
- [Skill genome loop runbook](docs/skill-graphs/runbooks/skill-genome-loop.md)
- [Agent governance](docs/agents/06-security-and-governance.md)

## Governance

- License: Apache 2.0 (`LICENSE`)
- Contributing: `CONTRIBUTING.md`
- Security: `SECURITY.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`

<!-- AGENT-FIRST-WORKFLOW:START -->
## Agent-first workflow

1. Create or update a plan in `.agent/PLANS.md`
2. Validate: `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
3. Verify: `bash scripts/verify-work.sh`
<!-- AGENT-FIRST-WORKFLOW:END -->
