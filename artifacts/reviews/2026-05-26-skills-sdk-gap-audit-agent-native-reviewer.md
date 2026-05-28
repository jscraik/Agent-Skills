# Review: agent-native-reviewer

## Findings

### Critical
1. **Invalid owner manifest is silently ignored instead of classified as a blocker** -- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2513-2538`
   `_load_project_skills_sdk_manifest` returns `None` on JSON decode errors, schema-version mismatch, and duplicate root declarations with no explicit error surface. That means doctor flow degrades into "manifest absent" behavior, losing the distinction between "undeclared" and "declared but invalid." For agent-native parity this is a trust failure: users can inspect and fix a bad manifest, but agents are not given a deterministic blocker class tied to the exact invalid state.
   Fix: add a manifest validation result (`present_valid`, `present_invalid`, `absent`) and emit `blocked_validation` with a new class like `blocked_manifest_invalid`, including parse/schema/duplicate-root reason text.

### Warnings
1. **Project root defaults are under-constrained, enabling ambiguous lifecycle targeting** -- `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:73-107`
   The schema requires `default_for_create/install/update` booleans per root but does not enforce exactly one default per operation. Multiple true or all false is schema-valid and can produce non-deterministic create/install/update behavior in future SDK lifecycle commands.
   Recommendation: enforce exactly one default root per operation via schema `oneOf` constraints or runtime validator checks.

2. **Existing `skills init` behavior conflicts with owner-repo SDK lifecycle intent** -- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:4158-4163`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:4184-4188`
   `init_skill` writes under `Skills/<category>` by default and hardcodes owner metadata (`--owner "Agent Skills Kit"`) plus repo-specific lifecycle defaults. This is a productization risk beyond "missing `skills sdk` namespace": today’s initializer semantics are coupled to this repo identity and do not align with owner-repo manifest-driven roots described in `skills-sdk.json`.
   Recommendation: split repo-internal scaffold defaults from SDK-owner mode; make owner metadata and root target manifest-driven.

3. **Rename blast radius is larger than surface docs and command names** -- `Infrastructure/config/schemas/skill-doctor.v1.schema.json:3`, `Infrastructure/config/schemas/skill-package.v1.schema.json:3`, `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:3`, `Infrastructure/config/schemas/skill-doctor.v1.schema.json:387`
   Schema `\$id` values are anchored to `https://agent-skills.local/...` and doctor schema includes `const: "Agent Skills Kit"`. Renaming repo/product without a compatibility alias strategy will break schema identity, fixture expectations, and downstream consumers that pin these IDs.
   Recommendation: introduce stable, product-neutral schema namespace before rename and support alias IDs during migration.

## Missing Improvements
- Add explicit manifest validity reporting to doctor payloads and readiness summaries. Right now invalid manifests are not represented as first-class state.
- Add a dedicated validator for `skills-sdk.project.v1` operational invariants (unique defaults, declared roots resolvable, evidence path writable intent).
- Add an owner-repo bootstrap fixture test that proves SDK flows from outside `agent-skills` without inheriting repo-specific constants.
- Add migration compatibility tests for schema `\$id` aliases (old `agent-skills.local` + new neutral namespace) before rename execution.

## Rename/Productization Risks
- **Contract identity lock-in:** schema `\$id` and hardcoded owner constants bind wire contracts to current branding.
- **Initializer coupling:** `skills init` defaults assume canonical source under this repo and can mislead external adopters.
- **State interpretation drift:** absent vs invalid manifest not distinguished, so external SDK diagnostics can silently misclassify owner setup problems.
- **Docs-to-runtime mismatch risk:** planning/runtime duality in `skills-sdk.json` plus repo-coupled initializer increases likelihood that agents claim support for lifecycle behavior not truly portable yet.

## Recommended Next Patch
Implement strict manifest-state classification in doctor path:

- Add helper return shape from `_load_project_skills_sdk_manifest`:
  - `status: absent|valid|invalid`
  - `error_class` + `error_message` when invalid
- Thread this into projection ownership + doctor blockers:
  - emit `blocked_validation` with `class: blocked_manifest_invalid`
  - include `owner_manifest_path`, schema reference, and exact parse/constraint failure
- Update `skill-doctor.v1` schema and tests for new blocker class and details.

Validation command:
```bash
python3 -m unittest Infrastructure.tests.test_ask_skills_doctor
```

## Coverage Notes
Inspected:
- `.harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md`
- `README.md`
- `UBIQUITOUS_LANGUAGE.md`
- `Infrastructure/config/skills-sdk.json`
- `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json`
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
- `Infrastructure/config/schemas/skill-package.v1.schema.json`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- live CLI probes:
  - `./bin/ask skills --help`
  - `./bin/ask skills init --help`
  - `./bin/ask skills doctor he-heartbeat --json --robot`
  - `./bin/ask skills events --json --robot`

Did not inspect:
- Full test suite execution outside targeted command probes.
- Non-skills command groups unless directly relevant to SDK contract claims.

WROTE: artifacts/reviews/2026-05-26-skills-sdk-gap-audit-agent-native-reviewer.md
