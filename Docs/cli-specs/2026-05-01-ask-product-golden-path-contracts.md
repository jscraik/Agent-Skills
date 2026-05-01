---
title: ask Product Golden Path Command Contracts
status: active-contract
date: 2026-05-01
agent_compatible: true
schema_version: 1
linear_issue: JSC-246
governing_plan: Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md
---

# ask Product Golden Path Command Contracts

## Purpose

Define namespace-first product command contracts for Agent Skills Kit before
adding executable command surface. These contracts keep the project oriented
around an agent capability control plane while avoiding top-level command
sprawl.

The rule for P4 is:

```text
Document the intended operator and agent contracts first. Add executable routes
only after baseline friction evidence proves a command will reduce real
decision cost.
```

## Baseline Friction Evidence

Captured on 2026-05-01 against branch
`codex/he-code-review-openclaw-flow`.

| Command                                                                                                                    | Observed Output                                                                                                              | Friction                                                                                                                                                     |
| -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `./bin/ask repo status --json --robot`                                                                                     | Reports `is_git` and `skills_synced` only.                                                                                   | It proves basic repo health but does not include runtime budget, handle health, surface policy status, blockers, or next command guidance.                   |
| `./bin/ask runtime budget --json --robot`                                                                                  | Reports `advanced_visible_count: 162`, advisory threshold `60`, `first_level_default_count: 109`, and `budget_status: pass`. | Runtime surface health is available, but agents must know to call it separately and then interpret large JSON.                                               |
| `./bin/ask repo surface --json`                                                                                            | Reports `status: warning`, `blocking_findings: 4003`, and tracked-surface classifications.                                   | Surface ownership evidence exists, but it is low-level inventory output and not yet combined with repo health or closeout readiness.                         |
| `./bin/ask repo --help`                                                                                                    | Exposes `status`, `validate`, `check-stability`, `doctor-catalog`, `provider-audit`, and `surface`.                          | There is no namespace-first health command that composes repo, runtime, handle, and surface signals.                                                         |
| `./bin/ask skills --help`                                                                                                  | Exposes `goal`, `route`, `proof`, `handles`, and related primitives.                                                         | Goal and skill explanation primitives exist, but product contracts do not yet define how they map to improve, explain, prove, or closeout workflows.         |
| `./bin/ask repo doctor-catalog --json --robot`                                                                             | Returns `decision_status: resolved` after `README.md` exposes canonical count `20`.                                          | Catalog parity is separately diagnosable, but product health still needs to surface this blocker when goal routing or closeout depends on it.                |
| `./bin/ask skills goal "continue implementing the Agent Skills Kit repo surface control-plane plan" --json --robot`        | Returns `intent_unresolved` with `route_decision_status: unresolved_ambiguity`.                                              | Broad goals can remain too ambiguous even after catalog parity is healthy; product flows need sharper repair prompts and next-command guidance.              |
| `./bin/ask skills goal "use he-work to implement P4 namespace-first product command contracts for JSC-246" --json --robot` | Resolves `he-work` with confidence `0.938`.                                                                                  | Goal routing works when the user names the workflow and phase, which supports a future `skills improve` contract that asks for narrower context when needed. |

P4 therefore implements contracts only. The first executable candidate should be
`ask repo doctor`, but it should ship only with a focused test proving that it
reduces this multi-command operator path into one stable envelope.

## Shared Envelope

All commands in this document must use the standard `ask` JSON envelope:

```json
{
  "status": "success",
  "trace_id": "uuid",
  "metadata": {
    "version": "0.1.0",
    "command": "repo doctor --json --robot",
    "next_steps": []
  },
  "data": {},
  "telemetry": {
    "latency_ms": 0
  },
  "errors": []
}
```

Every contract must preserve:

- `metadata.next_steps` for agent actionability;
- `trace_id` for run correlation;
- machine-readable blocker status;
- human-readable summary output when `--json` is absent;
- no top-level alias until command telemetry or baseline evidence proves it
  helps more than it widens the surface.

## `ask repo doctor`

Purpose: compose repo health into one operator and agent closeout view.

Inputs:

- `--json`
- `--robot`
- `--strict`, optional; returns non-zero only for true doctor blockers, not for
  expected diagnostic debt unless that debt is configured as blocking.

Required data fields:

```json
{
  "repo_doctor": {
    "repo": {
      "is_git": true,
      "branch": "string",
      "dirty": false,
      "skills_synced": true
    },
    "runtime_budget": {
      "status": "pass",
      "advanced_visible_count": 162,
      "advanced_visible_warn": 60,
      "first_level_default_count": 109,
      "advisories": []
    },
    "handles": {
      "status": "pass",
      "collisions": [],
      "unresolved": []
    },
    "surface_policy": {
      "status": "warning",
      "blocking_findings": 4003,
      "unknown_count": 39,
      "historical_artifact_count": 3959
    },
    "blockers": [],
    "next_command": "./bin/ask repo surface --json"
  }
}
```

Required behavior:

- Include repo, sync, runtime budget, handles, surface policy, blockers, and the
  next recommended command.
- Preserve runtime surface advisories even when the overall doctor status is
  pass.
- Distinguish strict failures from expected diagnostic warnings.
- Keep cleanup decisions out of doctor; link to `repo surface` or cleanup-prep
  evidence instead.

Measurable improvement target:

- Replace at least three separate diagnostic calls with one JSON envelope:
  `repo status`, `runtime budget`, and `repo surface`.

## `ask repo onboard`

Purpose: explain current repo and runtime state, then recommend one next action.

Inputs:

- `--json`
- `--robot`
- `--profile human|agent`, optional; default `agent`.

Required data fields:

```json
{
  "repo_onboard": {
    "repo_root": "/absolute/path",
    "runtime_projection": "rooted",
    "active_root_skills": 10,
    "command_handles": 109,
    "surface_policy_status": "warning",
    "recommended_next_action": {
      "command": "./bin/ask repo doctor --json --robot",
      "reason": "Establish current health before editing skills or projections."
    }
  }
}
```

Required behavior:

- Explain repo/runtime state without requiring the user to know projection,
  handle, or catalog internals first.
- Return exactly one primary next action, plus optional secondary links.
- Keep onboarding read-only.

## `ask skills improve`

Purpose: map a user goal to candidate capabilities, validation, and sync
actions.

Inputs:

- free-form goal string;
- `--json`;
- `--robot`;
- `--repo`, optional path defaulting to current repo.

Required data fields:

```json
{
  "skills_improve": {
    "goal": "make agents better at fixing PR comments",
    "candidate_capabilities": [
      {
        "name": "github:gh-address-comments",
        "source": "plugin",
        "confidence": 0.83,
        "reason": "Matches unresolved PR review thread workflows."
      }
    ],
    "required_validation": [
      "./bin/ask skills proof gh-address-comments --json --robot"
    ],
    "sync_actions": [],
    "next_command": "./bin/ask skills explain gh-address-comments --json --robot"
  }
}
```

Required behavior:

- Reuse existing `skills goal`, `skills route`, `skills proof`, and graph
  primitives rather than inventing a second resolver.
- Separate candidate skill/plugin capabilities from validation and sync actions.
- Never install, sync, or delete capabilities without an explicit command step.

## `ask skills explain`

Purpose: explain what a capability is, when to use it, and what runtime surfaces
it touches.

Inputs:

- skill, handle, or plugin capability name;
- `--json`;
- `--robot`.

Required data fields:

```json
{
  "skills_explain": {
    "query": "he-code-review",
    "canonical_source": "Plugins/harness-engineering/skills/code_quality_review/he-code-review/SKILL.md",
    "generated_handle": ".agents/skills/he-code-review/SKILL.md",
    "runtime_projection": "rooted",
    "loaded_references": [],
    "when_to_use": [],
    "when_not_to_use": [],
    "validation": [
      "./bin/ask skills audit Plugins/harness-engineering/skills/code_quality_review/he-code-review --level strict"
    ],
    "overlaps": []
  }
}
```

Required behavior:

- Distinguish canonical source, generated handle, runtime projection, loaded
  references, and validation.
- Include overlap with OpenAI or local plugin skills when available.
- Keep explanation output concise and link deeper references rather than loading
  full skill bodies by default.

## `ask skills prove`

Purpose: prove that a capability is reachable and useful from the current
runtime.

Inputs:

- skill, handle, or goal;
- `--json`;
- `--robot`;
- `--scenario`, optional named workout or eval case.

Required data fields:

```json
{
  "skills_prove": {
    "query": "he-code-review",
    "reachability": {
      "canonical_source_exists": true,
      "generated_handle_exists": true,
      "runtime_visible": true
    },
    "quality_evidence": {
      "audit_status": "pass",
      "workout_status": "not_run",
      "eval_status": "not_run"
    },
    "next_command": "./bin/ask skills audit <path> --level strict"
  }
}
```

Required behavior:

- Reuse existing `skills proof` where possible.
- Separate reachability from quality evidence.
- Do not claim outcome proof when only structural proof was run.

## `ask repo next`

Purpose: return one machine-readable next action for agents.

Inputs:

- `--json`;
- `--robot`;
- `--scope changed|repo|runtime`, optional; default `changed`.

Required data fields:

```json
{
  "repo_next": {
    "recommended_next_command": "./bin/ask repo closeout --changed --json --robot",
    "reason": "Changed files need focused validation and commit-readiness checks.",
    "blocking": false,
    "depends_on": []
  }
}
```

Required behavior:

- Emit one primary recommendation.
- Include `blocking: true` only when progress should stop until the command
  succeeds.
- Prefer smallest real validation over broad validation when the diff is
  narrow.

## `ask repo closeout`

Purpose: infer changed files, sync needs, validation, and commit-readiness.

Inputs:

- `--changed`;
- `--json`;
- `--robot`;
- `--strict`, optional.

Required data fields:

```json
{
  "repo_closeout": {
    "changed_files": [],
    "sync": {
      "needed": false,
      "commands": []
    },
    "runtime_budget": {
      "status": "pass",
      "advanced_visible_count": 162,
      "advisories": []
    },
    "surface_policy": {
      "status": "warning",
      "blocking_findings": 4003
    },
    "focused_validation": [],
    "commit_readiness": {
      "ready": true,
      "blockers": []
    },
    "next_command": "git commit"
  }
}
```

Required behavior:

- Include changed files, sync needs, focused validation, and commit-readiness.
- Keep runtime surface reporting visible.
- Treat known diagnostic repo-surface debt as warning unless the changed files
  make that debt worse.
- Never create a commit itself; report readiness and the exact suggested commit
  command class only.

## First Implementation Candidate

`ask repo doctor` should be implemented first because the baseline evidence
shows current health checks are fragmented across repo, runtime, and surface
commands.

Executable implementation is deferred until a focused slice can add:

- one route under the existing `repo` namespace;
- standard JSON envelope tests;
- a human summary output test;
- strict-mode behavior that separates diagnostic debt from true command failure;
- no top-level alias.

## Acceptance Mapping

| Plan AC | Covered By                                                      |
| ------- | --------------------------------------------------------------- |
| AC13    | `ask repo doctor` contract                                      |
| AC14    | `ask repo onboard` contract                                     |
| AC15    | `ask skills improve` contract                                   |
| AC16    | `ask skills explain` contract                                   |
| AC17    | `ask repo closeout --changed` contract                          |
| AC18    | `ask repo doctor` and `ask repo closeout` runtime budget fields |
| AC18a   | Baseline friction evidence and docs-only P4 implementation      |
