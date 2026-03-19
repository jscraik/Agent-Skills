---
name: cf-crawl
description: Crawl websites with Cloudflare Browser Rendering's /crawl API and export markdown or JSON results locally. Use when a user needs an authenticated Cloudflare crawl job started, monitored, or exported; do not use it for generic scraping or browser automation outside Cloudflare.
metadata:
  skill-type: data_fetch_analysis
---

# Cloudflare Crawl

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Authentication preflight](#authentication-preflight)
- [Workflow](#workflow)
- [Script helpers](#script-helpers)
- [Verification](#verification)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Remember](#remember)

## Standards snapshot
- Route only Cloudflare Browser Rendering crawl work here.
- Require a Cloudflare API token with `Browser Rendering Edit` permission.
- Verify Cloudflare auth before any live API call.
- Prefer bounded crawl jobs with explicit limits, include/exclude boundaries, and output paths.
- Export results locally with source URLs preserved so later agents can audit provenance.
- Vary response shape by action (`start`, `status`, `export`) instead of reusing one generic template.

## When to use
- Crawl a documentation site, knowledge base, or other web property through Cloudflare's `/crawl` API.
- Start a new crawl job, poll an existing job, or export finished crawl records.
- Save crawl results as markdown or JSON for later local analysis.
- Tune include/exclude controls, crawl depth, render behavior, and export layout.

## When not to use
- Generic scraping that should use Playwright, `agent-browser`, or a one-off HTTP fetch instead.
- Cloudflare deployment, Workers, Pages, or platform-routing work with no crawl job involved.
- UI cloning or visual replication planning requests: use `ui-cloner` after crawl context is gathered.
- Tasks that cannot provide Cloudflare account access and a token with Browser Rendering permissions.
- Requests to scrape private or unauthorized targets.

## Required inputs
- Requested action: `start`, `status`, `export`, or `cancel`.
- Target URL for new jobs or an existing crawl job ID.
- Desired output format: markdown, JSON, or both.
- Crawl bounds and behavior (if provided):
  - `limit` (max pages).
  - `depth` (max crawl depth).
  - `source` (`all`, `sitemaps`, `links`).
  - `render` mode (`true` default, `false` for fast static fetch).
  - `formats` (`html`, `markdown`, `json`).
  - `options` for discovery scope:
    - `includePatterns`, `excludePatterns`
    - `includeExternalLinks`, `includeSubdomains`
  - cache/rerun controls: `maxAge`, `modifiedSince`
  - JSON extraction tuning: `jsonOptions`.
  - optional runtime overrides such as `userAgent`, `rejectResourceTypes`, `gotoOptions`, `waitForSelector`, `authenticate`, `setExtraHTTPHeaders`.
- Export preferences: per-page files only or per-page plus merged digest.
- Cloudflare auth context: `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.

## Discovery interview
- Use discovery only when action, scope, or output expectations are unclear.
- Ask one round at a time; do not dump a full interview plan in one message.
- Use plain-language questions with 2-3 concrete options.
- Include one short sentence for why this matters in every round.
- Explain why the round matters in one short sentence before moving to the next round.
- Avoid dumping the whole interview plan at once.
- Use `references/discovery-interview.md` for reusable mini-templates and payload examples.

## Deliverables
- A crawl launch, status summary, or export plan matched to the requested action.
- Exact API call shapes for start, poll, and result export steps.
- Local output path plus counts for completed, skipped, disallowed, errored, or cancelled pages when results were exported.
- Clear blocker notes if auth, policy, or crawl limits prevent execution.
- If the user wants structured output, return the JSON contract in this file's Output contract section.

## Failure mode
- If auth is missing, stop after the auth preflight and say exactly which variable is absent.
- If the requested action is unclear, stop and ask whether the user wants `start`, `status`, or `export`.
- If the user only needs Cloudflare product routing, hand off to `cloudflare-deploy` instead of forcing crawl advice.
- If the user asks for visual cloning/adaptation guidance, hand off to `ui-cloner` and pass crawl artifacts forward.
- If policy, network, or account limits block a live crawl, report the blocker and preserve the lowest-risk next step.

## Output contract
Use this shape when the user asks for structured output:

```json
{
  "schema_version": 1,
  "action": "start|status|export",
  "job_id": "string|null",
  "status": "queued|running|completed|errored|cancelled_due_to_limits|cancelled_due_to_timeout|cancelled_by_user|unknown",
  "counts": {
    "completed": 0,
    "skipped": 0,
    "disallowed": 0,
    "errored": 0,
    "cancelled": 0
  },
  "output_path": "string|null",
  "blocker": "string|null",
  "next_step": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Set `job_id` and `output_path` to `null` when unavailable.
- Use `status: unknown` when a network or auth failure prevents status resolution.
- Keep `blocker` short and actionable, for example `missing CLOUDFLARE_API_TOKEN`.

Create responses are returned as a compact object where `result` is the crawl job ID string (not an object), for example `{"success": true, "result": "<crawl-job-id>"}`.

## Philosophy
- Keep crawl jobs bounded, authenticated, and auditable.
- Prefer provenance-rich local exports over one-line success claims.
- Route away quickly when the request is browser automation, deployment, or a single HTTP fetch.

## Authentication preflight
1. Check whether `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` are already set and non-placeholder values.
2. If either value is missing, inspect `.env`, `.env.local`, and `~/.env` in that order.
3. Parse only the two required keys; never `eval` untrusted `.env` content.
4. Confirm the token scope is intended for Browser Rendering access before issuing `POST` or `GET` calls.
5. If a crawl request returns `Authentication error`, treat that as a token-permission blocker and stop.

Safe parse is externalized to `scripts/cf_crawl_api.sh env-check`, which checks required variables and placeholder values without evaluating untrusted `.env` content.

If credentials are still missing, stop and ask the user to provide them through their environment or an approved secrets workflow.

## Workflow
1. Confirm whether the user wants to start a new crawl, inspect an existing job, cancel a job, or export prior results.
2. Normalize the action plan:
- `start`: requires `target_url`.
   - `status`: requires `job_id`.
- `cancel`: requires `job_id` (and optional confirmation language before performing destructive operations).
- `export`: requires `job_id`, `output_dir`, and output format.
3. Normalize crawl defaults:
   - default output `formats` to `html` unless the user explicitly asks for markdown or JSON.
   - set an explicit page `limit` (Cloudflare default is 10).
   - use `render: false` for clearly static sites when speed and browser-budget efficiency matter.
   - default `source` to `all` unless user asks otherwise.
   - add include/exclude controls only when the user names clear boundaries.
4. Start a crawl job with `scripts/cf_crawl_api.sh start --payload <payload.json>` when action is `start`.
5. Poll the crawl job with `scripts/cf_crawl_api.sh status --job-id <job_id>` when action is `status` or `export` until terminal.
6. Inspect category-specific records (for example skipped or disallowed URLs) with `scripts/cf_crawl_api.sh page-status --job-id <job_id> --status skipped --cursor <cursor>`.

7. Pull final export records with status filtering and cursor pagination (for example `status=completed`, `status=skipped`, `status=disallowed`, `status=errored`, `status=cancelled`).
8. Save each completed page to a bounded local directory. Include the source URL in the file header, use deterministic filenames, and surface any disallowed, skipped, errored, or cancelled records in the summary even if they are not written as markdown.
9. Deterministic filename pattern: `<zero-padded-index>-<slug>-<hash8>.md` where `hash8` is a short hash of the source URL.
10. If the user wants a merged artifact, concatenate the exported markdown files after per-page files exist; keep the per-page files as the auditable source of truth unless the user asks to remove them.
11. To cancel a running crawl, require explicit confirmation and use `scripts/cf_crawl_api.sh cancel --job-id <job_id>` when the target API version supports cancellation.

## Script helpers
- `scripts/cf_crawl_api.sh env-check` validates required environment variables and placeholder values.
- `scripts/cf_crawl_api.sh start --payload <payload.json>` starts a crawl job.
- `scripts/cf_crawl_api.sh status --job-id <job_id>` retrieves the latest crawl job state.
- `scripts/cf_crawl_api.sh page-status --job-id <job_id> --status <state> [--cursor <cursor>]` paginates category-specific records.
- `scripts/cf_crawl_api.sh cancel --job-id <job_id>` attempts cancellation when available.

### Optional parameter behavior (as documented)
- `formats` accepts `html`, `markdown`, and `json`; defaults are documented in the endpoint response. If unspecified, `formats` defaults to `["html"]`.
- `source` accepts `all`, `sitemaps`, or `links`.
- `excludePatterns` has priority over `includePatterns`.
- `limit` defaults to `10` and currently documents an upper bound of `100000`.
- `depth` defaults to `100000`.
- `modifiedSince` and `maxAge` let you constrain recrawl windows.
- `jsonOptions` applies when requesting JSON format and must be passed with the `formats` array.
- `maxAge` can be used with `modifiedSince` to constrain recrawl windows for incremental captures.
- `render: false` is a deliberate speed/quality tradeoff: faster but without browser DOM rendering behavior.
- `status` filters may include `queued`, `running`, `completed`, `disallowed`, `skipped`, `errored`, and `cancelled`.

## Verification
- Verify both Cloudflare environment variables are resolved before live API calls.
- Verify the requested crawl bounds are explicit enough to avoid an accidental site-wide crawl.
- Verify job status with a fresh `GET` before claiming completion.
- Verify exported files exist, are non-empty, and retain source URL metadata.
- Verify the final report includes completed totals plus any skipped, disallowed, errored, or cancelled counts.
- Verify structured output includes `schema_version` when JSON contract output is requested.

## Validation
- Fail fast: stop at the first failed auth, scope, or export gate, fix that blocker, then rerun the smallest relevant check.
- Verify `references/contract.yaml` matches the skill description and deliverables.
- Verify `references/evals.yaml` covers should-trigger, should-not-trigger, and pressure cases.
- Verify eval minimums stay at or above 3 should-trigger and 3 should-not-trigger cases.
- Verify command examples keep destructive operations out of scope and never suggest `eval` on untrusted env files.
- Verify any structured summary includes `schema_version`.

## Constraints
- Redact secrets, account identifiers, cookies, auth headers, and private URLs by default.
- Do not use `eval` against `.env` files or echo raw tokens back to the user.
- Do not crawl targets the user is not authorized to access.
- Do not imply Cloudflare execution succeeded if network policy, auth, or account limits blocked it.
- Keep output paths explicit and local; do not overwrite unrelated crawl artifacts without confirmation.

## Anti-patterns
- Using this skill for Playwright-style flows, login automation, or click-path testing.
- Launching a crawl with no page limit or no clear site boundary.
- Hiding auth failures behind fake success language.
- Dropping skipped or disallowed pages from the final summary.

## Examples
- "Crawl `https://developers.cloudflare.com/workers/` to markdown with a 25-page limit and save it under `.crawl-output/cloudflare-workers`."
- "Check whether crawl job `abc123` is done yet and summarize any skipped pages."
- "Run a fast static crawl of this docs site with `render: false` and exclude changelog pages."
- "Export an existing crawl job as markdown plus a merged single-file digest."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/discovery-interview.md`
- Cloudflare docs for Browser Rendering crawl workflows and API reference:
  - https://developers.cloudflare.com/browser-rendering/rest-api/crawl-endpoint/
  - https://developers.cloudflare.com/browser-rendering/rest-api/crawl-endpoint/#optional-parameters
  - https://developers.cloudflare.com/api/resources/browser_rendering/subresources/crawl/methods/create/

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[cloudflare-deploy]] | Deploy and authenticate the crawl target on Cloudflare |
| [[markdown-converter]] | Convert crawl output into clean Markdown |
| [[context7]] | Supplement crawl results with library documentation |
| [[visual-explainer]] | Present crawl findings in an HTML report |

**Topic map:** [[backend-platform]]

<!-- decision-feedback-protocol:v2 -->
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.

## Remember
- Keep crawl jobs bounded, authenticated, and auditable.
- Prefer precise export summaries over vague "crawl succeeded" claims.
- When the request is not actually about Cloudflare crawl jobs, route away instead of stretching the skill.

The agent is capable and can still apply judgment in edge cases where policy allows adaptation.

## Gotchas
- Symptom: Crawl starts with broad scope and burns budget quickly.
  Cause: Missing explicit `limit`, `depth`, and include or exclude boundaries.
  Do instead: Set bounded defaults and confirm scope before starting.
  Check: Payload includes concrete limits and boundary patterns.
- Symptom: Status looks stale or unknown after launch.
  Cause: Polling wrong job ID or polling before propagation.
  Do instead: Reconfirm `job_id`, then poll in short intervals until terminal status.
  Check: Latest status response timestamp is newer than launch time.
- Symptom: Export summary ignores skipped or disallowed URLs.
  Cause: Only completed records were inspected.
  Do instead: Query per-status records and report all categories.
  Check: Summary includes completed, skipped, disallowed, errored, and cancelled counts.
- Symptom: Auth fails despite env vars being set.
  Cause: Placeholder values or token lacks Browser Rendering permission.
  Do instead: Run env-check and verify token scope before retrying.
  Check: No placeholder values and API call returns non-auth error or success.
