# Portable skills for Codex and Claude Code

Use this guide when authoring a single skill that must work in both Claude Code and OpenAI Codex. Follow the strict subset rules to avoid parser mismatches and loading failures.

## Portability contract (strict subset)

### File and YAML rules
- Name the file exactly `SKILL.md`.
- Start YAML frontmatter on line 1 and end with `---`.
- Use spaces in YAML (no tabs).
- Keep `name` and `description` as single-line YAML scalars (quote if they contain `:` or could be parsed as YAML syntax).
- Use forward slashes in paths (for example, `references/guide.md`).

### Name and description limits
Use the tightest limits that all platforms accept:
- `name`: 1–64 chars, lowercase letters, digits, and hyphens only; no leading/trailing hyphen; no `--`; must match the parent folder name.
- `description`: 1–500 chars, single line. Include both what the skill does and when to use it (trigger contexts + keywords).

### Frontmatter fields
- Codex requires `name` and `description` for selection. Other keys are optional and may be ignored by some clients.
- If you include optional keys for portability, prefer spec-defined fields (`license`, `compatibility`, `metadata`, `allowed-tools`) and keep them minimal.
- `metadata.short-description` is a common optional field (user-facing in UIs that support it).

### Directory layout
```
<skill-name>/
  SKILL.md
  scripts/        # optional
  references/     # optional
  assets/         # optional
```
Keep `SKILL.md` concise and push depth into `references/`. Prefer executing helpers from `scripts/` over pasting large code blocks.

### Symlinks
Codex supports symlinked skill folders and follows symlink targets when scanning skill locations. For maximum portability (other tools or CI), consider resolving symlinks during packaging/exports.

## Invocation and loading differences

### Progressive disclosure
Both ecosystems optimize for context:
- At discovery time, only `name` and `description` are used to select a skill.
- The body of `SKILL.md` (and any referenced files) is only read when the skill is invoked.

Implication: **Your trigger keywords must live in the frontmatter description**. A perfect “When to Use” section in the body will not help discovery.

### How skills get invoked
- **Codex**
  - Explicit invocation: use `/skills` to browse or type `$` to mention a skill by name.
  - Implicit invocation: Codex may activate a skill when the task matches the description.
- **Claude Code**
  - Primarily model-invoked; may ask for confirmation before loading and using the skill.

Author the skill body so it works in both explicit and implicit flows:
- Start with a short “When to Use” confirmation to ensure the skill is being applied correctly.
- Ask only the clarifying questions you truly need.
- Produce concrete deliverables and a verification step.
