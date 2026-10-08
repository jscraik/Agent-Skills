# Migrate Flat Projection To Rooted

## Status

Rooted runtime projection mode is retired. Do not run `--projection rooted`.
The supported SDK projection mode is `flat`. Projection maintenance is a
transitional recovery operation, not the managed installation route. Follow the
[approved lifecycle](/Docs/agents/14-path-ownership-boundaries.md#approved-lifecycle):
new managed installations use SDK-checked private Tessl versions; verified OpenAI
plugins and system skills retain their provider-managed routes. If that route is
unavailable, report the capability gap without relinking home runtime paths.

## Authorised Transitional Recovery

Name the existing consumer, approved source and exact targets before mutation.
Only an explicitly authorised workspace refresh permits:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
python3 bin/ask skills handles --check --json
```

User sync is retired and rejects before mutation. Do not relink home targets to
this checkout. Preserve approved physical packages in `~/.agents/skills`; use
the authorised Skills SDK installation/proof lane for managed home packages.

Preserve prior working state and verify the selected consumer's discovery and
behaviour after recovery. Do not require every home link to target this checkout.
See [consumer-specific recovery proof](/Docs/agents/17-skill-management.md#user-runtime-links).

## Legacy Metadata

Some `.skillsets/**` and context-budget fixtures still use rooted terminology
as compatibility metadata. Maintain those with the dedicated manifest generator
and context-budget validator; do not use the removed `skills sync --projection
rooted` command.

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
```
