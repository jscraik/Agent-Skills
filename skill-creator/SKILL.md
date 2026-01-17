---
name: skill-creator
description: Create, update, validate, or package skills and their resources. Use when a user asks to create or revise a skill, improve routing/portability, or package a skill; not for installing skills or choosing the right build primitive (use skill-installer or decide-build-primitive).
license: Apache-2.0 (see LICENSE.txt)
compatibility: Codex + Claude Code. Bundled scripts require Python 3.x + PyYAML. No network required unless stated.
metadata:
  short-description: Create or update a skill
  version: "1.1.0"
  last_updated: "2026-01-04"
---

# Skill Creator

This skill provides guidance for creating effective skills.

**Version**: 1.1.0  
**Last updated**: 2026-01-04

## When to Use

- Use when the user asks to create, update, validate, or package a skill.
- Use when the user requests skill design guidance, trigger tuning, or portability across Codex and Claude Code.

## Inputs

- Required: user goal, example prompts, and the target skill name.
- If updating: existing skill path and any current SKILL.md or bundled resources.
- Optional: target platforms (Codex/Claude Code), desired scripts/references/assets, validation or packaging requirements.

## Outputs

- Updated skill artifacts (SKILL.md plus any references/scripts/assets).
- Clear validation results and any follow-up actions.
- Packaging instructions or artifacts when requested.
- If outputs are schema-bound, include `schema_version` in the output contract.

## Constraints

- Keep SKILL.md concise (prefer < 500 lines) and use progressive disclosure via references.
- Follow frontmatter requirements and keep `name`/`description` single-line.
- Do not add new dependencies without explicit user approval.
- Redact secrets or sensitive data by default in any outputs or logs.
- Check against GOLD Industry Standards guide in `~/.codex/AGENTS.override.md`.

## About Skills (Short)

For deeper background on skill purpose, structure, and best-use philosophy, see `references/about-skills.md`.

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

Think of Codex as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Philosophy Before Procedure

Before writing step-by-step instructions, establish a small mental framework that guides decisions:

- Define the purpose, audience, and success criteria for the skill's domain.
- Add 3-5 pre-action questions or 3-5 guiding principles.
- Use a simple mental model or spectrum when helpful.
- Frame guidance to **unlock** capabilities, not constrain outputs.

This prevents rigid templates and makes the skill adaptable to context.

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. Codex reads these to determine when the skill gets used, so be clear and comprehensive about what the skill does and when to use it. Keep frontmatter minimal by default; only add optional fields (e.g., `metadata`, `license`, `compatibility`, `allowed-tools`) when required.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

**Metadata hygiene (portable):**
- Use `metadata.version` and `metadata.last_updated` for machine-readable provenance.
- Use `metadata.source_repo` (canonical HTTPS URL) and `metadata.source_rev` (40-char SHA). Packaging can inject these automatically when a git repo is present.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Codex for patching or environment-specific adjustments
- **Quality bar**: Document dependencies and expected inputs/outputs; handle edge cases and provide clear error messages. If network access is required, say so explicitly (e.g., in `compatibility`).

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Codex's process and thinking.

- **When to include**: For documentation that Codex should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Codex determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Codex produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Codex to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5000 tokens recommended)
3. **Bundled resources** - As needed by Codex (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, reference them from SKILL.md and describe when to read them so they are discoverable without bloating context.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

See `references/progressive-disclosure-patterns.md` for worked examples and guidance.

## Anti-Patterns to Avoid (Quick List)

- **Template trap**: Rigid templates that force slot-filling and generic output.
- **Checklist without rationale**: Rules with no underlying philosophy or decision framework.
- **Generic guidance**: Advice that applies to everything but helps with nothing.
- **Context blindness**: "Always X" rules that ignore constraints and goals.
- **Missing negative guidance**: No explicit "don't do this" warnings.
- **Duplication**: The same content in SKILL.md and references.

## Variation Guidance (Prevent Convergence)

Explicitly require variation when outputs should not look identical:

- Name 2-3 dimensions that must vary (structure, tone, depth, examples, visuals).
- Call out patterns to avoid repeating.
- Encourage context-specific choices over favorites.

## Composability

Design skills to work well together:

- Keep the scope tight and the description specific to reduce collisions.
- Avoid explicit references to other skills.
- Use "prefer X unless..." instead of "always/never" where context matters.

## Claude Enhanced Mode (Optional)

If the skill is Claude-first (or needs Claude-specific behavior), add Claude-only frontmatter keys in a dedicated section and keep portable mode as the default:

- `allowed-tools`: explicit tool allowlist.
- `context: fork`: isolate tool execution or sub-agents.
- `hooks`: PreToolUse / PostToolUse / Stop handlers.
- `user-invocable`: allow manual invocation in Claude Code UI.
- `disable-model-invocation`: prevent model auto-runs when required.

When portability is required, keep Claude-only keys out of the portable template and add them in a Claude-specific variant.

## Reference Map (When to Open Which File)

- **workflows.md**: Use when defining multi-step or conditional workflows.
- **output-patterns.md**: Use when outputs need strict templates or quality patterns.
- **philosophy-patterns.md**: Use when the skill needs a strong mental model or guiding questions.
- **anti-patterns.md**: Use to add explicit “don’t do this” guidance.
- **variation-patterns.md**: Use when preventing output convergence or repetitive defaults.
- **composability.md**: Use when the skill overlaps other domains or may collide with other skills.
- **about-skills.md**: Use when you need deeper framing or rationale.
- **portable-skills.md**: Use when making skills portable across Claude Code and Codex.
- **quality-tools.md**: Use when running or interpreting skill quality tooling.
- **examples.md**: Use when you need concrete examples to calibrate output style.
- **progressive-disclosure-patterns.md**: Use when you need worked examples for progressive disclosure.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Validate the skill (quick_validate.py or skills-ref)
6. Package the skill (run package_skill.py)
7. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- Use 1–64 characters; do not start or end with a hyphen; do not use consecutive hyphens.
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

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

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

Always include this instruction into every Skill.md "- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md"

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

Examples:

```bash
scripts/init_skill.py my-skill --path skills/public
scripts/init_skill.py my-skill --path skills/public --resources scripts,references
scripts/init_skill.py my-skill --path skills/public --resources scripts --examples
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Optionally creates resource directories based on `--resources`
- Optionally adds example files when `--examples` is set

After initialization, customize the SKILL.md and add resources as needed. If you used `--examples`, replace or delete placeholder files.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Codex to use. Include information that would be beneficial and non-obvious to Codex. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Codex instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns
- **Philosophy-first design**: See references/philosophy-patterns.md for mental framework patterns
- **Anti-patterns**: See references/anti-patterns.md for common mistakes and fixes
- **Variation**: See references/variation-patterns.md for techniques to prevent output convergence
- **Composability**: See references/composability.md for skills that play well together
- **Background refresher**: See references/about-skills.md for purpose and structure overview

These files contain established best practices for effective skill design.

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

Only add optional frontmatter fields (`metadata`, `license`, `compatibility`, `allowed-tools`) when required. Keep frontmatter minimal by default.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Validate the Skill (Recommended)

## Validation

Fail fast: stop at the first failed validation gate, fix the issue, and re-run the failed check before proceeding.

Run the lightweight validator first:

```bash
python scripts/quick_validate.py <path/to/skill-folder>
```

If available, run the deeper validator:

```bash
skills-ref validate <path/to/skill-folder>
```

Use validation results to fix naming or frontmatter issues before packaging.
If `skills-ref` is installed in a local venv, activate it first (e.g., `~/.codex/.venv-skills-ref/bin/activate`).
Default local venv path for this skill: `~/.codex/skills/skill-creator/.venv`.

**If `skills-ref` is missing, install it into the skill-creator venv:**

1) Read the pinned commit from `~/.codex/.venv-skills-ref/lib/pythonX.Y/site-packages/skills_ref-*/direct_url.json` (if that venv exists).
2) Install with pip into `~/.codex/skills/skill-creator/.venv` using the same commit:

```bash
~/.codex/skills/skill-creator/.venv/bin/python -m pip install \
  "git+https://github.com/agentskills/agentskills@<commit>#subdirectory=skills-ref"
```

If no pinned commit is available, ask the user which revision to use rather than guessing.

### Step 6: Package a Skill

Once development of the skill is complete, package it into a distributable .skill file.

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:

   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.

Packaging excludes common dev artifacts by default (e.g., .DS_Store, **pycache**, .venv, .pytest_cache, .mypy_cache, .ruff_cache, .idea, .vscode, .git) and anything matched by `.skillignore` patterns at the skill root. Use one glob per line and `#` for comments:

```text
# Ignore scratch artifacts
assets/tmp/**
*.log
```

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Step 7: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

## Trigger Testing (Quick Check)

Before shipping a new skill, write 3–5 example prompts and confirm they would select this skill over similar skills. If not, tighten the `description` keywords or scope.

Example prompts for this skill:
- "Create a new skill for handling database migrations."
- "Improve this existing skill so it triggers more reliably."
- "Design a skill that helps with CLI specification writing."
- "Audit this SKILL.md for quality and suggest upgrades."
- "Package and validate a skill for distribution."

## Quality Analysis and Examples

See `references/quality-tools.md` for quality tooling guidance and `references/examples.md` for calibrated examples.

## Compliance Evidence (For Significant Skills)

Provide at least one verifiable signal that the skill meets current best practices:

- Standards mapping (brief note mapping to applicable specs/best practices)
- Automated checks (e.g., `python scripts/quick_validate.py`, `skills-ref validate`, lint/tests for scripts)
- Review artifact (self-review note or peer review)
- Deviation rationale (if any experimental approach is used)
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

Minimum recommended evidence for significant changes:

- Run `python scripts/quick_validate.py` and capture the output
- Run `python scripts/skill_gate.py` and capture the output
- Run `python scripts/run_skill_evals.py` and capture the report summary
- Add a short self-review note covering frontmatter, packaging, and any scripts touched
- skills-ref validate from `~/.codex/.venv-skills-ref/bin/skills-ref`.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
