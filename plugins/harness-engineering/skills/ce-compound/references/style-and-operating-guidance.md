# Style and Operating Guidance

Read when: you need standards rationale, operating philosophy, output-variation expectations, or discoverability-check policy while running `ce-compound`.

## Standards snapshot (April 2026)
- Keep the skill scoped to one reusable operational job and make the description say what it does and when to use it.
- Prefer explicit routing, realistic positive/negative examples, and eval-backed trigger coverage over hidden prompt assumptions.
- Use repository truth, prior artifacts, and documented learnings before broad external research.
- Keep one explicit current stage in focus and keep plan or stage state synchronized instead of letting the workflow drift.
- Preserve legacy breadth as explicit opt-in behavior when valuable, rather than making maximal fan-out the default.

## Philosophy
- `ce-compound` is the workflow spine: it decides where the user is, what is already trustworthy, and what comes next.
- The workflow should feel lighter than the old prompt pack, not weaker.
- Durable learnings are part of the workflow, not an afterthought.
- Each completed stage should reduce uncertainty for the next stage.
- Knowledge compounds only when the final learning artifact is specific, searchable, and faithful to the verified fix.

## Encouraging variation
Outputs should vary by active mode and evidence shape:
- orchestration runs should summarize actual stage state, not recite the full lifecycle
- learning-capture runs should match depth to complexity and selected mode (`full` or `compact-safe`)
- refresh recommendations should track stale-evidence strength, not mere related-doc existence

No two runs should look the same unless artifact state, risk, and evidence are materially identical.

## Discoverability check policy
After learning capture writes the final solution doc, verify root instruction docs make `docs/solutions/` discoverable to agents.

Assess whether an agent can infer:
- a searchable solution knowledge store exists
- how it is structured (category folders and frontmatter semantics)
- when it is useful (implementing, debugging, or deciding in documented areas)

If discoverability is already clear, no action.
If not clear, propose the smallest natural addition in existing instruction sections.

Interaction rule:
- ask for explicit user consent before editing instruction docs
- if the session is in `compact-safe` mode and context is tight, prefer reporting a recommendation over expanding scope
