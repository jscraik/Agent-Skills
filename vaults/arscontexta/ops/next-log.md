# /next recommendation log

## 2026-02-27 18:02 UTC

**State:** Inbox: 0 | Notes: 0 | Orphans: 0 | Dangling: 0 | Stale: 0 | Obs: 0 | Tensions: 0 | Queue: 0 | Sessions: 262
**Recommended:** /remember --mine-sessions
**Rationale:** 262 unprocessed sessions are accumulating uncaptured context; mining them restores continuity and prevents methodology drift.
**Priority:** session


## 2026-02-28 18:02 UTC

**State:** Inbox: 0 | Notes: 0 | Orphans: 0 | Dangling: 0 | Stale: 0 | Obs: 0 | Tensions: 0 | Queue: 0 | Sessions: 527
**Recommended:** /remember --mine-sessions
**Rationale:** Session backlog rose to 527 unprocessed files (up from 262), making this the highest-impact unblock to recover context and reduce methodology drift.
**Priority:** session

## 2026-03-01 18:03 UTC

**State:** Inbox: 0 | Notes: 0 | Orphans: 0 | Dangling: 0 | Stale: 0 | Obs: 0 | Tensions: 0 | Queue: 0 | Sessions: 527 | Goals: missing
**Recommended:** Create /Users/jamiecraik/dev/configs/vaults/arscontexta/ops/goals.md
**Rationale:** The prior two /next runs already recommended /remember --mine-sessions; to avoid recommendation loop and improve alignment quality, define explicit goals first so subsequent automation can prioritize which session backlog to mine first.
**Priority:** session

## 2026-03-03 18:02 UTC

**State:** Inbox: 0 | Notes: 0 | Obs: 1 | Tensions: 0 | Queue: 0 | Sessions(unmined): 1 (current.json)
**Recommended:** /reduce ops/observations/session-archives-are-metadata-only-need-transcript-capture.md
**Rationale:** Queue and inbox pressure are clear, but a pending process-gap observation remains and goals prioritize turning mined insights into durable notes; reducing this observation creates the first actionable note and unblocks meaningful graph growth.
**Priority:** multi-session

## 2026-03-04 18:02 UTC

**State:** Inbox: 0 | Notes: 1 | Obs: 0 | Tensions: 0 | Queue: 0 | Sessions(unmined): 1 (current.json) | Health: 1 FAIL (Link Health), 1 WARN (Schema)
**Recommended:** Fix the dangling link flagged in /Users/jamiecraik/dev/configs/vaults/arscontexta/ops/observations/session-archives-are-metadata-only-need-transcript-capture.md (line 19)
**Rationale:** Link-health failures are session-priority because broken traversal paths reduce retrieval reliability immediately; clearing this blocker keeps the first note+observation chain trustworthy before additional capture work.
**Priority:** session

## 2026-03-05 18:05 UTC

**State:** Inbox: 0 | Notes: 1 | Obs: 0 | Tensions: 0 | Queue: 0 | Sessions(unmined): 1 (current.json) | Health: 0 FAIL, 0 WARN
**Recommended:** /remember --mine-sessions
**Rationale:** With no queue or inbox pressure and goals prioritizing continued session-backlog reduction, mining the remaining unprocessed session keeps momentum toward producing additional durable notes from session-derived evidence.
**Priority:** multi-session

## 2026-03-07 18:08 UTC

**State:** Inbox: 0 | Notes: 1 | Queue: 2 pending maintenance | Dangling: 2 | Obs: 0 | Tensions: 0 | Sessions(unmined): 1 (current.json) | Health: 0 FAIL, 0 WARN in latest note-scan report
**Recommended:** Replace the process-gap link token with plain text in ops/health/2026-03-05-report.md and ops/health/2026-03-05-report-2.md
**Rationale:** Two dangling links remain in historical health reports, which makes vault traversal unreliable even though the latest note-scan health report is clean. Fixing them restores trustworthy retrieval before you either re-run `/health` or resume session-capture work tied to your goals.
**Priority:** session

## 2026-03-08 18:09 UTC

**State:** Inbox: 0 | Notes: 1 | Orphans: 1 | Dangling: 0 | Stale: 0 | Obs: 0 | Tensions: 0 | Queue: 2 (session maintenance: 1, slow maintenance: 1)
**Recommended:** /reduce ops/observations/session-archives-are-metadata-only-need-transcript-capture.md
**Rationale:** The vault is still in the 0-5 note stage (1 note total), so adding durable content is higher leverage than maintenance-only work. Reducing this process-gap observation into a full note improves graph growth immediately and prevents early over-optimization on structure.
**Priority:** session

## 2026-03-10 18:12 UTC

**State:** Inbox: 0 | Notes: 1 | Orphans: 1 | Dangling: 4 | Stale: 0 | Obs: 1 | Tensions: 0 | Queue: 2 (session maintenance: 1, slow maintenance: 1) | Sessions: 527 | Goals stale days: 9
**Recommended:** /remember --mine-sessions
**Rationale:** Unprocessed sessions are the largest active pressure signal by far (527), and your goals explicitly prioritize reducing this backlog before follow-on synthesis. Processing sessions now yields the highest immediate recovery in context continuity and reduces compounding maintenance drift across the next few cycles.
**Priority:** session
