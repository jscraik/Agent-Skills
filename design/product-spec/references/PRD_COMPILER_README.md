# spec_to_prd compiler

Drop `scripts/ralph/spec_to_prd.py` into your repo.

Run:
  python3 scripts/ralph/spec_to_prd.py --spec .spec/spec-YYYY-MM-DD-foo.md --out prd.json --strict

Contract:
- PRD title heading: `# PRD: <name>`
- Stories must use stable ids: STORY-001, STORY-002...
- Story header formats supported:
  - `1) **Story [STORY-001]:** As a ...`
  - `### STORY-001 — As a ...`
- Acceptance criteria must be `- [ ] ...` under `**Acceptance criteria:**`
- Priority must be `**Priority:** Must|Should|Could`

State preservation:
- preserves: status, passes, startedAt, completedAt, attempts, lastError
- regenerates: title, priority, acceptanceCriteria, tests
