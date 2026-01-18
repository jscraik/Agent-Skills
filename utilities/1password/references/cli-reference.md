# CLI reference overview

Source: https://developer.1password.com/docs/cli/reference/

Key points
- The CLI reference provides command groups, flags, and output formats.
- Use it to confirm flags and command variants before running sensitive operations.
- Prefer JSON output when parsing results in scripts.

Examples
```bash
op item list --format json | jq '.[] | .title'
```
