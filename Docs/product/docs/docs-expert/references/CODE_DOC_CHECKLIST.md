## Code documentation QA (TS/JS/React + configs)

### TS/JS / React
- [ ] All exported/public functions/classes/hooks/components have docblocks.
- [ ] Docblocks include constraints: units, allowed values, defaults, side effects.
- [ ] `@throws` used where errors can occur; conditions are explicit.
- [ ] At least one `@example` for multi-step or easy-to-misuse APIs.
- [ ] React components document a11y contract (keyboard/focus/ARIA) when interactive.
- [ ] No "narration" comments; comments explain intent/tradeoffs.

### JSON / TOML / YAML
- [ ] A schema exists (JSON Schema or Zod-derived) and is referenced by docs.
- [ ] Minimal + full examples exist and match the schema.
- [ ] Sensitive keys flagged with safe handling guidance.
- [ ] Migration notes exist for renamed/removed keys.

Run codebase documentation = [write, check, fix, update, polish]
