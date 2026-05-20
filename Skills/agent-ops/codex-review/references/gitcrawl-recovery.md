# Gitcrawl Recovery

Use this when PR/base discovery goes through Gitcrawl and the GitHub/Gitcrawl path fails.

## Cache Corruption

If the error includes:

```text
database disk image is malformed
```

run once:

```bash
gitcrawl doctor --json
```

Then retry review through the same shim path.

## Portable Store Drift

If Gitcrawl reports portable manifest mismatch, source/runtime DB health errors, or stale portable-store checkout:

1. Run `gitcrawl doctor --json`.
2. Inspect `source_db_health`.
3. Inspect `runtime_db_health`.
4. Inspect `portable_store_status`.
5. Retry the shim path if doctor repaired the issue.
6. Fall back to live GitHub only when repair fails and freshness is required.

Report the exact failure text and the fallback used.
