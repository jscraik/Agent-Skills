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

Admitted JSC-246 path: `repo doctor` -> `skills improve` -> `skills explain`
-> `skills doctor` -> `skills profiles` -> `skills prove` -> `repo closeout --changed`. `repo
onboard` and `repo next` are deferred candidates.

## Baseline Friction Evidence

Captured on 2026-05-01 against branch
`codex/he-code-review-openclaw-flow`.

Refreshed on 2026-05-13 against branch `codex/he-productization-pr`. The
contracts below remain product contracts, while several routes are now
implemented in the live `ask` surface.

| Command                                                                                                                    | Observed Output                                                                                                                  | Friction                                                                                                                                                     |
| -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `./bin/ask repo status --json --robot`                                                                                     | Reports `is_git` and `skills_synced` only.                                                                                       | It proves basic repo health but does not include runtime budget, handle health, surface policy status, blockers, or next command guidance.                   |
| `./bin/ask runtime budget --json --robot`                                                                                  | Reports `advanced_visible_count: 173`, advisory threshold `60`, `default_visible_count: 10`, and `budget_status: pass`.          | Runtime surface health is available, but agents must know to call it separately and then interpret large JSON.                                               |
| `./bin/ask repo surface --json --robot`                                                                                    | Reports tracked-surface classifications and diagnostic debt without deleting files.                                              | Surface ownership evidence exists, but it is low-level inventory output and must be summarized by doctor or closeout flows.                                  |
| `./bin/ask repo --help`                                                                                                    | Exposes `status`, `validate`, `check-stability`, `doctor`, `closeout`, `doctor-catalog`, `provider-audit`, and `surface`.        | Repo health and closeout now have namespace-first routes; deeper surface policy still needs detailed follow-up output.                                       |
| `./bin/ask skills --help`                                                                                                  | Exposes `goal`, `route`, `improve`, `explain`, `doctor`, `profiles`, `memory`, `prove`, `handles`, and related primitives.        | The product path is now executable, but outcome proof still requires real workout/eval/transcript evidence.                                                  |
| `./bin/ask skills package <handle-or-path> --json --robot`                                                               | Reports version, role compatibility, runtime needs, maturity, provenance, and share/install readiness for one capability.         | The command is read-only; it does not publish, install, or mutate marketplace metadata.                                                                        |
| `./bin/ask skills profiles --json --robot`                                                                                | Reports authoring, package-review, plugin-share, eval, and live-mutation profiles with roots, evidence, and stop conditions.     | Operation modes are now inspectable, but profile-specific enforcement remains a follow-up contract for validators and eval runners.                           |
| `./bin/ask skills memory search "projection" --json --robot`                                                             | Searches durable skill memory surfaces with provenance and freshness metadata.                                                   | The provider is read-only and does not replace Project Brain indexing or wiki mutation commands.                                                              |
| `./bin/ask repo doctor-catalog --json --robot`                                                                             | Returns `decision_status: resolved` after README, `SKILL.md`, `ask skills list`, and route metadata expose canonical count `32`. | Catalog parity is separately diagnosable, and doctor/closeout should continue surfacing this blocker when routing or delivery depends on it.                 |
| `./bin/ask skills goal "continue implementing the Agent Skills Kit repo surface control-plane plan" --json --robot`        | Returns `intent_unresolved` with `route_decision_status: unresolved_ambiguity`.                                                  | Broad goals can remain too ambiguous even after catalog parity is healthy; product flows need sharper repair prompts and next-command guidance.              |
| `./bin/ask skills goal "use he-work to implement P4 namespace-first product command contracts for JSC-246" --json --robot` | Resolves `he-work` with confidence `0.938`.                                                                                      | Goal routing works when the user names the workflow and phase, which supports a future `skills improve` contract that asks for narrower context when needed. |

P4 therefore started as contracts only. The first admitted executable route is
`ask repo doctor`, followed by the capability and closeout commands above.

## Shared Envelope

All commands in this document must use the standard `ask` JSON envelope:

```json
{
  "status": "success",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "version": "1.0.0",
    "command": "ask repo doctor --json --robot",
    "next_steps": [
      "Review runtime budget advisories",
      "Run ask repo surface --json for detailed findings"
    ],
    "correction_note": null
  },
  "data": {
    "repo_doctor": {
      "repo": {
        "is_git": true,
        "branch": "main",
        "dirty": false,
        "skills_synced": true
      },
      "runtime_budget": {
        "state": "pass",
        "severity": "info",
        "details": {
          "status": "pass",
          "advanced_visible_count": 173,
          "advisories": []
        }
      },
      "blockers": [],
      "next_command": "./bin/ask repo surface --json"
    }
  },
  "telemetry": {
    "latency_ms": 245
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
      "state": "pass",
      "severity": "info",
      "details": {
        "status": "pass",
        "default_visible_count": 10,
        "estimated_description_tokens": 3234,
        "violation_count": 0
      }
    },
    "handles": {
      "status": "pass",
      "collisions": [],
      "unresolved": []
    },
    "surface_policy": {
      "status": "warning",
      "blocking_findings": 16750,
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

## Deferred Candidate: `ask repo onboard`

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
      "./bin/ask skills prove gh-address-comments --json --robot"
    ],
    "sync_actions": [],
    "next_command": "./bin/ask skills explain gh-address-comments --json --robot"
  }
}
```

Required behavior:

- Reuse existing `skills goal`, `skills route`, `skills prove`, and graph
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

## `ask skills doctor`

Purpose: diagnose whether one capability is ready to use right now without
claiming full outcome proof.

Inputs:

- skill handle or repo-relative skill source path;
- `--json`;
- `--robot`;
- `--strict`, optional; run strict audit instead of the default compat audit.

Required data fields:

```json
{
  "skill_doctor": {
    "schema_version": "skill-doctor.v1",
    "query": "he-code-review",
    "target_kind": "command_handle",
    "handle": "he-code-review",
    "canonical_source_path": "Plugins/harness-engineering/skills/code_quality_review/he-code-review/SKILL.md",
    "audit_target": "Plugins/harness-engineering/skills/code_quality_review/he-code-review",
    "target_summary": {
      "query": "he-code-review",
      "target_kind": "command_handle",
      "handle": "he-code-review",
      "canonical_source_path": "Plugins/harness-engineering/skills/code_quality_review/he-code-review/SKILL.md"
    },
    "contract_schemas": {
      "doctor": {"version": "skill-doctor.v1", "owner": "Agent Skills Kit"},
      "events": {"version": "skill-events.v1", "owner": "Agent Skills Kit"},
      "profiles": "skill-operation-profiles.v1",
      "package": "skill-package-readiness.v1"
    },
    "operation_context": {
      "primary_profile": "authoring",
      "next_profiles": ["package-review", "proof"],
      "validation_commands": [
        "./bin/ask skills doctor he-code-review --json --robot",
        "./bin/ask skills audit Plugins/harness-engineering/skills/code_quality_review/he-code-review --json --robot"
      ]
    },
    "status": "pass",
    "blockers": [],
    "warnings": [],
    "readiness_taxonomy": {"blockers": {}, "warnings": {}},
    "lifecycle_event": {
      "schema_version": "capability-lifecycle-event.v1",
      "event_type": "skill_doctor_completed",
      "outcome": {"status": "pass", "blocker_classes": [], "warning_classes": []}
    },
    "checks": {
      "resolver": {"status": "pass"},
      "runtime_reachability": {"status": "pass"},
      "canonical_source": {"status": "pass"},
      "structural_audit": {"status": "pass", "level": "compat"},
      "capability_metadata": {
        "status": "pass",
        "readiness_level": "capability_declared",
        "required_fields": {"present": ["description", "name"], "missing": []},
        "capability_contract": {"present": [], "missing": []},
        "package_contract": {
          "present": ["maturity", "version"],
          "missing": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
          "values": {
            "version": "1.0.0",
            "compatible_roles": [],
            "runtime_needs": [],
            "maturity": "canonical",
            "provenance": null,
            "share_readiness": null
          },
          "role_compatibility": {"declared": false, "roles": []},
          "runtime_contract": {"declared": false, "needs": []},
          "install_gate": {
            "install_ready": false,
            "required_checks": ["version", "compatible_roles", "runtime_needs", "maturity", "provenance", "share_readiness"],
            "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
            "checkout_test": {"required": true, "status": "not_run", "evidence": []}
          },
          "promotion_gate": {
            "status": "blocked_validation",
            "promotion_ready": false,
            "share_ready": false,
            "share_readiness": null,
            "checkout_test_status": "not_run",
            "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
            "recommended_next_fields": ["compatible_roles", "runtime_needs", "provenance", "share_readiness"]
          }
        },
        "package_readiness": {
          "readiness_level": "versioned_capability",
          "required_fields": {
            "present": ["maturity", "version"],
            "missing": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"]
          },
          "values": {
            "version": "1.0.0",
            "compatible_roles": [],
            "runtime_needs": [],
            "maturity": "canonical",
            "provenance": null,
            "share_readiness": null
          },
          "role_compatibility": {"declared": false, "roles": []},
          "runtime_contract": {"declared": false, "needs": []},
          "install_gate": {
            "install_ready": false,
            "required_checks": ["version", "compatible_roles", "runtime_needs", "maturity", "provenance", "share_readiness"],
            "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
            "checkout_test": {"required": true, "status": "not_run", "evidence": []}
          },
          "promotion_gate": {
            "status": "blocked_validation",
            "promotion_ready": false,
            "share_ready": false,
            "share_readiness": null,
            "checkout_test_status": "not_run",
            "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
            "recommended_next_fields": ["compatible_roles", "runtime_needs", "provenance", "share_readiness"]
          }
        }
      },
      "outcome_proof": {"status": "available_not_run"}
    },
    "agent_summary": "$he-code-review passed capability doctor checks.",
    "next_command": "./bin/ask skills prove he-code-review --json --robot"
  }
}
```

Required behavior:

- Compose resolver, command-handle proof, canonical-source, audit, metadata,
  and outcome-proof availability signals for one capability.
- Emit `target_summary` with the resolved query, target kind, handle, and
  canonical source path so callers can assert which capability was inspected.
- Emit `contract_schemas` with the doctor, lifecycle events, operation profiles,
  and package-readiness schema references used by the response.
- Emit `operation_context` with deterministic profile and validation-command
  evidence for the invocation environment.
- Return `blocked` with machine-readable blocker classes when the capability
  cannot be used safely.
- Treat missing outcome proof as a warning, not as a structural failure.
- Emit stable readiness taxonomy classes for runtime, auth, user-input,
  timeout, artifact, source, and validation blockers.
- Emit a `capability-lifecycle-event.v1` object so automation can consume
  doctor outcomes without scraping prose.
- Leave `ask skills prove` responsible for the outcome-proof scorecard.

## `ask skills package`

Purpose: report whether one skill package has version and role-aware metadata
needed for promotion, sharing, install checks, or role compatibility claims.

Inputs:

- skill handle or repo-relative skill source path;
- `--json`;
- `--robot`; and
- `--strict`, optional; fail when package readiness metadata is incomplete;
- `--checkout-test`, optional; add read-only local checkout evidence to the
  install gate without cloning, installing, publishing, or mutating runtime
  projections.

Required data fields:

```json
{
  "skill_package": {
    "schema_version": "skill-package-readiness.v1",
    "query": "skill-builder",
    "target_kind": "command_handle",
    "handle": "skill-builder",
    "canonical_source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
    "audit_target": "Plugins/skill-factory/skills/code_quality_review/skill-builder",
    "status": "warning",
    "strict": false,
    "package_contract": {
      "readiness_level": "versioned_capability",
      "required_fields": {
        "present": ["maturity", "version"],
        "missing": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"]
      },
      "values": {
        "version": "1.0.0",
        "compatible_roles": [],
        "runtime_needs": [],
        "maturity": "canonical",
        "provenance": null,
        "share_readiness": null
      },
      "role_compatibility": {"declared": false, "roles": []},
      "runtime_contract": {"declared": false, "needs": []},
      "install_gate": {
        "install_ready": false,
        "required_checks": ["version", "compatible_roles", "runtime_needs", "maturity", "provenance", "share_readiness"],
        "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
        "checkout_test": {
          "required": true,
          "status": "not_run",
          "evidence": []
        }
      },
      "promotion_gate": {
        "status": "blocked_validation",
        "promotion_ready": false,
        "share_ready": false,
        "share_readiness": null,
        "checkout_test_status": "not_run",
        "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"],
        "recommended_next_fields": ["compatible_roles", "runtime_needs", "provenance", "share_readiness"]
      }
    },
    "gate_summary": {
      "install_ready": false,
      "checkout_test_status": "not_run",
      "promotion_status": "blocked_validation",
      "promotion_ready": false,
      "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"]
    },
    "blockers": [],
    "warnings": [
      {
        "class": "capability_contract_incomplete",
        "message": "Package readiness metadata is incomplete."
      }
    ],
    "lifecycle_event": {"schema_version": "capability-lifecycle-event.v1", "event_type": "skill_loaded"},
    "lifecycle_events": [
      {"schema_version": "capability-lifecycle-event.v1", "event_type": "skill_loaded"},
      {
        "schema_version": "capability-lifecycle-event.v1",
        "event_type": "package_readiness_checked",
        "details": {
          "gate_summary": {
            "install_ready": false,
            "checkout_test_status": "not_run",
            "promotion_status": "blocked_validation",
            "promotion_ready": false,
            "blocked_reasons": ["compatible_roles", "provenance", "runtime_needs", "share_readiness"]
          }
        }
      }
    ],
    "lifecycle_event_types": ["skill_loaded", "package_readiness_checked"],
    "agent_summary": "skill-builder has package gate blockers: compatible_roles, provenance, runtime_needs, share_readiness.",
    "next_command": "./bin/ask skills doctor skill-builder --strict --json --robot"
  }
}
```

Required behavior:

- Resolve either a command handle or canonical source path without writing files.
- Read package metadata from top-level frontmatter and nested `metadata`.
- Treat missing canonical source as blocked.
- Treat incomplete package metadata as warning by default; with `--strict`,
  return non-zero and set payload status `blocked` with a `blocked_validation`
  blocker.
- Include a read-only `install_gate` that reports whether package metadata is
  install-ready and whether follow-up checkout evidence still needs to run.
- Include a read-only `promotion_gate` with a machine-readable `status`,
  `promotion_ready`, `checkout_test_status`, and `blocked_reasons` so
  share/promotion checks do not require prose scraping.
- Include `gate_summary` as the automation-facing view of install, checkout,
  promotion, and blocker state.
- With `--checkout-test`, replace `checkout_test.status: "not_run"` with
  `pass`, `blocked_missing_source`, or `blocked_validation`, plus evidence such
  as source path, source readability, audit target, and missing metadata fields.
- Emit both `skill_loaded` and `package_readiness_checked` lifecycle events so
  automation can distinguish source resolution from package gate evaluation.
  The `package_readiness_checked` event must include `details.gate_summary`.
- Keep promotion, install, share, and marketplace mutation out of this command.

## `ask skills profiles`

Purpose: expose profile-v2-style operation modes for skill lifecycle work.

Inputs:

- optional profile name: `authoring`, `package-review`, `plugin-share`,
  `eval`, or `live-mutation`;
- `--json`;
- `--robot`.

Required data fields:

```json
{
  "skill_profiles": {
    "schema_version": "skill-operation-profiles.v1",
    "status": "pass",
    "workspace_roots": {
      "repo_root": ".",
      "canonical_skill_roots": ["Skills", "Plugins"],
      "runtime_projection_roots": [".agents/skills", ".skillsets"],
      "artifact_roots": ["Infrastructure/artifacts", "Infrastructure/workouts"],
      "memory_roots": [".harness/memory", "Wiki/wiki/learnings", "Docs/solutions"]
    },
    "profile_model": "profile-v2-inspired",
    "profiles": {
      "eval": {
        "intent": "Run smoke, workout, or release evidence for one capability.",
        "allowed_roots": ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        "effective_roots": ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        "write_policy": "artifact_write_only",
        "permissions": ["repo_read", "local_validation", "artifact_write"],
        "required_evidence": ["eval_started event", "eval_completed or eval_blocked event", "timeout classification"],
        "stop_conditions": ["blocked_user_input", "blocked_auth", "timeout_no_output", "timeout_partial_output"]
      }
    }
  }
}
```

Required behavior:

- Return all profiles when no profile name is provided.
- Return one profile when a valid profile name is provided.
- Return `blocked` with available profile names for unknown profiles.
- Include workspace-root groups and per-profile effective roots so automation can
  show the repo, runtime projection, artifact, and memory boundaries without
  parsing profile prose.
- Keep profile output read-only; profiles describe constraints and do not
  perform sync, install, eval, or mutation work.

## `ask skills memory`

Purpose: expose durable skill learnings as an extension-like read-only provider
instead of relying on agents to remember which markdown tree to search.

Inputs:

- mode: `list`, `read`, or `search`;
- optional query: entry id/path for `read`, keyword text for `search`;
- `--limit`, optional; cap returned entries;
- `--json`; and
- `--robot`.

Required data fields:

- `schema_version`: `skill-memory-provider.v1`.
- `provider_model`: `extension-like-read-only`.
- `roots`: provider root declarations with existence checks.
- `entries`: memory entries for `list` and `search`.
- `entry`: selected entry with full content for `read`.
- `provenance`: source provider and repo-relative path for each entry.
- `freshness`: modified timestamp and age in days for each entry.
- `agent_summary`: concise machine-friendly outcome.

Required behavior:

- Search `.harness/memory`, `Wiki/wiki/learnings`, and `Docs/solutions`.
- Return provenance and freshness for every listed or searched entry.
- Return full content only for `read`; `list` and `search` stay summary-first.
- Remain read-only. Mutations stay with `ask wiki add`, `ask wiki ingest`, or
  the approved memory/decision workflow.

## `ask evals run`

Purpose: run smoke or release evidence while classifying runner blockers
separately from skill behavior failures.

Required data fields for JSON output:

- `eval_status`: one of `pass`, `fail`, `blocked_user_input`, `blocked_auth`,
  `blocked_runtime`, `timeout_no_output`, or `timeout_partial_output`.
- `blocker_class`: `null` for pass/fail, otherwise the matching blocked or
  timeout class.
- `blocker_taxonomy`: stable class definitions for automation and dashboards.
- `lifecycle_events`: ordered `capability-lifecycle-event.v1` records starting
  with `eval_started` and ending with `eval_completed` or `eval_blocked`.
- `lifecycle_event`: the latest lifecycle event for consumers that only need
  the final eval outcome.
- `raw_output` and `raw_error`: captured runner output for exact evidence.

Required behavior:

- Emit `eval_started` before invoking the runner, then emit `eval_completed`
  for pass/fail outcomes or `eval_blocked` for classified blocker outcomes.
- A timeout with no captured output is `timeout_no_output`.
- A timeout after partial captured output is `timeout_partial_output`.
- Authentication or login failures are `blocked_auth`.
- User-input requests are `blocked_user_input`, not hangs.
- Local sandbox, context-window, or model-capacity failures are
  `blocked_runtime`.
- Scorecards produced by `run_skill_evals.py` should carry the same blocker
  class on runner and case records.

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

- Reuse existing `skills prove` where possible.
- Separate reachability from quality evidence.
- Do not claim outcome proof when only structural proof was run.

## Deferred Candidate: `ask repo next`

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
      "state": "pass",
      "severity": "info",
      "details": {
        "status": "pass",
        "default_visible_count": 10,
        "estimated_description_tokens": 3234,
        "violation_count": 0
      }
    },
    "surface_policy": {
      "status": "warning",
      "blocking_findings": 16750
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

## Current Implementation Path

The admitted first-contact route starts with `ask repo doctor` because the
baseline evidence showed health checks fragmented across repo, runtime, and
surface commands.

Executable expansion should remain bounded to:

- one route under the existing `repo` namespace;
- standard JSON envelope tests;
- a human summary output test;
- strict-mode behavior that separates diagnostic debt from true command failure;
- no top-level alias.

## Acceptance Mapping

| Plan AC | Covered By                                                      |
| ------- | --------------------------------------------------------------- |
| AC13    | `ask repo doctor` contract                                      |
| AC14    | `ask repo onboard` deferred candidate contract                  |
| AC15    | `ask skills improve` contract                                   |
| AC16    | `ask skills explain` contract                                   |
| AC17    | `ask repo closeout --changed` contract                          |
| AC18    | `ask repo doctor` and `ask repo closeout` runtime budget fields |
| AC18a   | Baseline friction evidence and docs-only P4 implementation      |
