## Simplification Analysis

### Core Purpose
The goal-governor review-mode guard slice needs to reliably route prompt-readiness requests into `review` mode, prevent execution-side effects, and keep board/runtime safety checks clear.

### Unnecessary Complexity Found
- medium - [Skills/agent-ops/goal-governor/SKILL.md:69](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:69)
- The same policy is repeated across both `Non-Optional Checklist` and `Response Requirements` (for `review`, `continue`, and `doctor`), creating two truth surfaces that can drift.
- Suggested simplification: keep one canonical normative block (preferably `Response Requirements`) and reduce the other section to pointers or terse reminders.

- medium - [Skills/agent-ops/goal-governor/SKILL.md:155](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:155)
- Doctor mode is constrained by both semantic requirements and an exact six-line literal template with duplicated phrase constraints nearby (`145-153`, `155-161`), which is stricter than needed for behavior and increases maintenance burden.
- Suggested simplification: keep one structured requirement source (either checklist labels or exact prelude template), not both.

- low - [Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:28](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:28)
- The test hard-codes many exact UI/wording fragments (for example, `no PR`, `no CI`) after whitespace normalization, which couples test validity to prose phrasing rather than contract semantics.
- Suggested simplification: validate against the machine contract in `references/contract.yaml` plus a smaller set of sentinel phrases; avoid asserting every wording token from SKILL prose.

- low - [Skills/agent-ops/goal-governor/references/contract.yaml:33](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/references/contract.yaml:33)
- `output_contract.required_fields` includes continuation-oriented fields (`goal_path`, `native_goal_status`) while review mode has a separate required-field contract; this split is correct, but it leaves an ambiguous “which list wins” reading path.
- Suggested simplification: add an explicit mode-conditional note under `output_contract` saying review mode uses `review_mode_contract.required_fields` instead.

### Code to Remove
- [Skills/agent-ops/goal-governor/SKILL.md:69](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:69) - collapse duplicated rule text now repeated later in [Skills/agent-ops/goal-governor/SKILL.md:115](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:115)
- Estimated LOC reduction: 25-45 lines

- [Skills/agent-ops/goal-governor/SKILL.md:145](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:145) - remove adjacent duplicate phrase-level doctor constraints once one canonical format is retained
- Estimated LOC reduction: 10-18 lines

- [Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:28](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:28) - trim phrase lock list to contract-level sentinel checks
- Estimated LOC reduction: 8-16 lines

### Simplification Recommendations
1. Consolidate SKILL normative rules into one canonical section
   - Current: duplicated obligations across `Non-Optional Checklist` and `Response Requirements`.
   - Proposed: one normative section + one short “quick checklist” reference section.
   - Impact: lower drift risk, easier future edits, approximately 35 LOC saved.

2. Keep one doctor format authority
   - Current: both phrase requirements and exact six-line prelude are simultaneously required.
   - Proposed: retain exact six-line prelude as sole format authority, remove duplicate phrase mandates.
   - Impact: less brittle writing constraints, approximately 12 LOC saved.

3. Contract-first tests over prose-lock tests
   - Current: prose wording is asserted heavily in test.
   - Proposed: assert contract keys and route semantics from `contract.yaml` and `evals.yaml`, with only 2-3 sentinel SKILL phrases.
   - Impact: fewer false failures on harmless prose refactors, approximately 10 LOC saved.

### YAGNI Violations
- Over-specified prose locking in tests ([test_check_goal_board.py:28](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:28)).
- Why YAGNI: guarding every wording token is not required to guarantee review-mode behavior.
- Do instead: verify behavior contracts and route/eval semantics, not exhaustive wording.

- Dual normative blocks in SKILL ([SKILL.md:69](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:69), [SKILL.md:115](/Users/jamiecraik/dev/agent-skills/Skills/agent-ops/goal-governor/SKILL.md:115)).
- Why YAGNI: maintaining two full policy surfaces adds maintenance work without adding safety guarantees.
- Do instead: one source of truth and a short summary pointer.

### Final Assessment
Total potential LOC reduction: approximately 12-20% in this slice (primarily SKILL prose + one test)
Complexity score: Medium
Recommended action: Proceed with simplifications

WROTE: .harness/reviews/2026-05-21-jsc-329-goal-governor/simplify.md
