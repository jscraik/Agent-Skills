# Project And Global Skill Scopes

## Scopes

`global` skills live under canonical topic folders:

```text
Skills/<topic-cluster>/<skill>/SKILL.md
```

`local-plugin` skills live inside local plugin packages:

```text
Plugins/<plugin>/skills/**/<skill>/SKILL.md
```

`project` skills live under:

```text
Skills/project/<skill>/SKILL.md
```

Project skills are reserved for repository-local overrides and should stay small.

## Precedence

When two sources use the same skill name, discovery uses this precedence:

```text
project > local-plugin > global
```

The lower-precedence skill remains on disk and visible in advanced provenance
reports, but only the winner is selected for the canonical default view.

## Local Plugin Browseability

Local plugin skills remain separately browsable under `Plugins/<plugin>/skills/**`.
Rooted runtime projection does not collapse those source trees. Instead, rooted
mode projects small root entrypoints and uses `.skillsets/**` manifests to route
to the selected canonical source path.

## Validation

`Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
reports:

- scope counts;
- shadowed entries;
- suppressed entries;
- unresolved same-scope collisions.

Same-scope collisions fail validation because no deterministic ownership winner
can be chosen safely.
