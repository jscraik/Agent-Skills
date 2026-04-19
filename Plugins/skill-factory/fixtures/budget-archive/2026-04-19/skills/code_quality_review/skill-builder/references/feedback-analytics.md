# Feedback Analytics (Subjects + Outcomes)

## Table of Contents
- [Purpose](#purpose)
- [Event schema](#event-schema)
- [Recorder command](#recorder-command)
- [Scoreboard command](#scoreboard-command)
- [Subject taxonomy](#subject-taxonomy)

## Purpose

Track whether skill decisions improve outcomes over time, and segment quality by subject area (for example UI vs code review).

## Event schema

Feedback events are JSONL records at:

- `Infrastructure/ops/metrics/skill-feedback/decision-feedback.jsonl`

Required fields:

- `decision`: `accepted | partial | rejected | deferred`
- `outcome`: `good | neutral | bad | unknown`
- `confidence`: `high | medium | low`
- `skill_path`
- `skill_name`
- `subject`

## Recorder command

```bash
python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py \
  --workspace . \
  --skill-path frontend/ui/figma/SKILL.md \
  --decision accepted \
  --outcome good \
  --confidence high \
  --notes "Applied prompt narrowing; less hallucinated selectors"
```

## Scoreboard command

```bash
python3 Skills/skill-builder/Infrastructure/scripts/skill_subject_scoreboard.py --workspace . --format table
```

Optional markdown report:

```bash
python3 Skills/skill-builder/Infrastructure/scripts/skill_subject_scoreboard.py --workspace . --write-report
```

## Subject taxonomy

Inferred from skill path (override supported via `--subject`):

- `ui`
- `code_review`
- `backend`
- `security`
- `auth`
- `docs`
- `utilities`
- `specs`
- `ops`
- `strategy`
- `general`
