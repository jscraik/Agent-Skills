# Item create

Source: https://developer.1password.com/docs/cli/item-create/

Key points
- Use `op item template <type>` or `op item create --template <type>` to generate a template.
- Edit the template JSON and pass to `op item create` to avoid missing required fields.
- Provide vault explicitly when needed (for example `--vault <vault>`).

Examples
```bash
op item template login > login.template.json
op item create --vault "Prod" --template login < login.template.json
```
