# PU-004 Ubiquitous Language Review

Status: pass

Reviewed terms: source_kind, risk_tier, sensors, sensor placement, blocking_behavior, receipt_required, placeholder lifecycle, optional adapter detection, and Skills SDK validation layer.

Findings: None requiring changes.

Notes:
- `source_kind` names describe observable skill-source shape rather than implementation guesses.
- `risk_tier` remains contract vocabulary: low, medium, high, privileged, placeholder.
- Sensor metadata says where evidence would be gathered and whether a receipt is required. It does not claim the scanner, sandbox, or external adapter has run.
- Placeholder classifications stay honest by using skip or optional behavior instead of pass language.
