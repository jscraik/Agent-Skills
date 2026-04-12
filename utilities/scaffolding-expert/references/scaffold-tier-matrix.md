# Scaffold Tier Matrix

Use this matrix to classify repository scaffolding depth.

## Scoring dimensions

Score each dimension from `0` (low) to `3` (high):

1. Blast radius of failure
2. Compliance/audit pressure
3. Number of runtime surfaces (CLI, service, SDK, automation)
4. Team size and contributor churn
5. Release frequency and change velocity
6. Toolchain complexity (single stack vs polyglot)
7. Operator maintenance capacity for governance controls

Total score = sum of all dimensions.

## Tier thresholds

- `lite`: `0-8`
- `growth`: `9-15`
- `strict`: `16-21`

When uncertain between tiers, choose the lower tier unless there is explicit compliance or safety pressure.

## Tier expectations

## Lite
- one clear entrypoint (`README`, minimal run/test contract)
- minimal scripts, minimal policy surface
- no duplicate ownership files

## Growth
- explicit ownership boundaries and documented command contract
- baseline environment contract (for example `.codex/environments/environment.toml`)
- stable validation wrapper(s) and CI checks

## Strict
- layered validation (`preflight` + `fast verify` + broader gates)
- explicit check-name parity/contract policy
- canonical source with projection strategy and drift detectors
- governance docs mapped to executable validation scripts

## Escalation rules

Escalate from `lite` to `growth` when:
- multiple teams contribute regularly; or
- repeated workflow drift causes delivery friction.

Escalate from `growth` to `strict` when:
- compliance/audit evidence is mandatory; or
- multi-surface release coordination failures recur.

De-escalate when controls exist but are consistently bypassed or unmaintained.
