---
source: https://docs.coderabbit.ai/finishing-touches/custom-finishing-touches
---

# Custom Finishing Touch Recipes

Define reusable, named recipes that run agentic code changes on your pull requests.

Custom recipes let you encode your team's repeated finishing-touch tasks -- things like enforcing import ordering, tightening TypeScript types, or applying project-specific conventions -- into named, reusable instructions. Once defined, anyone on your team can trigger a recipe with a single comment or checkbox click, and CodeRabbit's agent will carry out the work inside a sandbox and open a PR with the result.

## How it works

Custom finishing touches run as named recipes in pull request context. When a recipe is triggered, CodeRabbit sends the recipe instructions with PR metadata and changed files to an agent, then opens a follow-up PR with proposed updates.

## Supported Platforms

Custom finishing touches are available in repositories where CodeRabbit's finishing touches workflow is enabled. Triggering can happen from PR comments or from the Finishing Touches checkbox interface in the walkthrough.

## Configuration

Add custom recipes to `.coderabbit.yaml`:

```yaml
early_access: true # Enable Early Access features
reviews:
  finishing_touches:
    custom:
      - name: "cleanup stale imports"
        instructions: |
          Scan the changed files for unused imports and remove them.
          Preserve imports used in type positions.
          Do not reorder existing imports; only remove stale ones.

      - name: "tighten types"
        instructions: |
          Replace `any` types in the changed files with the most specific
          TypeScript type that is correct given the surrounding context.
          Add explicit return types to exported functions that are missing them.

      - name: "enforce error handling"
        instructions: |
          Audit all async functions in the changed files.
          Ensure every awaited call is wrapped in try/catch or has a .catch() handler.
          Use the project's existing error logger pattern when catching errors.
```

### Recipe fields

| Field | Required | Limits | Description |
| --- | --- | --- | --- |
| `name` | Yes | Max 100 characters | Identifier used in run commands. Case-insensitive. Must be unique across your recipes. |
| `instructions` | Yes | Max 10,000 characters | Freeform description of what the agent should do. The agent receives full PR context alongside these instructions. |
| `enabled` | No | -- | Set to `false` to temporarily disable a recipe without removing it. Defaults to `true`. |

You can define up to **5 custom recipes** per repository. Recipe names are matched case-insensitively, so `"Cleanup Stale Imports"` and `"cleanup stale imports"` refer to the same recipe.

## Triggering recipes

```text
@coderabbitai run cleanup stale imports
```

Recipe names can include spaces. Quoting is optional:

```text
@coderabbitai run "tighten types"
```

The command is matched case-insensitively and can appear anywhere in a comment, including multi-line comments.

### Ad hoc evaluation (without a saved recipe)

To try out a finishing touch without committing it to your config, use the evaluate command directly in a PR comment:

```text
@coderabbitai evaluate custom finishing touch --name <name> --instructions <text>
```

For example:

```text
@coderabbitai evaluate custom finishing touch --name "sort imports" --instructions "Sort all import statements alphabetically within each import group in the changed files."
```

The agent runs exactly as it would for a saved recipe -- with full PR context -- but the recipe is not persisted anywhere. This is useful for one-off tasks or for iterating on instructions before adding them to `.coderabbit.yaml`.

### Finishing Touches checkbox

Each enabled recipe appears as a checkbox in the **Finishing Touches** section of the CodeRabbit Walkthrough comment. Checking it triggers the recipe with the Create PR output mode.

## What the agent receives

When a recipe runs, CodeRabbit provides the agent with:

- Your **recipe instructions**
- **PR title and description**
- **CodeRabbit's PR summary** (walkthrough and objectives)
- **Global coding guidelines** from `reviews.path_instructions` in your config
- **Repository access scoped by assigned roles and policy** (for example Read, Write, Edit, Glob, Grep, and Bash only when permitted)

This means your recipes can reference project conventions, coding standards, and PR intent without you needing to repeat that context in every recipe.

## Example recipes

**Remove console statements:**

```yaml
- name: "remove console logs"
  instructions: |
    Find and remove all console.log, console.warn, and console.error calls
    from the changed files. Leave intentional logging that uses the project's
    logger utility (e.g. logger.info, logger.error) untouched.
```

**Add missing test coverage:**

```yaml
- name: "add edge case tests"
  instructions: |
    Review the changed source files and identify edge cases not covered
    by the existing tests. Add focused unit tests for those cases using
    the project's existing test framework and patterns.
```

**Enforce naming conventions:**

```yaml
- name: "fix naming conventions"
  instructions: |
    Check the changed files for variables, functions, or classes that
    do not follow the project's naming conventions (camelCase for variables
    and functions, PascalCase for classes and interfaces). Rename where needed
    and update all references in the same files.
```
