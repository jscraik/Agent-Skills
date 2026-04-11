# Operating Routine

## Table of Contents
- [Purpose](#purpose)
- [Session Start](#session-start)
- [During Work](#during-work)
- [Task Completion](#task-completion)
- [File Placement Rules](#file-placement-rules)
- [Decision and Quality Checks](#decision-and-quality-checks)
- [Review Cadence](#review-cadence)
- [Anti-Patterns](#anti-patterns)

## Purpose
Use this guide after Project Brain is bootstrapped. It defines how Codex should read, apply, and update Project Brain during normal repository work.

## Session Start
1. Read `.harness/memory/LEARNINGS.md`
2. If entering a new domain, read `.harness/knowledge/INDEX.md`
3. For significant choices, read relevant files under `.harness/decisions/`
4. Before completion, read `.harness/quality/criteria.md`

## During Work
- Check knowledge before writing new patterns
- Apply active rules unless contradicted by new evidence
- Gather confirming or refuting evidence for open hypotheses
- Prefer updating an existing entry over duplicating insights

Decision lookup helpers:

```bash
rg -l "Decision:" .harness/decisions/ | head -5
rg "{topic}" .harness/decisions/
```

## Task Completion
At the end of each task:
1. Record repo-specific learnings
2. Update domain knowledge for confirmed facts
3. Record or revise hypotheses for unconfirmed theories
4. Promote repeated patterns to rules when evidence is sufficient
5. Record significant decisions
6. Add or update quality criteria for recurring failure patterns
7. Update `.harness/knowledge/INDEX.md` when new domains are added

## File Placement Rules
- `.harness/memory/LEARNINGS.md`: repo-specific gotchas and fixes
- `~/.codex/instructions/Learnings.md`: cross-repo universal learnings
- `.harness/knowledge/{domain}/knowledge.md`: confirmed domain facts
- `.harness/knowledge/{domain}/hypotheses.md`: theories pending evidence
- `.harness/knowledge/{domain}/rules.md`: promoted recurring rules
- `.harness/decisions/YYYY-MM-DD-{topic}.md`: significant durable decisions
- `.harness/quality/criteria.md`: project completion checks
- `.harness/review-log.md`: periodic system reviews

## Decision and Quality Checks
Create a decision record when:
- Multiple valid options exist
- Choice sets a future pattern
- Trade-offs extend beyond the current task
- A previous decision is being replaced

Before marking complete:
- Read relevant quality criteria
- Evaluate criteria applicable to current task
- Capture new recurring failure patterns

## Review Cadence
Recommend Project Brain review when:
- Two or more weeks since last review
- Project milestone reached
- Major initiative starting
- Quality criteria triggered repeatedly

Record reviews in `.harness/review-log.md`.

## Anti-Patterns
- Duplicating content across Project Brain files
- Adding quality criteria without evidence
- Making significant decisions without checking prior records
- Leaving hypotheses stale without promote/revise/archive
- Treating repo-specific learnings as universal
- Using `--force` bootstrap when normal file edits are sufficient
