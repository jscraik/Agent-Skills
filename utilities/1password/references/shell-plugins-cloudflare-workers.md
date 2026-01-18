# Shell plugin: Cloudflare Workers

Source: https://developer.1password.com/docs/cli/shell-plugins/cloudflare-workers/

Key points
- Install the 1Password Shell Plugins integration, then run `op plugin init wrangler`.
- Use `op plugin run -- wrangler <command>` so the plugin injects credentials.
- Validate with `op plugin list` and a non-destructive command (for example `wrangler whoami`).

Examples
```bash
op plugin init wrangler
op plugin run -- wrangler whoami
```
