# AI Native DevCon 2026 London

This plugin contains a skill for every talk at AI Native DevCon 2026 London. Each skill captures the key concepts, frameworks, and insights from a session — distilled directly from the talk transcript — so you can explore the content interactively.

## What's inside

Each talk becomes a dedicated skill covering:

- The core ideas, frameworks, and patterns introduced
- Practical techniques and implementation guidance
- Key takeaways and the speaker's perspective

Every skill bundles four files:

| File | Purpose |
|---|---|
| `SKILL.md` | Skill definition and grounding rules |
| `transcript.md` | Full verbatim transcript |
| `outline.md` | Section map, used for navigation |
| `quote.md` | Pre-extracted key verbatim quotes by theme |

## Usage

Once installed, you can ask questions across any of the conference talks:

- **Explore a talk**: "What did [speaker] cover in their session on [topic]?"
- **Go deeper**: "Explain the [framework/approach] from [speaker]'s talk"
- **Connect ideas**: "How do [speaker A]'s and [speaker B]'s approaches to [topic] compare?"
- **Find relevant sessions**: "Which talks covered [topic]?"

## Publishing

```bash
tessl plugin publish .
```

## About

AI Native DevCon 2026 London is a conference focused on AI-native software development — building systems where AI is a first-class architectural concern, not an add-on. This plugin is generated from the actual talk transcripts.
