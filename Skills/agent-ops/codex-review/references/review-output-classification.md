# Codex Review Output Classification

## Clean Output

Treat output as clean only when the review command exits 0 and the output clearly has no actionable findings.

Clean indicators include:

- `no findings`
- `no issues`
- `no actionable findings`
- `no accepted/actionable findings`
- `0 findings`
- `0 issues`

## Findings

Treat output as actionable when it includes:

- `[P0]`, `[P1]`, `[P2]`, or `[P3]`
- JSON fields named `findings` or `issues` with entries
- heading-style `Findings:` or `Issues:` without a clear no-findings value
- any new format that mentions issues/findings without an explicit clean statement

## Triage

- Accepted: verified against source and worth fixing.
- Rejected: verified as intentional, speculative, unrealistic, or too costly for the value.
- Blocked: cannot verify because source, dependency docs, environment, auth, or permission authority is missing.

Add a code comment only when rejecting a finding reveals a real invariant or ownership decision that future reviewers need.
