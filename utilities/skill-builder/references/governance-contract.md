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

`GATE-GRAPH-READINESS`
- Commands:
  - `python3 scripts/check-see-also.py . --changed-files <skill>/SKILL.md`
  - `python3 utilities/skill-builder/scripts/validate_skill_graph_profiles.py --repo-root . --expected-count 0`
- Pass criteria:
  - changed skills have a `## See Also` table with at least 2 real skill links
  - active/in-scope skill profiles validate cleanly
- Scope: graph traversal quality, task-profile completeness, and onboarding-contract integrity

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
- Progressive disclosure is a preservation pattern:
  - relocate nuanced doctrine, caveats, and examples into `references/`,
  - do not delete valuable context solely to satisfy line-count or wrapper-size goals.
- Reference docs should include trigger hints:
  - `Read when: <specific condition>`
- `SKILL.md` should signpost the preserved material clearly enough that the right reference is easy to open at the right time.

`POL-04 Template contract`
- Skill template must include a `## Gotchas` section by default.

`POL-05 Graph contract`
- For repo-owned operational skills, create graph scaffolding at source:
  - `## See Also` with related skill links,
  - one topic-map signpost,
  - `references/task-profile.json` when the onboarding contract applies.
- Do not defer graph wiring to a later cleanup pass when the relevant skill is being created or materially improved.

`POL-06 Python composability contract`
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

`EX-04 Graph onboarding scope`
- Skills outside the operational graph or explicitly excluded by inventory policy may omit `references/task-profile.json`.
- If omitted, say why in the change summary instead of silently skipping it.

## Completion criteria
- Required gates complete and passing according to scope.
- Any warning-level deferrals are documented with owner and priority.
- Output summary states:
  - gates run,
  - pass or fail status,
  - applied exceptions (if any),
  - next remediation step when anything is deferred.
