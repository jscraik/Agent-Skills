# Skills SDK Command And Service Rationalization Inventory

Revision: `fc5e330d721db2e15b148a9af1621e032899c5bc`

This is read-only evidence for the later rationalization slice. It does not
authorize command changes, refactoring, moves, deprecation, or deletion.

## Public facade

- Compatibility boundary: `./bin/ask sdk`.
- Registration owners: `Infrastructure/scripts/lib/ask/commands/sdk.py`,
  `sdk_plugin.py`, `sdk_ci.py`, and `sdk_evidence.py`.
- Observed registration calls: 85 `add_parser(...)` occurrences across the SDK
  command modules.
- Characterized surfaces: `./bin/ask sdk --help`, `./bin/ask sdk status
  --json --robot`, and the validation-error envelope exercised by focused
  intake tests.
- Required disposition: `KEEP` until a later compatibility audit maps every
  command, flag, exit code, robot envelope, consumer, and receipt.

## Internal implementation

- Command orchestration: `Infrastructure/scripts/lib/ask/commands/skills_impl.py`.
- Domain and receipt logic: `Infrastructure/scripts/lib/ask/skills_sdk/`.
- External and filesystem adapters: `Infrastructure/scripts/lib/ask/services/`.
- Observed Python modules across domain/service roots: 90.
- Current classification: `unclear ownership` pending per-module audit. This
  classification blocks extraction but does not block the bounded stabilization
  fixes.

## Stabilization findings

| Surface | Finding | Disposition in this slice |
|---|---|---|
| Skill intake | `README.md` was rejected while hardening/install admit it | Align shared package boundary; preserve public command shape |
| Plugin cache projection | Transform retained nested duplicates despite an existing deterministic prune helper | Restore pruning in generated projection and verification transform |
| Capability evidence | 176 refs: 133 local passes, 43 command/external refs classified but not executed | Preserve v0 public receipt; exhaustive replay remains blocked pending a schema-safe implementation slice |

## Claims boundary

This inventory proves the named owners and observed counts at the recorded
revision. It does not prove that any command or module is deadwood, safe to
delete, correctly layered, or ready for repository extraction.
