# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Goal and name](#round-1-goal-and-name)
- [Round 2: Trigger](#round-2-trigger)
- [Round 3: Step-by-step process](#round-3-step-by-step-process)
- [Round 4: Inputs outputs and dependencies](#round-4-inputs-outputs-and-dependencies)
- [Round 5: Guardrails and edge cases](#round-5-guardrails-and-edge-cases)
- [Round 6: Confirmation](#round-6-confirmation)
- [Skipping rounds](#skipping-rounds)

## When to use this reference

Use this when a skill request is promising but underspecified:
- the user wants a new skill but has not fully described the workflow;
- the user wants to improve an existing skill but the failure mode is still fuzzy;
- the request spans multiple outputs, tools, or trigger conditions and you need a reliable boundary before building.

## How to run the interview

Default behavior:
- use Codex `request_user_input` (AskQuestion parity) first;
- if `request_user_input` is unavailable, ask 1-3 numbered chat questions for the same round;
- ask **one round at a time**;
- do not advance until the user answers the current round;
- skip rounds already answered by the thread;
- stop when you are about **95% confident** you understand the skill well enough to build it safely.

Tool-fit guidance:
- If a round can fit into **1–3 short prompts**, use `request_user_input`.
- If `request_user_input` is unavailable in the runtime, keep the same one-round flow in chat and preserve the same questions/options.
- Prefer recommended choices when the decision is common, and rely on the client’s free-form **Other** path when you need specifics.
- If a round truly needs richer prose than the tool can capture cleanly, ask **one concise follow-up in chat**, then return to the round flow.

Interaction style:
- Lead with one simple question, not a wall of bullets.
- Explain the purpose of the round in plain language before asking it.
- Prefer user language over framework language:
  - say “What should this skill help with?” before “Define the capability boundary.”
  - say “How should someone ask for this?” before “Describe trigger phrases.”
- When using `request_user_input`, make the options feel like realistic choices a user would actually recognize.
- Use recommended defaults, but keep the path open for “Other” details.
- If the user already answered 80 percent of a round, ask only the missing 20 percent.

Recommended `request_user_input` pattern:
1. short round intro in chat;
2. one tool question for the main choice;
3. if needed, one follow-up question for the missing detail;
4. summarize what you learned before moving on.

Do not:
- present all six rounds up front;
- ask duplicate questions in different wording;
- force users to translate their needs into internal skill jargon;
- use `request_user_input` when free-form explanation is clearly the easier path.

## Request user input mini-templates

Use these as patterns, not rigid scripts. Keep the tone conversational and adapt the labels to the user’s language.

Shared template rules:
- start with a one-line chat intro before the tool call;
- make the tool question about **one decision only**;
- use 2-3 options the user can recognize immediately;
- keep option labels short and outcome-focused;
- use the free-form follow-up only for the missing detail, not to restart the round;
- after each answer, summarize what you learned in one or two lines.

### Round 1 template: goal and name

Chat intro:
- “Let’s start simple: what should this skill help you do?”

Good tool question shape:
- **Header:** `Goal`
- **Question:** “What kind of help should this skill provide?”
- **Options:**
  - `Create new workflow (Recommended)` — Best when the skill is mostly net-new.
  - `Improve current workflow` — Best when an existing skill or prompt already exists.
  - `Package repeatable task` — Best when the workflow already works and needs reuse.

Follow-up prompt if needed:
- “In one sentence, what problem should it solve every time?”

### Round 2 template: trigger

Chat intro:
- “Next, let’s make sure Codex knows when this skill is the right fit.”

Good tool question shape:
- **Header:** `Trigger`
- **Question:** “How should this skill usually be invoked?”
- **Options:**
  - `User asks directly (Recommended)` — Best for slash-style or explicit requests.
  - `Codex can auto-pick it` — Best when the request is easy to recognize from natural language.
  - `Both` — Best when the skill needs a direct name and a strong auto-route description.

Follow-up prompt if needed:
- “Give me 2 or 3 example phrases someone would actually say.”

### Round 3 template: process

Chat intro:
- “Now let’s make the workflow concrete.”

Good tool question shape:
- **Header:** `Flow`
- **Question:** “What kind of run should this feel like?”
- **Options:**
  - `Guided back-and-forth (Recommended)` — Best when the skill needs confirmations or missing inputs.
  - `One-pass execution` — Best when the task can run start to finish with little interaction.
  - `Mixed` — Best when it starts with questions, then runs through the rest.

Follow-up prompt if needed:
- “List the main steps in order: first, next, then, and finally.”

### Round 4 template: inputs and outputs

Chat intro:
- “Let’s pin down what the skill reads and what it should produce.”

Good tool question shape:
- **Header:** `Inputs`
- **Question:** “Where should this skill mostly get its information from?”
- **Options:**
  - `User-provided details (Recommended)` — Best when prompts or answers are the main inputs.
  - `Files or repo context` — Best when local paths, code, or docs drive the workflow.
  - `Tools or external data` — Best when APIs, MCP servers, or scripts are required.

Follow-up prompt if needed:
- “What should it produce, and where should that output go?”

### Round 5 template: guardrails

Chat intro:
- “Last, let’s make the boundaries explicit so the skill behaves safely.”

Good tool question shape:
- **Header:** `Guardrails`
- **Question:** “What should this skill optimize for most?”
- **Options:**
  - `Safety and predictability (Recommended)` — Best when the skill should avoid surprising behavior.
  - `Speed and low friction` — Best when fast progress matters more than exhaustive checks.
  - `Depth and completeness` — Best when richer output is worth more time or tokens.

Follow-up prompt if needed:
- “What should this skill never do, even if the user sounds impatient?”

### Round 6 template: confirmation

Chat intro:
- “Here’s my understanding so far.”

Confirmation ask:
- summarize with the standard skill summary block;
- call out assumptions with an `Assumptions:` line when needed;
- end with one simple confirmation question:
  - “Does this capture it well enough for me to build?”

## Copy paste payload examples

Use these when you want a fast, tool-native starting point. Edit the wording to match the user’s language and the specific skill.

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Goal",
      "id": "goal_mode",
      "question": "What kind of skill are we shaping?",
      "options": [
        {
          "label": "New skill (Recommended)",
          "description": "Use this when the workflow is mostly net-new."
        },
        {
          "label": "Improve skill",
          "description": "Use this when an existing skill needs tightening."
        },
        {
          "label": "Package workflow",
          "description": "Use this when the workflow already works and needs reuse."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- “In one sentence, what should this skill reliably help with every time?”

### Round 2 example

```json
{
  "questions": [
    {
      "header": "Trigger",
      "id": "trigger_mode",
      "question": "How should Codex usually reach for this skill?",
      "options": [
        {
          "label": "User asks (Recommended)",
          "description": "Best for direct or slash-style requests."
        },
        {
          "label": "Auto pick",
          "description": "Best when the request is easy to recognize from natural language."
        },
        {
          "label": "Both",
          "description": "Best when the skill should work for direct naming and auto-routing."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- “Give me 2 or 3 phrases someone would naturally say when they want this.”

### Round 3 example

```json
{
  "questions": [
    {
      "header": "Flow",
      "id": "flow_mode",
      "question": "What should the run feel like?",
      "options": [
        {
          "label": "Guided flow (Recommended)",
          "description": "Best when the skill should ask questions or confirm decisions."
        },
        {
          "label": "One pass",
          "description": "Best when the task can run start to finish with little interaction."
        },
        {
          "label": "Mixed",
          "description": "Best when the skill starts with questions and then runs through the rest."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- “List the main steps in order: first, next, then, and finally.”

### Round 4 example

```json
{
  "questions": [
    {
      "header": "Inputs",
      "id": "input_mode",
      "question": "Where should this skill mostly get its information from?",
      "options": [
        {
          "label": "User details (Recommended)",
          "description": "Best when prompts or answers are the main inputs."
        },
        {
          "label": "Files or repo",
          "description": "Best when local paths, code, or docs drive the workflow."
        },
        {
          "label": "Tools or APIs",
          "description": "Best when scripts, MCP servers, or external data are required."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- “What should it produce, and where should that output go?”

### Round 5 example

```json
{
  "questions": [
    {
      "header": "Guardrails",
      "id": "guardrail_priority",
      "question": "What should this skill optimize for most?",
      "options": [
        {
          "label": "Safe default (Recommended)",
          "description": "Best when the skill should avoid surprising or risky behavior."
        },
        {
          "label": "Fastest path",
          "description": "Best when speed matters more than exhaustive checks."
        },
        {
          "label": "Deep output",
          "description": "Best when fuller output is worth more time or tokens."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- “What should this skill never do, even if the user sounds impatient?”

### Round 6 example

Round 6 is usually better as a chat summary than a tool call. Use the standard summary block, then end with:
- “Does this capture it well enough for me to build?”

## Round 1: Goal and name

**Why this matters:** a clear goal prevents scope creep. The name usually becomes the memorable handle, so it should be specific and easy to route on.

Ask:
- What does this skill do?
- What problem does it solve or workflow does it automate?
- What should we call it?

Friendly opener:
- “Let’s start with the basics: what should this skill help you do?”

Agent behavior:
- Suggest a name based on the answer.
- Prefer lowercase kebab-case.
- Keep it concise and distinctive.
- Offer 1-2 candidate names when the user has not named it yet.

## Round 2: Trigger

**Why this matters:** the frontmatter `description` is the routing boundary. Bad trigger language means the skill never fires; overly broad language means it fires when it should not.

Ask:
- What would someone naturally say to trigger this?
- Is it user-invoked, auto-invocable, or both?
- Does it accept arguments? If so, what kinds?

Friendly opener:
- “Next, how should Codex know this skill is the right fit?”

Capture:
- 2–3 realistic natural-language trigger phrases;
- any arguments such as topic, URL, file path, repo path, or mode.

## Round 3: Step-by-step process

**Why this matters:** vague steps produce vague outputs. Specific steps produce more consistent execution.

Ask:
- Walk me through what should happen from trigger to output.
- For each step, does Codex/Codex do it directly or delegate to a script/tool/subagent?
- Is the workflow conversational or fire-and-forget?

Friendly opener:
- “Now let’s make the workflow concrete. What should happen first, then next?”

Capture:
- the ordered workflow;
- delegation boundaries;
- whether the skill pauses for user confirmation or runs straight through.

## Round 4: Inputs outputs and dependencies

**Why this matters:** if inputs, outputs, or dependencies are fuzzy, the skill becomes inconsistent and hard to validate.

Ask:
- What inputs does the skill need?
- What does it produce, and where should outputs go?
- Which APIs, tools, scripts, MCP servers, or CLIs are required?
- Does it need templates, examples, reference docs, or style guides?

Friendly opener:
- “What does this skill need to read, and what should it produce?”

Capture:
- input file types or external data sources;
- output artifacts, paths, and formats;
- any hard dependencies or optional helpers.

## Round 5: Guardrails and edge cases

**Why this matters:** skills without explicit guardrails drift into costly, unsafe, or simply surprising behavior.

Ask:
- What could go wrong?
- What should this skill explicitly not do?
- Are there cost concerns?
- Are there ordering constraints or must-check conditions?

Friendly opener:
- “Last, what should this skill be careful about?”

Capture:
- failure modes;
- hard boundaries;
- cost or latency sensitivities;
- dependency ordering rules.

## Round 6: Confirmation

**Why this matters:** catching misunderstandings now is far cheaper than rebuilding the skill later.

Before writing the skill, summarize back to the user in this structure:

```markdown
## Skill Summary: [name]

**Goal:** [one sentence]
**Trigger:** `/name` + [natural language phrases]
**Arguments:** [what it accepts, or "none"]

**Process:**
1. [step]
2. [step]
...

**Inputs:** [what it reads/needs]
**Outputs:** [what it produces + where]
**Dependencies:** [APIs, scripts, agents, reference files]
**Guardrails:** [what can go wrong, what to avoid]
```

Then ask:
- “Does this capture it?”
- “Anything to add or change before I build it?”

Only proceed after the user confirms.

Good confirmation style:
- keep the summary tight;
- separate known facts from assumptions;
- make it easy for the user to say “yes” or correct one field quickly.

## Skipping rounds

Do not re-ask what you already know.

If the initial request already provides:
- a clear goal,
- trigger examples,
- the workflow,
- inputs/outputs,
- and guardrails,

skip the answered rounds and only ask for the missing pieces.
