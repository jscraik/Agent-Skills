# PU-008 Final Validation Ledger

## Scope

PU-008 is the final validation, docs accuracy, and delivery sweep for JSC-364. This ledger records current evidence without converting blocked runtime proof, stale PR events, or broad projection drift into success claims.

## Placement

- Runtime proof artifacts: `.harness/evidence/runtime-proof/<handle>/codex/`.
- PU-008 reviewer artifacts: `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/`.
- PR 206 green-sweep artifact: `artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/pr-green-sweep-pr206.md`.
- Governed board and receipts: `Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/`.
- Browser ledger: `.harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html`.

## Local Validation

| Command | Outcome | Evidence |
|---|---|---|
| `./bin/ask skills handles --check --check-command-handles --no-handles --json --robot` | pass | 105 command handles checked; no violations. |
| `./bin/ask repo doctor --json --robot` | pass_with_warning | Repo doctor returned non-blocking `repo_surface` warnings for historical/generated/unknown surfaces. |
| `./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/jsc-364-codex-parity-pu008 --json --robot` | pass | 12 fixture cases passed; modeled/live runtime split remains explicit. |
| `python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation` | pass | Runtime separation fixture contract passed. |
| `python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q` | pass | 30 passed. |
| `./bin/ask skills proof testing --runtime-target codex --json --robot` | blocked_expected | Exit 2 by design; wrote schema-valid blocked runtime evidence for `testing/codex`. |
| `python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py .harness/evidence/runtime-proof --json` | pass | Runtime-card validator passed over generated evidence. |
| `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q` | pass | 17 passed, 15 subtests passed. |
| `python3 -m pytest Infrastructure/tests/test_ask_cli_impl.py -q` | pass | 209 passed, 4 subtests passed. |
| `./bin/ask repo closeout --changed --json --robot` | pass | Closeout exposes changed runtime evidence and truth boundaries. |
| `bash scripts/validate-codestyle.sh` | fail_pre_existing_projection_drift | Broad PR-template gate fails on projection-integrity drift in `cache-harness-engineering` and `cache-skill-factory`; this remains outside PU-008 scope. |
| `./bin/ask repo validate --json --robot` | fail_pre_existing_projection_drift | Broad repo validate fails on the same projection-integrity drift and blocks downstream validation lanes. |
| `test -f memory.json && jq -e '.meta.version == "1.0" and (.preamble.bootstrap | type == "boolean") and (.preamble.search | type == "boolean") and (.entries | type == "array")' memory.json >/dev/null` | pass | Memory contract check passes. |
| `./bin/ask skills capabilities --runtime-target codex --json --robot` | pass | PU-008 added the public capability-discovery command; it emits `capability-discovery.v1` with runtime truth boundaries and no live-parity claim. |
| `./bin/ask skills capabilities --runtime-target any --json --robot` | pass | Discovery-only output routes runtime proof to explicit `codex` and `agents` targets; it does not claim `any` artifacts. |
| `./bin/ask skills capabilities --runtime-target agents --json --robot` | pass | Agents output carries source blockers and keeps live runtime parity at `not_claimed`. |
| `./bin/ask skills capabilities --runtime-target codex` | pass | Human output renders target, status, live-runtime boundary, blocked fidelity checks, and next command. |
| `python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py .harness/evidence/runtime-proof --require-shared-workspace --json` | pass | Shared-workspace runtime-card validation passed over context7, testing, and autofix evidence. |

## Runtime Evidence

| Path | Runtime status | Interpretation |
|---|---|---|
| `.harness/evidence/runtime-proof/context7/codex/runtime-card.json` | `blocked_runtime` | Schema-valid proof of runtime absence / manual session gate, not live runtime success. |
| `.harness/evidence/runtime-proof/testing/codex/runtime-card.json` | `blocked_runtime` | Schema-valid proof of runtime absence / manual session gate, not live runtime success. |
| `.harness/evidence/runtime-proof/autofix/codex/runtime-card.json` | `blocked_runtime` | Schema-valid proof of runtime absence / manual session gate, not live runtime success. |

## Review Artifacts

| Reviewer | Artifact | Status |
|---|---|---|
| Architecture strategist | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/architecture-strategist.md` | present; recommends proceeding after live delivery truth recheck. |
| Agent-native reviewer | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/agent-native-reviewer.md` | present; PASS, no blocking agent gaps in PU-008 scope. |
| Adversarial reviewer | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/adversarial-reviewer.md` | present; warns against stale PR/check truth and blocked_runtime false-success claims. |
| Architecture post-fix reviewer | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/architecture-capabilities-postfix-reviewer.md` | present; no material architectural findings after runtime-target constants were centralized. |
| Agent-native post-fix reviewer | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/agent-native-capabilities-postfix-reviewer.md` | present; warning about brittle human-output assertion fixed by loosening the test to the stable output prefix. |
| Adversarial post-fix reviewer | `artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/adversarial-capabilities-postfix-reviewer.md` | present; no material false-success findings after explicit runtime targets, source blockers, human boundaries, and fresh verification timestamp were added. |

## GitHub / Delivery Truth

- PR 206: https://github.com/jscraik/Agent-Skills/pull/206.
- Head/base: `codex/jsc-364-runtime-proof-plane-pu007` onto `codex/jsc-364-runtime-proof-plane-pu006`.
- Head SHA after synchronize refresh: `c3308116ad7a49e6cb91add4afacc32578f767a2`.
- Draft: true.
- Merge state at refresh: `UNSTABLE`.
- Current PR body has explicit `**(Pending)**` status markers on unchecked template items.
- Stale blocker resolved: a fresh empty Git API commit triggered a new `pull_request` synchronize event, and `pr-template` passed on run `26396477047`.
- Visible checks at refresh were successful: Harness PR Pipeline jobs, CircleCI, Semgrep, Trivy, Socket, Snyk, docs, skill diagnostics, security scans, and CodeRabbit status.

## Blockers / Residual Risks

1. Broad local gates remain blocked by projection-integrity drift in `cache-harness-engineering` and `cache-skill-factory`; this predates PU-008 and is not evidence of proof-plane code failure.
2. The former `skills capabilities` plan-gate drift is resolved in PU-008 by adding the public command and focused CLI coverage.
3. Runtime-card artifacts with `runtime_status=blocked_runtime` prove durable blocked evidence only. They must not be summarized as live Codex runtime parity success.
4. PR 206 is green but still draft/stacked; this is delivery readiness evidence, not merge or cleanup authority.

## Recommendation

Keep PU-008 open until the stacked PR truth, docs accuracy check, and final board receipt are current. PR 206 no longer has a template-check blocker after the synchronize refresh, and the planned capability-discovery gate is now reachable, but PR 206 remains draft/stacked and should not be treated as merged or cleanup-ready.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/final-validation-ledger.md
