---
description: Session archive JSON files contain lifecycle metadata only, so session mining cannot extract user-correction patterns without transcript-level capture.
category: process-gap
status: reduced
observed: 2026-03-01
source: session-mining
reduced: 2026-03-03
session_source: ops/sessions/*.json (batch)
---

# Session archives are metadata-only and block friction mining

Mined 526 archived session JSON files under ops/sessions. The files include id/timestamps/status fields but no transcript content, corrections, or workflow evidence, so session-mining cannot derive methodology learnings from them.

This indicates the capture pipeline is recording session lifecycle events but not the conversational material needed for /remember --mine-sessions pattern detection.

---

Related: [[notes/session-transcript-capture-is-required-for-friction-mining]]
