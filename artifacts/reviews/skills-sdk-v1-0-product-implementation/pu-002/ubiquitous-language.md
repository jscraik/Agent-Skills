schema_version: 1
execution_mode: ubiquitous_language_review
scope: PU-002 schema spine and goal receipts
findings: []
language_checks:
  - "Uses Skills SDK as the product facade term and keeps ./bin/ask as the repo control plane in notes and receipts."
  - "Uses receipt, risk classification, install preview, lockfile preview, and placeholder lifecycle consistently with the implementation plan."
  - "Separates canonical source from runtime projection in manifest-source schema fields."
  - "Keeps PR state, local validation, merge proof, pulled-main proof, and review evidence as separate truth lanes."
  - "Avoids claiming subagent review completion; codex-review notes the coordinator-only review status."
deferred_terms:
  - "Facade command vocabulary belongs to PU-003."
  - "Install promotion and rollback vocabulary belongs to PU-005."
validation:
  - "Goal board validator passed with PU-001 merge proof and PU-002 active."
status: pass_no_findings
