# Skill Builder Governance Contract

## Table of Contents
- [Purpose](#purpose)
- [Gate set](#gate-set)
- [Policy clauses](#policy-clauses)
- [Exceptions](#exceptions)
- [Completion criteria](#completion-criteria)

## Purpose
Define compact, enforceable quality rules for skill authoring and improvement work in this repository.

## Gate set
Run these gates before claiming completion for `create` or `improve` work.

`GATE-OPENAI-FORMAT`
- Command: `bash scripts/lint_openai_skill_format.sh --mode strict`
- Pass criteria: `Errors: 0`
- Scope: frontmatter contract (`name`, `description`, optional key whitelist)

`GATE-PROGRESSIVE-DISCLOSURE`
- Command: `bash scripts/lint_progressive_disclosure.sh --mode warn`
- Pass criteria: no hard-cap or structural errors; warnings are triaged with explicit remediation plan
- Scope: concise `SKILL.md`, key section presence, helper-material placement

`GATE-GOTCHA-GOVERNANCE`
- Command: `python3 scripts/gotcha_pipeline.py validate`
- Pass criteria: validation success with no contract violations
- Scope: gotcha structure and candidate-governance integrity

`GATE-SEMANTIC-TAGS` (only when tags changed)
- Commands:
  - `bash scripts/sync_skills.sh`
  - `bash scripts/lint_skill_types.sh`
- Pass criteria: `Missing: 0` and `Invalid: 0`
- Scope: taxonomy integrity and generated index consistency

## Policy clauses
`POL-01 Voice contract`
- Use hybrid instructional voice in skill body sections:
  - preferred pattern: `Do X because Y`
- Keep frontmatter `description` routing-first:
  - define what the skill does and when it should trigger
  - avoid procedural walkthrough language in `description`

`POL-02 Gotchas contract`
- Every `SKILL.md` must include `## Gotchas`.
- Gotchas should be concrete and actionable:
  - `Symptom -> Cause -> Do instead -> Check`

`POL-03 Progressive disclosure contract`
- `SKILL.md` stays concise and route-critical.
- Deep mechanics belong in `references/` or `scripts/`.
- Reference docs should include trigger hints:
  - `Read when: <specific condition>`

`POL-04 Template contract`
- Skill template must include a `## Gotchas` section by default.

`POL-05 Python composability contract`
- For reusable, importable module-style scripts:
  - include `__all__` exports,
  - include type hints on public APIs,
  - include module-level `Use when:` docstring guidance,
  - keep `__main__` blocks safe and non-destructive by default.

## Exceptions
`EX-01 frontmatter description`
- Exception rule: no exception for procedure-heavy descriptions.
- Required action: rewrite to routing-first wording before completion.

`EX-02 Python __all__`
- `__all__` is not mandatory for standalone CLI entrypoint scripts.
- Exemption applies when the script is not designed for import/reuse and has a clear `main` flow.

`EX-03 Progressive-disclosure warnings`
- Warning-only findings can ship only with explicit triage notes and prioritized fix queue.
- Hard-cap and schema failures do not qualify for warning-only treatment.

## Completion criteria
- Required gates complete and passing according to scope.
- Any warning-level deferrals are documented with owner and priority.
- Output summary states:
  - gates run,
  - pass or fail status,
  - applied exceptions (if any),
  - next remediation step when anything is deferred.
