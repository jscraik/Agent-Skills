# Cf-Crawl Discovery Interview

Use this only when required inputs are missing.

## Intuitive round-1 question
- Question: "Do you want to start a new crawl, check status, cancel a running crawl, or export an existing job?"
- Why this matters: action type determines whether we need a target URL or a job ID.
- Generic fallback phrasing for shared discovery harnesses: "What should this skill help you do?"

## Request user input mini-templates
- Start template: "Should we start a crawl from `<url>` with `<limit>` pages and export `<markdown|json|both>`?"
- Status template: "Please share the crawl job ID so I can check status and summarize skipped/disallowed pages."
- Export template: "Should I export completed pages only or also create a merged digest file?"

## Copy paste payload examples
- Start payload:
```json
{
  "action": "start",
  "target_url": "https://example.com/docs",
  "limit": 25,
  "output_format": "markdown"
}
```

- Status payload:
```json
{
  "action": "status",
  "job_id": "abc123"
}
```

- Export payload:
```json
{
  "action": "export",
  "job_id": "abc123",
  "output_format": "json",
  "output_dir": ".crawl-output/example-docs",
  "merge_digest": true
}
```
