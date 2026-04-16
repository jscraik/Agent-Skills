# Scripts

## `profile-dev-repos.sh`

Profiles local `~/dev` git repos and reports recurring scaffold-control signals.

### Usage

```bash
bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev --top 12
```

### Output

Deterministic plain-text key/value lines:
- repo discovery totals
- control-plane marker counts
- strongest-signal repos
- package-manager and lockfile distribution
- Python/uv marker counts

### Notes

- Requires: `bash`, `sort`, `awk`, `wc`
- Optional accelerators: `fd` (repo/package discovery), `jq` (package manager parsing)
- Falls back to `find` if `fd` is unavailable
