# Structured JSON Output

Read when: you need the stable JSON gate schema, safe `jq` patterns, or `health --auto-fix` dry-run extraction rules for `@brainwav/coding-harness`.

All gate commands (`drift-gate`, `docs-gate`, `policy-gate`, `pr-template-gate`, `plan-gate`, `linear-gate`) emit a canonical `GateResult` object when `--json` is passed. This reference preserves the operator-facing schema details outside `SKILL.md`.

## GateResult schema

```json
{
  "gate": "drift-gate",
  "version": "0.8.2",
  "timestamp": "2026-03-24T21:00:00.000Z",
  "status": "fail",
  "findings": [
    {
      "id": "drift-gate.docs.MD041/first-line-heading",
      "severity": "error",
      "gate": "drift-gate",
      "message": "First line must be a top-level heading",
      "baseline": false,
      "fix": {
        "command": "harness drift-gate --seed-baseline",
        "manual": "Add # heading as first line",
        "suppressible": true
      }
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 0,
    "info": 0,
    "total": 1
  }
}
```

## jq patterns for agent consumption

```bash
# Filter error-severity findings from drift-gate
harness drift-gate --json | jq '.findings[] | select(.severity=="error")'

# List all fixable findings (have fix.command) across all gates
harness health --auto-fix --dry-run --json | jq '.findings[] | select(.command != null) | .command'

# Count failing gates during health check
harness health --json | jq '[.gates[] | select(.status == "error")] | length'

# Extract all fix commands for safe automation
harness drift-gate --json | jq -r '.findings[].fix.command // empty'
```

## health --auto-fix usage

```bash
# Dry run: see what would be fixed (no execution)
harness health --auto-fix --dry-run

# Execute safe fixes (excludes: branch-protect, contract, ci-migrate commit)
harness health --auto-fix

# JSON output of AutoFixResult for agent parsing
harness health --auto-fix --dry-run --json | jq '.summary'

# Target specific gates only
harness health --gate drift-gate,plan-gate --auto-fix --dry-run
```

Excluded fix prefixes that require explicit human approval:
- `harness branch-protect`
- `harness contract`
- `harness ci-migrate commit`

Exit codes for `--auto-fix`:
- `0` means all fixes applied or no fixable findings existed.
- `2` means one or more fix commands failed while remaining fixes continued.
