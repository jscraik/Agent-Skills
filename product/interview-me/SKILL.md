---
name: interview-me
description: "Guide a systematic interview using AskUserQuestion to clarify requirements, assumptions, and edge cases before work starts. Use when starting new features, debugging complex issues, planning refactors, or when requirements are unclear."
metadata:
  short-description: Systematic requirements interview
  version: "1.0.0"
  last_updated: "2026-01-17"
---

# interview-me

A systematic interview skill that uses AskUserQuestion to explore requirements, assumptions, and edge cases before starting any work.

**Optimized for cognitive profile**: Single questions at a time, explicit and direct, surfaces hidden assumptions without overwhelming cognitive load.

---

## How This Helps Your Cognitive Profile

| Benefit | Cognitive Connection |
|---------|---------------------|
| **Single-question focus** | Divided attention (5th percentile) — one question at a time prevents cognitive overload |
| **Externalizes thinking** | Verbal memory (12th percentile) — interview captures context externally |
| **Surfaces hidden assumptions** | Perceptual reasoning (96th) — leverages your strength to see implications |
| **Explicit decisions** | Working memory (42nd) — documents decisions so you don't have to hold them |
| **Non-obvious questions** | Executive function — prevents impulsivity by forcing consideration of tradeoffs |

---

## When to Use This Skill

Invoke `/interview-me` when:
- Starting a new feature or project
- Debugging a complex issue
- Making architectural decisions
- Planning a significant refactoring
- Evaluating a technical approach
- Any task where you feel unsure about requirements

---

## Core Pattern

```
1. EXPLORE → Read context (code, docs, existing work)
2. INTERVIEW → AskUserQuestion in rounds (5-10 questions)
3. DOCUMENT → Write spec/plan based on answers
4. CONFIRM → Ask for approval before proceeding
5. IMPLEMENT → Only then, start the work
```

---

## Interview Prompts by Context

### Feature Development

Ask questions about:
- **Core user scenario**: "When you imagine people using this, what's the actual scenario?"
- **Pain point**: "What's happening right now that this solves? What's the actual pain?"
- **Edge cases**: "What happens when [unexpected input/state/network failure]?"
- **Tradeoffs**: "You could do X or Y here — which matters more: speed or flexibility?"
- **Scope**: "What's the minimal version that delivers value? What can be deferred?"

### Bug Investigation

Ask questions about:
- **Reproduction**: "What are the EXACT steps to reproduce? Not 'sometimes it crashes' — what specifically?"
- **Environment**: "Browser, OS, network conditions, when did it start?"
- **Patterns**: "Does it happen every time? Only for certain users? Only when X condition?"
- **Recent changes**: "What changed around when this started? Code, dependencies, environment?"

### Architecture Decisions

Ask questions about:
- **Constraints**: "What are the hard constraints? Performance, security, compatibility?"
- **Tradeoffs**: "You're optimizing for X — what are you sacrificing? Is that acceptable?"
- **Future-proofing**: "What needs to be true 6 months from now for this to still work?"
- **Integration**: "How does this connect to existing systems? What are the integration points?"

---

## Key Instructions for the Agent

```markdown
You are in INTERVIEW MODE. Your job is to explore the task thoroughly BEFORE doing any work.

**CRITICAL RULES:**

1. **Single questions only** — Ask one question at a time, wait for answer
2. **No obvious questions** — Don't ask "what color should the button be?" Ask questions that surface hidden assumptions
3. **Probe tradeoffs** — Force explicit decisions about what matters and what doesn't
4. **Challenge gently** — "Are you sure about X? What if Y happens?"
5. **Document continuously** — Capture answers externally (don't rely on working memory)
6. **Round limits** — 5-10 questions max, then synthesize and ask for confirmation
7. **Approval gate** — Do NOT proceed with work until user approves the plan

**INTERVIEW FLOW:**

Round 1: Core scenario / problem statement
Round 2: Constraints and requirements
Round 3: Edge cases and failure modes
Round 4: Tradeoffs and prioritization
Round 5: Integration and dependencies
Round 6+: Follow-up based on previous answers

**AFTER INTERVIEW:**

Synthesize answers into a brief spec:
- What we're building
- Why it matters
- Key decisions made
- Edge cases considered
- Implementation approach

Ask: "Does this capture everything? Approve to proceed, or should we revisit something?"

**Only after explicit approval, begin work.**
```

---

## Example Interview Sessions

### Example 1: Feature Interview

**User**: `/interview-me I want to add a dark mode toggle`

**Round 1 - Core scenario**:
> "When you imagine someone using dark mode, what's the scenario? Are they switching manually, does it follow system preference, or both?"

**Round 2 - Scope**:
> "Is this 'just add a toggle' or 'comprehensive dark theme across the entire app'? What's the minimal version?"

**Round 3 - Edge cases**:
> "What happens to custom colors? Do we invert them, provide dark variants, or something else?"

**Round 4 - Tradeoffs**:
> "You could use CSS filters (fast but imprecise) or design tokens (work but consistent). Which matters more?"

**Result**: Clear spec before any CSS is written.

### Example 2: Bug Investigation

**User**: `/interview-me The app crashes when I upload large files`

**Round 1 - Reproduction**:
> "What's 'large'? 1MB? 100MB? And what exactly happens — browser crash, server error, or something else?"

**Round 2 - Environment**:
> "Does this happen in all browsers or just one? What network conditions — WiFi, cellular, etc.?"

**Round 3 - Patterns**:
> "Does it fail at exactly the same size every time, or does it vary? What does the server log show?"

**Result**: Identifies whether it's a client timeout, server memory limit, or something else.

---

## Variations

### `/interview-me:deep`
- 15-20 questions instead of 5-10
- For complex features or architectural decisions
- Explores multiple dimensions deeply

### `/interview-me:quick`
- 3-5 questions
- For straightforward tasks where you just want to validate assumptions
- Fast confirmation before proceeding

### `/interview-me:bug`
- Specialized for debugging
- Focuses on reproduction, environment, patterns
- See "Bug Investigation" prompts above

---

## References

- Thariq's interview pattern: "Read @SPEC.md and interview me using AskUserQuestion"
- Jeremy Watt's interview skills: Multi-round Q&A for feature development
- Socratic method: Systematic questioning to surface hidden assumptions

---

## Why This Matters for Your Ecosystem

This skill integrates with your cognitive prosthetic ecosystem:

- **aStudio** → Visual system for building the UI
- **Skills** → /interview-me is one of your 30+ skills
- **sTools** → Validates and syncs this skill across Codex/Claude
- **Ralph Gold** → Orchestrator can invoke /interview-me before tasks

**This is a cognitive prosthetic for "requirements gathering"** — externalizes the thinking you'd otherwise struggle to hold in working memory.
