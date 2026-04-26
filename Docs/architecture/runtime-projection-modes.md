# Runtime Projection Modes

## Modes

`flat`:

- current default;
- projects the allowlisted first-level skill surface;
- keeps hidden/system bridge skills out of first-level runtime discovery.

`rooted`:

- projects only root skill sets;
- writes latent routing manifests under `.skillsets/**`;
- keeps atom, molecule, compound, router, and reference modules latent until
  selected.

`hybrid`:

- deferred;
- must not mutate runtime surfaces until a named consumer and budget test exist.

## Scope

`ask skills sync --scope workspace` mutates repository runtime projection
surfaces.

`ask skills sync --scope user` relinks user-facing runtime paths after the
repository projection is prepared.

The legacy shell flag `sync_skills.sh --project-local` maps to the canonical
workspace scope.

For non-flat projection modes, the legacy shell sync wrapper delegates to the
same `ask skills sync` engine so projection semantics do not drift by entry
point.

## Reporting

Use the runtime topic for projection and budget reports:

```bash
ask runtime surface --json
ask runtime budget --json
```

`ask runtime surface` reports the current visible runtime entries, hidden system
lane entries, plugin/local/global scope counts, duplicate names, largest
descriptions, and estimated description token cost.

`ask runtime budget` runs the same report as a gate and exits nonzero if the
runtime budget fails.

## Environment

`SYNC_SKILLS_PROJECTION_MODE` supplies a default mode when no `--projection`
argument is passed.

CLI arguments win over environment variables.

## Rollback

Use flat mode as the escape hatch:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
```
