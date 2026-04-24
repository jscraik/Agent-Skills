# Ubiquitous Language Output Format

Use this template when creating or updating `UBIQUITOUS_LANGUAGE.md`.

```md
# Ubiquitous Language

## Scope and Sources

- Scope: <project, repo, feature, or conversation scope>
- Sources: <current conversation, AGENTS.md, README.md, docs, session logs, etc.>
- Last updated: <YYYY-MM-DD>

## Canonical Terms

| Term | Definition | Aliases to avoid | Confidence |
| --- | --- | --- | --- |
| **Canonical Term** | One sentence defining what it is. | Old term, vague phrase | High |

## Prompt Translations

| User phrase | Canonical intent | Better Codex wording |
| --- | --- | --- |
| "Plain-language phrase" | Precise intent | "Actionable prompt using canonical terms." |

## Relationships

- A **Term** belongs to exactly one **Other Term**.
- A **Workflow** produces zero or more **Artifacts**.

## Example Dialogue

> **Dev:** "When I say **Plain Phrase**, do I mean **Canonical Term**?"
>
> **Domain expert:** "Yes. Use **Canonical Term** when the agent needs to act, and keep **Plain Phrase** as an alias."
>
> **Dev:** "So if I ask Codex to 'make sure it works', what should it do?"
>
> **Domain expert:** "Translate that into running the repo-defined validation gate and reporting exact pass/fail/blocker evidence."

## Flagged Ambiguities

- "Ambiguous term" was used to mean both **Term A** and **Term B**. Recommendation: use **Term A** for <case> and **Term B** for <case>.

## Agent Integration

- Instruction surface updated: <path or "not found">
- Integration summary: <how future agents are told to use this glossary>
- Validation/enforcement: <none, existing gate, or new check>

## Open Questions

- Should "<unclear phrase>" map to **Term A** or **Term B**?
```

## Quality Bar

- The glossary should help future agents act correctly without asking the user for technical vocabulary.
- Canonical terms should be boringly useful, not impressive.
- Prompt translations should be copy-pasteable.
- Ambiguities should be visible enough that future agents do not silently choose the wrong meaning.
- Agent integration should be short, operational, and attached to a high-traffic instruction surface.
