---
name: simple-tasks
description: Install a lightweight local task workflow backed by `tasks/TASKS.md` and `scripts/task.sh`. Use when the user wants simple in-repo task coordination, not team issue-tracker management.
metadata:
  skill-type: team_automation
---

# Simple Tasks

Install a lightweight local task workflow for one repo without dragging in external issue tooling.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Keep task state local, explicit, and markdown-backed.
- Preserve `tasks/TASKS.md` as the canonical source of truth.
- Prefer dry-run before upgrades in repos with existing task conventions.
- Optimize for fast daily execution rather than heavyweight planning systems.

## When to use
- The repo needs lightweight local task tracking.
- The user wants `scripts/task.sh` commands such as `claim`, `done`, `status`, or `summary`.
- A solo or agent-driven workflow needs a canonical markdown backlog without external sync.

## Required inputs
- `--project-dir PATH`
- Optional `--mode install|upgrade`
- Optional `--dry-run`

## Deliverables
- Installed or upgraded `scripts/task.sh` workflow.
- Canonical task files under `tasks/`.
- A short note on the main commands available after setup.

## Philosophy
- Local task tracking should be fast enough to actually use.
- The install should preserve clarity, not add another workflow layer.
- Verification matters because task tooling breaks quietly when files drift.

## Failure mode
- If the user needs multi-team issue management or external tracker sync, route to a project-management workflow instead.
- If the repo already has a conflicting task system, stop and make that migration risk explicit.
- If the project path is missing, pause before installing anything.

## Constraints
- Redact secrets, tokens, credentials, API keys, and PII in task notes and shared logs.
- Keep the scope to local project task tracking.
- Do not imply external system sync that the workflow does not provide.

## Workflow
1. Confirm the target project path and whether this is install or upgrade.
2. Run dry-run first when existing task files may already be present.
3. Install or upgrade the task workflow.
4. Verify `scripts/task.sh` and `tasks/TASKS.md` exist.
5. Run a small command check such as `status` or `summary`.

## Anti-patterns
- Using this workflow as a substitute for multi-team issue tracking.
- Spreading task state across unrelated markdown files.
- Installing without checking whether the repo already has custom task conventions.

## Validation
- Fail fast: stop at the first incomplete install or missing canonical task file.
- Ensure the installer exits successfully and creates expected files.
- Run `scripts/task.sh status` and `scripts/task.sh summary` at minimum.
- Confirm updates are reflected in `tasks/TASKS.md`.

## Examples
```bash
skills/simple-tasks/scripts/install.sh --project-dir /tmp/demo --dry-run
skills/simple-tasks/scripts/install.sh --project-dir /tmp/demo --mode upgrade
```

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[linear]] | Escalate to Linear when tasks need team-wide visibility |
| [[ce-plan]] | Seed task list from a finished implementation plan |
| [[alignment-checkpoint]] | Capture approved action items as simple tasks |
| [[verification-before-completion]] | Mark tasks done only after verification evidence |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
