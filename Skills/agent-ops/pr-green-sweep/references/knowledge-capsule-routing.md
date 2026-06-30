# PR Green Sweep Capsule Routing

description: Route PR Green Sweep capsule detail by the blocker or action lane currently under review.

Use this file after the `SKILL.md` entrypoint and before reading generated
capsule bodies. Select only the capsule needed for the active PR lane.

| Trigger | Read |
| --- | --- |
| Heartbeat, monitor cadence, thread continuation, duplicate heartbeat, or stop rule | `references/knowledge-capsules/pr-green-sweep-heartbeat-and-scope.md` |
| Latest head SHA, required checks, mergeability, review-thread state, stale evidence, or local-vs-remote readiness | `references/knowledge-capsules/pr-green-sweep-live-pr-evidence.md` |
| PR rotation queue, one-PR-at-a-time mutation, source-owned fixes, blocked lanes, waived external CI, or cleanup-only lanes | `references/knowledge-capsules/pr-green-sweep-action-queue.md` |
| Changed-path ownership, generated artifacts, validation output, docs, skills, CI config, or verifier selection | `references/knowledge-capsules/pr-green-sweep-validation-surface.md` |
| Push, CI rerun, merge, admin merge, force push, policy override, user decision, credentials, quota, or waiver boundary | `references/knowledge-capsules/pr-green-sweep-authorization-and-blockers.md` |
| Remote branch deletion, local branch deletion, worktree deletion, prune commands, merge proof, upstream state, or unique commits | `references/knowledge-capsules/pr-green-sweep-cleanup-proof.md` |

Waived external checks stay in `waived_external_ci`. They do not become green
checks, source failures, or stop conditions while non-waived action lanes remain.
