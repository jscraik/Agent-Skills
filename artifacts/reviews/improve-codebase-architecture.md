# Improve Codebase Architecture Pass

Status: pass

Architectural Question:
- Does this slice turn the planned Skills SDK source/projection boundary into an executable contract without widening the SDK surface prematurely?

Answer:
- Yes. The change adds a project manifest schema and wires projection ownership into `skills doctor`, so generated runtime projections are blocked as editable source unless an owner repo explicitly declares a canonical project source root.

In-Scope Architecture Fixes:
- Added `skills-sdk.project.v1.schema.json` for owner-repo skill roots, eval evidence paths, trust policy, precedence policy, and default operation flags.
- Added `projection_ownership` to the doctor schema and SDK layer map.
- Added a doctor blocker for generated runtime projections and Codex runtime config roots used as direct source targets.
- Fixed rooted runtime proof so source symlink projections satisfy the runtime handle check when the root runtime link points at the workspace projection.

Architecture Risks Checked:
- Source/projection ownership remains explicit and machine-readable.
- Telemetry/evidence remains optional; this slice does not introduce a collector dependency.
- Project-local manifest support is schema-first and does not imply registry, marketplace, or broad package lifecycle work.

Residual Notes:
- The next architecture slice should bridge doctor output to eval artifact bundles and lifecycle event logs, but this patch intentionally stops at the ownership/readiness seam.
