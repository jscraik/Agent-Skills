# Shell plugin: Homebrew

Source: https://developer.1password.com/docs/cli/shell-plugins/homebrew/

Key points
- Install the 1Password Shell Plugins integration, then use `op plugin init brew` to configure.
- Use `op plugin run -- brew <command>` (or equivalent alias) so secrets are injected when brew reads env vars.
- Validate with `op plugin list` and `op plugin run -- brew doctor`.

Examples
```bash
op plugin init brew
op plugin run -- brew doctor
```
