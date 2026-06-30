---
name: skill-creator
description: "Use when creating or updating a Codex skill package with focused triggers, progressive disclosure, evals, evidence, or tool integration."
metadata:
  short-description: Create or update a skill
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular folders that give Codex specialized workflows, tool
integrations, domain context, and bundled resources for tasks it must repeat
reliably.

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Codex needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Codex is already very smart.** Only add context Codex doesn't already have. Challenge each piece of information: "Does Codex really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

### Protect Validation Integrity

You may use subagents during iteration to validate whether a skill works on realistic tasks or whether a suspected problem is real. This is most useful when you want an independent pass on the skill's behavior, outputs, or failure modes after a revision.  Only do this when it is possible to start new subagents.

When using subagents for validation, treat that as an evaluation surface. The goal is to learn whether the skill generalizes, not whether another agent can reconstruct the answer from leaked context.

Prefer raw artifacts such as example prompts, outputs, diffs, logs, or traces. Give the minimum task-local context needed to perform the validation. Avoid passing the intended answer, suspected bug, intended fix, or your prior conclusions unless the validation explicitly requires them.

### Anatomy of a Skill

Every skill consists of required `SKILL.md`, recommended
`agents/openai.yaml`, and optional `scripts/`, `references/`, and
`assets/` resources. SDK-aware repositories may also require a minimal
`references/contract.yaml` package contract.

#### SKILL.md (required)

- **Frontmatter**: YAML with `name` and `description`. The description is the trigger surface, so include when to use the skill there.
- **Body**: Instructions loaded only after the skill triggers.

#### Agents metadata (recommended)

- UI-facing metadata for skill lists and chips
- Read references/openai_yaml.md before generating values and follow its descriptions and constraints
- Create: human-facing `display_name`, `short_description`, and `default_prompt` by reading the skill
- Generate deterministically by passing the values as `--interface key=value` to `scripts/generate_openai_yaml.py` or `scripts/init_skill.py`
- On updates: validate `agents/openai.yaml` still matches SKILL.md; regenerate if stale
- Only include other optional interface fields (icons, brand color) if explicitly provided
- See references/openai_yaml.md for field definitions and examples

#### SDK package contract (recommended)

OpenAI's skill shape keeps `SKILL.md` as the required authoring surface,
`agents/openai.yaml` as optional appearance/dependency metadata, and
`references/` as deeper loaded-on-demand material. For SDK-aware repositories,
put the strict package contract in `references/contract.yaml` rather than in
frontmatter or `agents/openai.yaml`.

Minimum contract fields:

- `purpose`
- `inputs`
- `outputs`
- `permission_profile`
- `observability` or `evidence_policy`

Recommended contract fields:

- `triggers`
- `non_goals`
- `risks`
- `output_contract`
- `rollback_procedure`
- `context_lifecycle`

The contract should let an agent answer: what does this skill do, what does it
accept, what does it emit, what may it read/write, what evidence proves it, what
does it not prove, and what is the next safe validation command. Local OTEL,
session, or observability collectors can enrich evidence, but deterministic
artifacts and validators remain the readiness authority.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code for repeated or fragile operations. Scripts are token
efficient and deterministic, but Codex may still need to read them when
patching or adapting behavior.

##### References (`references/`)

Load-on-demand documentation such as schemas, policies, API details, or detailed
workflow guides. Keep SKILL.md lean by moving bulky detail here, and add search
patterns for very large files. Markdown reference files and vendored
KnowledgeOS capsule bodies need specific, filename-aligned H1 headings so
agents can invoke the right file from routing text.

##### Assets (`assets/`)

Output resources such as templates, images, icons, boilerplate code, fonts, or
sample files. Use assets when Codex needs files for the final artifact without
loading them as instructions.

#### What to Not Include in a Skill

Do not create auxiliary process notes such as INSTALLATION_GUIDE.md,
QUICK_REFERENCE.md, CHANGELOG.md, or scratch handoff notes unless needed to run.
In SDK-aware repositories, always create or maintain README.md for skills and
plugins; Codex/OpenAI runtime may ignore README.md, but registry and
package-review surfaces use it.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Codex (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md to essentials and split detailed variants into references.
Common patterns:

- high-level SKILL.md with links to advanced reference files
- domain-specific references such as finance, sales, or product
- framework/provider-specific references such as aws, gcp, or azure
- conditional details linked from the relevant workflow step

Important guidelines:

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Codex can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Validate the skill (run quick_validate.py)
6. Iterate based on real usage and forward-test complex skills.

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

For SDK-aware create or update work, run ./bin/ask sdk start <skill-path>
--json --robot after the first package path exists. The start receipt decides
the next legal lane and blocks downstream eval, Tessl, registry, publish,
sync, or runtime-readiness claims until the shared SDK pipeline reaches them.

Shared SDK pipeline:

1. Strict audit and package verify.
1a. Package verify must pass `reference_quality`, including
    `reference_heading_invocable` for Markdown references and capsule bodies.
2. ./bin/ask sdk security risk-modes <skill-path> --preview --json --robot.
3. Scenario-quality, scorer-quality, and scorer-calibration previews.
4. oss-local internal eval through ./bin/ask sdk eval run ... --codex-profile oss-local.
5. Repair skill, references, scenarios, rubrics, validators, or judge expectations until oss-local is around the 70-75 success band for the current candidate.
6. oss-cloud internal eval through ./bin/ask sdk eval run ... --codex-profile oss-cloud.
7. Iterate from oss-local after every failure until internal evidence is at or above the 90 success band.
8. Prepare Tessl scenarios through `./bin/ask evals prepare-tessl-scenarios <skill-path> --json --robot`, review generated scenarios, and classify scenario drift before any live-private Tessl progression.
9. Tessl local proof with --execute, Tessl live-private dry-run, then handoff-readiness.
10. Tessl live-private is confirmational only: expected score is >=90 and >= baseline before registry or production claims.
11. Decide private workspace retention versus public registry publication explicitly for the operator-approved Tessl workspace.

## Examples

User: "Turn our recurring PR triage into a skill."
Action: identify triggers, create the minimal package, add evals, and run validation.

User: "Update this draft SKILL.md so Codex can use it."
Action: preserve the intent, move bulky detail to references, and rerun validation.

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- When generating names, generate a name under 64 characters (letters, digits, hyphens).
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

Clearly understand concrete examples of how the skill will be used. This can
come from direct user examples or generated examples validated with user
feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"
- "Where should I create this skill? If you do not have a preference, I will place it in `$CODEX_HOME/skills` (or `~/.codex/skills` when `CODEX_HOME` is unset) so Codex can discover it automatically."

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

Use examples to choose `scripts/`, `references/`, and `assets/`.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists. In this case, continue to the next step.

Before running `init_skill.py`, ask where the user wants the skill created. If they do not specify a location, default to `$CODEX_HOME/skills`; when `CODEX_HOME` is unset, fall back to `~/.codex/skills` so the skill is auto-discovered.

When creating a new skill from scratch, run `init_skill.py` to generate the
template skill directory.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

Examples:

```bash
scripts/init_skill.py my-skill --path "${CODEX_HOME:-$HOME/.codex}/skills"
scripts/init_skill.py my-skill --path "${CODEX_HOME:-$HOME/.codex}/skills" --resources scripts,references
scripts/init_skill.py my-skill --path ~/work/skills --resources scripts --examples
```

The script creates the skill directory, SKILL.md template, optional resource
directories, optional examples, and `agents/openai.yaml` values passed through
`--interface key=value`.

After initialization, customize the SKILL.md and add resources as needed. If you used `--examples`, replace or delete placeholder files.

For SDK-aware packages, add `references/contract.yaml` during customization.
Do not expand YAML frontmatter beyond `name` and `description`; frontmatter
is the trigger surface, while `references/contract.yaml` is the validation and
installation contract.

Generate `display_name`, `short_description`, and `default_prompt` by reading the skill, then pass them as `--interface key=value` to `init_skill.py` or regenerate with:

```bash
scripts/generate_openai_yaml.py <path/to/skill-folder> --interface key=value
```

Only include other optional interface fields when the user explicitly provides them. For full field descriptions and examples, see references/openai_yaml.md.

### Step 4: Edit the Skill

When editing the skill, include non-obvious procedural knowledge,
domain-specific details, and reusable assets that help another Codex instance
execute the task.

After substantial revisions, or if the skill is particularly tricky, you should use subagents to forward-test the skill on realistic tasks or artifacts. When doing so, pass the artifact under validation rather than your diagnosis of what is wrong, and keep the prompt generic enough that success depends on transferable reasoning rather than hidden ground truth.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

If you used `--examples`, delete any placeholder files that are not needed for the skill. Only create resource directories that are actually required.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps Codex understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Codex.
  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Codex needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Validate the Skill

Once development of the skill is complete, validate the skill folder to catch basic issues early:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

The validation script checks YAML frontmatter format, required fields, and naming rules. If validation fails, fix the reported issues and run the command again.

When the target repo exposes a Skills SDK package command, also validate the
portable contract:

```bash
./bin/ask skills package <path-or-handle> --json --robot
```

For strict SDK repositories, creation is not complete until
`package_contract.sdk_contract.required_fields.missing` is empty. This means
the skill must declare purpose, inputs, outputs, permission profile, evals, and
evidence policy. Treat local `~/.agents/` OTEL, session, or observability
providers as enrichment only; they explain runs but do not replace eval
artifacts or deterministic validation.

### Step 6: Iterate

After testing the skill, you may detect the skill is complex enough that it requires forward-testing; or users may request improvements.

User testing often this happens right after using the skill, with fresh context of how the skill performed.

**Forward-testing and iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again
5. Forward-test if it is reasonable and appropriate

## Forward-testing

To forward-test, launch subagents as a way to stress test the skill with minimal context.
Subagents should *not* know that they are being asked to test the skill.  They should be treated as
an agent asked to perform a task by the user.  Prompts to subagents should look like:
  `Use $skill-x at /path/to/skill-x to solve problem y`
Not:
  `Review the skill at /path/to/skill-x; pretend a user asks you to...`

Decision rule for forward-testing:
  - Err on the side of forward-testing
  - Ask for approval if you think there's a risk that forward-testing would:
    * take a long time,
    * require additional approvals from the user, or
    * modify live production systems

  In these cases, show the user your proposed prompt and request (1) a yes/no decision, and
  (2) any suggested modifictions.

Considerations when forward-testing:
   - use fresh threads for independent passes
   - pass the skill, and a request in a similar way the user would.
   - pass raw artifacts, not your conclusions
   - avoid showing expected answers or intended fixes
   - rebuild context from source artifacts after each iteration
   - review the subagent's output and reasoning and emitted artifacts
   - avoid leaving artifacts the agent can find on disk between iterations;
     clean up subagents' artifacts to avoid additional contamination.

If forward-testing only succeeds when subagents see leaked context, tighten the skill or the
forward-testing setup before trusting the result.
