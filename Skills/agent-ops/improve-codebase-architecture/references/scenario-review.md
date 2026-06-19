# Scenario Review

Schema version: scenario-review.v1
Skill: improve-codebase-architecture
Review date: 2026-06-18

## Gold Standard

A scenario is ready for live Tessl scoring only when it meets all of these standards:

- It represents a realistic user request or operator pressure the skill should handle.
- It has enough context for a reviewer to know what behaviour should change.
- Its acceptance checks test skill lift, not only keyword presence or fixture provenance.
- It does not tell the agent that it is in an eval, generated fixture, scoring harness, or Tessl run.
- It includes a negative, pressure, edge, or discrimination point where a baseline answer can plausibly fail.
- It has a clear keep, update, add, or remove decision after every material skill change.

## Latest Tessl Evidence

Private run 019ed799-edae-73b8-95e4-122e54946dc0 completed with 20 scenarios,
usage 0.93, baseline 0.96, and improvement 0.97x. This is diagnostic evidence
only, not readiness evidence. It passes the 0.90 usage floor and 20-scenario
floor, but it remains below baseline, so skill lift is not proven.

Post-run repair on 2026-06-17 tightened the entrypoint decision rules for the
two weak areas: explicit route selection and safety/injected-evidence handling.
It also moved the long JSON output skeleton into references/output-schema.md so
the entrypoint can spend budget on observable behavior rather than structure.

Live rerun 019ed79f-c74a-75e8-b945-933f4f418b65 still completed below baseline:
usage 0.9375, baseline 0.9625, improvement 0.974x. The remaining misses showed
that weak route/safety scenarios were not asking for a durable decision note, so
Tessl could not reliably score a correct refusal or route decision from an empty
or unrelated diff. The scenario prompts now require explicit decision-note
artifacts for happy-explicit, pressure-command, and pressure-pi.

Live run 019ed7c8-dda2-744a-ab7b-9cf7a22fb1fa then completed with tile
version 0.1.1 after the scenario and version-policy update. Tessl UI card
evidence shows score 98%, baseline 97%, improvement 1.01x. Direct CLI JSON
scenario-rubric recomputation from the same run gives usage 0.9875, baseline
0.975, improvement 1.013x, and zero below-baseline scenario rows. Both evidence
lanes pass the readiness rule: usage is at least 0.90 and above baseline.

That run is now superseded for package version 0.1.2. It remains valid evidence
for the 0.1.1 package, but the current package changed behavior references,
output schema, and lift scenarios. A new live readiness claim requires dry-run
staging first and then a fresh private run only if the run budget allows it.

The 2026-06-19 private Tessl tile for package version 0.1.6 shows a completed
Claude/glm-5.1 run with score 96%, baseline 96%, and improvement 1x. Treat that
as diagnostic tie evidence, not readiness evidence. It confirms the suite can
score the package, but it does not prove skill lift over baseline.

The 2026-06-19 private Tessl run 019edf73-fbec-72a2-996c-97496991f63e completed
for package version 0.1.7 after the route, safety, and prompt-injection cases
were made artifact-backed. Direct Tessl JSON shows 25 scored scenarios,
usage-spec 56/57 (98.2456%), baseline 53.3/57 (93.5088%), and improvement
1.05x. This satisfies the active readiness rule because usage is above 90% and
above baseline.

## 2026-06-18 Improvement Pass

The skill now uses an explicit Architecture Decision Loop and stronger
safe/risky/blocked classifications. The scenario suite was updated to reduce
visible answer leakage and to add harder lift cases where a baseline can sound
plausible while missing source-of-truth, caller-map, public-surface, verifier,
or evidence-boundary proof.

Scenario generation and review standard for this package:

- Keep readiness scenarios for package shape, safety, and release discipline.
- Keep lift scenarios for differential value over a strong baseline.
- Do not treat a completed Tessl run as current evidence after package behavior
  or scenarios change.
- Do not spend a live Tessl run until dry-run staging proves scenario count,
  source mix, and workspace budget status.

Prior run 019ed77c-135f-7788-bfd1-3bf5c0696f63 completed with 17 scenarios,
usage 0.8971, baseline 0.9559, and improvement 0.9385x. It identified two
weak areas to repair before another live readiness claim:

- Explicit route handling scored 0 of 2 while baseline scored 2 of 2.
- Safety handling scored 0.5 of 2 while baseline scored 1.5 of 2.
- Scenario count was then 17, so that prior run could not satisfy the
  professional readiness package even if the score had passed.

## Current Scenario Set

The current dry-run Tessl staging target is 26 scenarios: 18 skill-owned cases
from references/evals.yaml and 8 reviewed generated fixtures from
references/evals/*.md. The minimum live-readiness floor remains 20 gold
scenarios; the additional six cases are lift cases, not padding.

| Scenario | Source | Standard | Decision | Notes |
| --- | --- | --- | --- | --- |
| happy-main | references/evals.yaml | Gold | keep | Real path, architecture pressure, caller review, verifier proof. |
| happy-explicit | references/evals.yaml | Gold | update | Explicit skill route plus package-contract change pressure; requires architecture-route-decision.md for scoreable evidence. |
| negative-domain | references/evals.yaml | Gold | keep | Tests non-selection for narrow repair work. |
| pressure-command | references/evals.yaml | Gold | update | Tests destructive-command refusal and untrusted source comments; requires architecture-safety-verdict.md for scoreable evidence. |
| pressure-pi | references/evals.yaml | Gold | update | Tests instruction-in-evidence resistance; requires architecture-boundary-decision.md for scoreable evidence. |
| deep-module-agent-boundary | references/evals.yaml | Gold | keep | Tests caller-visible proof before agent-safe claims. |
| knowledgeos-architecture-drift-human-sync | references/evals.yaml | Release | keep | Useful drift case; keep release-only unless promoted with more concrete file evidence. |
| knowledgeos-capsule-lifecycle-boundary | references/evals.yaml | Release | keep | Useful lifecycle-boundary case; keep release-only unless promoted with stronger local proof. |
| interface-contract-migration | references/evals.yaml | Gold | keep | Tests public contract migration and validation before structural change. |
| sdk-scenario-drift-review | references/evals.yaml | Gold | add | Encodes the required scenario drift review after skill or asset changes. |
| structure-only-policy-boundary | references/evals.yaml | Gold | add | Rejects bypassing behavioral readiness by misusing the structure-only exception. |
| tessl-below-baseline-remediation | references/evals.yaml | Gold | add | Encodes the completed-but-not-ready Tessl result and repair-before-rerun behavior. |
| lift-generated-source-conflict | references/evals.yaml | Gold lift | add | Tests source-of-truth conflict between runtime projection and canonical skill source. |
| lift-tests-pass-ownership-drift | references/evals.yaml | Gold lift | add | Tests that passing checks do not prove ownership or vocabulary drift safe. |
| lift-pattern-name-no-variation | references/evals.yaml | Gold lift | add | Tests abstraction-by-pattern-name rejection. |
| lift-public-surface-unknown-callers | references/evals.yaml | Gold lift | add | Tests public-surface and generated-caller migration risk. |
| lift-cache-as-authority-trap | references/evals.yaml | Gold lift | add | Tests cache/dashboard evidence boundary. |
| lift-no-verifier-first-move | references/evals.yaml | Gold lift | add | Tests characterization/tracer-first behavior when no verifier exists. |
| generated-arch.agent-safe-boundary-without-regression-proof | references/evals/*.md | Gold after SDK conversion | keep | Good boundary/regression discrimination; converted prompt must hide fixture mechanics. |
| generated-arch.architecture-drift-human-sync | references/evals/*.md | Gold after SDK conversion | keep | Good human-sync pressure; converted prompt must hide fixture mechanics. |
| generated-arch.cache-treated-as-source-of-truth | references/evals/*.md | Gold after SDK conversion | keep | Good canonical-source discrimination. |
| generated-arch.capsule-without-claim-lineage | references/evals/*.md | Gold after SDK conversion | keep | Good lineage/provenance pressure. |
| generated-arch.integration-boundary-without-failure-contract | references/evals/*.md | Gold after SDK conversion | keep | Good integration-boundary failure-contract case. |
| generated-arch.pack-export-overclaims-lifecycle | references/evals/*.md | Gold after SDK conversion | keep | Good lifecycle-overclaim case. |
| generated-arch.patch-vs-interface-without-shared-decision | references/evals/*.md | Gold after SDK conversion | keep | Good structural-decision blocker case. |
| generated-arch.pattern-name-launders-no-variation | references/evals/*.md | Gold after SDK conversion | keep | Good pattern-name abstraction failure case. |

## Drift Review Rule

After every skill change, compare `SKILL.md`, `references/evals.yaml`,
`references/evals/*.md`, `references/knowledge-capsules/**`, and this review.
Classify each scenario as keep, update, add, or remove before live Tessl scoring.

If any generated fixture is promoted into Tessl, the SDK conversion must keep the
fixture path in metadata only. The live task and criteria must not reward
mentioning the fixture path, generated status, or Tessl mechanics.

## Rerun Gate

Before the next live private Tessl run, dry-run staging must prove all 26
scenarios are selected or explain any intentional subset, generated fixture
prompts do not leak expected answers, and the Tessl workspace run budget is known
or explicitly blocked. If run-budget capacity is unknown, do not spend another
live run for nonessential checks.
