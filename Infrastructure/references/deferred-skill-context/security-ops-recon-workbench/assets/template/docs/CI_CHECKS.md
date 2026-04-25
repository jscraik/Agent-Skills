# CI checks (suggested)

## Minimal
- Run schema validation for any generated JSON (plan, findings, manifest).
- Run doctor in JSON mode and store output as an artifact.

## Example commands
- Infrastructure/scripts/ci_check.sh
- Infrastructure/scripts/doctor.sh --json > runs/_ci/doctor.json
- python3 Infrastructure/scripts/validate_schema.py --schema schemas/findings.schema.json --data runs/_ci/findings.json
- python3 Infrastructure/scripts/validate_schema.py --schema schemas/manifest.schema.json --data runs/_ci/manifest.json
