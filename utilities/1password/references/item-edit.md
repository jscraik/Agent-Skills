# Item edit

Source: https://developer.1password.com/docs/cli/item-edit/

Key points
- Start from `op item get <item> --format json` to preserve IDs and sections.
- Edit JSON and pass to `op item edit <item> <json>` or use `--template` flow.
- Preserve field IDs/section IDs to avoid unintended field changes.

Examples
```bash
op item get "Prod DB" --format json > item.json
# edit item.json
op item edit "Prod DB" item.json
```
