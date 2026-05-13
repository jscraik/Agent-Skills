# Architecture Lens Canon

Use when `he-strategy` performs architecture review, repo cognition, moat review,
strategic critique, or structural triage and no fresh reference attachments are
supplied.

Status: `internal-canon`. Evidence role: lens only. This file is not repository
evidence and is not a substitute for the source books. The lens asks questions;
repo files, runtime behavior, validation output, and labeled inference answer
them.

If the user supplies books, notes, PDFs, EPUBs, or excerpts for the run, prefer
that material and record its attachment status separately.

## Lens Checklist

| Lens | Use it to test | Watch for |
| --- | --- | --- |
| Pragmatic engineering | Whether the repo helps humans and agents ship useful, reversible work without entropy. | Duplicate command contracts, routing drift, stale projections, docs not enforced by tooling, clever automation with manual sync cost. |
| Philosophy of Software Design | Whether modules are deep enough to justify their interfaces and reduce cognitive load. | Pass-through wrappers, broad orchestrators, terminology drift, hidden dependencies, mixed abstraction levels, complexity laundering. |
| Domain-Driven Design | Whether language and bounded contexts protect model integrity. | Fractured vocabulary, generated/runtime projections treated as source, overlapping skill/plugin ownership, context maps that exist only in prose. |
| XP / feedback | Whether change can proceed safely in small, observable slices. | Slow or flaky gates, CI/local drift, keyword-only evals, large plans without feedback slices, weak stop/pivot conditions. |
| Structural refactoring | Where complexity can be reduced mechanically without inventing a framework. | Giant files, repeated mode switches, nested policy conditionals, temporal coupling, spread-out state mutation, helpers that obscure intent. |
| Agent-native architecture | Whether agents can discover, route, validate, and reason locally. | Ambiguous handles, projection/source drift, prompt growth without eval proof, missing authority boundaries, high-context workflows. |
| Moat pressure | Whether defensibility is real operational leverage or impressive complexity. | Fake sophistication, unmeasured reliability claims, non-compounding process, weak trust surfaces, complexity that would vanish under simplification. |

## Required Claim Shape

For every major review conclusion, write:

- `Fact`: direct repo evidence, validation output, runtime observation, or documented command behavior.
- `Interpretation`: what the lens suggests the fact means.
- `Speculation`: plausible but unproven implication, if any.
- `Confidence`: high, medium, low, or blocked.

Never let lens language substitute for evidence. Do not summarize the reference
books; use the lenses to pressure-test the repository.
