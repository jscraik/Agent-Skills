# CI checks (suggested)

Summary from `docs/reference/CI_CHECKS.md`.

## Minimal
- Validate schemas for generated JSON (plan, findings, manifest).
- Run doctor + setup in JSON mode and store artifacts.
- Run CLI smoke checks to validate probe wiring.
- Optional: simulator smoke when runners support Simulator runtimes.

## Example commands
- `Infrastructure/scripts/ci_check.sh`
- `Infrastructure/scripts/doctor.sh --json > runs/_ci/doctor.json`
- `python3 Infrastructure/scripts/recon_cli.py setup --json > runs/_ci/setup.json`
- `python3 Infrastructure/scripts/validate_schema.py --schema Infrastructure/config/schemas/findings.schema.json --data runs/_ci/findings.json`
- `python3 Infrastructure/scripts/validate_schema.py --schema Infrastructure/config/schemas/manifest.schema.json --data runs/_ci/manifest.json`

## Python environment note
Schema validation depends on `jsonschema`; CI prefers `./.venv/bin/python` when present.
