---
name: rclone
description: Upload, sync, verify, or inspect files in remote storage with rclone. Use when the user wants S3, R2, B2, Google Drive, Dropbox, or similar remote file operations, not local file moves or app deployment.
metadata:
  skill-type: infrastructure_ops
---

# rclone

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Setup preflight](#setup-preflight)
- [Workflow](#workflow)
- [Script helpers](#script-helpers)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Gotchas](#gotchas)

## Standards snapshot
- Route only remote-storage transfer work here.
- Verify `rclone` installation and remote configuration before proposing live transfer commands.
- Prefer dry runs, explicit source and destination paths, and provider-specific guidance when auth or endpoint details matter.
- Preserve upstream provider examples and transfer caveats in references instead of bloating the wrapper.
- Treat remote credentials, access keys, and config output as sensitive.

## When to use
- Upload a file or directory to remote object storage or cloud drives with `rclone`.
- Sync a local directory to a remote bucket or vice versa.
- Verify that a remote file exists, matches, or transferred successfully.
- Inspect configured remotes, test connectivity, or help set up a new remote.
- Work with S3, Cloudflare R2, Backblaze B2, Google Drive, Dropbox, or another `rclone`-supported backend.

## When not to use
- Generic local file moves or renames with no remote storage involved.
- Cloud deployment or infrastructure provisioning work that should use deployment-specific skills instead.
- App-specific upload flows where a product API or SDK is the real interface.
- Requests to expose secrets or dump full credential material.

## Required inputs
- Requested action: `setup`, `list`, `copy`, `sync`, `verify`, or `troubleshoot`.
- Local source path, remote target, or both.
- Provider or remote name if known.
- Transfer constraints when relevant:
  - dry run versus live transfer
  - include or exclude patterns
  - bandwidth or concurrency limits
  - large-file behavior

## Deliverables
- A chosen `rclone` action plan matched to the request.
- Exact commands or script helper to run.
- Setup or troubleshooting guidance when installation or remotes are missing.
- Verification steps for the transfer or remote state.
- If structured output is requested, return the contract in this file's Output contract section.

## Failure mode
- If `rclone` is not installed, stop after setup guidance and do not pretend transfers can run.
- If no remote is configured, stop at configuration guidance unless the user explicitly wants a create command drafted.
- If the requested operation would be destructive or mirror deletes with `sync`, require clear confirmation language.
- If the task is really a product-specific upload flow, route to the narrower product skill instead of stretching `rclone`.

## Output contract
Use this shape when the user asks for structured output:

```json
{
  "schema_version": 1,
  "action": "setup|list|copy|sync|verify|troubleshoot",
  "remote": "string|null",
  "source_path": "string|null",
  "destination_path": "string|null",
  "dry_run": true,
  "command": "string|null",
  "blocker": "string|null",
  "next_step": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Set unknown paths or remote names to `null`.
- Use `dry_run: true` by default when proposing a transfer unless the user clearly asked for a live command.
- Keep `blocker` short and actionable.

## Setup preflight
Run the setup preflight before any live transfer:
1. Check whether `rclone` is installed.
2. Check whether any remotes are configured.
3. If remotes exist, test connectivity before claiming the remote is usable.

Use `scripts/check_setup.sh` for the deterministic setup check.

If a remote must be created, use the provider guidance in `references/provider-operations.md`.

## Workflow
1. Resolve the user's intent: setup, list, copy, sync, verify, or troubleshoot.
2. Run the setup preflight.
3. If the remote is missing, guide the user through `rclone config` or a provider-specific `rclone config create ...` command.
4. Normalize the source and destination paths and confirm whether a dry run is preferred.
5. Choose the narrowest command:
   - `copy` for one-way upload without deletes
   - `sync` only when mirroring behavior is intended
   - `ls`, `lsl`, or `lsd` for inspection
   - `check` for verification
6. Add only the flags the request actually needs, such as `--progress`, `--dry-run`, `--transfers`, `--bwlimit`, `--include`, `--exclude`, or provider-specific large-file flags.
7. For large file transfers, use the preserved guidance in `references/provider-operations.md` instead of inventing upload heuristics.
8. End with a verification step so the transfer result can be checked explicitly.

## Script helpers
- `scripts/check_setup.sh` verifies installation, configured remotes, and connectivity.

## Validation
- Verify `rclone` installation before live commands.
- Verify the resolved remote name exists before copy, sync, or verify commands.
- Verify destructive `sync` recommendations are clearly labeled and not presented as interchangeable with `copy`.
- Verify structured output includes `schema_version` when requested.
- Verify secrets are redacted from any quoted setup guidance.

## Constraints
- Redact access keys, secret keys, tokens, and full config dumps by default.
- Do not suggest piping secrets into shell history when safer alternatives exist.
- Do not treat `sync` as a harmless upload; it can delete remote files.
- Keep remote and local paths explicit to avoid accidental wide-scope transfers.

## Anti-patterns
- Using `sync` when the user only asked to upload a file.
- Skipping installation or remote checks and assuming the environment is ready.
- Echoing raw credentials back to the user.
- Giving provider-agnostic advice when endpoint details are required.

## Examples
- "Upload `artifacts/demo.mp4` to my R2 bucket with rclone."
- "Sync this local backup folder to S3, but show me the dry run first."
- "List the contents of my `b2:archive` remote."
- "Help me configure a new Google Drive remote in rclone."
- "Verify that the uploaded video matches the local file."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/provider-operations.md`

## Gotchas
- Symptom: `rclone` commands fail immediately.
  Cause: Tool is not installed or not on `PATH`.
  Do instead: Run `scripts/check_setup.sh` and install `rclone` first.
  Check: `rclone version` returns successfully.
- Symptom: Transfer command looks correct but remote access fails.
  Cause: Remote is missing or credentials are invalid.
  Do instead: Re-check `rclone listremotes` and connectivity before retrying the transfer.
  Check: `rclone lsd remote:` succeeds.
- Symptom: A transfer plan could delete unexpected remote files.
  Cause: `sync` was chosen when `copy` was safer.
  Do instead: Default to `copy` unless mirror semantics are explicitly required.
  Check: The command choice matches the user's intent.

## See Also

| Skill | When to use together |
|---|---|
| [[1password]] | Inject remote credentials or secrets safely into the runtime |
| [[cf-crawl]] | Export crawl results locally, then move them to remote storage |
| [[feature-video]] | Upload generated demo artifacts after rendering or capture |
| [[video-transcript-downloader]] | Transfer downloaded media or transcripts to long-term storage |

**Topic map:** [[backend-platform]]
