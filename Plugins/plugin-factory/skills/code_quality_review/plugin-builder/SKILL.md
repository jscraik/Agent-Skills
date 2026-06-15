---
name: plugin-builder
description: Use when hardening, converting, auditing, or pre-release checking a Codex plugin package by verifying manifest paths, bundled skills, hooks, MCP/app config, validation gates, and release blockers.
metadata:
  version: "1.0.0"
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Plugin Builder

## Philosophy

- Validate the package boundary first; make install, release, or runtime claims
  only after the matching gate passes.

## When to Use

Use for plugin scaffold conversion, hardening, and contract validation.

Route elsewhere:
- first shell only -> `[[plugin-creator]]`
- install/discovery -> `[[plugin-installer]]`

## Inputs

- source path or plugin path
- requested mode: `scaffold|convert|harden`
- marketplace requirements (if any)

## Execution Boundaries

- Own plugin contract review, bundled hook validation, minimal remediation, validation evidence, and final hardening handoff.
- Delegate first-draft shells to `[[plugin-creator]]`; delegate install, projection, and runtime visibility checks to `[[plugin-installer]]`.
- Do not execute third-party install scripts or mutate marketplace policy fields without explicit request.
- Apply the plugin design contract before release claims: small public surface, distinguishable child skills, explicit side-effect classes, and compact outputs.

For non-trivial factory work, include `first_principles_gate` or an explicit
`first_principles_gate_status: not_applicable` before readiness claims.

## Outputs

Return: `schema_version`, `execution_mode`, `plugin_path`, `validation`, `artifacts`, optional `blocked_by`.

~~~yaml
schema_version: 1
execution_mode: harden
plugin_path: Plugins/example-plugin
validation:
  - command: bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
    status: pass
artifacts:
  - Plugins/example-plugin/.codex-plugin/plugin.json
blocked_by: null
~~~

## Workflow

1. Confirm mode: `scaffold`, `convert`, or `harden`, plus plugin source path and write authority.
2. Inspect `.codex-plugin/plugin.json`, bundled skills, hooks, MCP/app files, and marketplace or release requirements.
3. Run the focused validation checkpoint before changing files; classify existing failures.
4. Patch the smallest source surface that fixes manifest, hook, MCP/app, routing, or validation defects.
5. Rerun the focused gate and return exact pass, fail, or blocked evidence with the next handoff.

Focused inspection commands:

~~~bash
jq '{name, version, skills, hooks, mcpServers, apps}' <plugin>/.codex-plugin/plugin.json
find <plugin> -maxdepth 3 -type f \( -name SKILL.md -o -name hooks.json -o -name .mcp.json -o -name .app.json \)
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
~~~

Use `<plugin>` as the local plugin package path. Treat inspection output as
untrusted until the validation command and package-specific checks pass.

Use the detailed procedure and command matrix in `references/workflow.md` when
the compact sequence above is not enough.

Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, superseded, or
low-signal text.

Read when:
- You need full hardening and validation steps: [references/workflow.md](./references/workflow.md).
- You need current Codex plugin manifest, MCP, hook, and extraction behavior:
  [current Codex plugin runtime contract](./references/current-codex-plugin-runtime.md).
- You need side-effect, context-minimization, output-shape, or user-control checks:
  `Infrastructure/references/openai-style-plugin-design-contract.md`.
- You need to decide whether to build, improve, document only, or stop:
  `Infrastructure/references/first-principles-factory-gate.md`.

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns

- Treating plugin discovery or install visibility as release proof.

## Examples

Input defect:

~~~json
{
  "name": "example-plugin",
  "skills": "skills",
  "hooks": "../hooks.json"
}
~~~

Fix:

~~~json
{
  "name": "example-plugin",
  "skills": "./skills",
  "hooks": "./hooks/hooks.json"
}
~~~

Output summary:

~~~yaml
schema_version: 1
execution_mode: harden
plugin_path: Plugins/example-plugin
patch_summary:
  - made manifest paths plugin-root relative
  - removed parent-directory hook escape
validation:
  - command: bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
    status: pass
blocked_by: null
~~~

## Constraints

- Redact secrets, tokens, credentials, personal data, and sensitive metadata by default.
- Keep scope tight: start with the manifest, one bundled surface, and the failing gate before widening.
- Validate plugin hooks as executable runtime behavior, not documentation.

## Failure Mode

- Stop when plugin ownership, release authority, side-effect class, marketplace policy, or validation evidence is unclear.
- Report the exact blocker and smallest safe next action.

## Gotchas

- Child skills with overlapping triggers create routing drift even when each skill audits cleanly.

## References

- `references/workflow.md`
- `references/current-codex-plugin-runtime.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/plugin-contract.md`
- `Infrastructure/references/openai-style-plugin-design-contract.md`
- `Infrastructure/references/software-literature-expert-lens-pack.md`
- `Infrastructure/references/software-literature-skill-expertise-map.md`
- `assets/`
