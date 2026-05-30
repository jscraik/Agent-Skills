# Review: adversarial-reviewer

## Findings

### High: Roadmap command chain is self-contradictory and creates guaranteed operator dead-ends
Evidence:
- Trigger: The audit proposes `./bin/ask skills eval <handle> --json --robot` as part of the minimal spine ([.harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md:133](/Users/jamiecraik/dev/agent-skills/.harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md:133)).
- Execution path: `ask skills` currently has no `eval` action; valid actions include `prove`, `doctor`, `package`, `conformance`, `sync`, etc. (CLI output from `./bin/ask skills --help`).
- Failure outcome: Teams implementing the audit literally will ship docs/contracts that point users to an invalid command; adoption flow halts at first-run with "unknown action", and trust in the new SDK facade drops immediately.
Impact:
- This is a contract-level failure, not a polish issue. The "small public spine" claim becomes non-executable.

### High: Rename to Skills SDK will break package provenance trust gates unless allowlists migrate first
Evidence:
- Trigger: A renamed emitter writes package provenance values like `skills-sdk` or `skills-sdk-kit`.
- Execution path: package verification trusts a fixed allowlist that currently includes `agent-skills` and `agent-skills-kit`, but not `skills-sdk` ([Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py:20-29](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py:20)).
- Failure outcome: `skills package verify` blocks otherwise valid archives as untrusted provenance post-rename.
Impact:
- Multi-step cascade: rename -> packaging metadata update -> verification gate blocks -> release lane marked blocked_validation despite healthy code.

### High: Project-manifest filename collision can silently mutate doctor ownership semantics in the maintainer repo
Evidence:
- Trigger: Introducing `skills sdk init` at repo root writes `skills-sdk.json` project manifest (as proposed repeatedly in audit).
- Execution path:
- Runtime code auto-loads `<repo_root>/skills-sdk.json` and applies it as ownership authority when `schema_version == "skills-sdk.project.v1"` ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:2493-2538](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2493)).
- The extraction/planning contract file is also named `skills-sdk.json` (under `Infrastructure/config`) and the docs repeatedly reference "skills-sdk.json" as a central contract surface ([Infrastructure/config/skills-sdk.json:1-3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/skills-sdk.json:1)).
- Failure outcome: A root-level manifest created for SDK smoke tests can unexpectedly change source/projection ownership classification in day-to-day `skills doctor` runs for this repo.
Impact:
- This creates a hidden stateful toggle in diagnostics, making results depend on whether a test manifest exists in cwd.

### Medium: Rename migration risk is wider than repo name; plugin marketplace identity is hard-coded
Evidence:
- Trigger: Repository and product rename to Skills SDK without alias migration.
- Execution path:
- Default marketplace identity and fallback names are hard-coded to `agent-skills-local` ([Infrastructure/scripts/lib/ask/services/plugin_cache.py:232-237](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/services/plugin_cache.py:232)).
- Plugin state normalization also force-appends `agent-skills-local` ([Infrastructure/scripts/lib/ask/plugin_state.py:172-173](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/plugin_state.py:172)).
- Failure outcome: renamed docs and user mental model diverge from persisted plugin IDs/state; installs or lookups can appear inconsistent across old/new identities.
Impact:
- Productization risk: "rename done" externally while internal identities remain legacy, causing long-tail support churn.

### Medium: Audit underestimates command-surface ambiguity around init
Evidence:
- Trigger: Users follow "run init first" guidance.
- Execution path: Existing `ask skills init` already means "Initialize a new skill scaffold" (CLI help), while audit recommends adding `ask skills sdk init` for project-level bootstrap ([.harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md:130](/Users/jamiecraik/dev/agent-skills/.harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md:130)).
- Failure outcome: non-expert users run the wrong init path, scaffold a skill, and still lack manifest/evidence directories; follow-on doctor output looks "mysteriously blocked".
Impact:
- This is a predictable abuse case in normal usage, not edge behavior.

## Missing Improvements

- Add a "contract command lint" that validates every command string embedded in audit/docs/config against live argparse action tables (e.g., fail CI if docs reference `ask skills eval` when no such action exists).
- Add explicit rename migration checks:
- provenance alias map (`agent-skills* -> skills-sdk*`) in package verify.
- plugin marketplace alias map and deprecation window.
- Introduce a dedicated project manifest filename that cannot be confused with extraction contract docs (e.g., `.skills-sdk/project.json`), then gate doctor on that location.
- Add a "diagnostic determinism" test: doctor output must not change unless manifest file exists at declared path and passes schema validation.

## Rename/Productization Risks

- Contract identity drift:
- Schema IDs remain on `https://agent-skills.local/... ` across core schemas ([Infrastructure/config/schemas/skill-package.v1.schema.json:3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skill-package.v1.schema.json:3), [Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:3)).
- Risk: external SDK branding says Skills SDK while machine contracts continue emitting agent-skills namespace; this creates dual identity for integrators.
- Stateful alias debt:
- Hard-coded `agent-skills-local` and provenance allowlists mean rename cannot be "single PR"; it needs staged dual-write/dual-read compatibility.
- Operational confusion risk:
- Reusing `skills-sdk.json` as both "conceptual contract name" and root project manifest path will produce accidental behavior changes during migration testing.

## Recommended Next Patch

Smallest high-leverage patch:
- Add a CI validator that parses known contract sources (initially:
- `.harness/research/audits/*.md` command fences/inline command lines for `./bin/ask skills ...`
- `Infrastructure/config/skills-sdk.json` interface strings)
- Then executes a non-mutating argparse check to confirm each referenced `ask skills <action>` exists.
- Start by failing specifically on nonexistent `skills eval` references and suggesting `ask evals ...` or `ask skills prove/package/conformance` based on mapping.

Validation command:
- `python3 Infrastructure/scripts/validation-and-linting/validate_skills_command_contracts.py --json`

## Coverage Notes

Inspected:
- Updated audit doc.
- Live `./bin/ask skills --help` and `./bin/ask skills sdk --help`.
- `Infrastructure/config/skills-sdk.json`.
- `Infrastructure/config/schemas/skill-package.v1.schema.json`.
- `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json`.
- `Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py`.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py` (manifest loading and ownership logic).
- Plugin identity code in `plugin_cache.py` and `plugin_state.py`.

Not fully inspected:
- Full downstream plugin install/lookup execution flow.
- End-to-end packaging publish pipeline beyond local verification logic.
- Any external consumer repos or migration scripts outside this tree.

WROTE: artifacts/reviews/2026-05-26-skills-sdk-gap-audit-adversarial-reviewer.md

