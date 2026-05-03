# Source Review

This skill was informed by `https://github.com/vibeforge1111/keep-codex-fast.git` at commit `7fa4ed5b7c109779e3f8d32afce7996719124f7a`.

Borrowed ideas:
- report-only first pass
- handoff-first archival
- backup-before-apply
- archive instead of delete
- restore manifests for moved sessions
- recurring reminders should be report-only

Changed for this repo:
- apply requires `--confirm-codex-home`
- failed process detection blocks apply
- config pruning is split from default apply
- command output is shaped around Harness Engineering evidence: current state, decision, action, verification, and handoff
- skill context is shorter, with detail moved into references
