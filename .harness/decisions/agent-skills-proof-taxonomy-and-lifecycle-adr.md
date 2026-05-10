# ADR: Proof Taxonomy And Skill Lifecycle States

## Status

Accepted for `JSC-287` as a decision-only slice.

## Context

Agent Skills Kit already distinguishes canonical skill sources, runtime
projections, generated command handles, visible runtime surface, advanced repo
discovery, strict skill audit, and policy identity in `UBIQUITOUS_LANGUAGE.md`.
Those terms explain where a skill lives and whether agents can reach it.

They do not yet define what kind of proof exists for a skill. That gap matters
because reachability, structural validity, quality evidence, and outcome
evidence are not interchangeable. A generated command handle can prove a skill
is invokable without proving the workflow produces useful results. A strict
audit can prove structural readiness without proving real task success.

This ADR defines proof vocabulary for future enforcement work without changing
selection policy, command behavior, runtime visibility, or promotion gates.

## Decision

Use four proof levels:

| Level | Meaning | Sufficient evidence | Explicit non-proof |
| --- | --- | --- | --- |
| `reachability` | The skill can be resolved and invoked through the expected repo/runtime path. | `./bin/ask skills resolve <handle> --json`, command-handle metadata, or runtime projection evidence. | Does not prove the skill is structurally complete or useful. |
| `structural` | The skill package satisfies repository structure, metadata, routing, and security/audit requirements. | Strict skill audit, schema checks, package validation, command-handle validation, path ownership checks. | Structural audit is not outcome proof. |
| `quality` | The skill has credible task design, examples, tests/evals, and review evidence for expected usage. | Targeted evals, benchmark cases, review artifacts, focused tests, documented limitations. | Quality evidence is not proof of repeated successful production outcomes. |
| `outcome` | The skill has produced useful, validated results in real or representative execution. | Completed task evidence, eval-backed closure artifacts, user-accepted outputs, reproducible before/after evidence. | A successful invocation alone is not outcome proof. |

Use eight lifecycle states:

| State | Meaning | Minimum proof expectation |
| --- | --- | --- |
| `experimental` | The skill is exploratory or unstable and should not be treated as reliable. | None, or partial design evidence only. |
| `latent` | The skill exists but is intentionally not part of the default visible runtime surface. | Source exists; may have reachability only through advanced discovery or owner routing. |
| `structurally-valid` | The skill passes structural checks for its package shape and metadata. | `structural`. |
| `reachable` | The skill resolves through the intended runtime or command-handle path. | `reachability`. |
| `outcome-proven` | The skill has validated task success evidence for its intended job. | `outcome`. |
| `trusted` | The skill is reliable enough for repeated agent use in its stated scope. | `structural`, `quality`, and `outcome`; limitations are documented. |
| `default-visible` | The skill is allowed onto the bounded visible runtime surface. | `trusted` plus explicit runtime-budget and policy approval. |
| `deprecated` | The skill should no longer be selected except for migration or historical compatibility. | Deprecation rationale and replacement or removal path. |

## Operating Rules

- Do not call a skill `trusted` from structural evidence alone.
- Do not promote a skill to `default-visible` merely because it exists, resolves,
  or is strategically important.
- Keep `reachability` useful and separate from `structural`, `quality`, and
  `outcome`.
- Treat missing outcome evidence as an honest state, not a failure by itself.
- Preserve the current `Visible Runtime Surface` budget discipline.
- Keep generated command handles as pointers to canonical skill sources, not as
  proof of workflow quality.

## Enforcement Scope

Out of scope for this slice:

- selection policy changes;
- command behavior changes;
- default-visible promotion gates;
- proof command output schema changes;
- migration of existing skill metadata;
- global `UBIQUITOUS_LANGUAGE.md` edits.

Future enforcement may add machine-readable proof labels, promotion gates, and
pilot skill evidence, but that work must happen in a separate implementation
slice with eval proof.

## Consequences

Positive:

- Future agents can distinguish "can invoke" from "should trust."
- Catalog growth no longer implies capability maturity.
- Default-visible promotion can be tied to evidence instead of importance.
- Review and eval artifacts have a common vocabulary.

Costs:

- Some skills will remain honestly classified as `latent` or `experimental`
  longer.
- Future enforcement work must avoid turning proof labels into manual ceremony.
- Outcome proof requires real task evidence, not just audit output.

## Traceability

- Plan: `.harness/plan/agent-skills-ask-control-plane-decomposition-plan.md`
- Refactor program: `.harness/refactors/proof-driven-skill-promotion.md`
- Eval artifact: `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`
- Glossary checked: `UBIQUITOUS_LANGUAGE.md`

## Non-Decision

This ADR does not decide which existing skills are trusted or default-visible.
It defines the vocabulary required before those decisions can be made safely.
