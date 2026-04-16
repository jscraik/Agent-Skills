# Refactor Playbook (Behavior-Preserving)

Read when:
- the user says "refactor this" or "clean up structure";
- changed code is hard to read or maintain;
- behavior must remain unchanged.

Do this because it reduces maintenance risk while preserving delivery velocity.

## Boundary

- Keep behavior unchanged.
- Default to changed files and directly adjacent helpers.
- Avoid whole-repo rewrites unless explicitly requested.
- If tests are missing for risky edits, either add targeted tests first or mark the finding as skipped with reason.

## Execution Mode Selection (Cross-File Refactors)

Choose mode by blast radius:

- `1-9 files`: native mode (manual review + targeted replacements in each file).
- `10+ files` or high replacement volume: batch mode (scripted codemod/execution lane with explicit verification).

Use this because large-scale mechanical edits are easier to apply consistently in batch mode and can reduce token/interaction overhead.

Batch-mode guardrails:
- enumerate candidate files before any write;
- run a dry-run or sample transform on 1-2 files first;
- apply transform in one bounded pass;
- verify that old patterns are removed and new patterns are present;
- run targeted validation for impacted packages/modules.

## Smell-to-Operation Mapping

1. Long function/method:
- Extract smaller functions with descriptive names.
- Keep orchestration in the top-level function.

1. Duplication:
- Reuse existing utilities first.
- If no utility exists, extract one narrowly scoped helper.

1. Oversized module/class:
- Split by responsibility only when call boundaries are clear.
- Prefer low-risk extraction over interface redesign in simplify mode.

1. Long parameter list:
- Introduce a parameter object or typed options shape.
- Keep call sites readable; avoid over-engineered builders unless already used.

1. Primitive obsession and magic values:
- Replace repeated literals with named constants or unions/enums.
- Use domain types where the codebase already supports them.

1. Nested conditionals:
- Use guard clauses for invalid/early-exit paths.
- Keep happy-path flow linear.

1. Dead code:
- Remove unused imports, stale helpers, and commented-out code.
- Do not preserve dead code "just in case"; git history is the backup.

## Native Search-and-Replace Workflow

Use this when refactors are small and context-sensitive.

1. Find all occurrences.
2. Review context around each match.
3. Replace all intended instances in the scoped files.
4. Verify no stale usage remains.
5. Run lint/tests for touched surfaces.

Example command pattern:
- find files: `rg --files-with-matches "oldName" <scope>`
- inspect context: `rg -n "oldName" <scope>`
- verify removal: `rg -n "oldName" <scope>` should return no matches

For API/path updates, also search for quoted and unquoted forms to avoid partial migrations.

## Safe Refactor Sequence

1. Capture baseline diff and target scope.
2. Choose one smell class and apply one small operation.
3. Run validation for touched code.
4. Repeat until no high-value findings remain.
5. Record applied operations and skipped suggestions with concise rationale.

## High-Value Skip Reasons

- `missing_tests_for_risky_change`
- `scope_exceeds_changed_files`
- `speculative_pattern_without_evidence`
- `unclear_behavioral_equivalence`

## Pattern Escalation Rule

Use pattern-level refactors (strategy, chain, delegation) only when:
- conditional complexity is repeated and growing;
- the existing codebase already uses that pattern;
- the change can stay behavior-preserving and testable in small steps.

Otherwise, prefer local extracts and naming improvements.
