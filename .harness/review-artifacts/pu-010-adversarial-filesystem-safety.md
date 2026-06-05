# PU-010 Adversarial Filesystem Safety Review

## Findings

### 1. High: Receipt path containment can still escape through symlinks or hardlinks
- **Evidence:** Spec lines 54-57, 125-128, 186, 202-204 only require target-path containment, digest checks, and that cleanup paths remain under the resolved project root.
- **Why it matters:** A path can be lexically inside the project root while the final inode lives outside it. If rollback or uninstall follows a symlinked directory entry, or deletes a hardlinked file that shares an inode with data outside the project root, the command can destroy content the spec does not actually own. Digest matching does not prove exclusive ownership of the inode.
- **Remediation:** Require filesystem-aware resolution for every parent and target path, reject symlinked path components unless the receipt explicitly records and approves them, and refuse destructive operations on hardlinked files unless the receipt proves exclusive ownership or the link count is safe.
- **Confidence:** 95/100
- **Validation ownership:** human / implementation team

### 2. High: Case-insensitive path aliases can bypass or confuse root and receipt checks
- **Evidence:** Spec lines 54-57, 124-125, 131-135, 200-203 rely on path matching and containment, but never require case-normalized canonical comparison.
- **Why it matters:** On case-insensitive filesystems, /Users/.../Project, /users/.../project, and mixed-case receipt paths can refer to the same location while string comparisons treat them as different. That can produce false safe/unsafe decisions, duplicate bookkeeping, or cleanup against the wrong path when the same file is addressed through a different casing.
- **Remediation:** Canonicalize paths with filesystem-aware normalization before every comparison, and treat case-colliding path variants as ambiguous until resolved by real filesystem identity rather than raw strings.
- **Confidence:** 90/100
- **Validation ownership:** human / implementation team

### 3. High: Directory cleanup is underspecified, so pruning can delete user content or leave dangerous orphan state
- **Evidence:** Spec lines 127-129, 134-140, 234-240, 247-255 model only files and file digests; no requirement defines owned directories, pruning boundaries, or directory-content revalidation.
- **Why it matters:** Rollback or uninstall will almost certainly need to remove empty directories after deleting owned files. Without an ownership model for directories, a recursive prune can cross into directories that now contain user-added files, or it can leave empty install directories behind and make later runs reason about a stale tree. Either outcome is a filesystem safety gap.
- **Remediation:** Track owned directories explicitly, prune only directories proven empty and install-owned after a fresh content check, and stop pruning as soon as an unowned entry is present. If the design will not own directories, say so explicitly and never recurse-delete parent directories.
- **Confidence:** 88/100
- **Validation ownership:** human / implementation team

### 4. High: Atomic JSON writes do not make the cleanup transaction atomic, so crashes can strand a half-mutated tree
- **Evidence:** Spec lines 135-139, 214-216, 233-240, 261-262 require atomic JSON writes and partial receipts, but do not require a resumable mutation journal or a two-phase filesystem transaction across file deletes/restores and lockfile updates.
- **Why it matters:** A rollback/uninstall can delete several files, then fail while updating skills.lock.json, emitting the receipt, or reaching a final consistency step. The spec allows partial status, but it does not require a recovery journal that makes the next run know exactly which mutations already happened. That leaves the project in a state where the lockfile, receipt, and filesystem can disagree after a crash or abrupt termination.
- **Remediation:** Add an explicit mutation journal or staged state marker, require the cleanup plan to be fully validated before the first delete, and define crash recovery so a rerun can distinguish "not started", "partially applied", and "completed but receipt write failed" states.
- **Confidence:** 82/100
- **Validation ownership:** human / implementation team

### 5. High: The spec does not explicitly block the live repo as a project root, so a mispointed apply can clean the workspace itself
- **Evidence:** Spec lines 52-60, 117-121, 165-176, 182-187, 314-318 require an explicit project root, but they do not prohibit dangerous roots such as the live agent-skills checkout, filesystem root, or home directory for rollback/uninstall the way PU-009 did for install.
- **Why it matters:** A cleanup command aimed at the wrong root can delete files from the active repository or its working tree. Because these commands are destructive by design, "explicit project root" is not enough; the spec needs a hard unsafe-root gate so a mistaken or scripted invocation cannot turn into self-mutation of the toolchain repo.
- **Remediation:** Add an explicit unsafe-root rejection list for rollback/uninstall that covers the live repo/worktree, filesystem root, home directory, missing paths, file paths, ambiguous relative roots, and any root that is not a validated project workspace.
- **Confidence:** 86/100
- **Validation ownership:** human / implementation team

## Residual Risks
- The spec does say to preserve user-modified files and to keep cleanup under the resolved project root, so the current intent is good; the gaps are in the operational details that make those promises enforceable.
- I did not validate the implementation because this review was limited to the spec artifact.
- No runtime test evidence was collected in this pass.

## Testing Gaps
- No temp-project execution trace exists yet for symlink, hardlink, or case-insensitive path edge cases.
- No crash/restart recovery test is specified for cleanup after partial mutation and failed lockfile or receipt writes.
- No directory-pruning test is described that proves user-added files inside install-owned trees survive cleanup.

## Accountability Receipt
- **status:** complete
- **artifact_paths:** ["/Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-adversarial-filesystem-safety.md", "/Users/jamiecraik/dev/agent-skills/artifacts/reviews/adversarial-reviewer.md", "/Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-2026-06-05-pu-010-filesystem-safety/manifest.json"]
- **findings:** 5 high-severity filesystem safety gaps in rollback/uninstall spec coverage
- **failures_or_blockers:** none
- **improvement_opportunities:** add explicit symlink/hardlink rules, case-normalized canonical comparisons, directory ownership semantics, crash-recovery journaling, and unsafe-root rejection
- **strengths:** the spec already requires receipt validation, digest checks, partial-state reporting, and explicit project-root targeting
- **validation_evidence:** spec lines 54-57, 117-129, 135-140, 182-204, 210-218, 247-255, 291-295, 314-318
- **next_action:** carry these safety gaps into the implementation plan before any cleanup code is written
- **manifest_path:** /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/adversarial-reviewer-2026-06-05-pu-010-filesystem-safety/manifest.json

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-010-adversarial-filesystem-safety.md

