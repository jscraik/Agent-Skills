# Error Messages And Recovery

Write developer-facing errors that preserve cause, name invalid input and constraints, explain recovery, fit the audience, and support diagnosis.

Pack id: pack.developer-advocate-writing
Facet id: error_messages_and_recovery
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.creator-writing.error-messages-enable-recovery: Error Messages Enable Recovery

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Error messages should report failures, preserve root cause, identify the cause or invalid input, state relevant constraints, and tell users how to recover.

Interpretation notes:
- Treat error text as recovery writing, not merely notification text.

### claim.creator-writing.error-messages-need-diagnostic-identifiers: Error Messages Need Diagnostic Identifiers

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Error codes and stable identifiers help support and engineering teams trace, monitor, and document failures even when message wording changes.

Interpretation notes:
- Keep user-facing recovery text separate from operator-facing identifiers when the audiences differ.

### claim.creator-writing.error-message-craft-preserves-signal: Error Message Craft Preserves Signal

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Error messages should be concise without becoming cryptic, fit the audience, use consistent terms, remain readable and accessible, and avoid blame, humor, or performative apology.

Interpretation notes:
- Editing an error message should improve diagnostic signal instead of sanding away the useful details.

### claim.creator-writing.audience-gap-defines-document: Audience Gap Defines Document

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A useful document is shaped by what its audience already knows, what they need to learn, and what task or decision the document supports.

Interpretation notes:
- Scope, prerequisites, and key points should appear early enough to orient busy readers.

### claim.creator-writing.accessible-docs-benefit-everyone: Accessible Docs Benefit Everyone

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Accessible documentation helps readers with permanent, temporary, situational, visible, and invisible disabilities, and often improves usability for everyone.

Interpretation notes:
- Apply accessibility expectations to docs, comments, UI copy, CLI help, and error messages.

## Principles

### principle.creator-writing.error-messages-are-recovery-paths: Error Messages Are Recovery Paths

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.error-messages-enable-recovery, claim.creator-writing.error-messages-need-diagnostic-identifiers, claim.creator-writing.error-message-craft-preserves-signal

A good error message is a recovery path for the user and a diagnostic path for support and engineering.

Rationale: The error-message source material joins cause, invalid input, constraints, fixes, examples, codes, identifiers, formatting, audience fit, accessibility, and tone.

Application notes:
- Preserve cause before polishing tone.
- Include actual and expected values when comparison helps recovery.
- Pair user-facing fixes with stable operator-facing identifiers when needed.

## Heuristics

### heuristic.creator-writing.show-actual-expected-fix: Show Actual Expected Fix

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.error-messages-enable-recovery

When a user can fix a failure, show what happened, the actual value, the expected constraint, and the next action.

Use when:
- The failure involves user input, config, permissions, quota, syntax, or structured data.
- A vague message would send the reader to logs or support.
- The fix is known and safe to suggest.

Avoid when:
- Revealing the actual value or root cause would expose secrets or create a security risk.

### heuristic.creator-writing.concise-not-cryptic: Concise Not Cryptic

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.error-message-craft-preserves-signal

Shorten an error until only recovery-critical words remain, then stop before the message loses cause, constraint, or fix information.

Use when:
- The message contains boilerplate, passive phrasing, repetition, or apology.
- The message is long enough that users may skip it.
- The error appears in a constrained UI or CLI surface.

Avoid when:
- Concision would remove the only clue that lets users recover.

## Checklists

### checklist.creator-writing.error-message-editing-pass: Error Message Editing Pass

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.error-messages-enable-recovery, claim.creator-writing.error-messages-need-diagnostic-identifiers, claim.creator-writing.error-message-craft-preserves-signal

- [ ] Report the failure instead of failing silently.
- [ ] Name the cause without swallowing root cause.
- [ ] Show invalid input when it helps the user recover.
- [ ] State the actual value, expected value, limit, or constraint when useful.
- [ ] Explain how to fix the problem.
- [ ] Add an example when the valid shape is hard to infer.
- [ ] Keep the message concise but not cryptic.
- [ ] Avoid double negatives and exceptions to exceptions.
- [ ] Match terminology and detail to the target audience.
- [ ] Use consistent terms and formats for similar product-area errors.
- [ ] Link or progressively disclose long explanations.
- [ ] Place code or config diagnostics near the failure location.
- [ ] Ensure meaning does not depend on color alone.
- [ ] Keep tone neutral, positive, non-blaming, and non-humorous.
- [ ] Include stable error codes or identifiers when support and engineering need to look up failures.

## Rubrics

### rubric.creator-writing.error-message-readiness: Error Message Readiness

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.error-messages-enable-recovery, claim.creator-writing.error-messages-need-diagnostic-identifiers, claim.creator-writing.error-message-craft-preserves-signal

- specificity: Does the error name the cause and relevant context?
  - pass: The message identifies what failed and includes invalid input, actual value, or violated constraint when useful.
  - fail: The message uses vague labels such as invalid input or server error without useful context.
- recoverability: Does the reader know what to do next?
  - pass: The message gives a fix, valid example, documentation link, or next step.
  - fail: The message stops at failure notification.
- diagnostic-value: Can support or engineering trace the failure?
  - pass: The message or surrounding payload includes a stable code, identifier, or evidence pointer when appropriate.
  - fail: The failure cannot be matched reliably across UI, logs, or support reports.
- craft: Does the wording preserve signal while staying readable?
  - pass: The message is concise, audience-fit, consistent, accessible, neutral, and non-blaming.
  - fail: The message is wordy, cryptic, inconsistent, color-dependent, joking, apologetic, or blame-heavy.

## Lenses

### lens.creator-writing.reader-access-and-recovery: Reader Access And Recovery Lens

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.creator-writing.audience-gap-defines-document, claim.creator-writing.accessible-docs-benefit-everyone, claim.creator-writing.error-messages-enable-recovery

- Start from the reader's goal, prior knowledge, constraints, and access needs.
- Treat clarity, accessibility, and recoverability as writing quality, not afterthoughts.
- Preserve the information a reader needs to act: scope, cause, actual value, expected constraint, example, or next step.
- Check whether meaning survives without color, perfect context, expert vocabulary, or visual inspection.
- Keep generated or AI-assisted wording accountable to audience fit, correctness, and final human judgment.
