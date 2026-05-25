# Architecture Final Review - JSC-364 PU-008 Capability Discovery

## 1) Architecture Overview
The change adds a new public command surface `ask skills capabilities` that reports capability discovery for the runtime proof-plane without claiming live runtime parity. The implementation follows the existing layering pattern:
- CLI/action wiring in `Infrastructure/bin/ask`
- command taxonomy/help/fuzzy metadata in `Infrastructure/scripts/lib/ask/command_metadata.py`
- command behavior in `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- facade export in `Infrastructure/scripts/lib/ask/commands/skills.py`
- regression tests in `Infrastructure/tests/test_ask_skills_codex_preview.py`

This is consistent with current `ask` architecture and proof-plane conventions.

## 2) Change Assessment
- Capability discovery is in the correct command layer (`skills_impl`) and exposed through the existing `skills` command family.
- The result envelope and metadata usage are consistent with existing patterns (`CallResult`, `result.metadata["command"]`, structured `result.data` payload).
- The modeled-vs-live boundary is explicitly preserved:
  - `truth_boundaries.live_runtime_parity = "not_claimed"` for codex target
  - `known_limitations` explicitly states command availability does not equal live parity evidence.
- Validation/docs artifacts are placed in governed modules (command metadata + tests) rather than ad hoc docs-only surfaces.

## 3) Compliance Check
- Separation of concerns: upheld (CLI parsing vs command implementation vs metadata registry).
- API contract stability: upheld (new additive command, no breaking action renames/removals).
- Runtime truth boundary: upheld (explicit non-claim for live parity in capability mode).
- Test coverage for new surface: upheld (discoverability + payload assertions added).

## 4) Risk Analysis (Severity-ranked Findings)

### MEDIUM - Duplicated runtime-target contract can drift across modules
- Evidence:
  - `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2629` defines local `supported_targets = ["any", "codex", "agents"]`.
  - `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2655` hardcodes `evidence_targets`.
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:14` already defines canonical `SUPPORTED_RUNTIME_TARGETS`.
  - `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:15` already defines canonical `EVIDENCE_RUNTIME_TARGETS`.
- Why this matters:
  - The architectural source of truth for runtime target semantics already exists in the SDK adapter layer. Re-declaring the same contract in command code increases drift risk (for example if a new runtime target is introduced later).
- Remediation:
  - Import and use `SUPPORTED_RUNTIME_TARGETS` and `EVIDENCE_RUNTIME_TARGETS` from `runtime_adapters.py` in `skills_capabilities`.
  - Convert to one canonical iterable/serialization path (e.g., sorted(list(...))) so command output remains deterministic while sharing the contract.

## 5) Recommendations
1. Centralize runtime target constants by consuming `runtime_adapters` exports inside `skills_capabilities`.
2. Keep `truth_boundaries` and `known_limitations` fields mandatory for this command family, since they are now the key guardrail against modeled/live truth confusion.
3. Optionally add one focused test asserting command output target sets mirror adapter constants to prevent future contract drift.

## Overall
No material boundary violations were found. The command placement, abstraction level, result-shape discipline, and modeled-vs-live truth posture are architecturally sound. Residual risk is limited to duplicated runtime-target contract data across layers.
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/architecture-capabilities-final-reviewer.md
