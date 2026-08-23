# PR #345 Candidate `db50255` Independent QA Disproof

schema_version: qa-proof/v1
status: rejected
agent_id: 019f753b-4f48-7c30-858b-1831cdd94631
candidate: db50255eb80917362b9a8d60e3fcc72b70ba041b
candidate_worktree: /private/tmp/agent-skills-jsc389-approved-auth-stream

## Scope

Independent, immutable-commit review of PR #345 candidate `db50255eb80917362b9a8d60e3fcc72b70ba041b`. I inspected only its parent/diff and relevant runtime/schema contracts. I did not edit, stage, commit, push, create or update a PR, mutate hosted reviews, or run a provider-backed eval or judge.

## Verdict

Reject the candidate as a complete closeout of the six findings. Four contract repairs are substantiated locally, but two high-impact defects remain:

1. **P1 — the claimed approved cloud-auth path is still only shape-checked.** `is_opaque_env_reference` accepts any FIFO whose trailing components are `.codex/.env`; it does not require that the path equals `Path.home() / ".codex" / ".env"` or another explicit allowlisted operator reference. Because `_approved_cloud_auth_fact` takes `SKILLS_SDK_OSS_CLOUD_ENV_FILE` directly and `_cloud_catalog_fact` repeats the same predicate, an arbitrary temporary `.../.codex/.env` FIFO is admitted and reaches the catalog-runner boundary. The parent commit `5a55b745` introduced the weaker basename/parent predicate; `db50255` does not modify it.

2. **P1 — the typed receipt reader still accepts an unordered completed A/B receipt.** The candidate makes the JSON Schema require `command_variant_labels == ["A", "B"]` and ordered top-level `variant_results`, but `validate_ab_run_receipt` delegates to `AbRunReceipt`, whose completed validators use set equality / `exact_variant_labels`. An otherwise valid receipt with labels `["B", "A"]` and both runtime gates/results reversed is accepted by the typed reader, while the authoritative JSON Schema rejects it. This contradicts the candidate's stated ordered-A/B receipt contract and leaves a public reader bypass.

## Six-Finding Matrix

| Hosted finding | Independent result | Evidence |
| --- | --- | --- |
| Cloud approved opaque env path (parent P1) | **Not disproved; persists.** | Arbitrary temporary `.../.codex/.env` FIFO produced `auth=pass` and `catalog=pass` through a fake non-provider runner. |
| Blocked receipts require top-level blockers | **Disproved.** | The v1 JSON Schema has a root-required `blockers` field and a `status=blocked` `minItems: 1` conditional; focused schema test passes. |
| Completed receipt proves side effects | **Disproved.** | Both schema and `validate_run_receipt_status` require mutation, provider, network, and Codex-exec side-effect flags for `completed`; focused schema test passes. |
| Judge schema accepts versioned `ex_` identifiers | **Disproved.** | Both judge schemas accept `^(?:ex_[a-z0-9]{16}|[0-9a-f]{16})$`; focused test passes. |
| `--output-last-message` binds to receipt path | **Disproved.** | Candidate's guard requires exactly one flag and an adjacent matching value; focused test rejects forged/multiple path cases. |
| Exact ordered A/B labels | **Partially fixed; not disproved overall.** | JSON Schema rejects reversed A/B order, but the typed reader accepts the same reversed completed receipt. |

## Scope And Churn

`db50255` changes seven files only: the two judge schemas, the v1 run schema, two Skills SDK contract modules, and two focused tests. The diff is coherent with the named receipt-contract work and has no whitespace errors. I found no unrelated churn.

## Exact Evidence

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream status --short --branch` -> pass (candidate checkout was clean on `codex/jsc-389-approved-auth-stream`, ahead of `origin/main` by two commits)

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream rev-parse HEAD` -> pass (`db50255eb80917362b9a8d60e3fcc72b70ba041b`)

Command: `git -C /private/tmp/agent-skills-jsc389-approved-auth-stream diff --no-ext-diff --check db50255eb80917362b9a8d60e3fcc72b70ba041b^ db50255eb80917362b9a8d60e3fcc72b70ba041b` -> pass (no whitespace errors)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_skills_sdk_auth_stream_identity.py tests/test_skills_sdk_ab_argv_binding.py tests/test_skills_sdk_schema_spine.py tests/test_skills_sdk_ab_run.py tests/test_skills_sdk_ab_judge.py tests/test_skills_sdk_ab_judge_score.py` -> pass (202 passed, 89 subtests passed)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh - <<'PY' ... validate_ab_run_receipt(reversed_completed_receipt); schema_validation.validate_payload_against_schema(reversed_completed_receipt, ...) ... PY` -> pass (typed reader accepted the reversed completed receipt; JSON Schema returned `fail`)

Command: `XDG_CACHE_HOME=/private/tmp/codex-xdg-cache XDG_STATE_HOME=/private/tmp/codex-xdg-state PYTHONDONTWRITEBYTECODE=1 bash Infrastructure/scripts/run-infrastructure-python.sh - <<'PY' ... create arbitrary temporary .codex/.env FIFO; _approved_cloud_auth_fact(...); _cloud_catalog_fact(..., fake_runner) ... PY` -> pass (`arbitrary_dot_codex_fifo_auth=pass`; `arbitrary_dot_codex_fifo_catalog=pass`; no provider or judge invoked)

## Limitations

This is local deterministic contract evidence only. It does not prove hosted review-thread state, current CI, mergeability, provider availability, cloud credential validity, actual Codex execution, a provider-backed eval/judge result, or release readiness.

WROTE: artifacts/reviews/default.md

manifest_path: artifacts/agent-runs/default-20260815T233420Z/manifest.json

## Scenario-quality baseline comparison — PR Green Sweep

### Verdict

The current working-tree preview reports 39 scenarios, 7 promotion-ready, and
32 blocked. The same command against an archive of `origin/main` reports the
same 39 / 7 / 32 totals. Therefore all 32 blocked rows are pre-existing on
`origin/main`; this diff introduces no additional blocked scenario.

Thirty-one blocked IDs are identical between baseline and current. The only
ID change is a rename from
`eval.pr-green-sweep.waived-external-ci-does-not-stop-rotation` to
`eval.pr-green-sweep.blocked-external-ci-does-not-hide-independent-work`.
The renamed row remains `blocked_quality_gate` in both versions' equivalent
case, so the rename did not introduce the blocked state.

### Exact renamed-case evidence

Baseline (`origin/main`, `Skills/agent-ops/pr-green-sweep/references/evals.yaml:1021-1052`):

- `promotion_status: blocked_quality_gate`.
- Blockers: `safety_boundary_present`, `release_case_metadata_present`,
  `release_rubric_evidence_anchored`, `release_rubric_regex_not_primary`,
  `release_rubric_semantic_coverage`, `release_rubric_failure_guard`,
  `platform_tessl_quality:skill_name_primary_proof`, and
  `platform_tessl_quality:missing_concrete_output_artifact`.
- The fixture is the tracked
  `eval.pr-green-sweep.waived-external-ci-does-not-stop-rotation.md`.

Current (`Skills/agent-ops/pr-green-sweep/references/evals.yaml:1021-1052`):

- `promotion_status: blocked_quality_gate`.
- Blockers: the same quality families except
  `release_rubric_failure_guard` (seven blockers total).
- The fixture is the new
  `eval.pr-green-sweep.blocked-external-ci-does-not-hide-independent-work.md`.

The current fixture explicitly names `blocked_external_ci`, keeps merge
blocked, and requires independent action lanes (fixture lines 16-24); this is
a semantic rename/contract update, not a newly introduced blocked scenario.

### Validation evidence

Command: `./bin/ask sdk eval scenario-quality Skills/agent-ops/pr-green-sweep --preview --json --robot` (current checkout) -> blocked (exit 2; receipt status `blocked`; scenario_count `39`, promotion_ready_count `7`, blocked_count `32`; preview performed no mutation)

Command: `./bin/ask sdk eval scenario-quality Skills/agent-ops/pr-green-sweep --preview --json --robot` (safe `git archive origin/main` temporary copy) -> blocked (exit 2; receipt status `blocked`; scenario_count `39`, promotion_ready_count `7`, blocked_count `32`; preview performed no mutation)

Command: Python comparison of the two JSON receipts -> pass (38 common IDs have identical promotion status and non-pass check signatures; 31 common blocked IDs, plus one baseline-only renamed ID and one current-only renamed ID)

### Boundary

The comparison is read-only with respect to the supplied
`/private/tmp/agent-skills-active-waiver-owner-retirement` checkout: no files,
worktrees, branches, pushes, or Git state were mutated there. The temporary
archive was used only to run the baseline command.

WROTE: artifacts/reviews/default.md

---

---

# Skills SDK Tightening Adversarial Review

schema_version: adversarial-review/v1
status: changes_requested
agent_id: 019fc818-3dfd-77a0-94fd-d1875a05ee2a
candidate: working tree at 4ced957e3; proposal review only
base: origin/main observed two commits ahead; no refresh performed

## Verdict

Adopt transitive package-local reachability and distinct A/B candidate identity in the existing SDK owners. Do not represent exemplar quality, routing correctness, or judge-rationale quality as deterministic keyword/metadata checks. Those require semantic fixtures or executed evidence. Keep live A/B proof promotion-scoped; making it mandatory for routine corrections violates the repository's thin-surface and correction boundaries.

## Smallest disproof matrix

| Surface | Deterministic gate | Semantic gate | Live gate |
| --- | --- | --- | --- |
| Reference closure | Traverse package-local references from declared roots; pass a two-hop chain and cycle; block unreachable, missing, traversal, and symlink-escape targets. | None. Reachability is structural; whether the reference is useful is separate. | None. |
| Progressive disclosure | Permit multi-hop conditional references; verify compact entrypoint, safe roots, and no unreachable support file. | Given representative tasks, verify the right branch loads the right reference without loading unrelated branches. | Optional runtime trace only when claiming installed behavior. |
| Exemplar | Require a package-local, digest-bound exemplar identity and provenance when declared. | Reject rubric-copying, answer leakage, wrong-domain exemplars, and polished but behaviorally wrong exemplars through paired held-out cases. | A/B only when claiming the exemplar improves outcomes. |
| Routing | Exact handle, stable ordering, candidate-set identity, and replayable result are deterministic. | Labelled paraphrase, lexical-collision, negation, ambiguity, and multi-intent fixtures establish routing correctness; expected target is human-curated semantic truth. | Runtime picker/invocation only for activation claims. |
| Judge rationale | Schema, artifact path, sample count, decision ids, scorer/prompt/model digests, and score arithmetic are deterministic. | Review sampled rationales for evidence grounding, rubric copying, verbosity bias, and contradictions with scores. | Required when claiming actual judge calibration; metadata alone is not execution. |
| A/B | Reject identical A/B package digests; bind immutable package, fixture, rubric, profile, command, and output digests; preserve exact case ids and lane separation. | Blind paired judging plus held-out scenario coverage; inconclusive remains valid. | Actual OSS-local/OSS-cloud execution is required for comparative outcome claims; external Tessl remains a separate promotion lane. |

## Existing owners

- Closure, reference quality, construction, and progressive disclosure: `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`; tests in `Infrastructure/tests/test_ask_skills_package_contract.py` and CLI integration in `Infrastructure/tests/test_ask_skills_package.py`.
- Routing algorithm and semantic fixture set: `Plugins/skill-factory/scripts/skill-builder/skill_router.py`, `Plugins/skill-factory/scripts/skill-builder/test_skill_router.py`, and `Plugins/skill-factory/scripts/skill-builder/test_skill_router_fixtures.json`; public command integration in `Infrastructure/tests/test_ask_skills_route.py` and `Infrastructure/tests/test_ask_skills_goal.py`.
- Semantic acceptance anti-keyword guard: `Infrastructure/scripts/lib/ask/skills_sdk/release_rubric_checks.py` and its existing release-rubric test owner.
- Rationale metadata: `Infrastructure/scripts/lib/ask/skills_sdk/scorer_quality.py`; tests in `Infrastructure/tests/test_skills_sdk_scorer_quality.py`.
- A/B identity, preview, plan, run, and judging: `Infrastructure/scripts/lib/ask/skills_sdk/ab_contracts.py`, `eval_ab_preview.py`, `eval_ab_plan.py`, `eval_ab_run.py`, and `eval_ab_judge.py`; tests in `Infrastructure/tests/test_skills_sdk_ab_preview.py`, `test_skills_sdk_ab_plan.py`, `test_skills_sdk_ab_run.py`, `test_skills_sdk_ab_run_profile_guards.py`, `test_skills_sdk_ab_judge.py`, `test_skills_sdk_ab_judge_semantic_evidence.py`, and `test_skills_sdk_ab_judge_score.py`.

## Critical negative fixtures

1. `SKILL.md -> a.md -> b.md` passes; `b.md -> a.md` cycle terminates; unreferenced `c.md` blocks.
2. A basename mention in prose does not establish an edge; `../`, absolute, backslash, and symlink targets block.
3. An exemplar that repeats acceptance wording, leaks the answer, or is from a mismatched domain loses to a shorter correct control.
4. Routing rejects shared-word collisions, negated skill names, vague requests, and multi-intent prompts instead of manufacturing a confident winner.
5. `rationale_audit.required: true` plus `sampled_count: 3` without three digest-bound decision/rationale artifacts blocks.
6. A/B preview blocks when A and B package digests are equal; a completed run with missing semantic output or mismatched fixture/rubric/profile identity blocks.

## Contract and mantra conflicts

- Requiring every support file to be linked directly from `SKILL.md` breaks progressive disclosure; require reachability from declared roots, including valid multi-hop routes.
- Treating reference usefulness, exemplar quality, routing correctness, or rationale quality as keyword presence creates false greens and conflicts with Professional Output.
- Exposing all of these internals as new default CLI steps breaks Thin Surface; strengthen existing package, scorer, router, and A/B owners.
- Requiring live A/B or external Tessl for routine local corrections violates the project-specific correction boundary. Reserve it for selected behavioral proof/promotion claims.
- Closure supports Strong Guardrails and Durable Memory only when unreachable material blocks without forcing every conditional reference into always-loaded context.

## Claims boundary

This is static source and contract review of the local candidate. No source patch, paid/provider/Tessl eval, hosted CI/review check, runtime activation, or release/promotion action was performed. One attempted direct A/B probe was blocked before execution by `ModuleNotFoundError: No module named 'ask'`; the identical-digest gap is therefore source-backed, not runtime-proved.

WROTE: artifacts/reviews/default.md

---

# Mantra and CODESTYLE alignment audit: Skills SDK tightening

Reviewer: default `019fc813-b2da-7352-a4d1-907f81438449`

Candidate: current dirty checkout on `main` at audit time, with the proposed
`Skills/agent-ops/testing/**` consolidation and adjacent documentation changes.

Verdict: directionally aligned, corrections required before acceptance.

## Findings

1. **Required: remove or repair the stale post-deletion route at
   `Skills/agent-ops/testing/SKILL.md:197-199`.** The proposal deletes
   `Skills/agent-ops/testing/references/evals/**`, but the entrypoint still tells
   the agent to treat “references/evals notes” as evidence. That is no longer a
   resolvable package path and forces the agent to guess. Name only
   `references/evals.yaml`, or explicitly route Skills SDK fixture work to the
   owning `evals-router` / `sdk-scenario-generator` package. This conflicts with
   `docs/reference/skills-sdk-skill-construction-contract.md:52-57`, which
   requires support files to be reachable through an entrypoint, and with
   `AGENTS.md:53-57`, which forbids guessed or stale identifiers.

2. **Required: fix the malformed continuation at
   `Docs/agents/25-sdk-runtime-lane-contract.md:309-313`.** The edited
   `--tessl-workspace` line lost its list-item indentation. This is pure
   presentation damage in a command contract and should be restored or the edit
   dropped. It contributes no tightening and makes the canonical command harder
   for an agent to copy reliably.

3. **Required: make the condensed capsule provenance truthful at
   `Skills/agent-ops/testing/references/evals-production-guardrails.md:3-9` and
   `Skills/agent-ops/testing/references/source-context.yaml:90-101`.** The body
   was manually collapsed from claim cards into synthesized “Core Guidance,”
   while the metadata still calls it a generated, vendored KnowledgeOS
   extraction. Either regenerate the capsule from its owning source with a
   current digest, or reclassify it as a package-maintained distillation and
   retain exact source/digest pointers. The current shape weakens the claim-to-
   source boundary even though the prose itself is sensible. This violates the
   evidence-first posture in `CODESTYLE.md:72-79` and the rule that structured
   evidence, rather than summaries, carries claims in
   `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md:22-35,86-90`.

4. **Required before deletion acceptance: prove ownership and reachability for
   every removed Skills SDK / KnowledgeOS asset.** The consolidation is correct
   only if each deleted testing-owned reference and eval fixture is either an
   exact duplicate in `Skills/agent-ops/evals-router/**` or
   `Skills/agent-ops/sdk-scenario-generator/**`, or is intentionally retired
   with no remaining inbound pointer. The proof should mechanically fail on a
   missing target or a surviving pointer into the deleted tree. This follows
   the single-source/pruning contract at
   `docs/reference/skills-sdk-skill-construction-contract.md:87-106` without
   sacrificing its reachability requirement at lines 52-57.

5. **Should correct: move generic textbook test-layer prose out of the always-
   loaded entrypoint unless an eval proves it changes behavior.** The useful new
   contract is `Skills/agent-ops/testing/SKILL.md:125-129` (inventory gates as
   present/missing/not_applicable/unverified) plus lines 152-156 (do not invent a
   gate when the repository evidence is unavailable). Keep those. The layer
   table and generic gate descriptions at lines 102-123 are branch-specific
   reference material; move them behind a routed reference or delete any line
   that does not beat model default behavior. This is the direct “every line
   earns its place” test in
   `docs/reference/skills-sdk-skill-construction-contract.md:58-61,94-106` and
   the focused-entrypoint rule in `Skills/AGENTS.md:19-21`.

6. **Should delete: unrelated whitespace-only README churn.**
   `README.md:70-76` changes table spacing without changing the user contract.
   It adds review noise and should not travel with the Skills SDK tightening
   unless a repository formatter required it and that command is recorded.

## Keep, delete, internalize

- **Keep:** the narrower testing description and explicit gate-audit trigger at
  `Skills/agent-ops/testing/SKILL.md:2-3,23-28`; evidence-lane separation at
  lines 65-70 and 81-94; human authority for subjective judgment in
  `Skills/agent-ops/testing/references/evals-production-guardrails.md:9`; and
  the `unverified` stop rule at `Skills/agent-ops/testing/SKILL.md:125-129,
  150-156`.
- **Delete:** duplicated Skills SDK and KnowledgeOS capsules from the generic
  testing package after the mechanical reachability/identity proof passes;
  stale pointers to deleted paths; the malformed docs edit; and formatting-only
  churn.
- **Internalize behind a route:** broad test-layer taxonomy and gate-placement
  explanation that is not needed on every testing invocation. Preserve the
  decision rule and status vocabulary in `SKILL.md`; put detail in one nearby
  reference.

## Product-boundary conclusion

Removing Skills SDK-specific research from the generic `testing` skill is
consistent with `UBIQUITOUS_LANGUAGE.md:13-20`: the Agent Skills Kit is the
foundry/control plane, while Skills SDK is the professional lifecycle contract,
and the default product surface should stay thin. It is also consistent with
`AGENTS.md:30-40,68-74`, which requires the smallest existing mechanism and
compact evidence pointers rather than duplicated technical plans. The proposal
must still preserve the canonical ten-stage evidence boundaries in
`UBIQUITOUS_LANGUAGE.md:27-41`; deletion is not proof that the owning router can
still reach the material.

## Measurable acceptance criteria

1. Every path named by `Skills/agent-ops/testing/SKILL.md`, its
   `knowledge-capsule-routing.md`, `source-context.yaml`, and manifest exists;
   zero pointers resolve beneath the deleted `references/evals/**` tree.
2. Every deleted Skills SDK / KnowledgeOS reference is classified as exact
   duplicate-at-owner or intentionally retired; zero unique claim IDs and zero
   active eval IDs disappear without an explicit retirement record.
3. The testing entrypoint contains no branch-specific paragraph that lacks an
   action, route, completion criterion, evidence obligation, or safety
   obligation, per the construction contract.
4. The production-guardrails reference has provenance matching its actual
   generation mode and an auditable source digest or source pointer for every
   retained claim group.
5. Focused package verification and strict skill audit pass for `testing`, and
   at least one routing eval proves ordinary repository-test intent selects
   `testing` while LLM-eval / Skills SDK scenario intent routes to the owning
   specialized skill.
6. Evidence reports local package/audit/routing proof only; Tessl, runtime,
   hosted CI, review, publication, and release remain unclaimed unless each is
   separately run.

## Claims boundary

This was a read-only source and diff audit. No package verifier, strict skill
audit, routing eval, runtime projection, Tessl run, hosted CI, or review state
was executed by this reviewer. The conclusions establish contract alignment
and identified correction requirements; they do not establish readiness.

WROTE: artifacts/reviews/default.md

---

# Reference-closure audit

Reviewer: `019fc813-7de0-7372-ba55-12e90c0ce205`
Candidate: `4ced957e36ea6ebe4c65d8754db5328d3879fefb` on a dirty, owner-shared `main` checkout (`origin/main` behind by two commits)
Verdict: tightening should cover all reachable `references/`, `scripts/`, `assets/`, `examples/`, and evaluator inputs, but current enforcement is partial and shallow.

## Findings

1. High: `_orphaned_support_files` recursively inventories `references`, `scripts`, `assets`, `agents`, and `workflows`, but decides routing by substring search over only SKILL.md plus seven fixed metadata surfaces. It does not traverse `A -> B -> C` reference edges. A support file reachable only through an ordinary routed reference remains orphaned; conversely any basename occurrence can make an unrelated file appear routed.
2. High: orphan closure is normally advisory. It becomes a package-readiness blocker only for knowledge-capsule files and two provenance files, and only when `references/knowledge-capsule.manifest.yaml` exists. Scripts and assets can therefore be packaged and hashed while still being unreachable without blocking readiness.
3. High: top-level `examples/` is absent from SkillIR source enumeration and from orphan-support roots. Examples nested under `references/` are included as references, but a canonical `examples/` tree is invisible to package digest, security signature, and closure checks.
4. Medium: `references/evals/**` is considered implicitly routed whenever `references/evals.yaml` exists, and `references/scorer-calibration/**` whenever its manifest exists. The closure check does not parse those declarations to prove each child is actually named. Scorer calibration later performs stronger manifest-relative path and example/raw-artifact checks, but that semantic check is separate from general package closure.
5. Medium: evaluator inputs are split. Package readiness recognizes three eval declaration locations; scenario alignment only validates `references/evals.yaml`; deterministic eval accepts an arbitrary repo-relative or absolute dataset; scorer calibration uses a separate manifest graph. No single check binds every consumed evaluator input into the package digest and reachability graph.

## Recommended deterministic and semantic checks

- Build one normalized package dependency graph rooted at `SKILL.md`, `agents/openai.yaml`, declared workflow/contract manifests, and evaluator entry manifests. Parse exact package-local paths; reject absolute paths, parent traversal, symlinks, missing files, duplicate/ambiguous basenames, and edges outside the package.
- Enumerate all governed roots (`references/`, `scripts/`, `assets/`, `examples/`, `evals/`, plus declared evaluator datasets) and require every included file to be transitively reachable or explicitly allowlisted as generated/non-runtime evidence with a reason.
- Bind the closure result and every evaluator input digest into the package manifest. Compare the closure set with archive contents, security-signature inputs, scenario-set inputs, scorer-calibration examples/raw artifacts, and any CLI `--dataset` before readiness passes.
- Add semantic checks that each branch-specific reference is selected from an observable task branch, scripts are invoked by a named workflow/validation step, assets have a named consumer, examples are tied to a rubric/scorer, and eval cases verify the claimed branch behavior. Keep semantic wording tolerant while requiring action, object, order, and positive/negative branch evidence.

## False-positive and false-negative risks

- Exact string extraction from Markdown can miss link syntax, YAML objects, templated paths, glob declarations, case/encoding variants, and generated manifests.
- Basename matching creates false reachability when two directories contain the same filename or prose merely mentions the name.
- Globs and directory-level declarations can over-include stale files; requiring every generated/raw artifact to be hand-linked can create noise unless the manifest defines bounded generated families.
- Dynamic script imports and files selected by runtime arguments cannot be proven by static text alone; require declared resource manifests and focused runtime/evaluator proof rather than guessing.

## Evidence

Command: `git status --short --branch` -> pass (checkout identity recorded; unrelated dirty ownership preserved)

Command: source inspection of `package_contracts.py`, `ir.py`, `package_build.py`, `package_security_signature.py`, `eval_runner.py`, `scorer_calibration.py`, and focused tests -> pass (current shallow-versus-transitive gap established)

## Claims boundary

This is a source-backed audit of current checkout `4ced957e`. No validator was changed, no focused tests were executed, and no Tessl, cloud, runtime-install, hosted CI, review, or release lane was evaluated. The dirty checkout and the branch being two commits behind `origin/main` mean this does not establish current upstream behavior.

WROTE: artifacts/reviews/default.md

---

# Evaluation Reliability Candidate: Calibration Evidence Binding

schema_version: evaluation-reliability-candidate/v1
status: proposal
agent_id: 019fc35c-21a4-73d3-832f-f580c318673e
mode: read_only
candidate: 4ced957e36ea6ebe4c65d8754db5328d3879fefb
base: origin/main

## Verdict

P1 — `sdk eval scorer-calibration` can return `ready: true` and perfect
metrics from a self-consistent, repository-authored evidence bundle without
proving the declared scorer or its held-out inputs produced the artifacts.

## Evidence and failure mode

`Infrastructure/scripts/lib/ask/skills_sdk/scorer_calibration.py:250-259`
only compares raw artifact `id`, `predicted_label`, and `score` against the
adjacent JSONL row. The command loads that manifest, its examples, and its raw
artifacts from the same package tree (`:369-405`), then computes the confusion
matrix directly from the JSONL rows. It neither executes a scorer nor binds the
bundle to the current `references/evals.yaml` scorer declaration or a
content-addressed scorer/input digest.

The current package demonstrates the unbound parallel declarations:
`Skills/agent-ops/sdk-scenario-generator/references/evals.yaml:73-108` and
`references/scorer-calibration/manifest.json:2-20` repeat scorer identity,
version text, threshold, and parameters. The example raw artifact at
`references/scorer-calibration/raw/cal-pass-evidence-lanes.json:1-8` has no
input/prompt/package digest. The existing regression explicitly accepts raw
artifacts that omit provenance beyond the output fields
(`Infrastructure/tests/test_skills_sdk_scorer_calibration.py:207-260`).

Consequently a changed scorer prompt, implementation, or held-out input can
leave the old hand-authored rows and artifacts aligned with each other. The
preview will still calculate TP=3, TN=3, FP=0, FN=0 and advertise calibration
readiness, creating false confidence in a current scorer.

## Smallest durable mechanism

Extend the calibration bundle contract with canonical SHA-256 bindings for:

- the relevant `scorer_quality` declaration in `references/evals.yaml`;
- the normalized held-out input/examples JSONL; and
- each raw artifact's input digest plus the declared scorer id/version/digest.

Make `build_scorer_calibration_receipt` recompute and require all bindings,
including equality between the manifest and canonical `scorer_quality`
identity/parameters. Return a blocker such as
`calibration_provenance_matches_current_scorer` on mismatch. This is a
validator/schema/test change only: it prevents stale or substituted evidence
from being presented as calibration proof without turning the preview command
into a networked or live-model run.

## Focused validation

1. Add a fixture whose `references/evals.yaml` scorer version or parameter is
changed after its calibration bundle is created; assert preview blocks with the
new provenance check.
2. Add a fixture whose raw artifact has a mismatched scorer or input digest;
assert preview blocks.
3. Verify the existing governed package still passes after refreshing only its
bound digests:
`./bin/ask sdk eval scorer-calibration Skills/agent-ops/sdk-scenario-generator --preview --json --robot`.

## Observed commands

Command: `./bin/ask sdk eval scorer-calibration Skills/agent-ops/sdk-scenario-generator --preview --json --robot` -> pass (returns `ready: true`, six examples, TP=3, TN=3, FP=0, FN=0; it proves the present structural preview only).

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.test_skills_sdk_scorer_calibration` -> pass (13 tests; current behavior is covered, including missing raw artifacts and row-output consistency, but no stale-scorer/input binding case).

## Claims boundary

This proposal does not assert that the current calibration is fabricated, that
the scorer is inaccurate, or that a live Tessl/provider run is required. It
addresses a local provenance gap: a passing preview currently proves internal
consistency of committed metadata, not that the current declared scorer
produced the held-out outcomes.

WROTE: artifacts/reviews/default.md

---

# Case-sensitive plugin-root review

schema_version: architecture-review/v1
status: finding
agent_id: 019fc35c-0f1c-7102-9cca-81b461ad8263
candidate: current working tree (no patch authored)
base: HEAD on main

## P2 — Normalize the one canonical `Plugins/` source path instead of keeping a lowercase alias

`Infrastructure/scripts/lifecycle-and-sync/normalize_skill_headings.sh:33` enumerates `plugins/harness-engineering`, `plugins/plugin-factory`, and `plugins/skill-factory`. The tracked tree has only the capitalized `Plugins` root (`git ls-tree -d HEAD Plugins plugins` returns only `Plugins`). On the case-insensitive macOS checkout, the alias appears valid; on a case-sensitive checkout, the normalizer omits every plugin skill (or its finder reports missing roots), so the command's `Checked files` result cannot establish plugin coverage.

The repository already treats `Plugins/` as the source path: `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh:160-175` and `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1114-1117` use it first. Keeping aliases in the normalizer creates a platform-dependent second vocabulary with no benefit.

Smallest safe repair: replace the three lowercase entries in the `roots` array with their `Plugins/...` canonical forms. Add a focused fixture test that makes the lowercase directories absent and asserts `--dry-run` discovers a `Plugins/skill-factory/.../SKILL.md`; delete the lowercase-path fallback from any path list that is only compensating for this spelling.

## Evidence

Command: `git ls-tree -d HEAD Plugins plugins` -> pass (`Plugins` exists; `plugins` is absent from the tracked tree)

Command: `bash Infrastructure/scripts/lifecycle-and-sync/normalize_skill_headings.sh --dry-run` -> pass on this macOS checkout (`Checked files: 137`; this result does not prove case-sensitive behavior because APFS resolves the alias)

## Claims boundary

This is a static source-layout and cross-platform execution finding. I did not alter source files or test the script on a Linux/case-sensitive filesystem; the proposed fixture is the focused regression proof. It makes no claim about hosted CI, runtime installation, or release readiness.

WROTE: artifacts/reviews/default.md

---

# Codex Security Deep-Scan Capability Preflight

schema_version: capability-preflight/v1
status: ready
agent_id: 019fbf5a-7b30-7451-9d92-adfcdaee4e21
target_cwd: /Users/jamiecraik/dev/agent-skills

## Exact command

`/Users/jamiecraik/.local/share/mise/shims/python3 /Users/jamiecraik/.codex/plugins/cache/openai-curated-remote/codex-security/0.1.15/scripts/config_preflight.py --profile deep_security_scan --cwd /Users/jamiecraik/dev/agent-skills --runtime-check delegation_available=true --runtime-check goal_tools_available=true --available-plugin-skill security-scan --available-plugin-skill threat-model --available-plugin-skill finding-discovery --available-plugin-skill validation --available-plugin-skill attack-path-analysis`

Exit code: `0`

Unmet capabilities: none
Unknown capabilities: none
user_config_path: `/Users/jamiecraik/.codex/config.toml`

## Remediation

The helper reports the optional recommendation `features.goals=true`, sourced from `/Users/jamiecraik/.codex/config.toml`; the capability is already passing, so no config change is applicable. No conflicting settings were reported. Required deep-scan phase skills, native multi-agent v2 ownership/version, and child-config compatibility all passed.

WROTE: artifacts/reviews/default.md

---

# Product-Leverage Review: Conservative `skills improve` Resolution

candidate/base: `main` at the local checkout observed 2026-08-02; no source changes reviewed as part of this candidate.

verdict: **P1 — implement one conservative-resolution guard in `skills improve`.**

chosen improvement: An `intent_unresolved` goal must not become a primary recommendation solely because the fallback finds two overlapping words in a skill description. Keep fallback only for an explicit exact handle (for example, `autofix` or `$autofix`); otherwise return the existing disambiguation prompts, `recommended_capability: null`, and the target-bound `skills goal` retry without running runtime proof.

evidence:

- The product contract records that broad goals resolve as `intent_unresolved` and need sharper repair prompts ([Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md](../../Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md), lines 52-53); the SDK promise is a compact, target-bound local journey ([Docs/product/agent-capability-control-plane.md](../../Docs/product/agent-capability-control-plane.md), lines 25-49).
- `improve_skills` explicitly enables `_fallback_improvement_candidate` for `unresolved_ambiguity` (Infrastructure/scripts/lib/ask/commands/skills_impl.py:12301-12305), then labels the result `resolved_with_fallback` and recommends it after runtime proof (lines 12347-12366). The fallback itself selects a skill on only two overlapping tokens, including description text (lines 12174-12233).
- Direct reproduction: `./bin/ask skills improve "make this repository safer and more useful for agent authors" --json --robot` returned `status: success`, `recommended_capability.handle: github`, and `why: ["fallback SDK skill description match", "matched terms=more,repository"]`, while its embedded `goal_decision_status` remained `intent_unresolved` with `recommended_candidate: null`.
- The current test suite codifies promotion of an unresolved natural-language goal to a recommendation (Infrastructure/tests/test_ask_skills_goal.py:219-259), despite the same suite asserting that unresolved goals otherwise block and retain disambiguation (lines 195-217).

impact: Jamie and Ryan get a control plane that fails safely at the point where it lacks intent evidence, rather than demonstrating runtime visibility for an unrelated installed skill. Maintainers gain one simple invariant: a non-exact recommendation requires a resolved router decision. This reduces false confidence without enlarging the CLI or adding new lifecycle process.

smallest effective mechanism and proof:

1. Gate both lexical fallback paths in `improve_skills` on an explicit exact registered handle; leave normal `resolved` router decisions unchanged.
2. Add table-driven tests for ambiguous natural language (no recommendation/proof; `blocked_ambiguity`) and exact `$handle` input (allowed target-bound fallback, if retained).
3. Run `bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest Infrastructure.tests.test_ask_skills_goal` and replay the quoted `skills improve` command, asserting `intent_unresolved`, no primary recommendation, and no proof payload.

claims boundary: This is a source-and-local-command observation only. It does not establish user demand frequency, hosted CI, review acceptance, runtime picker invocation, or release readiness.

WROTE: artifacts/reviews/default.md

---

# JSC-468 CI Repair Adversarial Review

schema_version: adversarial-ci-review/v1
status: changes_requested
agent_id: 019f7b91-c82b-7a12-a6fe-5d8938afa0df
mode: read_only

## Scope

Reviewed the in-progress CI repair for the `audit`, `check`, and `lint` PR
failures. I inspected the current candidate diff, the previously proposed
single-commit CI remedy `140ca1b6c`, the maintained validation router, and the
canonical manifest generator. I made no source, workflow, skill, Git, hosted,
package-manager, or external-eval mutation.

## Findings

### P1 — New regression test is not in a CI-owned execution path

`Infrastructure/tests/test_pr_pipeline_validation_dependencies.py` is a useful
unit test, but no PR job currently selects it. `scripts/validate_all_impl.sh`
limits `--scope=test` to `skill-lifecycle-tests`, `skill-authoring-family`,
`skill-graph-profiles`, and `gotcha-store` (lines 305-310). The only selected
pytest targets in
`Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh`
are enumerated at lines 584-598, and this file is absent. The test therefore
does not ratchet a future removal of `uv` from the workflow.

Minimal remediation: add this exact test to a maintained CI test command, or
move the assertion into an existing validator that `audit`/`check` already run.
Prove both the direct test and its canonical CI-owned caller path.

### P2 — Test accepts unsafe ordering and an unspecified Python runtime

`_uses_python_setup` in
`Infrastructure/tests/test_pr_pipeline_validation_dependencies.py:32-37` only
checks for an `actions/setup-python` action, while `_installs_uv` at lines 40-46
only checks that some step contains `uv`. Neither asserts a `python-version:
"3.12"` nor that setup and installation precede the `repo validate` step. A
workflow that installs `uv` after validation, or uses Python 3.11, would pass
the test even though `Infrastructure/pyproject.toml:5` and
`Infrastructure/uv.lock:3` require `>=3.12`.

Minimal remediation: derive step indexes and assert, per scope, pinned Python
3.12 setup < uv install < validation command.

### P2 — Added CI tool version bypasses the repository tool pin

The candidate uses `python -m pip install --upgrade pip uv pyyaml pytest
jsonschema` in `.github/workflows/pr-pipeline.yml:538` and `:555`.
`.mise.toml:5` declares the repository's `uv` version as `0.11.3`; the new
unqualified `uv` install can change independently of the repo tool contract.
This is not a root package-manager contract, but it is a CI toolchain
reproducibility and supply-chain drift risk.

Minimal remediation: install the repository-approved `uv` version (or a
SHA-pinned `setup-uv` action admitted by the existing action-pinning policy),
then update the test to assert the chosen mechanism.

### P3 — Two unrelated heading-level edits should be removed

The progressive-disclosure repair requires `## Gotchas`; it does not require
changing `### Anti-Patterns`. The candidate also promotes that heading in
`Skills/agent-ops/improve-codebase-architecture/SKILL.md:116` and
`Skills/agent-ops/testing/SKILL.md:129`. Both strict package audits pass, so
this is not a correctness blocker, but restoring the two headings to their
original nesting keeps the approved repair minimal.

### Confirmed non-finding — Full manifest rewrite is generator-owned

The manifest change is broad because each row records `source_revision`.
`Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py:113-122`
writes every root manifest and the generated rows now bind to the current
candidate revision. The repository explicitly identifies manifests as generated
and forbids hand edits in
`Docs/specs/2026-04-24-feat-context-budgeted-skill-trees-spec.md:912`.
Retain the complete generator output after reviewing it; do not trim it to the
two edited skills.

## Evidence

Command: `git show --format= 140ca1b6c | git apply --check --verbose` -> pass (the proposed CI commit applies cleanly to the current workflow surface)

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_pr_pipeline_validation_dependencies.py --disable-warnings --maxfail=1` -> pass (the new test passes locally, but static routing evidence shows CI does not select it)

Command: `bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict` -> pass (the two required H2 Gotchas headings are now accepted; three unrelated warnings remain)

Command: `./bin/ask skills audit Skills/agent-ops/improve-codebase-architecture --level strict --json --robot` -> pass (the candidate skill shape is accepted)

Command: `./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot` -> pass (the candidate skill shape is accepted)

Command: `bash Infrastructure/scripts/run-infrastructure-python.sh scripts/validation-and-linting/check_context_budget.py --projection rooted --json` -> fail (14 stale `SKILLSET_SOURCE_HASH_STALE` rows plus one local runtime-exposure finding before the candidate generator output; the 14 source paths match `origin/main`)

Command: `git diff --quiet origin/main -- Skills/agent-ops/agents-md/SKILL.md Skills/agent-ops/autoreview/SKILL.md Skills/agent-ops/evals-router/SKILL.md Skills/agent-ops/goal-governor/SKILL.md Skills/agent-ops/improve-agent-native/SKILL.md Skills/agent-ops/improve-codebase-architecture/SKILL.md Skills/agent-ops/pr-green-sweep/SKILL.md Skills/agent-ops/simplify/SKILL.md Skills/agent-ops/technical-writer/SKILL.md Skills/agent-ops/testing/SKILL.md Skills/agent-ops/ubiquitous-language/SKILL.md Plugins/aidevcon/skills/talk-podjarny-skills-are-the-new-code/SKILL.md Plugins/aidevcon/skills/talk-tal-skills-security/SKILL.md Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md` -> pass (all 14 stale source paths were unchanged from `origin/main` before the approved repair)

## Boundary

No Tessl, provider-backed, cloud, or other live external evaluation was run.
This review does not prove hosted CI, hosted review state, mergeability, or the
future post-push check results.

WROTE: artifacts/reviews/default.md
