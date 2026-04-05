# Scripts

Read when: you are looking for deterministic helper scripts for the canonical `coding-harness` skill.

This canonical copy primarily relies on the upstream `harness` CLI and the reference docs in `references/`.

Available helper scripts:

- `validate_reference_contracts.py`
  - Purpose: fail fast when skill docs regress to deprecated command references.
  - Checks for banned patterns:
    - legacy `verify-<provider>` command alias
    - legacy `request-<provider>-review` command alias
    - legacy `<Provider> Review` check label
    - `source scripts/codex-preflight.sh && preflight_repo`
  - Checks for required patterns:
    - `verify-coderabbit`
    - `bash scripts/codex-preflight.sh --stack auto --mode required`

Run:

```bash
python3 scripts/validate_reference_contracts.py
```
