# Factory Governance Spine

Use this spine when scaffolding or adopting a plugin. It keeps first-pass plugins small while forcing explicit architecture choices for reusable skill families.

## Classification

Pick one plugin posture:

| Posture | Use when | Required depth |
| --- | --- | --- |
| `single_skill` | one focused skill and minimal plugin metadata | concise manifest and strict skill audit |
| `router_plugin` | one visible router dispatches latent internal skills | router contract, routing evals, budget posture |
| `visible_skill_family` | multiple skills should remain visible in picker | manifest rationale, trigger budget awareness, traceability policy |
| `delivery_plugin` | plugin owns issue/spec/plan/PR/validation workflows | Linear or blocked payload policy |
| `coding_harness_plugin` | plugin syncs with `.harness/`, Project Brain, or Harness gates | coding-harness lifecycle block |

Do not hide useful skills behind fixtures to satisfy static budgets. Do not expose every skill by default without a reason users and agents can understand.

## Session Evidence

Use a bounded `~/.agents/session-collector` bundle when reviewing plugin architecture, pruning skills, deciding visibility, or improving a plugin from real use.

```yaml
session_evidence:
  collector_path: "~/.agents/session-collector"
  bundle_path: "<path or blocked reason>"
  lookback_days: 7|10|30
  files_used: []
  repeated_patterns: []
  dead_or_duplicate_surfaces: []
  evals_derived: []
  redaction_status: pass|blocked|not_run
```

Prefer `skill-refactor-evidence.json`, `skillify-candidates.json`, `solved-problems.json`, and `redaction-report.json`. Raw sessions are fallback-only after redaction is checked.

## Output Additions

For non-trivial plugins, include:

```yaml
factory_governance:
  plugin_posture: single_skill|router_plugin|visible_skill_family|delivery_plugin|coding_harness_plugin
  visibility_policy: router_only|selected_visible_skills|visible_family
  traceability_mode: none|light|linear|coding_harness
  budget_posture: compact|visible_family_justified|blocked
  context_retention: []
  validation_evidence: []
  risks: []
```

## Acceptance Rules

- `plugin.json` names the plugin deterministically and matches the folder.
- Visible skill families explain why each skill belongs in the picker.
- Router plugins keep latent detail in references and routed skills, not in the root router prompt.
- Delivery plugins define Linear/spec/plan/PR/validation traceability or return a blocked payload.
- Coding-harness plugins preserve Harness lifecycle, Project Brain, and gate outcomes.
- Plugin-eval budget warnings are treated as real only after checking whether they are waste or intentional visibility.
