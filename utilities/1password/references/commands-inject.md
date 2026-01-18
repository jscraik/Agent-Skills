# op inject

Source: https://developer.1password.com/docs/cli/reference/commands/inject/

Key points
- Replaces secret references in a template and writes resolved output.
- Supports stdin or input file, with optional output file.
- Use for config/templates that should never store plaintext secrets.

Examples
```bash
op inject -i config.yml.tpl -o config.yml
```
