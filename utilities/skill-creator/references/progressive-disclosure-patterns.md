# Progressive disclosure patterns

Use these patterns to keep SKILL.md concise while enabling depth on demand.

## Pattern 1: High-level guide with references

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [references/FORMS.md](references/FORMS.md) for complete guide
- **API reference**: See [references/REFERENCE.md](references/REFERENCE.md) for all methods
- **Examples**: See [references/EXAMPLES.md](references/EXAMPLES.md) for common patterns
```

## Pattern 2: Domain-specific organization

For skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── references/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

Similarly, for skills supporting multiple frameworks or variants:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
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
