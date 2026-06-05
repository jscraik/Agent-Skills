# PU-010 Adversarial Review: Receipt, Schema, and Lockfile Contracts

Reviewed artifact: `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md`

## Findings

### 1. High: Cleanup trusts a receipt label, not a receipt identity

**Spec refs:** lines 191-205, 220-230

**Scenario**
- A cleanup command receives a valid-looking install receipt path or label via `source_install_receipt`.
- The receipt is copied, moved, or swapped in place after the install, or the caller points at another receipt file with the same shape.
- The spec only requires a readable, schema-valid receipt plus a string label for `source_install_receipt`; it does not require a receipt digest, immutable receipt id, or a lockfile-bound receipt reference.
- Cleanup can therefore validate the wrong source document and plan removals against an install that did not authorize the current project root or file set.

**Why it matters**
- This is the main tamper-resistance hole: a valid-looking receipt is not the same as the authoritative receipt for this project.
- It also weakens project-root matching, because the spec does not require the cleanup receipt to prove the source receipt was issued for the same resolved root as the current apply target.
- A stale but still schema-valid receipt can be replayed after the project has changed, which makes rollback/uninstall decisions depend on file location instead of provenance.

**Remediation**
- Require a canonical receipt identity, not just a path label: add a receipt id or digest and make the lockfile store that immutable reference.
- Bind `source_install_receipt` to the validated receipt's digest, schema version, and resolved target root.
- Reject cleanup if the referenced receipt is not the same object the lockfile recorded for that installed skill.

### 2. High: Duplicate skill ids collapse into one lock entry, so uninstall cannot prove which install instance it owns

**Spec refs:** lines 131-132, 208-218, 257-258

**Scenario**
- A project installs the same skill twice, or installs a renamed/republished source that keeps the same skill id.
- The lockfile schema models `entries` as an object keyed by handle, and uninstall resolves by skill id.
- The spec does not define a unique install-instance id, a multivalue history, or a refusal rule for repeated active installs of the same skill id.
- The later install can overwrite the earlier entry, or the parser can only observe one surviving entry, which makes rollback/uninstall act on the wrong file set or leave orphaned files behind.

**Why it matters**
- This is a duplicate-id and stale-receipt failure at the same boundary: the spec needs to distinguish "the skill id exists" from "this specific installation instance exists".
- Without a unique instance key, a stale receipt can still look valid enough to satisfy uninstall, even though the lockfile entry now refers to a different install.
- The current shape also makes duplicate or ambiguous lock entries a detection problem rather than a prevented state.

**Remediation**
- Introduce a unique per-install instance id or receipt id in the lockfile and cleanup receipt.
- Make duplicate active skill ids an explicit refusal case, not an implicit last-write-wins overwrite.
- If repeated installs of the same skill id are allowed, require a versioned list or history so uninstall can target a specific instance.

### 3. High: Overwritten-file recovery has no machine-checkable before-state

**Spec refs:** lines 129-130, 204, 220-241

**Scenario**
- A real install overwrote a file, and the user later asks for rollback.
- The rollback requirement says restoration is only allowed when the install receipt contains before-content or an approved before-state reference with digest proof.
- But the cleanup receipt contract only requires `files_restored` with before/after digests, and the install receipt schema only records overwritten file digests, not before-content or a before-state reference.
- The implementation is forced either to invent restoration logic, to guess from the current filesystem state, or to silently downgrade to manual action without a proof-bearing field that explains why.

**Why it matters**
- This is the missing-before-state gap: the spec says safe restoration needs before-state evidence, but the source receipt shape does not actually require that evidence.
- It leaves the spec unable to prove that restored content is the same content that existed before install, which is exactly the dangerous branch for rollback.
- If the command falls back to manual actions, there is still no structured field showing whether the file was blocked because before-state was absent or because the file drifted later.

**Remediation**
- Add explicit before-state fields to the install receipt for overwritten files, such as before-content digest, before-content ref, or a signed/approved before-state reference.
- Mirror that provenance in the cleanup receipt so restored files can be audited without inferring state from the live filesystem.
- Keep manual-action reporting, but make it a deliberate branch with an explicit reason code instead of an emergent fallback.

### 4. Medium: Cleanup schema versioning and lockfile path selection are both underspecified

**Spec refs:** lines 208-216, 222-230

**Scenario**
- A future cleanup implementation ships a new receipt version, or a project uses a renamed or migrated lockfile path.
- The spec says the lockfile is `skills.lock.json` "unless a later plan proves a different canonical path," and it allows either separate cleanup schemas or one discriminated cleanup schema.
- There is no v1-specific schema id/URI requirement for cleanup receipts, no compatibility rule for older receipts, and no migration rule for alternate lockfile paths.
- A parser can therefore accept the wrong cleanup schema version, or read the wrong lockfile if the project has more than one candidate path or a path alias.

**Why it matters**
- This is the contract drift point: the command may be mechanically correct against one project layout and silently wrong against another.
- Ambiguous lockfile selection is especially risky for uninstall because the authority source becomes "whatever file happens to be treated as the lockfile" rather than the project's canonical lock state.
- Version drift without explicit compatibility rules makes stale receipts harder to reject deterministically.

**Remediation**
- Pin cleanup receipt v1 with explicit `schema_version` and `schema_uri` constants, just like the install receipt does.
- Define the canonical lockfile path in the spec now, or require an explicit migration rule and validation fallback if multiple lockfile candidates exist.
- Reject cleanup receipts and lockfiles whose version or path cannot be resolved to a single canonical authority record.

## Accountability Receipt

- status: complete
- artifact_paths:
  - `.harness/review-artifacts/pu-010-adversarial-receipt-lockfile.md`
  - `artifacts/agent-runs/adversarial-reviewer-20260605T204326-e59d1c23/manifest.json`
- manifest_path: `artifacts/agent-runs/adversarial-reviewer-20260605T204326-e59d1c23/manifest.json`
- findings:
  - High: receipt identity is not digest-bound, so tampering and stale-receipt replay can redirect cleanup authority.
  - High: duplicate skill ids collapse into one lock entry, making uninstall/rollback instance-ambiguous.
  - High: overwritten-file recovery lacks before-state evidence, so rollback cannot prove restored content.
  - Medium: cleanup schema versioning and canonical lockfile path are underspecified, creating drift and ambiguity.
- failures_or_blockers: none
- improvement_opportunities:
  - Add immutable receipt identity and lockfile-bound receipt references.
  - Introduce per-install instance ids or history in the lockfile.
  - Extend install receipts with before-state proof for overwritten files.
  - Pin cleanup schema v1 and canonicalize lockfile selection.
- strengths:
  - The spec already requires preview-first flow, project-root validation, digest checks, and partial-state reporting.
  - The cleanup receipt contract does at least name the core action buckets and mutation flag.
- validation_evidence:
  - Read `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md`
  - Read `Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json`
  - Read `Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json`
  - Read `.harness/specs/2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle-spec.md`
- next_action: fold these gaps into the implementation plan so cleanup authority is receipt-bound, instance-safe, and version-pinned before code is written.
- useful_findings:
  - The current spec is strong on containment checks and explicit apply semantics.
  - The remaining risk is all about authority binding, not just path safety.
  - The lockfile model is the narrowest place where duplicate-id and stale-receipt bugs become visible.
- avoided_false_positive:
  - I did not flag generic missing tests or style issues.
  - I did not assume global uninstall or networked cleanup, which the spec explicitly excludes.
  - I did not claim a live exploit; each finding is a concrete failure scenario against the written contract.
- evidence_quality: medium-high
- followed_scope: yes
- reusable_learning: cleanup authority should be proved by immutable receipt identity plus canonical project-root binding, not by a path string alone.
- coordinator_score: 9/10

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-adversarial-receipt-lockfile.md
