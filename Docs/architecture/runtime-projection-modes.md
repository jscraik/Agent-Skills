# Runtime Projection Mode

## Current Mode

Agent Skills Kit supports one active runtime projection mode: `flat`.

`flat`:

- projects SDK-visible skills directly under `.agents/skills/<skill>/SKILL.md`;
- uses the canonical skill name as the runtime handle;
- keeps hidden/system bridge skills out of first-level runtime discovery;
- treats canonical `Skills/**/SKILL.md` and `Plugins/*/skills/**/SKILL.md` as the source of truth.

Generated rooted manifests and command-surface metadata are obsolete. They are not SDK inputs, not runtime handles, and not a compatibility mode operators should select.

## Scope

`ask skills sync --scope workspace` mutates repository runtime projection surfaces.

`ask skills sync --scope user` relinks user-facing runtime paths after the repository projection is prepared.

The legacy shell flag `sync_skills.sh --project-local` maps to the canonical workspace scope.

## SDK Skill Names

Use SDK skill names directly:

```bash
./bin/ask skills resolve agents-md --json --robot
./bin/ask skills handles --check --json --robot
./bin/ask skills prove agents-md --json --robot
```

Resolver output is only one gate. Source resolution, workspace projection, user runtime links, runtime budget, and live invocation evidence remain separate acceptance gates.

## Reporting

Use the runtime topic for projection and budget reports:

```bash
./bin/ask runtime surface --json --robot
./bin/ask runtime budget --json --robot
```

`ask runtime surface` reports the current visible runtime entries, hidden system lane entries, plugin/local/global scope counts, duplicate names, largest descriptions, and estimated description token cost.

`ask runtime budget` runs the same report as a gate and exits nonzero if the runtime budget fails.

## Environment

`SYNC_SKILLS_PROJECTION_MODE` may be set to `flat` or omitted. Other values are rejected by SDK validation.

CLI arguments win over environment variables.

## Recovery

Use flat mode as the recovery path:

```bash
./bin/ask skills sync --scope workspace --projection flat --json --robot
```
