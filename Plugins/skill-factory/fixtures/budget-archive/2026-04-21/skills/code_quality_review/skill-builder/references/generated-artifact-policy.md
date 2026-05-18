# Generated Artifact Policy

Use this reference when auditing, relocating, or deleting generated skill artifacts.

## Policy

- Treat generated manifests, dashboards, reports, eval outputs, and release bundles as projections unless a repo contract names them as source.
- Prefer regenerating projections from canonical scripts over hand-editing generated output.
- When a generated artifact must be committed, record the source command and validation evidence in the handoff.
- Do not copy generated output into expected paths to satisfy a gate unless the producing command is broken and the workaround is explicitly documented.
- Keep high-churn runtime caches, local app state, and temporary reports ignored unless the repo explicitly tracks them as release evidence.

## Audit Questions

- What source file or script owns this artifact?
- Is the artifact deterministic enough to review?
- Does the repository contract require it to be tracked?
- Can the artifact be regenerated from the committed source without hidden local state?
