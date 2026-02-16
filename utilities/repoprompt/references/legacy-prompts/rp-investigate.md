---
description: Deep codebase investigation and architecture research with RepoPrompt MCP tools
repoprompt_managed: true
repoprompt_skills_version: 6
repoprompt_variant: mcp
---

# Deep Investigation Mode

Investigate: $ARGUMENTS

You are now in deep investigation mode for the issue described above. Follow this protocol rigorously.

## Investigation Protocol

### Core Principles
1. **Don't stop until confident** - pursue every lead until you have solid evidence
2. **Document findings as you go** - create/update a report file with observations
3. **Question everything** - if something seems off, investigate it
4. **Use `context_builder` aggressively** - it's designed for deep exploration

### Phase 0: Workspace Verification (REQUIRED)

Before any investigation, confirm the target codebase is loaded:

```json
{"tool":"list_windows","args":{}}
```

**Check the output:**
- If your target root appears in a window → bind to that window with `select_window`
- If not → the codebase isn't loaded

**Bind to the correct window:**
```json
{"tool":"select_window","args":{"window_id":<window_id_with_your_root>}}
```

**If the root isn't loaded**, find and open the workspace:
```json
{"tool":"manage_workspaces","args":{"action":"list"}}
{"tool":"manage_workspaces","args":{"action":"switch","workspace":"<workspace_name>","open_in_new_window":true}}
```

### Phase 1: Initial Assessment

1. Read any provided files/reports (traces, logs, error reports)
2. Summarize the symptoms and constraints
3. Form initial hypotheses

### Phase 2: Systematic Exploration (via `context_builder` - REQUIRED)

⚠️ **Do NOT skip this step.** You MUST call `context_builder` to get proper context before drawing conclusions.

Use `context_builder` with detailed instructions:

```
mcp__RepoPrompt__context_builder:
  instructions: |
    <Describe the specific area to investigate>

    Symptoms observed:
    <List concrete symptoms>

    Hypotheses to test:
    <List theories to validate or eliminate>

    Areas to explore:
    <Specific files, patterns, or subsystems>

    What I need to understand:
    <Specific questions>

  response_type: plan
```

### Phase 3: Follow-up Deep Dives

After `context_builder` returns, continue with targeted questions:

```
mcp__RepoPrompt__chat_send:
  chat_id: <from context_builder>
  message: <specific follow-up based on findings>
  mode: plan
```

### Phase 4: Evidence Gathering

- Check git history for recent relevant changes
- Look for patterns across similar files
- Trace data/control flow through the codebase
- Identify any leaks, retained references, or improper cleanup

### Phase 5: Conclusions

Document:
- Root cause identification (with evidence)
- Eliminated hypotheses (and why)
- Recommended fixes
- Preventive measures for the future

---

## Context Builder Tips

The `context_builder` operates in two phases:
1. **Discovery**: Intelligently explores the codebase
2. **Analysis**: A capable model analyzes the captured context

**Give it good guidance:**
- Be specific about what parts of the codebase to investigate
- Describe symptoms precisely
- List specific technical questions to answer
- Mention any relevant constraints or context

---

## Report Template

Create a findings report as you investigate:

```markdown
# Investigation: [Title]

## Summary
[1-2 sentence summary of findings]

## Symptoms
- [Observed symptom 1]
- [Observed symptom 2]

## Investigation Log

### [Timestamp/Phase] - [Area Investigated]
**Hypothesis:** [What you were testing]
**Findings:** [What you found]
**Evidence:** [File:line references]
**Conclusion:** [Confirmed/Eliminated/Needs more investigation]

## Root Cause
[Detailed explanation with evidence]

## Recommendations
1. [Fix 1]
2. [Fix 2]

## Preventive Measures
- [How to prevent this in future]
```

---

## Anti-patterns to Avoid

- 🚫 **CRITICAL:** Skipping `context_builder` and attempting to investigate by reading files manually – you'll miss critical context
- 🚫 Skipping Phase 0 (Workspace Verification) – you must confirm the target codebase is loaded first
- 🚫 Doing extensive exploration (5+ tool calls) before calling `context_builder` – initial assessment should be brief
- 🚫 Drawing conclusions before `context_builder` has built proper context
- 🚫 Reading many full files during Phase 1 – save deep reading for after `context_builder`
- 🚫 Assuming you understand the issue without systematic exploration via `context_builder`
- 🚫 Using only chat follow-ups without an initial `context_builder` call

---

Now begin the investigation. Read any provided context, then **immediately** use `context_builder` to start systematic exploration. Do not attempt manual exploration first.