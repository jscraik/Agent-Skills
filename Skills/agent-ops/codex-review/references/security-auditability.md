# Security Suppression Auditability

Use this when Codex review suggests changing security-audit suppressions or filtering logic.

## Required Properties

- Suppressed findings remain present in structured output.
- Active output includes an unsuppressible notice that suppression occurred.
- Aggregate summaries cannot hide unrelated active risk.
- A suppression for one finding cannot mask a different finding.
- Final reports distinguish accepted, suppressed, active, rejected, and blocked findings.

## Review Questions

- Can a reader still audit which findings were suppressed?
- Can active risk still fail the gate?
- Does the suppression key match only the intended finding?
- Are counts and summaries consistent with detailed output?
- Is there a deterministic test or fixture for the suppression behavior?
