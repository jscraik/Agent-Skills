# PU-010 adversarial review

## Findings

### 1. High: Rollback preview cannot prove it is looking at the right project root
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 116-125, 156-186, 191-205.
- Why it matters: FR-001 lets rollback preview run with only --receipt, but the receipt validation contract also requires target_root to resolve against the supplied project root and says rollback must refuse target-root mismatches. That means preview can either skip the consistency check entirely or invent an implicit project root from ambient context. In the bad case, a stale or transplanted receipt can produce a believable cleanup plan for the wrong tree.
- Impacted behavior: preview output can become authoritative-looking while being tied to the wrong project root, which is exactly the case this slice is supposed to prevent.
- Remediation: make rollback preview accept --project-root as an explicit required input whenever it validates receipt-root consistency, or remove the consistency claim from preview and restrict it to apply only. Add an acceptance case for receipt-root mismatch on preview.
- Confidence: 90
- Validation ownership: spec gap

### 2. High: The spec never says whether --preview and --apply are mutually exclusive or what happens when neither is passed
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 116-121, 156-187, 247-258.
- Why it matters: The command contract defines preview and apply as separate modes, but it never rejects --preview --apply, never says which flag wins if both are present, and never says whether one flag is mandatory. A parser that silently prefers one branch can pass the listed acceptance cases while still letting a caller think they requested a dry run when the command actually mutated files.
- Impacted behavior: a cleanup command can mutate when the user intended a dry run, or a dry run can be reported when the command took the apply branch.
- Remediation: add an explicit mode rule: exactly one of --preview or --apply is required for rollback and uninstall. Add a negative acceptance case for both flags and for missing mode.
- Confidence: 88
- Validation ownership: spec gap

### 3. Medium: Robot-mode failure JSON shape is underspecified, so CLI consumers can break even if the command fails correctly
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 151-152, 222-241, 247-265, 269-277; plus current envelope behavior in Infrastructure/scripts/lib/ask/envelope.py and Infrastructure/scripts/lib/ask/cli_errors.py.
- Why it matters: The spec asks for blocker class, fix suggestion, and evidence path, but it never pins down the actual JSON envelope for blocked rollback/uninstall paths. Without a concrete error-shape contract, one implementation can emit a normal CallResult with errors, another can tuck the blocker info into data, and a third can return a success envelope with a warning. Robot-mode automation will then parse the wrong field or miss the failure entirely.
- Impacted behavior: downstream tooling that relies on --json --robot can misclassify a blocked cleanup as success or lose the remediation hint.
- Remediation: add an explicit robot error schema or at least a blocked-path acceptance case that asserts status: error, errors[0].code, errors[0].message, errors[0].fix_suggestion, metadata.command, and mutation_performed: false.
- Confidence: 81
- Validation ownership: spec gap

### 4. Medium: bin/ask and bin/skills-sdk parity is only proven for status, not for the new cleanup routes
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 107, 160-176, 271-275; bin/skills-sdk; Infrastructure/tests/test_skills_sdk_capability_status.py; Infrastructure/tests/test_skills_sdk_install_preview.py.
- Why it matters: The public wrapper is just a pass-through into Infrastructure/bin/ask sdk, so any cleanup-specific parsing, metadata, or argument-order regression will surface only if rollback/uninstall are tested through both entry points. Right now the spec’s validation plan only exercises wrapper parity for status, not for the new commands. That leaves room for ask and bin/skills-sdk to diverge on command metadata, error payloads, or flag handling while still passing the spec’s checks.
- Impacted behavior: one entry point can reject or reinterpret rollback/uninstall differently from the other, which breaks scripted adoption and makes the reported CLI surface inconsistent.
- Remediation: add mirrored rollback and uninstall tests for both Infrastructure/bin/ask and bin/skills-sdk, including at least one preview path and one blocked apply path, and assert identical JSON payloads and metadata.command values.
- Confidence: 87
- Validation ownership: spec gap

### 5. Medium: Status and artifact truth can overclaim implementation because the spec never defines the threshold for implemented versus partial and never forces artifact regeneration
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 61-62, 87, 101-109, 141-142, 264-265, 275, 284-285, 296.
- Why it matters: The spec allows capability truth to move from deferred to implemented when evidence exists, but it never states what evidence is sufficient. That lets a parser-only or preview-only implementation flip the matrix too early, while the HTML artifacts can lag behind because they are only change_if_truth_changes and only checked if required. The result is a locally green status surface that still contradicts the visual artifact truth.
- Impacted behavior: local status can claim rollback/uninstall are implemented while the supporting artifacts still show deferred or partial truth, or vice versa.
- Remediation: define a strict status ladder for cleanup routes, and require explicit artifact regeneration plus a diff check when any capability label changes.
- Confidence: 76
- Validation ownership: spec gap

### 6. High: The validation plan never actually runs rollback or uninstall, so a dead or parser-only cleanup path could still satisfy every listed command
- Spec evidence: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md lines 267-277 versus the new command contract in lines 156-187.
- Why it matters: The listed validation commands only check status, install compatibility, codestyle, and a broad repo gate. None of them execute sdk rollback or sdk uninstall, so the plan can pass even if the new CLI routes do not exist, ignore --apply, or reject all cleanup receipts. That is a classic traceability hole: the spec promises cleanup behavior, but the validation list never proves it.
- Impacted behavior: implementation can ship with no exercised rollback/uninstall path while still appearing validated.
- Remediation: add explicit temp-project commands for rollback preview, rollback apply, uninstall preview, uninstall apply, and at least one negative-path robot invocation for each.
- Confidence: 94
- Validation ownership: spec gap

## Accountability receipt

- status: complete
- artifact_paths: .harness/review-artifacts/pu-010-adversarial-cli-tests-status.md
- manifest_path: artifacts/agent-runs/adversarial-reviewer-pu-010/manifest.json
- findings: 6
- failures_or_blockers: none
- improvement_opportunities: add explicit cleanup mode exclusivity, receipt-root consistency requirements for preview, and cleanup-route robot error schemas; extend validation to execute rollback/uninstall paths through both wrappers.
- strengths: the spec is already strong on ownership, temp-project safety, and receipt/lockfile provenance; the cleanup slice is clearly scoped away from global mutation.
- validation_evidence: inspected the spec lines cited above, the current bin/skills-sdk wrapper, the existing status/install preview tests, and the current envelope and CLI error helpers.
- next_action: feed the spec back into planning with a cleanup-focused test matrix that covers argument conflicts, wrapper parity, blocked robot JSON, and artifact truth regeneration.

WROTE: .harness/review-artifacts/pu-010-adversarial-cli-tests-status.md
