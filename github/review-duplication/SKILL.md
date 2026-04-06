---
name: review-duplication
description: Use this skill during code reviews to proactively investigate the codebase for duplicated functionality, reinvented wheels, or failure to reuse existing project best practices and shared utilities.
metadata:
  short-description: Proactively investigate for duplicated functionality during code reviews.
  skill-type: code_quality_review
---

# Review Duplication

## Table of Contents

- [Overview](#overview)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow-investigating-for-duplication)
- [Examples](#examples)
- [See Also](#see-also)
- [Validation](#validation)

## When to use
Use this skill during code reviews to proactively investigate the codebase for duplicated functionality, reinvented wheels, or failure to reuse existing project best practices and shared utilities.

## Overview
This skill provides a structured workflow for investigating a codebase during a code review to identify duplicated logic, reinvented utilities, and missed opportunities to reuse established patterns. By executing this workflow, you ensure that new code integrates seamlessly with the existing project architecture.

## Required inputs
- Code Review Context: The PR diff or new code being introduced.
- Codebase Access: Ability to search and read files throughout the repository.
- Project Documentation: Access to existing style guides or component libraries.

## Deliverables
- Review comments identifying duplicated logic with specific file paths and symbols.
- Reuse guidance showing how to integrate existing code.
- Refactoring suggestions where applicable.
- Contract: Adheres to `schema_version: 1` output standards.

## Failure mode
- If codebase search tools are unavailable, stop and report the blocker.
- If no existing implementation is found after thorough search, report this clearly rather than assuming duplication exists.

## Gotchas
- **Absolute Paths:** When referencing files, use repo-relative paths (e.g., `utilities/date-helpers.ts`), never absolute paths from your local filesystem.
- **Redaction:** Never print, log, or commit secrets, API keys, or other sensitive data discovered during investigation.
- **Privacy:** Always redact PII or sensitive values in review comments or logs.
- Be specific: provide exact file paths and symbol names when identifying existing code.

## Philosophy
Code reuse is a foundational principle for maintainable systems. Every reinvented utility increases the maintenance burden and cognitive load on the team. This skill prioritizes the discovery of existing "well-lit paths" over the acceptance of new implementations for solved problems.

## Workflow: Investigating for Duplication

When reviewing code, perform the following steps before finalizing your review:

### 1. Extract Core Logic
Analyze the new code to identify the core algorithms, utility functions, generic data structures, or UI components being introduced. Look beyond the specific business logic to see the underlying mechanics.

### 2. Hypothesize Existing Locations & Trace Dependencies
Think about where this type of code *would* live if it already existed in the project. Provide repo-relative paths to disambiguate.
- **Utilities:** `utilities/`, `packages/core/src/utils/`
- **UI Components:** `frontend/ui/components/`, `packages/cli/src/ui/`
- **Services:** `packages/core/src/services/`, `backend/services/`
- **Configuration:** `config/`, `packages/core/src/config/`

**Trace Third-Party Dependencies:** If the PR introduces a new import for a utility library (e.g., `lodash.merge`, `date-fns`), trace how and where the project currently uses that library. There is likely an existing wrapper or shared utility.

**Check Package Files:** Before flagging a custom implementation of a complex algorithm, check `package.json` to see if a standard library (like `lodash` or `uuid`) is already installed that provides this functionality.

### 3. Investigate the Codebase (Sub-Agent Delegation)
Utilize specialized sub-agents to assist with investigative research into the codebase. These assistants are capable of deep semantic mapping and wide-ranging searches.

Define clear goals for these research passes, utilizing the context discovered in earlier steps.

- **Discovery Research:** Use codebase researchers to find similar implementations. Goals should include search vectors like:
 - **Structural Similarity:** Checking for identical underlying API usage (e.g., `Intl.DateTimeFormat` or `setTimeout`).
 - **Naming Conventions:** Identifying existing symbols with similar naming patterns (e.g., `*Format*` or `*Debounce*`).
 - **Comments & Documentation:** Searching for keywords from JSDoc that describe similar behavior elsewhere.
 - **Architectural Fit:** Determining where this type of logic is currently centralized.
 - **Refactoring Potential:** Identifying how the new code could be adjusted to use existing logic.
- **Detailed Comparison:** Perform semantic comparisons against existing modules. For example: "Examine the implementation of the new component in the PR and compare it against all components in the UI package to see if any could be extended instead."
- **Direct Checks:** For simple, unambiguous checks (e.g., checking dependencies in `package.json`), use local search tools directly.

### 4. Evaluate Best Practices
Check if the new code aligns with the project's established conventions.
- **Error Handling:** Does it use the project's standard error classes or logging mechanisms?
- **State Management:** Does it circumvent established stores or contexts?
- **Styling:** Does it hardcode colors or spacing instead of using theme variables?
If the PR introduces a new pattern, compare it against the documented standards and confirm if an existing project pattern should have been used instead.

### 5. Formulate Constructive Feedback
If you discover that the PR duplicates existing functionality or ignores a best practice:
- Provide a clear review comment.
- **Identify the Source:** Explicitly mention the repo-relative file path and the specific symbol (function, component, class) that should be reused.
- **Implementation Guidance:** Provide a brief code snippet or a clear explanation showing **how** to integrate the existing code to fulfill the task's requirements.
- **Explain the Value:** Briefly explain why reusing the existing code is beneficial (e.g., maintainability, consistency, built-in edge case handling).

Example comment:
> "It looks like this PR introduces a new `formatDate` utility. We already have a robust, tested `formatDate` function in `utilities/date-helpers.ts`. 
>
> You can replace your implementation by importing it like this:
> ```typescript
> import { formatDate } from 'utilities/date-helpers';
> 
> // Then use it here:
> const displayDate = formatDate(userDate, 'MMM Do, YYYY');
> ```
> Reusing this ensures that the date formatting remains consistent with the rest of the application and handles timezone conversions correctly."

## Examples
- **When the user asks:** "I'm reviewing PR #123. The author added a currency formatter in the checkout package; can you check if we already have one in `packages/ui`?"
- **When the user says:** "The new PR adds `date-fns` as a dependency. Help me check if we already use a different date library or have internal helpers."
- **When the user asks:** "I noticed PR #456 uses a custom debounce. Can you verify if we have a standard debounce utility in the `utilities` package?"

## Anti-Patterns
- **Surface-Level Review:** Only checking naming without verifying the underlying logic or APIs used.
- **Absolute Path Usage:** Providing local machine paths that the PR author cannot use.
- **Vague Feedback:** Telling the author "this already exists" without providing the specific path or symbol to reuse.

## Validation
Review the detailed contracts and evaluation cases before making changes:
- `references/contract.yaml`
- `references/evals.yaml`

Run these checks and fail fast: stop at the first failed gate and do not proceed.
```bash
python3 scripts/diagnose_skill.py github/review-duplication
python3 utilities/skill-builder/scripts/quick_validate.py github/review-duplication --mode strict
```

## See Also

| Skill | When to use |
|-------|-------------|
| [[backend-engineer]] | When duplication is found in backend code |
| [[frontend-ui-design]] | When duplication is found in UI components |
| [[codex-home-audit]] | When reviewing Codex configuration for duplicates |

**Topic map:** [[github]]
