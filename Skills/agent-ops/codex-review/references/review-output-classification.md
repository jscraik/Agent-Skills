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

- line-start `[P0]`, `[P1]`, `[P2]`, or `[P3]` findings
- JSON fields named `findings` or `issues` with entries
- heading-style `Findings`, `Findings: one issue`, `Issues`, or similar output without a clear no-findings value
- any new format that mentions issues/findings without an explicit clean statement

Do not treat inline quoted examples or reviewed documentation text that merely mentions `[P2]` as a finding.
If actionable severity lines and clean prose or clean headings both appear, severity lines win.
A line-start severity line is actionable; inline severity-shaped examples inside otherwise clean prose are not.
Markdown headings such as `## Findings` followed by `None` or equivalent clean values are clean.

## Triage

- Accepted: verified against source and worth fixing.
- Rejected: verified as intentional, speculative, unrealistic, or too costly for the value.
- Blocked: cannot verify because source, dependency docs, environment, auth, or permission authority is missing.

Add a code comment only when rejecting a finding reveals a real invariant or ownership decision that future reviewers need.
