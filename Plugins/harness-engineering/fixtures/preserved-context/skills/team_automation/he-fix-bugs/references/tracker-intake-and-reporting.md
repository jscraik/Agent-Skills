# Tracker Intake And Reporting

Use this when bug reports originate from issue trackers and findings must remain traceable.

## Intake Priority
1. Linear issue ID or URL (preferred in this repo).
2. GitHub issue number or URL (fully supported).
3. Manual-context report when no tracker entry exists yet.

## Intake Minimum
- issue/source identifier,
- symptom and expectation,
- reproduction clues,
- environment clues,
- latest relevant comments.

If any critical element is missing, ask one focused blocker question before deeper investigation.

## Investigation Logging Contract
- preserve tracker source in notes (`linear`, `github`, or `manual-context`),
- preserve exact reproduction status (`confirmed`, `not_reproduced`, `partial`, `blocked`),
- map evidence back to commands/paths/events,
- keep remediation recommendation separate from intake summary.

## Reporting Back
- prepare concise tracker-ready update text after diagnosis.
- do not post externally without explicit user direction.
- include:
  - confirmed root cause summary,
  - reproduction status and key evidence,
  - minimal recommended fix direction,
  - test coverage recommendation.

## Privacy And Safety
- redact secrets, tokens, credentials, and personal data.
- avoid quoting sensitive payloads when a summary is enough.
