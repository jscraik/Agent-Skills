# Item template JSON

Source: https://developer.1password.com/docs/cli/item-template-json/

Key points
- Use `op item template <item-type>` (or `op item create --template <item-type>`) to generate a JSON template for an item type.
- Templates are not JSON Schema; they are concrete JSON objects you can edit and pass to `op item create` or `op item edit`.

Examples
```bash
# Generate a template for a login item
op item template login > login.template.json

# Create an item from a template file
op item create --vault "Prod" --template login < login.template.json
```

Typical top-level keys
- `title`, `category`, `tags`, `vault`, `fields`, `sections`, `urls`.

Notes
- Preserve field IDs and section IDs when editing templates so `op item edit` can map updates correctly.
- Prefer starting from a template instead of writing JSON from scratch to avoid missing required fields.
