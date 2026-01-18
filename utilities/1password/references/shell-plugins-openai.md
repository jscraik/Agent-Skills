# Shell plugin: OpenAI

Source: https://developer.1password.com/docs/cli/shell-plugins/openai/

Key points
- Install the 1Password Shell Plugins integration, then run `op plugin init openai`.
- Source the `plugins.sh` file path output by `op plugin init` to enable the plugin.
- Use the OpenAI CLI normally; the plugin injects credentials at runtime.
- Validate with `op plugin list` and a safe OpenAI CLI command.

Examples
```bash
op plugin init openai
# Source the plugins.sh file path printed by op
source <path-to-plugins.sh>
openai --help
```
