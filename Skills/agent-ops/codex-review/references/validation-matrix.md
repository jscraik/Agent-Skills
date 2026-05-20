# Codex Review Validation Matrix

## Backup And Baseline

Before major refactors, create a backup copy outside the canonical skill path and run helper syntax plus dry-run checks against both backup and live skill.

## Helper Edits

Run:

```bash
bash -n Skills/agent-ops/codex-review/scripts/codex-review
bash Skills/agent-ops/codex-review/scripts/codex-review --help
bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --dry-run
CODEX_REVIEW_YOLO=0 bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --dry-run
bash Skills/agent-ops/codex-review/scripts/codex-review --mode commit --commit HEAD --no-yolo --dry-run
```

The default dry-run review command must not include `--add-dir` unless `--runtime-skills-dir DIR` or `CODEX_REVIEW_RUNTIME_SKILLS_DIR` opts in. Cross-repo runtime validation should prove explicit runtime-skill access fixes nested Codex system-skill refreshes only when the outer sandbox grants write access to `$HOME/.codex/skills`.

For output-classification edits, use a fixture or direct helper path that proves untagged `Findings`, `Findings: one issue`, or `Issues` output does not get marked clean, inline quoted `[P2]` examples are not treated as actionable, line-start severity findings override broad clean prose, and `## Findings` followed by `None` or `- None` stays clean.

For runtime-policy edits, first run the helper without permission expansion when nested Codex review is expected to fail locally. Then rerun the helper from the active Codex session with scoped filesystem access to Codex runtime state only and no extra network permission. Pass condition: the filesystem-only run launches nested Codex review, while a still-blocked run emits `codex-review blocked: blocked_runtime` and a source-backed fallback instruction instead of silently failing.

For portability edits, add fixtures that prove:

- an app-server initialization failure emits `codex-review blocked: blocked_runtime`, the filesystem-only retry profile, and the source-backed fallback instruction
- a branch fetch failure emits `codex-review warning: degraded_existing_refs`, the exact fetch blocker text, and recovery guidance
- `--fetch-required` turns a branch fetch failure into `codex-review blocked: blocked_fetch`

## Skill Or Reference Edits

Run:

```bash
vale Skills/agent-ops/codex-review/SKILL.md Skills/agent-ops/codex-review/references/*.md
./bin/ask skills audit Skills/agent-ops/codex-review --level strict --json --robot
./bin/ask evals run Skills/agent-ops/codex-review --mode smoke --runner discovery-smoke --skip-tessl --json --robot --no-dashboard
python3 Infrastructure/bin/ask skills external-review Skills/agent-ops/codex-review --audit-level compat --json
```

## Failure Classification

Classify every failed gate as one of:

- introduced by current patch
- pre-existing
- unrelated dirty worktree
- environment or tooling failure
- blocked on user input or permission
