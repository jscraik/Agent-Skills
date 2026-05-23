# Standards/Docs Review — JSC-351 PU-006

No blocker/high/medium findings found.

## Coverage
- Reviewed the current diff for:
  - `Infrastructure/scripts/lib/ask/services/codex_preview.py`
  - `Infrastructure/scripts/lib/ask/commands/skills.py`
  - `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
  - `Infrastructure/scripts/lifecycle-and-sync/{skill_discovery.py,skillset_model.py,generate_root_skill_sets.py,generate_skillset_manifests.py,command_surface.py}`
  - `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
  - Related tests and touched docs surfaces in this slice.

## Standards checks applied
- Root AGENTS rule: “Use `./bin/ask` for repo operations” — no new guidance in reviewed files introduces conflicting ad hoc repo-operation commands.
- Root AGENTS rule: “Edit canonical sources, not runtime projections” — reviewed code changes are in canonical script/service sources; generated-surface handling in this slice appears to tighten projection boundaries (including explicit skip logic when rooted runtime symlinks already satisfy handle projection).
- Root AGENTS high-signal steering rule — evidence-oriented validation language and command selection changes remain structured and deterministic; no downgrade to vague/non-actionable follow-up guidance observed.
- Codex-subtree AGENTS routing/validation constraints were checked for contradiction with this slice; no direct conflict introduced by the reviewed files.

## Residual risks
- The preview-service extraction and facade forwarding changes are structurally correct in diff review, but monkeypatch forwarding behavior remains sensitive to future wrapper additions; guardrail depends on tests continuing to cover all patchable exports.
- System-bridge visibility and generated-handle skip behavior are policy-sensitive; if root/flat visibility policy changes later, this logic may need synchronized updates in both discovery and command-surface generation paths.
- Package-contract/schema additions in `skills_impl.py` rely on companion schema fixtures and snapshot discipline; drift risk is low for this patch but remains an ongoing maintenance surface.

WROTE: artifacts/reviews/jsc-351-pu006/standards-docs.md

