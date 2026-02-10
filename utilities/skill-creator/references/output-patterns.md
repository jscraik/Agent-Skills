# Output Patterns (Gold Standard)

Use these patterns when skills must produce consistent, high-quality output.
Prefer deterministic formats, explicit schemas, and verifiable evidence.

## Normative Rules

- MUST define an output contract for any structured output.
- MUST include error handling for partial or failed results.
- SHOULD provide a schema with versioning for machine-readable outputs.

## Automation Mapping

- skill_gate.py: requires output-related sections in SKILL.md.
- analyze_skill.py: scores output specificity (non-gating).
- upgrade_skill.py: suggests contract/schema improvements.

## Output Contract (Required)

Define format, ordering, units, encoding, and compatibility up front.

```markdown
## Output contract
- Format: JSON
- Encoding: UTF-8
- Ordering: sort by id ascending
- Units: milliseconds
- Timezone: UTC
- Compatibility: backward compatible within major version
- Schema version: v1
```

## Output Contract Schema (Required for Structured Outputs)

- Store schemas at `references/schemas/<skill-name>.schema.json` (or `.yaml`).
- Include `schema_version` and follow SemVer (`MAJOR.MINOR.PATCH`):
  - **MAJOR**: breaking schema change
  - **MINOR**: backward-compatible additions
  - **PATCH**: clarifications / docs only
- Outputs MUST validate against the current schema version.

## Template Pattern

Provide a strict template when the format must be exact.

```markdown
## Report structure (strict)

ALWAYS use this exact structure:

# [Analysis Title]

## Executive summary
[One paragraph]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```

For flexible guidance, provide a default format and allow adjustments.

```markdown
## Report structure (flexible)

Default structure:
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on discoveries]

## Recommendations
[Tailor to context]
```

## Schema-First Pattern

Define a schema first, then emit data that conforms to it.

```markdown
## Output schema
```

```json
{
  "type": "object",
  "required": ["schema_version", "id", "title", "status", "risks"],
  "properties": {
    "schema_version": { "type": "string" },
    "id": { "type": "string" },
    "title": { "type": "string" },
    "status": { "type": "string", "enum": ["ok", "warn", "fail"] },
    "risks": { "type": "array", "items": { "type": "string" } }
  }
}
```

## Output (example)
```json
{
  "schema_version": "v1",
  "id": "task-123",
  "title": "Package skill",
  "status": "ok",
  "risks": []
}
```

## Deterministic Ordering

Specify sorting and grouping rules to keep outputs stable.

```markdown
## Ordering
- Sort keys alphabetically
- Sort items by created_at asc
- Group by status: ok, warn, fail
```

## Example Pair Pattern

Use input/output pairs to communicate style and depth.

```markdown
## Commit message format

Example 1
Input: Added user authentication with JWT tokens
Output:
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware

Example 2
Input: Fixed bug where dates displayed incorrectly
Output:
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

## Quality Checklist Pattern

Add a short checklist to enforce quality gates.

```markdown
## Quality checklist (must pass)
- Accuracy: claims supported by evidence
- Completeness: required sections present
- Safety/Privacy: no secrets, no PII exposure
- Accessibility: headings are semantic, code fences have language tags
```

## Provenance / Citations Pattern

Require sources for external data.

```markdown
## Sources
- Data source: [Name] (link)
- Date accessed: YYYY-MM-DD

## Notes
Cite sources inline with (Source: Name, Date).
```

## Redaction / Anonymization Pattern

Show how to remove or mask sensitive data.

```markdown
## Redaction rules
- Emails: replace with <redacted-email>
- IDs: hash with SHA-256 and truncate to 8 chars
- Names: replace with <redacted-name>
```

**MUST** redact sensitive data unless explicitly authorized and scoped.

## Error / Partial Results Pattern

Separate errors from results and be explicit about partial output.

```markdown
## Result
[Partial output]

## Errors
- Step 3 failed: timeout contacting service
- Data for region EU missing

## Next steps
- Retry with longer timeout
```

## Error Taxonomy (Required)

- Include `errors[]` with fields: `code`, `message`, `step`, `retryable`.
- Ensure partial outputs are clearly separated from errors.

## Change Report Pattern

Standardize change summaries for code edits or proposals.

```markdown
## Change summary
- What changed
- Why it changed

## Risk / impact
- Possible regressions
- Mitigations

## Verification
- Tests run
- Manual checks
```

## Accessibility Pattern

Call out accessibility requirements for UI or docs.

```markdown
## Accessibility
- Use semantic headings
- Provide alt text for images
- Ensure contrast in UI specs
```

## Length / Verbosity Controls

Offer short/medium/long variants for output size.

```markdown
If user asks "short":
- 3 bullets max, no extra sections

If user asks "detailed":
- Include full template + evidence section
```
