# Troubleshooting

Read when: listing or install operations fail due to source availability, auth, provenance, or destination conflicts.

## Source and availability caveats

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Optional catalogs such as `.experimental` can appear or disappear over time; verify via GitHub API/path existence before promising availability.
- Verified on 2026-04-18 (UTC): `skills/.curated` and `skills/.system` returned HTTP 200, while `skills/.experimental` returned HTTP 404.
- The skills at `https://github.com/openai/skills/tree/main/skills/.system` are preinstalled; if users ask to install them, explain they are already present unless they explicitly insist on overwrite behavior.

Availability probe command:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "https://api.github.com/repos/openai/skills/contents/skills/.experimental?ref=main"
```

## Auth and transport caveats

- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.

## Destination and visibility caveats

- Installed annotations come from canonical repo category directories (default `github/`).
- For dedicated role creation during install handoff, use `[[codex-agent-creator]]`.
