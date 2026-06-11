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

Use these as pressure prompts, not book summaries.

| Lens | Test | Watch for |
| --- | --- | --- |
| Pragmatic engineering | DRY, orthogonality, reversibility, tracer-bullet paths, automation maturity, knowledge capture, and whether tooling reduces entropy. | Duplicate command contracts, routing drift, stale projections, unenforced docs, automation with manual sync cost. |
| Philosophy of Software Design | Deep/shallow modules, pass-through abstractions, information leakage, change amplification, mixed levels, hidden dependencies, interface obviousness. | Complexity laundering, broad orchestrators, terminology drift, helpers that obscure intent. |
| Domain-Driven Design | Ubiquitous language, bounded context integrity, anti-corruption boundaries, domain/service separation, model and naming stability. | Fractured vocabulary, generated/runtime projections treated as source, prose-only context maps, code that merely moves files and prompts. |
| XP / feedback | Feedback-loop speed, CI/local parity, small safe slices, test realism, observability, stop/pivot conditions, whether change encourages learning or fear. | Slow/flaky gates, keyword-only evals, large plans without feedback slices. |
| Structural refactoring | Giant orchestrators, temporal coupling, procedural leakage, spread state mutation, brittle conditionals, low-signal complexity, agent regression risk. | Repeated mode switches, nested policy conditionals, refactor choke points. |
| Agent-native architecture | Skill/plugin discoverability, deterministic execution, context efficiency, machine-readable boundaries, validation loops, memory, workflow composability. | Ambiguous handles, projection/source drift, prompt growth without eval proof, missing authority boundaries. |
| Moat pressure | What is hard to copy, measurable, compounding, and still valuable after simplification. | Fake sophistication, unmeasured reliability claims, weak trust surfaces, complexity that a smaller competitor could delete. |

## Required Claim Shape

For every major review conclusion, write:

- `Fact`: direct repo evidence, validation output, runtime observation, or documented command behavior.
- `Interpretation`: what the lens suggests the fact means.
- `Speculation`: plausible but unproven implication, if any.
- `Confidence`: high, medium, low, or blocked.

Never let lens language substitute for evidence. Do not summarize the reference
books; use the lenses to pressure-test the repository.
