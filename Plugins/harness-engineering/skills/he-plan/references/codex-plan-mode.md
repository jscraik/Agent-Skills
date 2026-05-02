# Codex Plan Mode Lessons

Read when `he-plan` is used inside Codex or when plan/chat behavior affects handoff.

- Plan Mode is not the same thing as the `update_plan` checklist tool. A Harness Engineering plan is a durable artifact; `update_plan` is only live progress UI.
- Explore first, ask second. Use non-mutating inspection to answer repo, schema, config, and pattern questions before interrupting the user.
- Mutating work belongs in `he-work`: no code edits, patching, migrations, codegen, or formatter rewrites during planning.
- Ask only for material preferences, tradeoffs, or choices that cannot be discovered from sources.
- If a plan is revised after feedback, output a complete replacement artifact rather than partial deltas.

Full retained notes: `Plugins/harness-engineering/references/he-plan-doctrine.md`.
