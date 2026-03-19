---
description: Friction mining quality depends on transcript-level session capture rather than lifecycle metadata alone.
category: process-design
status: open
created: 2026-03-03
source: ops/observations/session-archives-are-metadata-only-need-transcript-capture.md
topics:
  - "process-gap"
  - "session-capture"
  - "friction-mining"
---

# Session transcript capture is required for friction mining

## Table of Contents
- [Claim](#claim)
- [Why it matters](#why-it-matters)
- [Evidence](#evidence)
- [Next step](#next-step)

## Claim

Session archives that only store lifecycle metadata (id, timestamps, status) cannot support `/remember --mine-sessions` pattern extraction.

## Why it matters

Without transcript-level content, the vault can mark sessions as mined but still fail to produce methodology learnings, so backlog reduction appears successful while insight generation remains blocked.

## Evidence

A batch mining run processed 526 archived session JSON files and found only metadata fields, producing a single process-gap observation instead of correction-pattern learnings.

## Next step

Add transcript or correction-event capture to the session pipeline, then rerun `/remember --mine-sessions` on new sessions to validate extraction quality.
