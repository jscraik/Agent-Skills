# Workflow: Create a New Skill

<required_reading>
**Read these reference files NOW:**
1. references/recommended-structure.md
2. references/skill-structure.md
3. references/core-principles.md
4. references/cso-description-writing.md (frontmatter description quality)
</required_reading>

<process>
## Step 1: Adaptive Requirements Gathering

**If user provided context** (e.g., "build a skill for X"):
→ Analyze what's stated, what can be inferred, what's unclear
→ Skip to asking about genuine gaps only

**If user just invoked skill without context:**
→ Ask what they want to build

### Using default_mode_request_user_input

Use `default_mode_request_user_input` when available; otherwise use direct `a/b/c` questions in chat.

Discovery protocol (adaptive, gap-only):
- Ask one topic round at a time: Goal/Name -> Trigger -> Process -> Inputs/Outputs/Dependencies -> Guardrails/Edge Cases -> Confirmation.
- Skip rounds already answered by the user.
- Ask 1-2 questions per turn (max 4 turns total) unless user asks for deeper discovery.
- Stop asking once remaining unknowns are non-blocking.

Question quality contract (required):
- 2-4 options per question.
- Recommended option first.
- One-sentence tradeoff/impact per option.
- Stable option IDs (snake_case) so later steps can reference choices.
- Focus on scope, complexity, outputs, and boundaries only; do not ask obvious questions.

`default_mode_request_user_input` payload shape (required when tool is available):
```yaml
id: snake_case_question_id
question: "Single focused question"
options:
  - id: recommended_option_id
    label: "Recommended label"
    description: "One-sentence tradeoff"
  - id: alternate_option_id
    label: "Alternate label"
    description: "One-sentence tradeoff"
```

Fallback if tool is unavailable:
- Ask the same question in plain chat with `a/b/c` options.
- Keep option IDs in parentheses so later steps can reference selections deterministically.
- Continue the same round flow; do not switch to open-ended questions.

Example questions:
- "What specific operations should this skill handle?" (with options based on domain)
- "Should this also handle [related thing] or stay focused on [core thing]?"
- "What should the user see when successful?"

### Decision Gate

After initial questions, ask:
"Ready to proceed with building, or would you like me to ask more questions?"

Options:
1. **Proceed to building** - I have enough context
2. **Ask more questions** - There are more details to clarify
3. **Let me add details** - I want to provide additional context

Proceed only when either:
- user explicitly selects proceed, or
- confidence is high enough to build safely (target ~95%) and unresolved gaps are non-blocking.
- hard stop reached (4 turns); in that case, proceed with explicit assumptions listed in the summary.

Before moving to Step 2+, provide a concise discovery summary:

```markdown
## Skill Summary: [name]

**Goal:** [one sentence]
**Trigger:** `/name` + [natural language phrases]
**Arguments:** [accepted args, or "none"]
**Process:** [3-7 numbered steps]
**Inputs:** [files/data/services]
**Outputs:** [artifacts + location]
**Dependencies:** [scripts/APIs/tools/references]
**Guardrails:** [boundaries + failure modes]
```

Ask: "Does this capture it? Anything to add or change?"

### Lock down triggers + description (CSO)

Before writing the skill body, draft the `description:` using **WHAT + WHEN** (but *no workflow*). Use:
- `references/cso-description-writing.md`
- the user’s 3–10 example prompts (happy-path + edge + negative) to ensure the description matches real trigger language

## Step 2: Research Trigger (If External API)

**When external service detected**, ask via `default_mode_request_user_input` (or `a/b` fallback if unavailable):
"This involves [service name] API. Would you like me to research current endpoints and patterns before building?"

Options:
1. **Yes, research first** - Fetch current documentation for accurate implementation
2. **No, proceed with general patterns** - Use common patterns without specific API research

If research requested:
- Use Context7 MCP to fetch current library documentation
- Or use WebSearch for recent API documentation
- Focus on 2024-2025 sources
- Store findings for use in content generation

## Step 3: Decide Structure

**Simple skill (single workflow, <200 lines):**
→ Single SKILL.md file with all content

**Complex skill (multiple workflows OR domain knowledge):**
→ Router pattern:
```
skill-name/
├── SKILL.md (router + principles)
├── workflows/ (procedures - FOLLOW)
├── references/ (knowledge - READ)
├── templates/ (output structures - COPY + FILL)
└── scripts/ (reusable code - EXECUTE)
```

Factors favoring router pattern:
- Multiple distinct user intents (create vs debug vs ship)
- Shared domain knowledge across workflows
- Essential principles that must not be skipped
- Skill likely to grow over time

**Consider templates/ when:**
- Skill produces consistent output structures (plans, specs, reports)
- Structure matters more than creative generation

**Consider scripts/ when:**
- Same code runs across invocations (deploy, setup, API calls)
- Operations are error-prone when rewritten each time

See references/recommended-structure.md for templates.

## Step 4: Create Directory

Use the initializer (auto-creates beneficial resources):

```bash
python scripts/init_skill.py {skill-name} --category utilities --description "Use when ..." --owner "Agent Skills Team" --review-cadence monthly --last-reviewed 2026-03-24
```

**Auto-created by default:**
- `references/` - for evals.yaml, contracts, progressive disclosure
- `assets/` - for templates, icons, static files
- `agents/openai.yaml` - OpenAI/Codex configuration
- `scripts/` - only for `--run-type python` or `container`

**Required lifecycle inputs:**
- `--description` - real discovery description for routing
- `--owner` - accountable maintainer or team
- `--review-cadence` - concrete cadence such as `monthly` or `quarterly`
- `--last-reviewed` - ISO date for the most recent governance review
- `--lifecycle-state` - defaults to `incubating`
- `--maturity` - defaults to `experimental`

**Override options:**
- `--minimal` - Just SKILL.md + agents/openai.yaml (no resources)
- `--resources scripts,references,assets` - Explicit list
- `--examples` - Add example files to resources

Or manually:
```bash
mkdir -p ~/.claude/skills/{skill-name}
# If complex:
mkdir -p ~/.claude/skills/{skill-name}/workflows
mkdir -p ~/.claude/skills/{skill-name}/references
mkdir -p ~/.claude/skills/{skill-name}/agents
# If needed:
mkdir -p ~/.claude/skills/{skill-name}/templates  # for output structures
mkdir -p ~/.claude/skills/{skill-name}/scripts    # for reusable code
```

## Step 5: Write SKILL.md

**Simple skill:** Write complete skill file with:
- YAML frontmatter (name, description)
- `<objective>`
- `<quick_start>`
- Content sections with pure XML
- `<success_criteria>`

**Complex skill:** Write router with:
- YAML frontmatter
- `<essential_principles>` (inline, unavoidable)
- `<intake>` (question to ask user)
- `<routing>` (maps answers to workflows)
- `<reference_index>` and `<workflows_index>`

## Step 6: Configure agents/openai.yaml (Optional)

For OpenAI/Codex compatibility, create `agents/openai.yaml`:

```yaml
# OpenAI Agents SDK Configuration
# interface:
#   display_name: "User-facing name"
#   short_description: "User-facing description"
#   icon_small: "./assets/small-logo.svg"    # 16x16px SVG
#   icon_large: "./assets/large-logo.png"    # 100x100px PNG/JPG
#   brand_color: "#3B82F6"
#   default_prompt: "Optional surrounding prompt"
#
# dependencies:
#   tools:
#     - type: "mcp"
#       value: "serverName"
#       description: "MCP server description"
#       transport: "streamable_http"
#       url: "https://example.com/mcp"
```

See: https://developers.openai.com/codex/skills/create-skill/

## Step 7: Write Workflows (if complex)

For each workflow:
```xml
<required_reading>
Which references to load for this workflow
</required_reading>

<process>
Step-by-step procedure
</process>

<success_criteria>
How to know this workflow is done
</success_criteria>
```

## Step 8: Write References (if needed)

Domain knowledge that:
- Multiple workflows might need
- Doesn't change based on workflow
- Contains patterns, examples, technical details

## Step 9: Validate Structure

Check:
- [ ] YAML frontmatter valid
- [ ] Name matches directory (lowercase-with-hyphens)
- [ ] Description says what it does AND when to use it (third person)
- [ ] No markdown headings (#) in body - use XML tags
- [ ] Required tags present: objective, quick_start, success_criteria
- [ ] All referenced files exist
- [ ] SKILL.md under 500 lines
- [ ] XML tags properly closed

## Step 10: Create Slash Command

```bash
cat > ~/.claude/commands/{skill-name}.md << 'EOF'
---
description: {Brief description}
argument-hint: [{argument hint}]
allowed-tools: Skill({skill-name})
---

Invoke the {skill-name} skill for: $ARGUMENTS
EOF
```

## Step 11: Test

Invoke the skill and observe:
- Does it ask the right intake question?
- Does it load the right workflow?
- Does the workflow load the right references?
- Does output match expectations?

Iterate based on real usage, not assumptions.
</process>

<success_criteria>
Skill is complete when:
- [ ] Requirements gathered with appropriate questions
- [ ] API research done if external service involved
- [ ] Directory structure correct
- [ ] SKILL.md has valid frontmatter
- [ ] agents/openai.yaml configured (if targeting OpenAI/Codex)
- [ ] Essential principles inline (if complex skill)
- [ ] Intake question routes to correct workflow
- [ ] All workflows have required_reading + process + success_criteria
- [ ] References contain reusable domain knowledge
- [ ] Slash command exists and works
- [ ] Tested with real invocation
</success_criteria>
