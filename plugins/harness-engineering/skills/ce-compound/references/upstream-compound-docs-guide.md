# Upstream Compound Docs Guide

Imported from `EveryInc/compound-engineering-plugin` commit `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`.

Read when:
- the target repository already uses YAML-frontmatter `docs/solutions/` files
- the team wants enum-validated solved-problem capture
- the learning-capture flow should include a post-documentation decision menu

## Purpose

Capture solved problems as categorized documentation with YAML frontmatter for fast lookup.

## Overview

This workflow captures problem solutions immediately after confirmation, creating structured documentation that serves as a searchable knowledge base for future sessions.

Organization:
- single-file architecture
- each problem lives in one markdown file inside its symptom category directory
- files use YAML frontmatter for metadata and searchability

## 7-Step Process

### Step 1: Detect confirmation

Auto-invoke after phrases such as:
- `that worked`
- `it's fixed`
- `working now`
- `problem solved`
- `that did it`

Manual trigger:
- `/doc-fix`

Document only non-trivial problems:
- multiple investigation attempts were needed
- debugging was tricky or time-consuming
- the solution was non-obvious
- future sessions would benefit from a durable record

Skip documentation for:
- simple typos
- obvious syntax errors
- trivial fixes corrected immediately

### Step 2: Gather context

Extract from conversation history:
- module name
- exact symptom or error
- investigation attempts
- root cause
- solution
- prevention guidance
- environment details such as version, stage, and file references when available

Blocking rule:
- if module name, exact error or symptom, stage, or resolution steps are missing, ask for them before proceeding

### Step 3: Check existing docs

Search `docs/solutions/` for similar issues.

If a similar issue exists, present a user choice:
1. Create a new doc with a cross-reference
2. Update the existing doc only if the root cause is the same
3. Choose another action

If no similar issue exists, continue without pausing.

### Step 4: Generate filename

Format:
- `[sanitized-symptom]-[module]-[YYYYMMDD].md`

Rules:
- lowercase
- replace spaces with hyphens
- remove special characters except hyphens
- keep the slug reasonably short

### Step 5: Validate YAML schema

Blocking requirement:
- validate frontmatter against the schema before writing documentation

Validation expectations:
- required fields are present
- enum values match exactly
- arrays and date formats are valid

If validation fails, stop and surface specific corrections needed.

### Step 6: Create documentation

Determine the category from the validated `problem_type` using the YAML schema mapping.

Then:
- create the target category directory if needed
- write one documentation file
- populate it from the resolution template with verified context and validated YAML frontmatter

### Step 7: Cross-reference and critical pattern detection

If related issues were found:
- add reciprocal links where appropriate

If the issue represents a repeated or foundational pattern:
- suggest promotion to a critical pattern
- never auto-promote without the user's choice

Use the critical pattern template when promoting a repeated lesson into a `critical-patterns.md` style document.

## Post-documentation decision menu

After successful documentation, pause for an explicit next step:
1. Continue workflow
2. Add to Required Reading / promote to critical patterns
3. Link related issues
4. Add to an existing skill
5. Create a new skill
6. View the captured documentation
7. Other

## Integration notes

This upstream package was designed as a terminal documentation-capture skill.

Within this repo, its strongest ideas are preserved as a learning-capture variant inside `ce-compound`, rather than as a separate duplicate skill:
- schema-driven YAML validation
- filename and category discipline
- richer solution and critical-pattern templates
- explicit post-capture routing decisions

## Success criteria

Successful capture means:
- YAML frontmatter is valid
- the file lands in the correct category directory
- enum values match the schema
- code examples are included when relevant
- cross-references are added when related docs exist
- the user is offered a next-step decision menu
