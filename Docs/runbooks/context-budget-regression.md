# Context Budget Regression

## Symptoms

- Rooted projection exposes individual latent skills at first level.
- Root descriptions or bodies exceed budget.
- Router returns too many candidates.
- `.skillsets/**` contains missing provenance, stale hashes, or non-canonical
  source paths.

## Triage

Run the flat budget gate:

```bash
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json
```

Run the legacy rooted budget gate only when explicitly maintaining
`.skillsets/**` compatibility metadata:

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
```

Inspect:

- `violations`;
- `runtime_entries`;
- `root_description_words_total`;
- manifest provenance violations.

## Fix

If root text is too large, edit
`Infrastructure/templates/root-skill-set/SKILL.md.j2` or
`ROOT_SKILL_SET_METADATA` in
`Infrastructure/scripts/lifecycle-and-sync/skillset_model.py`.

If manifests are stale, regenerate them:

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
```

If first-level latent skills are exposed in the current runtime surface,
refresh the flat projection:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
```

Refresh flat mode explicitly:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
```
