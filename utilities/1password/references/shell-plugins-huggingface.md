# Shell plugin: Hugging Face

Source: https://developer.1password.com/docs/cli/shell-plugins/huggingface/

Key points
- Install the 1Password Shell Plugins integration, then run `op plugin init huggingface`.
- Use `op plugin run -- huggingface-cli <command>` so the plugin injects auth env vars.
- Validate with `op plugin list` and a no-op command.

Examples
```bash
op plugin init huggingface
op plugin run -- huggingface-cli whoami
```
