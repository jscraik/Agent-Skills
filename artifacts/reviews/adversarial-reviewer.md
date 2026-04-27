# Adversarial Review: 2026-04-24 Context-Budgeted Skill Trees Plan

## Findings

### 1) HIGH: Repeated user-scope mutation in cutover validation can corrupt operator runtime state
- Evidence: `Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:1042` requires five consecutive runs of the same validation set, and that set includes non-dry-run user mutations at `:1155` and rollback at `:1157`, with repeated execution mandated at `:1165-1169`.
- Breakage path: Running this on a real workstation repeatedly rewrites user-facing runtime projection (`--scope user`) while sessions may be active. A partial failure between forward mutation and rollback can strand the user in rooted mode or a mixed surface. Repeating five times multiplies the chance of interruption/race with active agents.
- Remediation: Require isolated execution for C3/C4 (ephemeral profile/sandboxed home directory) and add a hard precondition that no active Codex sessions target the same user runtime. Add pre/post snapshot+hash verification for user-scope files to prove rollback restored exact prior state.

### 2) HIGH: Rollback safety claims lack an atomicity contract, so interrupted runs can leave mixed workspace/user surfaces
- Evidence: The plan mandates forward then rollback commands across both scopes (`:1087-1092`, `:1153-1160`, `:1177-1179`) and treats success as command pass/fail, but does not define transactional semantics or an interruption recovery protocol.
- Breakage path: If validation or process termination occurs after workspace rollback but before user rollback (or vice versa), surfaces diverge. Subsequent routing/debug signals become misleading because one scope is flat and the other rooted.
- Remediation: Add an explicit two-phase mutation contract: snapshot -> mutate -> validate -> rollback -> verify snapshot parity, with required recovery command(s) on partial failure and a mandatory post-run invariant check that both scopes match intended mode.

### 3) MEDIUM: Plan is marked in late phase while key decision gates remain unresolved, weakening soak evidence integrity
- Evidence: Frontmatter says `current_phase: C3-rooted-soak` at `:11`, but the plan still lists unresolved decisions that must be settled before earlier execution slices (`:1223-1236`), including router threshold and root inventory.
- Breakage path: Soak evidence collected before freezing these decisions is not stable; later decision changes can invalidate C3 results and produce false confidence for C4 default flip.
- Remediation: Add a gating invariant that C3 cannot start until all decision items tagged as pre-A1/A2/B3 are closed with artifact IDs and revision stamps; otherwise force phase rollback to decision-closure.

## Residual Risks (if findings are fixed)
- Workout determinism is still sensitive to ambient environment variance unless execution hosts and fixture seeds are pinned.
- User/workspace path ownership checks may still miss drift if manifest provenance validation does not include full file inventory hashing.

WROTE: artifacts/reviews/adversarial-reviewer.md
