# Organizational Review Policy: AI-Integrated Code Quality & Governance

## Table of Contents
- [Policy framework and objectives](#policy-framework-and-objectives)
- [Configuration standards and cascading governance](#configuration-standards-and-cascading-governance)
- [Interpreting review metrics and confidence thresholds](#interpreting-review-metrics-and-confidence-thresholds)
- [Feedback loops and AI training protocols](#feedback-loops-and-ai-training-protocols)
- [Governance of custom context and pattern repositories](#governance-of-custom-context-and-pattern-repositories)
- [Automated workflow and MCP integration](#automated-workflow-and-mcp-integration)
- [Runtime policy gate checklist (required on each run)](#runtime-policy-gate-checklist-required-on-each-run)

## Policy framework and objectives
- This policy is the **absolute grounding** for Greptile review behavior in the organization.
- Reviews must go beyond diff-only checks and include graph-aware consistency across dependencies, contracts, and adjacent files.
- Goal: faster merge cycles with high-integrity releases and lower reviewer fatigue.

### Independent validation and compliance
- The coding agent and review agent must remain independent.
- A coding agent must not approve its own work.
- If independent validation cannot be confirmed, review workflows must return `blocked`.

## Configuration standards and cascading governance

### Precedence hierarchy
When settings conflict, apply this precedence order:

1. Org-enforced dashboard rules (highest)
2. Directory-scoped `.greptile/` folders
3. Legacy `greptile.json` (ignored if `.greptile/` exists in the same directory)
4. Dashboard defaults (lowest)

### Required local governance files
Every governed segment should provide:

```text
.greptile/
  config.json
  rules.md
  files.json
```

- `files.json` is mandatory and must point to primary schema/API specs to support cross-file graph queries.

### Merge logic for multi-directory PRs
When a PR spans directories with different configs:
- strictness: MAX (most restrictive)
- fileChangeLimit: MIN (most restrictive)
- comment types: union
- booleans: OR (enabled if any config enables)

## Interpreting review metrics and confidence thresholds

### Confidence score actions
- **5/5**: production ready; merge permitted.
- **4/5**: minor polish; merge permitted after low-risk fixes.
- **3/5**: implementation issues; fix and re-review required.
- **2/5**: significant bugs; blocked for rework.
- **0–1/5**: critical problems; blocked for architectural/security rethink.

### Strictness defaults
- **Strictness 1 (Verbose)**: security-critical directories and initial calibration.
- **Strictness 2 (Default)**: required baseline for PRs targeting `main`/production branches.
- **Strictness 3 (Critical-only)**: stable, non-critical internal infrastructure.

### Indexing warning
- `ignorePatterns` excludes files from **review**, not from **indexing**.
- Exclude heavy binaries/assets/node_modules at repo/dashboard indexing scope to prevent indexing failures.

## Feedback loops and AI training protocols
- Use 👍/👎 feedback on review comments; 👎 should include a short rationale.
- Rely on commit-delta analysis to confirm whether suggestions were addressed.
- Apply the 3-ignore suppression rule only when patterns are intentionally ignored.
- Expect a 2–3 week calibration period for new repositories.

## Governance of custom context and pattern repositories
- Rules must be specific, measurable, and example-backed.
- Prefer scoped rules by glob (`**/*.ts`, `**/api/**`) to reduce noise.
- Use `patternRepositories` (`org/repo`) to reference shared libraries/spec repositories and detect duplicated implementations.

## Automated workflow and MCP integration

### Manual fix loop (universal)
1. Fetch unaddressed comments (`addressed: false`).
2. Apply concrete fixes (prefer `suggestedCode` when valid).
3. Commit changes; let Greptile re-evaluate addressed state.

### Skill loop (agent automation)
- `check-pr`: readiness audit with policy gate, CI state, and unresolved thread triage.
- `greploop`: bounded review-fix iterations (max 5 by default) until target confidence and zero actionable items.

### Manual trigger standards
Use `@greptileai` to:
- trigger a review on a draft PR,
- force re-review after settings updates,
- ask targeted checks (for example memory leak checks).

## Runtime policy gate checklist (required on each run)
Every `check-pr` and `greploop` run must emit a policy gate summary and fail fast on violations.

1. **Independent validation gate**
   - Confirm reviewer identity is independent from the coding agent/authoring actor.
   - If independence cannot be verified, return `blocked`.
2. **Auth + MCP gate**
   - `gh auth status` passes.
   - MCP endpoint and `GREPTILE_API_KEY` wiring are valid.
3. **Governance files gate**
   - Verify applicable `.greptile/config.json`, `.greptile/rules.md`, and `.greptile/files.json` presence.
4. **Precedence and merge-logic gate**
   - Apply org → directory → legacy → defaults precedence.
   - Apply strictness/fileChangeLimit/comment-type/boolean merge logic for multi-directory PRs.
5. **Branch strictness gate**
   - Require strictness >= 2 for `main`/production targets unless org-enforced rules specify stricter behavior.
6. **Confidence decision gate**
   - Map confidence score to mandatory team action (merge, polish, rework, blocked).
7. **Training signal gate**
   - Encourage 👍/👎 feedback and preserve unresolved rationale where suggestions are declined.
8. **Output gate**
   - Include `policy_gate_status`, blockers, and next actions in the final report.
