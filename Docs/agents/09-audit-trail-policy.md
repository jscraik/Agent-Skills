# Audit Trail Policy

## Table of Contents
- [Artifact rules](#artifact-rules)
- [Session hygiene](#session-hygiene)

## Artifact rules
- Use the current pull-request template and repository validation receipts for
  change evidence. Do not create AI prompt or session artifacts unless an active
  workflow or explicit task requires them.
- Use commit messages that describe purpose, not generic text.

## Session hygiene
- Do not include secrets in command output, notes, or docs.
- Log assumptions only when they affect execution risk.
