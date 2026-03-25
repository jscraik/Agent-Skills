# Progressive Disclosure Fix Queue

Prioritized remediation queue for high-severity progressive-disclosure findings.

## Table of Contents
- [Source](#source)
- [Priority order](#priority-order)
- [Execution checklist](#execution-checklist)

## Source

- Snapshot command: `bash scripts/lint_progressive_disclosure.sh --mode warn`
- Snapshot artifact: `/tmp/pd-lint.out`
- High-severity findings (5):
  - `frontend/tools/agentation/SKILL.md`: `SKILL.md exceeds hard cap (lines=488, cap=360)`
  - `frontend/tools/playwright-interactive/SKILL.md`: `many code fences (6) but scripts/ directory is missing`
  - `interview/interview-me/SKILL.md`: `SKILL.md exceeds hard cap (lines=398, cap=360)`
  - `utilities/cf-crawl/SKILL.md`: `many code fences (12) but scripts/ directory is missing`
  - `utilities/spreadsheet/SKILL.md`: `many code fences (6) but scripts/ directory is missing`

## Priority order

1. `P0` Reduce oversized `agentation` skill doc  
File: [frontend/tools/agentation/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/frontend/tools/agentation/SKILL.md)  
Why first: highest absolute overflow and broad usage surface.  
Fix target:
  - move deep setup/troubleshooting detail into `references/`
  - keep `SKILL.md` <= 360 lines (target <= 320)
  - preserve trigger clarity in frontmatter `description`

2. `P0` Reduce oversized `interview-me` skill doc  
File: [interview/interview-me/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/interview/interview-me/SKILL.md)  
Why second: hard-cap breach and central requirement-discovery workflow impact.  
Fix target:
  - move question-bank detail to `references/discovery-rounds.md`
  - keep response envelope and trigger logic in `SKILL.md`

3. `P1` Externalize mechanics for `cf-crawl`  
File: [utilities/cf-crawl/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/utilities/cf-crawl/SKILL.md)  
Why third: highest code-fence count (`12`) with no `scripts/`.  
Fix target:
  - create `scripts/` for repeatable command sequences
  - trim inline fenced blocks; leave short examples only

4. `P1` Externalize mechanics for `playwright-interactive`  
File: [frontend/tools/playwright-interactive/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/frontend/tools/playwright-interactive/SKILL.md)  
Why fourth: code-fence threshold breach with missing `scripts/`.  
Fix target:
  - add `scripts/` helper stubs for common launch/debug patterns
  - keep only interface-level examples inline

5. `P1` Externalize mechanics for `spreadsheet`  
File: [utilities/spreadsheet/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/utilities/spreadsheet/SKILL.md)  
Why fifth: same breach pattern as above with smaller blast radius.  
Fix target:
  - add `scripts/` helper(s) for deterministic spreadsheet workflows
  - reduce inline fence count below hard threshold

## Execution checklist

- After each file/class fix: run `bash scripts/lint_progressive_disclosure.sh --mode warn`.
- After the full queue: run `bash scripts/validate_all.sh`.
- Keep OpenAI skill format contract intact:
  - required frontmatter: `name`, `description`
  - optional-only top-level keys: `license`, `allowed-tools`, `metadata`
