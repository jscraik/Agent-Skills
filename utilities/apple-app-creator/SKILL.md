---
name: apple-app-builder
description: Orchestrate iOS/macOS app scaffolding and optional subskill adoption for existing projects. Use when users need a guided wizard to scaffold with XcodeGen and optionally install xcode-makefiles and simple-tasks.
---

# Apple App Builder

Scaffold or adopt reproducible iOS and macOS project tooling with XcodeGen plus optional local workflow helpers.

## Standards snapshot (March 2026)
- Prefer reproducible project generation over hand-built Xcode drift.
- Keep adoption non-destructive by default.
- Separate greenfield scaffolding from tooling adoption in existing repos.
- Print exact next commands so the result is easy to continue from.

## When to use
- Scaffolding a new iOS or macOS app with XcodeGen.
- Adding app-builder tooling into an existing Apple project.
- Installing optional subskills such as `xcode-makefiles` or `simple-tasks`.

## When not to use
- Editing an already-established Apple app without changing scaffolding or workflow tooling.
- General Xcode debugging with no scaffolding or adoption goal.
- Non-Apple platform setup.

## Required inputs
- Project mode: `new` or `adopt`.
- For `new`: app name, bundle ID, platform, UI framework, and output directory.
- Optional subskill-selection flags.
- Optional git-init and baseline-commit preferences.

## Deliverables
- A scaffolded project or adopted workflow update.
- Optional subskill installation results.
- Exact next commands for build, run, and follow-on setup.
- If requested, a structured status report with a `schema_version` field.

## Philosophy
- Scaffolding should be reproducible and reversible.
- Existing projects deserve low-drama adoption paths.
- The safest default is to make the next step explicit, not implicit.

## Constraints
- Redact secrets, credentials, provisioning data, and sensitive repo details by default.
- Do not overwrite unrelated project files outside the chosen scaffold or adoption path.
- Skip auto-commit when the repo is already dirty unless the user explicitly wants otherwise.

## Workflow
1. Collect required inputs for the selected mode.
2. Run doctor or preflight checks.
3. Choose the path:
   - `new` for templates plus XcodeGen
   - `adopt` for tooling-only installation
4. Install selected subskills unless explicitly skipped.
5. Optionally initialize git and create a baseline commit.
6. Print the exact next commands.

## Entrypoint
Use the bundled initializer:

```bash
scripts/init.sh --project-mode new
```

or

```bash
scripts/init.sh --project-mode adopt
```

## Tooling and references
- Use `scripts/init.sh` as the primary entrypoint.
- Load:
  - `references/workflow.md`
  - `references/placeholders.md`
  - `references/contract.yaml`
  - `references/evals.yaml`

## Validation
- Prefer `--dry-run` when project state is uncertain.
- Verify generated or updated files match the selected mode.
- Verify git-onboarding behavior matches the flags when enabled.
- Fail fast at the first missing input or failed doctor check.

## Anti-patterns
- Running `new` mode against an existing project expecting zero scaffold changes.
- Skipping dry-run in path-sensitive scenarios.
- Treating optional subskill installs as mandatory.

## Examples
- Scaffold a new macOS app and install both workflow helpers.
- Adopt makefile tooling into this existing iOS app without regenerating the project.
- Run the app-builder flow in dry-run mode first.

## See Also

| Skill | When to use together |
|---|---|
| [[xcode-makefiles]] | Add reproducible CLI builds after scaffolding the app |
| [[design-system]] | Apply design tokens to native UI components |
| [[fixing-accessibility]] | Add UIAccessibility labels to native views |
| [[recon-workbench]] | Audit the app binary and entitlements after creation |
| [[simple-tasks]] | Track app build and release tasks locally |

**Topic map:** [[mobile-native]]

## Remember
Good Apple project setup reduces future Xcode drift. Keep the scaffold reproducible and the adoption path deliberate.
