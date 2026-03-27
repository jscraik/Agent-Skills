# Agent Skills

A shared skill library and quality system for AI coding agents — Codex, Claude Code, and Gemini.

Author a skill once. Run `just sync`. It appears in all three runtimes.

---

## Table of Contents

- [What it is](#what-it-is)
- [What you get](#what-you-get)
- [Quickstart](#quickstart)
- [Using skills](#using-skills)
- [Creating a skill](#creating-a-skill)
- [Skill quality system](#skill-quality-system)
- [Governance and safety](#governance-and-safety)
- [Repository layout](#repository-layout)
- [Limits and constraints](#limits-and-constraints)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

---

## What it is

Three problems, one repo:

- **Drift** — running the same skill across Codex, Claude Code, and Gemini without a shared source means they diverge over time.
- **Scale** — evaluating skill quality manually doesn't scale past a handful of skills.
- **Safety** — letting agents self-modify skills without human gates is unsafe.

This repo addresses all three: one source of truth, automated quality gates, and a human-gated improvement loop.

**Current state (2026-03-27):**
- 126 skill files across 8 domains
- 72 active eval profiles, 804 eval runs this week
- 100% non-regression compliance, GO decision on daily health
- Wave-0, Wave-1, Wave-2 all ready
- 248 cross-skill graph edges
- 13 CI workflows enforced on every PR

---

## What you get

### 1. Cross-runtime skill library (126 skills)

Skills are authored in domain folders and projected to every runtime on sync:

| Runtime | Install location |
|---------|-----------------|
| Codex | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| Gemini / Antigravity | `~/.gemini/antigravity/skills/` + `skills.txt` |

Domain breakdown:

| Domain | Skills | Examples |
|--------|--------|---------|
| `utilities/` | 40 | `skill-builder`, `diagram-cli`, `systematic-debugging`, `interview-me` |
| `product/` | 38 | `product-spec`, `docs-expert`, `security-threat-model`, `linear` |
| `frontend/` | 29 | `shadcn-ui`, `react-ui-patterns`, `figma`, `stitch-design` |
| `github/` | 5 | `gh-workflow`, `gh-fix-ci`, `check-pr`, `resolve-pr-parallel` |
| `backend/` | 4 | `backend-engineer`, `mcp-builder`, `workers-mcp`, `cli-spec` |
| `auth/` | 2 | `create-auth`, `best-practices` |
| `interview/` | 3 | `interview-me`, `architecture-interview`, `deep-interview` |

`just sync` also projects MCP server configs from `~/.codex/config.toml` to Antigravity.

### 2. Skill graph (248 edges)

Every skill has a `## See Also` table and a topic-map tag. These are extracted into `docs/skill-graphs/adjacency.yaml` and used to surface related skills when routing. The graph is browsable as an HTML visual:

```bash
python3 scripts/build-adjacency-yaml.py     # rebuild from SKILL.md tables
python3 scripts/validate-adjacency.py       # check for broken references
```

### 3. Skill router

`utilities/skill-builder/scripts/skill_router.py` routes natural-language queries to the most relevant skill:

```bash
python3 utilities/skill-builder/scripts/skill_router.py \
  --query "fix failing CI on my PR" \
  --top-k 3 \
  --json
```

The router scores by keyword overlap, path context, and explicit name mention, and emits confidence bands (`low` / `medium` / `high`). In the current build, most queries return `band=low` — the router is useful for discovery, not guaranteed routing.

It runs security checks via `openclaw_skill_guard.py` before routing to high-risk skills, and appends telemetry to `artifacts/skill-graphs/telemetry/route-events.jsonl`.

### 4. Automated quality gates (13 CI workflows)

Every `SKILL.md` change runs tiered gates:

**Tier 1 — Structure gate** (every PR):
- Validates YAML frontmatter (`name`, `description`, `metadata.skill-type`)
- Compares against `benchmark-policy.json` baseline; fails on regressions
- Progressive disclosure lint (description routing vs. procedure depth)

**Tier 2 — Eval baseline** (on `workflow_dispatch`):
- Runs `run_skill_evals.py` per skill in dual-run mode
- Captures JSONL traces and builds a scorecard dashboard

```bash
just diagnose      # Tier-1 equivalent, all skills
just validate      # Full quality suite
just ci-local      # Full CI bundle locally
```

Full CI workflow list:

| Workflow | Trigger | Enforces |
|----------|---------|---------|
| `pr-pipeline` | Every PR | PR template, validate, harness preflight |
| `ci-tests` | Push + PR | Docs lint, skill diagnostics |
| `skill-quality` | SKILL.md changes | Tier-1 structure + benchmark; Tier-2 evals |
| `skill-graph-diff` | SKILL.md changes | See Also gate, adjacency validation |
| `recursive-promotion-gate` | Promotion artifacts | Validates promotion decisions |
| `recursive-skill-shadow` | Mon 1am UTC + dispatch | Shadow cycle, failure-pattern candidates |
| `benchmark-policy-refresh` | Mon 7am UTC + dispatch | Threshold ratchet, auto-opens PR |
| `greptile-review` | Every PR | AI-assisted code review |
| `security-scan` | Every PR | Semgrep + Trivy CVE scanning |
| `codeql` | Push + PR | CodeQL static analysis (Python, TypeScript) |
| `secret-scan` | Every PR | Gitleaks secret detection |
| `docs-governance` | Docs changes | Link integrity, policy conformance |
| `gov-security-gates` | Governance changes | Policy file integrity |

### 5. Recursive improvement loop

The loop runs every Monday against 72 pilot profiles:

```
generate → evaluate → diagnose → improve → re-score
```

Each run writes artifacts under `artifacts/skill-graphs/runs/<run_id>/`:

| Artifact | What it records |
|----------|----------------|
| `run.json` | Status, stop reason, counters |
| `iteration_journal.jsonl` | Per-iteration scores |
| `events.jsonl` | Event envelope (required for wave gates) |
| `promotion_decision.json` | Meets promotion criteria? |
| `lesson_candidates.json` | Generalizable lessons |

**Daily health report** (`docs/skill-graphs/telemetry/daily-skill-health.md`) gives a GO / HOLD / STOP decision based on six gates: non-regression compliance, budget compliance, quality uplift, first-pass acceptance delta, failure reduction delta, and event envelope errors.

**Human promotion gate:** before any lesson is merged, a human runs `scripts/human_promote_recursive_run.sh`. It validates the run ID, enforces the approver allowlist (`docs/skill-graphs/governance/recursive-loop-approvers.yaml`), checks the policy signature, and guards against path traversal.

```bash
just genome-loop          # dry-run: see what would be proposed
just genome-loop-live     # live run: stages candidates for review
python3 scripts/review_candidates.py --list
python3 scripts/review_candidates.py --approve <candidate_id>
```

**Safety controls:**

| Control | How |
|---------|-----|
| Kill-switch | `touch artifacts/skill-graphs/controls/kill-switch.txt` |
| Rollout mode | `echo active > artifacts/skill-graphs/controls/rollout-mode.txt` |
| Rollback | `touch artifacts/skill-graphs/controls/rollback-required.txt` |
| Confidence gate | `composite_score ≥ 0.82`, `window_count ≥ 2` |

```bash
just rollout-drill    # confirm kill-switch works
```

### 6. Wave readiness (staged rollout control plane)

Three waves govern skill rollout from lab to production:

| Wave | Skills | Gate |
|------|--------|------|
| Wave-0 (controls) | All | Zero event envelope errors, ≥2 approvers |
| Wave-1 (manual) | 10 hand-curated | Wave-0 ready, all profiles valid |
| Wave-2 (co-pilot) | 62 remaining | Wave-1 ready, all profiles valid |

Current state: all three waves ready (`wave-readiness.json`).

### 7. Feedback protocol (123 skills)

After every skill run, the agent asks:

> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"

Responses are recorded to `ops/metrics/skill-feedback/decision-feedback.jsonl` and aggregated by domain:

```bash
just subject-scoreboard    # domain-level quality metrics
```

Bad-outcome rates surface which skills need improvement. The scoreboard feeds the improvement loop.

### 8. Visual outputs

```bash
just spotlight            # daily health — one skill needing attention
just subject-scoreboard   # domain quality scoreboard
just router-metrics       # routing telemetry summary
just smoke-slides         # visual explainer smoke test
```

---

## Quickstart

```bash
just status           # system health overview
just validate         # full validation suite
just count-skills     # count active skills
just sync             # project skills + MCP config to all runtimes
```

---

## Using skills

Skills are invoked as slash commands inside the agent runtime:

```
/skill-builder        # create, improve, or validate a skill
/systematic-debugging # trace a bug to root cause
/gh-fix-ci            # diagnose failing CI on a PR
/interview-me         # surface requirements before building
/diagram-cli          # generate architecture diagrams
/product-spec         # write a spec from an idea
```

The full list is at `SKILL.md` (auto-generated index) or:

```bash
just count-skills
ls ~/.claude/skills/         # Claude Code
ls ~/.codex/skills/          # Codex
```

To find a skill for a task:

```bash
python3 utilities/skill-builder/scripts/skill_router.py \
  --query "your task description" \
  --top-k 5
```

---

## Creating a skill

```bash
# From template
mkdir -p domain/my-skill
cp templates/SKILL.md.template domain/my-skill/SKILL.md

# Or use the skill-builder skill
/skill-builder
```

Minimum required structure:

```text
my-skill/
└── SKILL.md      # YAML frontmatter + instructions
```

Required frontmatter:

```yaml
---
name: my-skill
description: "One routing sentence — what it does and when to use it. Max 80 chars."
metadata:
  skill-type: scaffolding_templates  # see canonical values below
---
```

Canonical `skill-type` values: `library_api_reference`, `product_verification`, `data_fetch_analysis`, `team_automation`, `scaffolding_templates`, `code_quality_review`, `ci_cd_deployment`, `runbook`, `infrastructure_ops`.

After authoring:

```bash
just validate          # run all quality gates
just sync              # project to runtimes
```

The CI `skill-quality` workflow runs automatically on PR.

---

## Skill quality system

### harness.contract.json

The contract (`v1.2.0`) defines merge policies:

- **Risk tiers**: `scripts/**`, `.github/workflows/**` → high; `**/SKILL.md` → medium; `README.md` → low
- **Merge policy**: high requires `review-gate` + `evidence-verify`; medium requires `review-gate`
- **Diff budget**: max 10 files, max 400 net LOC (overridable with `diff-budget-override` label)
- **Branch protection**: PRs to `main`, `master`, `release/*` blocked by default

### Benchmark policy

`benchmark-policy.json` sets coverage and quality floor thresholds. The `benchmark-policy-refresh` workflow auto-ratchets thresholds Monday morning and opens a PR if any threshold improved.

---

## Governance and safety

- **Approver allowlist**: `docs/skill-graphs/governance/recursive-loop-approvers.yaml` — signature-verified; required for any lesson promotion
- **Path confinement**: promotion scripts enforce `confine_run_dir()` — run dirs must stay within `artifacts/skill-graphs/runs/`
- **Secret redaction**: `recursive_skill_loop.py` scrubs API keys, PATs, Slack tokens, SSH keys, AWS keys, JWTs, and IP addresses before writing any candidate
- **Kill-switch**: one file write halts the improvement loop
- **OpenClaw guard**: router runs readiness and security checks before routing to high-risk skills

---

## Repository layout

```text
agent-skills/
├── auth/               # Auth skills (create-auth, best-practices)
├── backend/            # Backend, architecture, MCP, CLI skills
├── frontend/           # UI, graphics, design tools, Stitch skills
├── github/             # GitHub workflow, CI, PR review skills
├── interview/          # Requirements and interview skills
├── product/            # Planning, specs, docs, security, ops skills
├── utilities/          # General-purpose + skill-builder tooling
│   └── skill-builder/
│       └── scripts/    # Router, eval runner, quality gates, shadow report
├── .agents/skills/     # Flat symlink view (agent entrypoint)
├── skills-antigravity/ # Antigravity-specific projection
├── scripts/            # Repo-level tooling (sync, genome loop, promote)
├── templates/          # SKILL.md and eval templates
├── artifacts/          # Generated outputs (benchmarks, telemetry, runs)
├── docs/
│   └── skill-graphs/   # Governance docs, runbooks, telemetry, wave readiness
├── ops/metrics/        # Feedback logs and scoreboard reports
└── harness.contract.json
```

---

## Limits and constraints

| Capability | Current state |
|------------|--------------|
| Skill isolation | Per-folder; no sandboxing between skills |
| Versioning | Repo-level only; no per-skill semver |
| Language | English only |
| Sync | Local symlinks; use git for cross-machine distribution |
| Skill router | Keyword-based; confidence is currently low for most queries |
| Tier-2 evals | Require `codex` and/or `claude` CLI + auth on the runner |
| Improvement loop | Simulation mode; real Claude agents not yet wired |

---

## Troubleshooting

### Skill not found after sync

```bash
just check-nested-git                       # nested .git is the most common cause
just sync
python3 scripts/diagnose_skill.py <skill>   # diagnose specific skill
head -5 <skill-dir>/SKILL.md                # confirm name + description fields present
```

### Validation failures

```bash
python3 scripts/docs_lint.py --mode warn --config docs-policy.json
python3 scripts/verify_router_schema.py
bash scripts/lint_openai_skill_format.sh --mode strict
```

### Improvement loop stuck

```bash
ls artifacts/skill-graphs/controls/             # check active control files
cat artifacts/skill-graphs/telemetry/.genome-watermark
just rollout-drill                              # confirm kill-switch works
```

---

## Documentation

- **[Skills index](SKILL.md)** — auto-generated list of all surfaced skills
- **[Contributor docs](docs/index.md)** — add, validate, and ship skills
- **[Skill Genome runbook](docs/skill-graphs/runbooks/skill-genome-loop.md)** — operating the improvement loop
- **[Agent governance](docs/agents/06-security-and-governance.md)** — security policy and audit trail
- **[Wave readiness](artifacts/skill-graphs/onboarding/wave-readiness.json)** — current staged rollout state
- **[Daily health](docs/skill-graphs/telemetry/daily-skill-health.md)** — live GO/HOLD/STOP decision

---

## Governance

- **License**: Apache 2.0 ([LICENSE](LICENSE))
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

<div align="center">

**brAInwav** — _from demo to duty_

</div>
