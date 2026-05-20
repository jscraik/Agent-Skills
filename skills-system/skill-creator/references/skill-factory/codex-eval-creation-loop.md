# Codex Eval Creation Loop

Read when: creating or materially improving a Codex skill and deciding how to
prove the skill works beyond a manual vibe check.

This pattern adapts the useful ideas observed in Anthropic's public
`claude-plugins-official/plugins/skill-creator/skills/skill-creator` package at
commit `b5a156b6ecd2f69c418184b7c093930ddabaf9c0`. This file is the durable
local extraction, so future agents do not need to keep or consult a copy of the
Claude package to understand the borrowed patterns.

Do not import external local paths, browser viewers, account assumptions,
agent names, scripts, schemas, or publishing flows. Keep canonical source,
evals, and evidence in this repo's formats.

## Extracted Patterns To Keep

- Draft realistic prompts early, before the skill is polished.
- Run the skill against a meaningful comparator: no skill for a new capability,
  the old skill for an improvement, or the closest local owner for overlap.
- Capture behavior evidence, not just final prose: commands, artifacts, errors,
  timing, token use, and whether the agent followed the skill.
- Grade with evidence. Each expectation should say what passed or failed and
  cite the output, run trace, file, or command evidence.
- Analyze the evals themselves. A passing assertion that only checks a filename,
  trigger word, or shallow phrase is weak evidence.
- Let repeated run behavior shape the skill. If every run recreates the same
  helper or reference lookup, add a bundled script, asset, or reference.
- Iterate from the combination of deterministic results, qualitative review,
  user feedback, and cost signals.

## External Details Not Kept

- Claude-specific subagent names, prompts, package paths, and viewer scripts.
- Browser-review UI requirements. In this repo, use artifacts, dashboards, or
  human review only when they are already part of the local eval lane.
- External schema field names that conflict with Agent Skills Kit
  `references/evals.yaml`, strict audit, or reporting contracts.
- Any publish, registry, upload, or marketplace step.
- Assumptions that the baseline runner is Claude. Codex evals must compare
  Codex behavior through repo-owned commands and recorded evidence.

## Codex-Local Workflow

1. Define success before editing:
   - expected user outcome
   - process expectations such as skill trigger, safe commands, and artifacts
   - style or domain criteria that need reviewer judgment
   - efficiency signals such as command count, time, or token budget

2. Add or update `references/evals.yaml`:
   - include happy, edge, negative, and pressure cases when applicable
   - mark realistic prompts with `realistic: true` and `why_realistic`
   - set `should_trigger` and `prepend_skill` deliberately
   - add deterministic checks for commands, forbidden commands, artifacts, and
     schema/output fields
   - add acceptance checks that prove the real outcome, not just a phrase

3. Run a focused comparison when the skill's value is uncertain:
   - new skill: compare with no-skill or plain-Codex behavior
   - improved skill: compare against the pre-change version or a saved snapshot
   - overlapping external pattern: compare against the closest local owner before
     creating another canonical skill

4. Grade and critique:
   - pass only with concrete evidence from output files, run traces, or command
     output
   - record `pass`, `fail`, or `blocked`; do not use vague readiness language
   - flag weak evals that would pass a bad output, cannot be verified, or miss
     the main outcome
   - note repeated helper creation, unnecessary commands, high token use, and
     brittle recovery loops as skill-improvement signals

5. Improve the skill:
   - keep `SKILL.md` concise and move deep policy or examples to `references/`
   - add scripts only when repeated deterministic work justifies them
   - explain the reason behind instructions instead of adding brittle command
     overfitting
   - rerun the focused failed eval before broader gates

6. Report readiness with the repo lane names:
   - strict audit: `./bin/ask skills audit <path> --level strict --json --robot`
   - local evals: `./bin/ask evals run <path> --mode smoke|release --json --robot`
   - Second-Review Lane: `./bin/ask skills external-review <path> --json --robot`
   - Snyk: include only for manifest-backed release candidates with
     `--include-snyk`

## Comparator Choice

Use the smallest comparator that answers the question:

| Situation | Comparator |
| --- | --- |
| New capability | no-skill baseline |
| Existing skill improvement | pre-change snapshot or previous iteration |
| External skill intake | closest local owner skill |
| Trigger tuning | prompts with and without explicit `$skill` invocation |
| Security or dependency change | release eval plus Snyk when manifest-backed |

Do not turn every small helper into a benchmark project. Tiny private helpers
can use one or two focused prompts plus strict audit. Reusable, risky, or
externally visible skills need release-mode evidence.

## Readiness Output

Close out with a short evidence block:

```yaml
skill_eval_loop:
  comparator: no_skill|previous_skill|closest_local_owner|not_applicable
  eval_cases_added_or_updated: []
  deterministic_checks: []
  qualitative_checks: []
  weak_eval_findings: []
  efficiency_signals: []
  validation_evidence:
    - command: "<exact command>"
      result: pass|fail|blocked
      reason: "<blocker or short outcome>"
  readiness_decision: ready|not_ready|blocked
```

`readiness_decision: ready` is allowed only when the claimed lane gates have
actually run or are explicitly not applicable.
