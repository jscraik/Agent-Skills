# Architecture Review: Commandable Skill Trees (Uncommitted)

## 1) Architecture Overview

The change set establishes a manifest-driven command surface for latent skills and introduces generated runtime stubs for command-visible handles. The core architectural direction is sound:

- Rooted manifests remain the intended source for command-handle metadata.
- `.skillsets/command-surface.json` is framed as a generated projection.
- Runtime stubs are intentionally thin pointers to canonical latent modules.
- Public `./bin/ask` surfaces now expose handle listing, resolve, and proof operations.

The main risks are around verification semantics and ownership boundaries rather than the high-level decomposition.

## 2) Change Assessment

The implementation fits the target architecture in broad strokes:

- Command surface generation and stub generation are integrated into rooted sync (`_sync_rooted_projection`) and included in validation paths.
- Rooted workspace validation now tolerates command stubs while still enforcing root-skill-set policy.
- CLI adds explicit entrypoints (`skills handles ...` and `skills proof ...`) for operator/agent workflows.

However, three gaps materially weaken design integrity:

1. drift detection for the generated `command-surface.json` projection is missing;
2. `skills proof` can return pass without proving live invocation;
3. source ownership checks now permit fallback to a second repo root, weakening strict provenance boundaries.

## 3) Compliance Check (Severity-Ranked Findings)

### HIGH: Generated command-surface drift is not detectable via a check path

- Evidence:
  - `handles_report(...)` computes an in-memory payload from manifests: `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:413`.
  - `skills handles --check` only validates computed payload status and violations; it does not compare against on-disk `.skillsets/command-surface.json`: `Infrastructure/scripts/lib/ask/commands/skills.py:475`, `Infrastructure/scripts/lib/ask/commands/skills.py:492`.
  - `write_command_surface_projection(...)` writes/returns payload but there is no companion `check_command_surface_projection(...)` analogous to stub drift checking: `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:447`.
- Why this violates architecture intent:
  - The design labels `.skillsets/command-surface.json` as generated projection, but there is no enforcement that committed/runtime projection matches canonical generation. This leaves a silent drift lane.
- Remediation:
  - Add `check_command_surface_projection(...)` to compare generated payload vs existing file (missing/mismatch/read error codes), and wire it into `skills handles --check` and rooted user/workspace validation.

### HIGH: `skills proof` reports `pass` without a live invocation gate

- Evidence:
  - Pass/fail is computed from `gates` that exclude live invocation: `Infrastructure/scripts/lib/ask/commands/skills.py:565`, `Infrastructure/scripts/lib/ask/commands/skills.py:577`.
  - Live invocation is always a manual placeholder (`manual_session_gate`) and does not affect status: `Infrastructure/scripts/lib/ask/commands/skills.py:600`.
- Why this violates architecture intent:
  - Public proof semantics imply end-to-end proof; current contract proves resolver/stub/symlink surfaces only. This can produce false confidence for command usability in live Codex sessions.
- Remediation:
  - Split contracts explicitly:
    - keep current command as `skills proof --mode surfaces` (resolver/stub/sync proof), and
    - add a separate `skills live-proof` artifact with explicit pass/fail derived from invocation evidence.
  - Alternatively, keep one command but require `live_codex_invocation.status == pass` before overall proof can pass.

### MEDIUM: Source ownership boundary is weakened by dual-root fallback checks

- Evidence:
  - Skill-handle validation now accepts source existence in either caller-provided root or canonical `repo_root()`: `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:326`.
  - Router manifest validation similarly accepts either `skillsets_dir.parent` or canonical `repo_root()`: `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py:89`, `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py:110`.
- Why this violates architecture intent:
  - Canonical-only ownership becomes ambiguous in worktrees/snapshots: a manifest can validate against a second root even if local source is missing, masking projection drift and reducing reproducibility.
- Remediation:
  - Enforce single-root validation by default (the active repo root passed into command execution).
  - If fallback is needed for narrow compatibility scenarios, gate it behind explicit opt-in (`--allow-canonical-root-fallback`) and emit a warning artifact when used.

## 4) Risk Analysis

- Projection integrity risk: stale `command-surface.json` can survive checks and propagate inconsistent runtime behavior.
- Operational confidence risk: `skills proof` may be interpreted as full handle viability despite no live invocation evidence.
- Boundary drift risk: dual-root acceptance increases chance of non-deterministic behavior between local worktree and canonical checkout.

## 5) Recommendations

1. Add and enforce command-surface drift checks as first-class validation gates (same rigor as stub drift checks).
2. Tighten `skills proof` semantics so pass/fail aligns with the name and operator expectation; separate surface proof vs live invocation proof if needed.
3. Restore strict single-root ownership for source validation, with any fallback explicitly opt-in and auditable.

These corrections keep the current architecture direction while closing the highest-risk integrity gaps.

WROTE: artifacts/reviews/architecture-strategist.md
