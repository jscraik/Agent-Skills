# Simplify Pass

Status: pass

Scope:
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- `Infrastructure/config/schemas/*skills-sdk*.json`
- Targeted tests and generated `.skillsets` manifests.

Review:
- The new ownership check is a single helper plus one doctor check insertion. That keeps path classification local and avoids spreading root ownership decisions through the doctor flow.
- The runtime proof change reuses the existing runtime-link payload instead of adding another filesystem traversal path.
- The project manifest schema is intentionally small: root classifications, eval evidence paths, trust policy, precedence policy, and operation defaults.

Changes Made From This Pass:
- Aligned the `.codex/skills` classifier with the manifest enum by using `client_runtime_config`.
- Promoted `default_for_create`, `default_for_install`, and `default_for_update` from documented required fields into schema-required fields.

Residual Notes:
- No further simplification is recommended for this slice without weakening the executable ownership guard.
