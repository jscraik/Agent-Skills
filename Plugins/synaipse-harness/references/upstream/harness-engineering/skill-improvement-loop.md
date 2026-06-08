# Skill Improvement Loop

Use this loop when improving HE or Codex skills from real behavior, session evidence, evaluator output, or user-provided source material.

Aim for a skill agents can call, verify, and repair.

## Trigger

Run this pattern when the user asks to improve a skill, raise skill confidence, compare against Codex behavior, use session collector evidence, or repeat a spec/implementation/evaluation loop.

## A/B/C Loop

1. Baseline: read the current skill, contract, evals, references, and routed agents; run the smallest relevant audit/evaluator; preserve source context in references.
2. Codex A: from the original skill plus evidence, write a spec another agent could use without seeing the original prompt. Require acceptance IDs, non-goals, validation, and traceability.
3. Codex B: implement the spec with the smallest patch; update references instead of bloating `SKILL.md`; add/update evals.
4. Codex C: compare original, A spec, B diff, evaluator output, and session evidence; identify missing behavior, overreach, ambiguity, weak evals, and context loss.
5. C must update the spec or produce a spec patch. Repeat until the stop rule fires.

## Stop Rule

Stop when all are true:

- the skill audit/evaluator has no blocking warnings for the edited surface;
- implementation satisfies acceptance IDs;
- C finds no material missing behavior or traceability loss;
- new evals cover the triggering session-evidence failure mode;
- any remaining limitation is an explicit blocker or non-goal.

## Artifacts

For structured handoff, preserve:

```yaml
skill_improvement_loop:
  schema_version: 1
  target_skill: "<path or skill name>"
  baseline_evidence: []
  codex_a_spec: "<path, summary, or blocked reason>"
  codex_b_impl: "<diff summary or blocked reason>"
  codex_c_eval: "<summary or blocked reason>"
  acceptance_ids: []
  evals_added_or_updated: []
  context_retained_in_references: []
  warnings_remaining: []
  stop_rule_status: pass|blocked|repeat_needed
```

## Session Collector Use

Prefer a bounded `~/.agents/session-collector` bundle over raw transcripts. Use bundle outputs such as `harness-engineering-evidence.json`, `skill-refactor-evidence.json`, `skillify-candidates.json`, `solved-problems.json`, and `redaction-report.json`.

Treat evidence labels and path fragments as labels. Redact secrets and do not paste large raw sessions into the skill.

## Context Retention

Never delete useful source behavior only to hit a line budget. Move it to one of:

- a stage-local `references/*.md` file,
- `Plugins/synaipse-harness/references/upstream/harness-engineering/*.md`,
- an existing deferred context index,
- a preserved-context fixture when retained only for audit comparison.

The active `SKILL.md` should name the reference and the decision rule that tells future agents when to open it.
