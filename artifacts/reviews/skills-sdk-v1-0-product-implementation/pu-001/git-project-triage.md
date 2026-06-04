# PU-001 Git Project Triage

schema_version: 1
status: ready_for_local_packaging
mode: coordinator_run
date: 2026-06-04
branch: codex/skills-sdk-v1-0-pu-001-setup
base_head: c3ff670f3 feat(skills-sdk): add agent-first scaffold gate (#221)

## Scope

PU-001 is setup/governance packaging for the Skills SDK V1.0 product implementation goal. It does not implement runtime SDK product behavior.

## Included Dirty Surface

- .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
- .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
- .harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html
- .harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.mdx
- docs/goals/skills-sdk-v1-0-product-implementation/**
- artifacts/reviews/skills-sdk-v1-0-product-implementation-plan/review-loop-summary.md
- artifacts/reviews/skills-sdk-v1-0-product-implementation/pu-001/**
- Infrastructure/GOVERNANCE/runtime-separation/current.json

## Excluded Surface

- artifacts/reviews/skills-sdk-v1-0-product-implementation/pu-001/codex-review.raw.txt: excluded as raw runtime transcript noise and not part of PR evidence.
- artifacts/reviews/default.md: excluded after canonicalizing the adversarial fallback report under the PU-001 path.
- artifacts/agent-runs/default-019e926e-4eed-7bc1-a39a-8f06d1a77c72/manifest.json: excluded final-response probe metadata.
- artifacts/agent-runs/default-019e9270-af68-7892-a1f4-8bc9106081af/manifest.json: canonicalized into artifacts/reviews/skills-sdk-v1-0-product-implementation/pu-001/adversarial-reviewer-fallback-manifest.json.
- goal-governor-output.yaml: excluded as stale setup output that still reported auto_continue_allowed before later blocked/waiver evidence.

## Generated Validation Output

`./bin/ask repo validate --json --robot` regenerated `Infrastructure/GOVERNANCE/runtime-separation/current.json` evidence hashes. The diff is validation-output churn only; no runtime-separation policy fields or parity decisions were intentionally changed by PU-001.

## Review And Waiver Truth

- simplify, improve-codebase-architecture, codex-review, testing, and ubiquitous-language artifacts are present.
- adversarial-reviewer.md is present as a coordinator-preserved fallback artifact with runtime-substitution labels.
- agent-native-reviewer.md is present as an explicit owner-waiver artifact, not a completed subagent review.
- Jamie waived the missing subagent review lane for PU-001 with: "ok don't use the subagent review then continue".

## Local Validation

- python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/skills-sdk-v1-0-product-implementation -> pass
- git diff --check -> pass
- python3 -m json.tool artifacts/reviews/skills-sdk-v1-0-product-implementation/pu-001/adversarial-reviewer-fallback-manifest.json -> pass
- bash scripts/validate-codestyle.sh -> pass
- ./bin/ask repo validate --json --robot -> pass
- test -f memory.json && jq -e '.meta.version == "1.0" and (.preamble.bootstrap | type == "boolean") and (.preamble.search | type == "boolean") and (.entries | type == "array")' memory.json >/dev/null -> pass

## Delivery Gates Still Required

- Stage only included dirty surface.
- Commit PU-001 setup artifacts.
- Push codex/skills-sdk-v1-0-pu-001-setup.
- Open or update PR with explicit waiver and substitution language.
- Run PR green-sweep against live GitHub truth.
- Do not continue to PU-002 until PU-001 merges and main is pulled back.

WROTE: artifacts/reviews/skills-sdk-v1-0-product-implementation/pu-001/git-project-triage.md
