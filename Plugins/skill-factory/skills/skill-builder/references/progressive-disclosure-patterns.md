# Progressive disclosure patterns

Use these patterns to keep `SKILL.md` concise while enabling depth on demand.

Progressive disclosure is a signposting pattern, not a compression mandate:
- keep route-critical guidance in `SKILL.md`;
- preserve nuanced doctrine, caveats, and richer examples in `Infrastructure/references/`;
- explicitly point to the right reference when that deeper context is needed.

## Pattern 1: High-level guide with references

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [Infrastructure/references/FORMS.md](Infrastructure/references/FORMS.md) for complete guide
- **API reference**: See [Infrastructure/references/REFERENCE.md](Infrastructure/references/REFERENCE.md) for all methods
- **Examples**: See [Infrastructure/references/EXAMPLES.md](Infrastructure/references/EXAMPLES.md) for common patterns
```

## Pattern 2: Domain-specific organization

For skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── Infrastructure/references/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

Similarly, for skills supporting multiple frameworks or variants:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── Infrastructure/references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

## Pattern 3: Conditional details

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

## Guidelines

- Avoid deeply nested references; keep references one level deep from SKILL.md.
- For reference files longer than 100 lines, include a table of contents.
- If a detail changes the recommendation or safety posture, preserve it in `Infrastructure/references/` instead of summarizing it away.
- Add direct cues such as `Read when: <condition>` or `Use this reference for <specific task>` so the wrapper remains navigable.
