# CI checks (suggested)

Summary from `docs/reference/CI_CHECKS.md`.

## Minimal
- Validate schemas for generated JSON (plan, findings, manifest).
- Run doctor + setup in JSON mode and store artifacts.
- Run CLI smoke checks to validate probe wiring.
- Optional: simulator smoke when runners support Simulator runtimes.

## Example commands
- `scripts/ci_check.sh`
- `scripts/doctor.sh --json > runs/_ci/doctor.json`
- `python3 scripts/recon_cli.py setup --json > runs/_ci/setup.json`
- `python3 scripts/validate_schema.py --schema config/schemas/findings.schema.json --data runs/_ci/findings.json`
- `python3 scripts/validate_schema.py --schema config/schemas/manifest.schema.json --data runs/_ci/manifest.json`

## Python environment note
Schema validation depends on `jsonschema`; CI prefers `./.venv/bin/python` when present.
