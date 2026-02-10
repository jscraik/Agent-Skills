# Workflow Patterns (Gold Standard)

Use these patterns to keep multi-step skills predictable, safe, and verifiable.
Prefer short, numbered steps with explicit gates and evidence.

## Normative Rules

- MUST define gates for fragile or high-risk steps.
- MUST stop on failed gate, report evidence, and propose the smallest fix.
- SHOULD include an evidence bundle for auditability.

## Gate Types (Standard)

- schema
- lint
- tests
- security
- a11y
- diff-review
- artifact-exists

## Automation Mapping

- skill_gate.py: requires workflow/validation sections in SKILL.md.
- analyze_skill.py: scores workflow clarity (non-gating).
- upgrade_skill.py: suggests workflow improvements.

## Universal Skeleton (Template)

```markdown
## Preflight
- Goal: [clear outcome]
- Inputs: [files, paths, ids]
- Constraints: [do not modify originals, time limit]
- Environment: [tooling/version checks]
- Questions: [only if needed]

## Definition of Done
- [Acceptance criteria]
- [Required artifacts]

## Plan
1. [Step]
   - Gate: [check or validation]
2. [Step]
   - Gate: [check or validation]

## Execute
- Run steps in order, stop on failed gate.

## Verify
- Tests/validation: [commands]
- Artifacts: [paths]
- Diagnostics: [logs, traces, error IDs]

## Deliver
- Summary of changes
- Risks/mitigations
- Next steps
```

## Planning with `$create-plan`

If the `$create-plan` skill is available, use it for non-trivial work before writing files, then store the output as a plan artifact (recommended: `references/plan.md`).

If `$create-plan` is not available, write an equivalent plan manually and store it the same way.

## Preflight (Required)

Capture inputs, constraints, and any required confirmations.

```markdown
## Preflight
- Inputs: report.csv, config.yml
- Constraints: no network calls, do not overwrite input files
- Environment: python3.11 available, ruff installed
- Ask: confirm output format if not specified
```

## Scope + Assumptions

List what is in scope and what is explicitly out of scope.

```markdown
## Scope
- In: normalize timestamps, fix header row
- Out: redesign schema, backfill missing data

## Assumptions
- Input is UTF-8
- Timezone is UTC unless specified
```

## Definition of Done

Make acceptance criteria explicit.

```markdown
## Definition of Done
- All gates pass
- Output artifact created at dist/report.json
- Summary + verification included in response
```

## Sequential Workflow with Gates

Insert a validation gate after each fragile step. Do not proceed on failure.

```markdown
## Workflow
1. Analyze input (run analyze_form.py)
   - Gate: analysis.json exists and non-empty
2. Create mapping (edit fields.json)
   - Gate: validate_fields.py passes
3. Apply changes (run fill_form.py)
   - Gate: verify_output.py passes
4. Deliver result
```

## Conditional / Decision Tree

Use decision points to steer the agent. Ask 1-2 questions when ambiguous.

```markdown
1. Determine task type:
   - New content? -> Creation workflow
   - Edit existing? -> Editing workflow
2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Parallelizable Steps

Call out steps that can run in parallel safely.

```markdown
## Parallel steps (safe to do together)
- Draft summary
- Prepare evidence section
- Collect risks/mitigations

Then merge into final output.
```

## Risk Classification + Confirmation

Require confirmation for destructive or high-risk actions.

```markdown
## Risk
- Low: formatting only
- Medium: modifies config values
- High: deletes data or migrates schema

If High, ask for explicit confirmation before proceeding.
```

## Resilience (Idempotency + Retry)

Define safe re-run behavior and retry policy for transient failures.

```markdown
## Resilience
- Idempotency: safe to re-run step 2 without side effects
- Retries: max 3, exponential backoff (1s, 2s, 4s)
- Timeouts: 30s per request
- Rate limits: honor Retry-After
```

## Failure + Rollback

Define recovery steps and rollback plan.

```markdown
If a gate fails:
1. Stop and report the failing step.
2. Include error output.
3. Propose the smallest fix.
4. If rollback exists, restore prior state and confirm.
```

## Evidence Capture

Record checks and artifacts for auditability.

```markdown
## Evidence
- Tests: pytest -q (pass)
- Lint: ruff check (pass)
- Diagnostics: logs/app.log, error-id: abc123
- Artifacts: dist/output.json
```

## Evidence Bundle (Required)

- Command(s) run
- Exit status
- Key output lines or artifacts
- Paths for logs and generated files

## Data Safety + Privacy

Add explicit rules when data is sensitive.

```markdown
## Data rules
- Do not log secrets or tokens
- Redact PII in outputs
- Minimize copied data
```
