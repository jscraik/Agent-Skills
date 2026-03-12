# Agent Skills

<!-- Skill count: 133 | Genome: active -->

<div align="center">

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docs](https://img.shields.io/badge/docs-passing-brightgreen)](/docs)
[![Skills](https://img.shields.io/badge/skills-133-blue)](/SKILL.md)

</div>

**Production-grade skill library for AI agents.** 133 validated skills that work across Codex, Claude Code, Gemini, and Antigravity—with automated quality gates, visual outputs, and a self-improving feedback loop.

## Why this exists

Building reliable AI agents requires more than good prompts. It requires:

- **Consistent execution** — skills that behave predictably across tools
- **Quality at scale** — validation that catches issues before they reach users
- **Continuous improvement** — learning from usage patterns, not just manual updates
- **Visual communication** — artifacts that humans can actually review and trust

This repository solves all four.

---

## What you get

### 1. Cross-Runtime Skills (133 and counting)

One canonical skill library, automatically projected to multiple agent runtimes:

| Runtime | Location | Format |
|---------|----------|--------|
| **Codex** | `~/.codex/skills/` | Native skill format |
| **Claude Code** | `~/.claude/skills/` | Native skill format |
| **Gemini** | `~/.gemini/skills/` | Native skill format |
| **Antigravity** | `~/.gemini/antigravity/skills.txt` | Flat list index |

**How it works**: Skills live in categorized folders (`frontend/`, `backend/`, `product/`, etc.). Running `just sync` creates symlinks to all runtime directories and regenerates the skill index. Edit once, propagate everywhere.

### 2. Visual-First Outputs

Skip the ASCII tables. These skills generate browser-native artifacts:

- **`visual-explainer`** — Self-contained HTML pages for architecture diagrams, comparisons, and data tables
- **`diagram-cli`** — Mermaid-based architecture diagrams with automatic context packs
- **`slides`** — Presentation-ready slide decks from markdown source

**Rule**: If a table has 4+ rows or 3+ columns, render it as HTML. Always.

### 3. Industrial-Grade Validation

11 CI workflows catch issues before they reach production:

| Workflow | What it validates |
|----------|-------------------|
| `skill-quality` | Skill structure, evals, contracts, industry benchmarks |
| `recursive-promotion-gate` | Skill graph artifact compliance |
| `docs-governance` | Link integrity, policy conformance |
| `security-scan` | CodeQL, Semgrep, Trivy CVE scanning |
| `codeql` | Static analysis for Python/TypeScript |

**Local verification**: `just validate` runs the same checks locally.

### 4. Self-Improving Skill Genome

The Skill Genome Loop analyzes usage patterns and proposes improvements through a human-gated workflow:

```bash
# Run analysis (dry-run)
just genome-loop

# Review pending candidates
python3 scripts/review_candidates.py --list

# Approve a candidate
python3 scripts/review_candidates.py --approve <candidate_id>
```

**Safety controls**:
- Kill-switch: `touch artifacts/skill-graphs/controls/kill-switch.txt`
- Rollout modes: shadow → canary → live
- Confidence gating: composite_score ≥ 0.82, window count ≥ 2
- Human approval required for all changes

**Operations**:
```bash
just spotlight          # Show skill needing attention today
just subject-scoreboard # View quality by domain (ui/backend/security)
just rollout-drill      # Test kill-switch and rollback behavior
```

---

## Quickstart

```bash
# Show system status
just status

# Run all validations
just validate

# Diagnose skill health
just diagnose

# Sync skills to all runtime directories
just sync

# Create a new skill from template
cp templates/SKILL.md.template frontend/my-skill/SKILL.md
```

### Available commands

```bash
just --list               # Show all commands
just count-skills         # Count active skills
just docs-lint            # Check documentation
just smoke-slides         # Test visual explainer
just spotlight            # Daily skill health spotlight
just subject-scoreboard   # Domain-level quality metrics
just rollout-drill        # Resilience testing (kill-switch, rollback)
just install-cron         # Set up nightly automation
just watch-readiness      # Check Agentation watch-mode readiness
just router-metrics       # Analyze router telemetry
```

---

## Repository layout

```text
~/dev/agent-skills/
├── auth/               # Authentication-focused skills
├── backend/            # Backend, architecture, CLI skills
├── frontend/           # Frontend and UI skills
│   ├── graphics/       # Image/video generation
│   ├── tools/          # Browser and design tooling
│   ├── ui/             # UI component and motion skills
│   └── website/        # Web publishing skills
├── github/             # GitHub and DevOps workflow skills
├── interview/          # Interview workflows
├── ops/                # Operational and deployment skills
├── product/            # Product specs, docs, planning
├── utilities/          # General-purpose utilities
├── .agents/skills/     # Flat symlink directory (tool entrypoint)
├── skills-antigravity/ # Antigravity-compatible projection
├── scripts/            # Repo-level tooling
├── references/         # Shared contracts (evals.yaml, contract.yaml)
└── templates/          # Skill templates
```

### Categorization rule

Put skills under the closest domain folder. Skills are self-contained with their own `references/` and `scripts/` when needed.

---

## How skills work

### Structure

Each skill is a folder containing:

```text
skill-name/
├── SKILL.md              # Main skill definition (YAML frontmatter + markdown)
├── references/           # Optional: evals.yaml, contract.yaml, task-profile.json
└── scripts/              # Optional: supporting scripts
```

### YAML frontmatter (required)

```yaml
---
name: skill-name
description: "One-line description (max 80 chars)"
metadata:
  category: frontend | backend | product | utilities
  tags: [tag1, tag2]
---
```

### Learning Posture (pilot)

Four skills support a novel execution mode that adds a learning dimension to delegation:

| Posture | Behavior |
|---------|----------|
| `learn` | Explain alternatives, assumptions, and risks first |
| `guided` | Propose concrete improvements, require checkpoint confirmation |
| `execute` | Apply agreed changes after safety gates pass |

Pilot skills: `skill-builder`, `agentation`, `systematic-debugging`, `interview-me`

---

## Creating a skill

```bash
# 1. Create folder and copy template
mkdir -p frontend/my-skill
cp templates/SKILL.md.template frontend/my-skill/SKILL.md

# 2. Edit SKILL.md with your content
# 3. Run validation
just validate

# 4. Sync to runtime directories
just sync

# 5. Test the skill
python3 scripts/diagnose_skill.py my-skill
```

---

## Troubleshooting

### Skill not loading

```bash
# Run diagnostics
python3 scripts/diagnose_skill.py <skill-name>

# Common fixes:
# - Remove nested .git: rm -rf .agents/skills/<name>/.git
# - Re-sync: just sync
# - Check YAML frontmatter has 'name:' and 'description:'
```

### Validation failures

```bash
# Docs lint
python3 scripts/docs_lint.py --mode warn --config docs-policy.json

# Plan graph validation
python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

---

## Documentation

- **[Skills index](/SKILL.md)** — Browse all 133 skills
- **[Contributor docs](/docs/index.md)** — How to add and validate skills
- **[Skill Genome runbook](/docs/skill-graphs/runbooks/skill-genome-loop.md)** — Operating the improvement loop

---

## Limits and constraints

| Capability | Current State |
|------------|---------------|
| Skill isolation | Per-folder (no sandboxing between skills) |
| Versioning | Repo-level only (no per-skills semver) |
| Language | English only |
| Sync | Local symlinks (use git for cross-machine sync) |

---

## Governance

- **License**: Apache 2.0 ([LICENSE](/LICENSE))
- **Contributing**: See [CONTRIBUTING.md](/CONTRIBUTING.md)
- **Security**: See [SECURITY.md](/SECURITY.md)
- **Code of Conduct**: See [CODE_OF_CONDUCT.md](/CODE_OF_CONDUCT.md)

---

<div align="center">

**brAInwav** — _from demo to duty_

</div>

---

<!-- AGENT-FIRST-WORKFLOW:START -->
## Agent-first workflow

1. Create or update a plan in `.agent/PLANS.md`
2. Validate: `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
3. Verify: `bash ~/.codex/scripts/verify-work.sh`
<!-- AGENT-FIRST-WORKFLOW:END -->
