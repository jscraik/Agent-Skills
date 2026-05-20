# Factory Governance Spine

Use this spine when creating, refactoring, or hardening a skill. It keeps small skills light while giving durable workflows traceability, session evidence, and eval coverage from the start.

## Classification

Pick one posture before editing:

| Posture | Use when | Required depth |
| --- | --- | --- |
| `tiny_helper` | narrow local helper, private note, one-off utility | concise `SKILL.md`, light validation |
| `reusable_skill` | user-facing, repeated, risky, delegated, or cross-agent workflow | acceptance IDs, evals, validation, context routes |
| `delivery_workflow` | creates or changes product/project delivery artifacts | Linear traceability or explicit blocked payload |
| `coding_harness` | target repo has `.harness/`, `harness.contract.json`, Project Brain, or north-star gates | `coding_harness` lifecycle block |
| `skill_improvement` | improves/refactors an existing skill or removes warnings | A/B/C loop and session evidence when available |

Do not force Linear or Project Brain onto `tiny_helper`. Do not let `reusable_skill`, `delivery_workflow`, or `coding_harness` ship as an untraceable prompt.

## Evidence Intake

Prefer bounded session-collector bundles over raw transcripts when improving/refactoring skills or deriving a skill from repeated behavior.

```yaml
session_evidence:
  collector_path: "~/.agents/session-collector"
  bundle_path: "<path or blocked reason>"
  lookback_days: 7|10|30
  files_used: []
  repeated_patterns: []
  blockers_seen: []
  evals_derived: []
  context_to_preserve: []
  redaction_status: pass|blocked|not_run
```

Use bundle outputs such as `skill-refactor-evidence.json`, `skillify-candidates.json`, `solved-problems.json`, and `redaction-report.json`. Raw sessions are fallback-only after redaction is checked.

## Output Additions

For non-trivial skills, include these fields in the handoff:

```yaml
factory_governance:
  posture: tiny_helper|reusable_skill|delivery_workflow|coding_harness|skill_improvement
  traceability_mode: none|light|linear|coding_harness
  context_retention: []
  eval_coverage: happy_edge_negative_pressure|blocked|not_applicable
  agent_injection: none|reuse-existing|create-purpose-built|blocked
  validation_evidence: []
  risks: []
```

For `skill_improvement`, also preserve:

```yaml
skill_improvement_loop:
  baseline_evidence: []
  codex_a_spec: "<spec path, summary, or blocker>"
  codex_b_impl: "<diff summary or blocker>"
  codex_c_eval: "<eval summary or blocker>"
  evals_added_or_updated: []
  warnings_remaining: []
  stop_rule_status: pass|blocked|repeat_needed
```

## Acceptance Rules

- Keep active `SKILL.md` concise; move durable details to `references/` with `Read when` signposts.
- For delivery workflows, require Linear issue linkage or a ready-to-create blocked payload.
- For coding-harness repos, preserve Harness lifecycle state, Project Brain status, and gate outcomes as run or blocked.
- For skill improvements, use source behavior -> spec -> implementation -> evaluator revision -> validation.
- Add evals from real failure modes, not generic happy paths only.
