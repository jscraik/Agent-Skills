# Skills SDK Module Contracts

JSC-391 defines module landing zones for future Skills SDK work. These contracts
reserve ownership and proof vocabulary only; they do not implement user-facing
CLI behavior, signing execution, sandbox execution, eval execution, install
writes, registry publication, package upload, or global/project skill writes.

The machine-readable ownership map lives at
`.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json`.
Future feature work must name one owning module and any collaborators before it
adds behavior.

## Shared Work Modes

| Work mode     | Meaning                                                                           | Receipt expectation                                                                   |
| ------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| inferential   | Model judgment, classification, review, or synthesis.                             | Record prompt/input context, decision, uncertainty, and reviewer or model provenance. |
| computational | Deterministic parsing, schema validation, command execution, or file inspection.  | Record command, exit status, parsed result, evidence ref, and redaction status.       |
| hybrid        | A deterministic check wrapped around model judgment or model-generated artifacts. | Record both computational proof and inferential rationale, keeping them separate.     |

## Shared Risk Model

Risk rows use probability, impact, and detectability so future agents can
separate likely harm from hard-to-detect harm. Unimplemented sensors use
`blocked`, `not_run`, or `skipped_optional`; they never report pass by
absence.

| Field            | Contract                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| probability      | Expected likelihood for the risk in this module's workflow.                                      |
| impact           | Consequence if the risk reaches a user, repo, runtime projection, tracker, or package.           |
| detectability    | How easily the risk is caught by local tests, validators, receipts, review, or runtime evidence. |
| sensor_placement | The earliest local artifact, command, schema, or review lane that should catch it.               |

## Receipt And Redaction Boundary

Receipt proof metadata records command, parsed result, blocker class, evidence
ref, redaction status, and lane ownership. Redaction removes secrets, local-only
tokens, and private runtime paths when needed, but it must not erase the claim
being proven. Receipts do not claim PR, CI, Linear, review-thread, artifact, or
merge-readiness truth without fresh lane-specific proof.

## Module Contract Matrix

| Module      | Owns                                                                                                                                    | Public contract                                                                                                                   | Hidden internals                                                                                       | Collaborators                                | Forbidden ownership                                                                                     | Status                             |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| manifest    | Skill manifest/frontmatter field interpretation, package shape metadata, project skill source classification.                           | Manifest validation reports structured blocker classes through `ask.skills_sdk.contracts` and `ask.skills_sdk.package_contracts`. | Field normalization details, package archive verification, command parser glue.                        | packaging, install, receipts                 | Runtime projection writes, install mutation, archive verification internals, user-facing CLI ownership. | preserve_existing_plus_placeholder |
| receipts    | SDK proof metadata, redaction boundary, baseline/post-change comparison vocabulary.                                                     | Receipts include command, parsed result, blocker class, evidence ref, and redaction status.                                       | Telemetry collection, command execution, tracker mutation.                                             | runtime, risk, evals, install                | PR/CI/Linear/merge claims without fresh lane proof.                                                     | placeholder_contract               |
| risk        | Risk sensor placement, probability/impact/detectability vocabulary, feature-planning refusal criteria.                                  | Risk rows name sensor placement and probability, impact, and detectability values.                                                | Security scanner implementation, sandbox platform, signing trust decisions.                            | manifest, receipts, sandbox, install         | Treating absent sensors as pass.                                                                        | placeholder_contract               |
| install     | Install lifecycle contract, target root classification, promote/rollback/blocked decision shape.                                        | Install is lifecycle-gated and receipt-backed.                                                                                    | Actual writes, global/project mutation, runtime projection generation.                                 | manifest, packaging, sandbox, receipts, risk | Global skill mutation, registry publication, marketplace publication, runtime projection source edits.  | placeholder_contract               |
| sandbox     | Sandbox interface contract, permission and environment boundary vocabulary, unavailable-execution status.                               | Sandbox placeholders report `blocked` or `not_run` when execution is absent.                                                      | Filesystem/network execution, sandbox provider selection, runtime projection discovery.                | runtime, risk, install, receipts             | Sandbox execution platform, filesystem mutation, network execution, signing.                            | placeholder_contract               |
| refs        | Reference ingestion contract, reference quality and provenance vocabulary, external-reference blocked status.                           | Reference contracts preserve provenance and quality status.                                                                       | Network fetching, external registry sync, package publication.                                         | manifest, packaging, receipts                | Fetching or ingesting external data during JSC-391.                                                     | preserve_existing_plus_placeholder |
| evals       | Eval dataset contract, eval result placeholder semantics, portable eval evidence shape.                                                 | Eval placeholders remain local and parseable; external Tessl is not required for JSC-391 scaffold acceptance.                     | Live eval service mutation, registry upload, external Tessl execution.                                 | manifest, receipts, risk                     | External eval service dependency as scaffold gate.                                                      | placeholder_contract               |
| signing     | Signing placeholder contract, provenance vocabulary reservation, honest `not_run` or `blocked` signing status.                          | Signing is documentation/schema-only in JSC-391.                                                                                  | Key handling, signing execution, trust-store writes, registry publication, package upload.             | packaging, risk, receipts                    | Key handling, signing execution, trust-store writes, registry publication, package upload.              | placeholder_contract               |
| runtime     | Runtime target vocabulary, command-handle proof, reachability blocker classification, evidence path redaction.                          | Runtime proof uses `ask.skills_sdk.runtime_adapters` public functions.                                                            | Sandbox execution, global runtime mutation, CLI parser ownership.                                      | sandbox, receipts, risk                      | Pretending missing runtime projection is readiness.                                                     | preserve_existing                  |
| packaging   | Package metadata, package readiness, archive verification public contract.                                                              | Packaging uses `package_contracts.py` and `package_verify.py` public functions.                                                   | Install mutation, registry publication, signing execution, runtime projection writes.                  | manifest, install, refs, signing, receipts   | Publishing, upload, or install behavior during JSC-391.                                                 | preserve_existing                  |
| lenses      | Shared expert-lens catalog, deterministic lens validation, and task-signal-based lens selection for skill-agnostic agent review passes. | `ask sdk lenses` emits schema-versioned list, explain, validate, and select receipts from `Infrastructure/references/lenses/`.    | Model judgment, prompt rewriting, automatic skill mutation, skill-local persona routing.               | refs, evals, receipts, risk                  | Always-loading every lens, treating lenses as conclusions, or hiding selection rationale from agents.   | preserve_existing_plus_contract    |
| determinism | Advisory detection of prompt-only skill rules that can become validators, schemas, selectors, fixtures, or command receipts.            | `ask sdk determinism audit` emits schema-versioned candidates with area, priority, evidence, and recommended mechanism.           | Automatic rewrites, blocking gates, model-quality scoring, or claiming candidate findings are defects. | lenses, refs, evals, receipts, manifest      | Treating advisory candidates as failures before an owning gate adopts them.                             | preserve_existing_plus_contract    |

## Placeholder Status Semantics

| Status           | Meaning                                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| not_run          | The contract is defined, but no execution was attempted.                                                                     |
| skipped_optional | The contract is optional for the current scaffold slice and was intentionally skipped.                                       |
| blocked          | The contract is required for a later slice or feature but cannot run without a missing dependency or explicit authorization. |

Any placeholder that reports `pass` for signing, sandbox, eval, install,
registry, publish, or global/project skill writes violates JSC-391.
