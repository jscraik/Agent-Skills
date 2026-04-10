# Skillify Output Template

Use this template when generating the final `SKILL.md` for the user.

```markdown
---
name: <skill-name>
description: <one-line description with when-to-use intent>
allowed-tools:
  - <tool pattern>
when_to_use: Use when <clear trigger statement>. Examples: "<trigger 1>", "<trigger 2>".
argument-hint: "<optional argument hint>"
arguments:
  - <optional argument name>
context: <fork|inline; omit when inline>
---

# <Skill Title>
<short description>

## Inputs
- `$<arg_name>`: <description>

## Goal
<explicit completion target and expected artifacts>

## Steps

### 1. <Step name>
<actionable instructions>

**Success criteria**:
- <proof item 1>
- <proof item 2>

### 2. <Step name>
<actionable instructions>

**Execution**: <Direct|Task agent|Teammate|[human]>
**Artifacts**: <artifact(s) produced>
**Human checkpoint**: <when to pause>
**Rules**:
- <hard constraint from user corrections>

## Validation
- <command 1>
- <command 2>

## See Also
| Skill | When to use |
|---|---|
| `<adjacent-skill-1>` | <when this neighboring skill is a better fit> |
| `<adjacent-skill-2>` | <another related skill in the local graph> |

**Topic map:** `[[<topic-name>]]`
```

Notes:
- Include `Success criteria` on every step.
- Only include optional annotations (`Execution`, `Artifacts`, `Human checkpoint`, `Rules`) when they materially help execution.
- Keep the skill concise and move deep references into `references/`.
- Keep `allowed-tools` minimal and pattern-based (for example `Bash(gh:*)`), based on observed requirements.
- Include a real `## See Also` table in final output (replace placeholders with real local skill links before saving).
- For parallel work, use sub-step labels such as `3a`, `3b`.
- For user-owned actions, mark step titles with `[human]`.
