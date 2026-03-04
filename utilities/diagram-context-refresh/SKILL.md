---
name: diagram-context-refresh
description: Refresh Mermaid diagram context packs for Codex and Claude using diagram-cli. Use when the user asks to keep architecture context current, automate diagram refresh, or prepare AI-ready repo context from code.
---

# Diagram Context Refresh

Generate architecture diagrams from code and compact them into one AI context file.

## Philosophy

- Keep architecture context deterministic and regenerated from code.
- Favor one shared context pack for both Codex and Claude.
- Keep automation quiet, reversible, and easy to validate.
- Use a consistent approach (principle: deterministic source-of-truth refresh) so context is always derived from the same code snapshot, not manual edits.
- This is about tradeoff management: faster onboarding via fresh context versus reduced churn from unnecessary refreshes.
- Use the shared mental model that context accuracy is a function of completeness, correctness, and recent source-of-truth generation.
- How frequent are changes in this repository, and when does staleness become an actual risk?
- Which refresh mode best balances signal-to-noise for this team’s risk tolerance?
- What would make the generated context less trustworthy in practice?

## Scope and triggers

- User asks to automate Mermaid/context refresh.
- User wants Codex and Claude to share the same architecture context.
- User asks to update `.diagram` artifacts (`.diagram/*.mmd`, `.diagram/context/diagram-context.md`).

## Required inputs

- Repo root path (canonical git root, not a nested subdirectory).
- Refresh mode: `dry-run`, `manual`, `silent-on-open`, or `ci-only`.
- Confirmation whether GitHub Action PR-merge refresh should be enabled.

## Deliverables

- Fresh `.diagram/*.mmd`.
- Fresh `.diagram/context/diagram-context.md`.
- Fresh `.diagram/context/diagram-context.meta.json` (including `schema_version`).
- Preflight readiness result (pass/fail + actionable checks).
- Optional shell hook install for silent-on-open behavior.
- Optional CI workflow for merged PR refresh.

## Mode matrix

| Mode | Primary goal | Local refresh | Hook install | CI workflow |
| --- | --- | --- | --- | --- |
| `dry-run` | Verify readiness and planned actions | No (`--dry-run`) | No | Optional |
| `manual` | One-time explicit refresh | Yes (`--force`) | No | Optional |
| `silent-on-open` | Local automatic refresh on repo open | Yes (`--force`) | Yes | Optional |
| `ci-only` | Keep refresh managed by CI only | Optional | No | Yes (required) |

## Workflow

1. Set execution context variables:

   ```bash
   SKILL_DIR=/path/to/diagram-context-refresh
   REPO_ROOT=/path/to/repo
   MODE=manual
   REPO_ROOT="$(cd "$REPO_ROOT" && git rev-parse --show-toplevel)"
   ```

2. Choose refresh invocation (prefer npm script when available):

   ```bash
   refresh_command() {
     local mode_flag="$1"
     if [[ -f "$REPO_ROOT/package.json" ]] && jq -e '.scripts["refresh-diagram-context"]' "$REPO_ROOT/package.json" >/dev/null 2>&1; then
       (cd "$REPO_ROOT" && npm run refresh-diagram-context -- "$mode_flag")
     else
       bash "$REPO_ROOT/scripts/refresh-diagram-context.sh" "$mode_flag"
     fi
   }
   ```

3. Run preflight checks (fail fast if any check fails):

   ```bash
   bash "$SKILL_DIR/scripts/preflight.sh" --repo-root "$REPO_ROOT" --mode "$MODE"
   ```

4. If local companion agent `diagram-cli` is installed, align execution with its guardrails:
   - `~/.codex/agents/diagram-cli/diagram-cli.toml`
   - `~/.codex/agents/diagram-cli/diagram-cli.instructions.md`

5. Execute mode-specific actions in order:
   - `dry-run`:

     ```bash
     refresh_command --dry-run
     ```

   - `manual`:

     ```bash
     refresh_command --force
     ```

   - `silent-on-open`:

     ```bash
     refresh_command --force
     bash "$REPO_ROOT/scripts/install-repo-open-hook.sh"
     ```

   - `ci-only`: do not install local hook; keep refresh execution in CI workflow only.

6. If requested (or if `MODE=ci-only`), ensure PR-merge workflow exists at:
   - `.github/workflows/refresh-diagram-context.yml`

7. Stop immediately on any command failure and report the first failing check/action with the exact command.

## Validation

- Fail fast: stop at first failed validation gate and fix it before continuing.
- Preflight passes for the selected mode:

  ```bash
  bash "$SKILL_DIR/scripts/preflight.sh" --repo-root "$REPO_ROOT" --mode "$MODE"
  ```

- Context file exists and is non-empty:

  ```bash
  test -s "$REPO_ROOT/.diagram/context/diagram-context.md"
  ```

- Metadata is valid JSON:

  ```bash
  jq -e . "$REPO_ROOT/.diagram/context/diagram-context.meta.json" >/dev/null
  ```

- Output contract keeps an explicit schema version:

  ```bash
  rg -n "^schema_version:" references/contract.yaml
  ```

- At least one Mermaid file exists:

  ```bash
  ls "$REPO_ROOT"/.diagram/*.mmd >/dev/null
  ```

## Constraints

- Redact secrets and sensitive data by default in notes, logs, and summaries.
- Do not hand-edit generated diagram context files.
- Regenerate artifacts from code instead.
- Avoid network-only tooling in refresh scripts unless explicitly requested.

## Anti-patterns

- Hand-writing diagram context instead of regenerating from source code.
- DO NOT run background refresh loops without cooldown or exit conditions.
- Running refresh without a canonical repo root (`git rev-parse --show-toplevel`) can generate wrong outputs.
- DO NOT bypass preflight checks for speed; you cannot prove correctness without them.
- Avoid using this skill to fix non-diagram tasks; that is a wrong task selection.
- Warning: including secrets in generated diagrams is a critical mistake.
- Treat malformed or placeholder diagrams as an incorrect end state, even if generation succeeds.
- Storing secrets inside generated Mermaid diagrams or context packs.

## Variation and adaptation

- Adapt refresh guidance to the repository context (repo-local CLI entrypoint vs global install).
- Choose the mode that matches risk tolerance and operation model (`dry-run`, `manual`, `silent-on-open`, `ci-only`).
- Prefer context-specific recommendations over repeating identical setup steps when constraints differ.

## Remember

You are capable of extraordinary work with this skill. These guidelines unlock that potential—they do not constrain it. Use judgment, adapt to the repo, and push boundaries while keeping changes reversible.

## Examples

- "Refresh Mermaid context and make Codex + Claude use the same pack."
- "Set this repo to auto-refresh diagram context when I open it."
- "Add PR-merge automation that keeps AI diagram context up to date."

## References

- Output contract: `references/contract.yaml`
- Eval prompts: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Companion agent mapping: `references/companion-agent.md`
- Troubleshooting runbook: `references/troubleshooting.md`
