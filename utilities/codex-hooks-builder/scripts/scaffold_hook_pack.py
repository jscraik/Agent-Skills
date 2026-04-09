#!/usr/bin/env python3
"""
Use when: you need a deterministic project-local or user-level Codex hook pack
scaffold that matches the currently documented command-hook contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a Codex hook pack for a project root or CODEX_HOME."
    )
    parser.add_argument(
        "--target-root",
        required=True,
        help="Repo root for project scope, or CODEX_HOME for user scope.",
    )
    parser.add_argument(
        "--scope",
        choices=("project", "user"),
        default="project",
        help="Where hooks.json should live.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for each generated command hook.",
    )
    return parser.parse_args()


def ensure_writeable(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; rerun with --force to overwrite")


def write_text(path: Path, content: str, force: bool) -> None:
    ensure_writeable(path, force)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_hooks_json(
    session_start_path: Path,
    user_prompt_submit_path: Path,
    stop_guard_path: Path,
    timeout: int,
) -> str:
    """
    Create the JSON content for a Codex `hooks.json` that defines the three scaffold command hooks.
    
    Parameters:
        session_start_path (Path): Path to the session-start hook script used as the `SessionStart` command.
        user_prompt_submit_path (Path): Path to the user-prompt-submit hook script used as the `UserPromptSubmit` command.
        stop_guard_path (Path): Path to the stop-guard hook script used as the `Stop` command.
        timeout (int): Timeout in seconds applied to each command hook.
    
    Returns:
        json_text (str): Pretty-printed JSON for `hooks.json`, including a trailing newline.
    """
    payload = {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "^(startup|resume)$",
                    "hooks": [
                        {
                            "type": "command",
                            "command": str(session_start_path),
                            "timeout": timeout,
                            "statusMessage": "loading repo-aware startup context",
                        }
                    ],
                }
            ],
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": str(user_prompt_submit_path),
                            "timeout": timeout,
                            "statusMessage": "checking prompt safety and shortcut requests",
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": str(stop_guard_path),
                            "timeout": timeout,
                            "statusMessage": "checking final-response completeness",
                        }
                    ],
                }
            ],
        }
    }
    return json.dumps(payload, indent=2) + "\n"


def session_start_template() -> str:
    return dedent(
        """\
        #!/bin/zsh

        set -euo pipefail

        if ! command -v jq >/dev/null 2>&1; then
          printf '%s\\n' '{"continue":true,"systemMessage":"jq not found; skipping SessionStart hook."}'
          exit 0
        fi

        input_json="$(cat)"
        source_name="$(printf '%s' "$input_json" | jq -r '.source // "startup"')"
        cwd="$(printf '%s' "$input_json" | jq -r '.cwd // "."')"
        permission_mode="$(printf '%s' "$input_json" | jq -r '.permission_mode // "default"')"

        repo_root=""
        git_root=""
        repo_name="${cwd:t}"
        branch_name=""
        dirty_count="0"
        preflight_hint=""
        validation_hint=""
        system_message=""

        if command -v git >/dev/null 2>&1 && git -C "$cwd" rev-parse --show-toplevel >/dev/null 2>&1; then
          git_root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)"
          candidate_root="$cwd"

          while true; do
            if [[ -f "$candidate_root/scripts/codex-preflight.sh" \\
               || -f "$candidate_root/AGENTS.md" \\
               || -f "$candidate_root/pnpm-lock.yaml" \\
               || -f "$candidate_root/package-lock.json" \\
               || -f "$candidate_root/Cargo.toml" \\
               || -f "$candidate_root/pyproject.toml" \\
               || -f "$candidate_root/go.mod" ]]; then
              repo_root="$candidate_root"
              break
            fi

            if [[ "$candidate_root" == "$git_root" ]]; then
              break
            fi

            parent_root="${candidate_root:h}"
            if [[ "$parent_root" == "$candidate_root" ]]; then
              break
            fi
            candidate_root="$parent_root"
          done

          if [[ -z "$repo_root" ]]; then
            repo_root="$git_root"
          fi

          repo_name="${repo_root:t}"
          branch_name="$(git -C "$git_root" symbolic-ref --quiet --short HEAD 2>/dev/null || git -C "$git_root" rev-parse --short HEAD 2>/dev/null || true)"
          dirty_count="$(git -C "$git_root" status --porcelain=v1 -- "$repo_root" 2>/dev/null | wc -l | tr -d '[:space:]')"
          dirty_count="${dirty_count:-0}"

          if [[ -f "$repo_root/scripts/codex-preflight.sh" ]]; then
            preflight_hint="Use the repo preflight helper before path-sensitive or multi-step work."
          fi

          if [[ -f "$repo_root/scripts/validate-codex-config.py" ]]; then
            validation_hint="After config edits, run validate-codex-config.py and then the repo preflight helper."
          elif [[ -f "$repo_root/pnpm-lock.yaml" ]]; then
            validation_hint="After edits, prefer the smallest relevant pnpm validation command before broader checks."
          elif [[ -f "$repo_root/package-lock.json" ]]; then
            validation_hint="After edits, prefer the smallest relevant npm validation command before broader checks."
          elif [[ -f "$repo_root/Cargo.toml" ]]; then
            validation_hint="After edits, prefer the smallest relevant cargo validation command before broader checks."
          elif [[ -f "$repo_root/pyproject.toml" ]]; then
            validation_hint="After edits, prefer the smallest relevant Python validation command before broader checks."
          fi

          if [[ "$dirty_count" != "0" ]]; then
            system_message="Dirty worktree detected in ${repo_name}; keep unrelated changes intact."
          fi
        fi

        typeset -a context_parts

        if [[ -n "$repo_root" ]]; then
          context_parts+=("Session opened in repo ${repo_name}.")
          if [[ -n "$branch_name" ]]; then
            context_parts+=("Current branch: ${branch_name}.")
          fi
          if [[ "$dirty_count" != "0" ]]; then
            context_parts+=("Worktree already has ${dirty_count} local change(s); do not revert unrelated edits.")
          fi
        else
          context_parts+=("Session opened in ${repo_name}.")
        fi

        context_parts+=("Inspect local instructions before edits.")

        if [[ -n "$preflight_hint" ]]; then
          context_parts+=("$preflight_hint")
        fi

        if [[ -n "$validation_hint" ]]; then
          context_parts+=("$validation_hint")
        fi

        case "$permission_mode" in
          bypassPermissions)
            context_parts+=("Full-access permission mode is active; verify before destructive commands.")
            if [[ -z "$system_message" ]]; then
              system_message="High-autonomy permission mode is active."
            fi
            ;;
          dontAsk)
            context_parts+=("Autonomous permission mode is active; avoid risky commands unless clearly necessary.")
            ;;
          acceptEdits)
            context_parts+=("Edits are pre-approved, but verification still matters.")
            ;;
          plan)
            context_parts+=("Plan permission mode is active; inspect and explain before making edits or running risky commands.")
            ;;
        esac

        if [[ "$source_name" == "resume" ]]; then
          context_parts+=("Resume from the existing session state before re-exploring.")
        fi

        additional_context="${(j: :)context_parts}"

        jq -n \\
          --arg additional_context "$additional_context" \\
          --arg system_message "$system_message" \\
          '{
            continue: true,
            systemMessage: (if $system_message == "" then null else $system_message end),
            hookSpecificOutput: {
              hookEventName: "SessionStart",
              additionalContext: $additional_context
            }
          }'
        """
    )


def user_prompt_submit_template() -> str:
    return dedent(
        """\
        #!/bin/zsh

        set -euo pipefail

        if ! command -v jq >/dev/null 2>&1; then
          printf '%s\\n' '{"continue":true,"systemMessage":"jq not found; skipping UserPromptSubmit hook."}'
          exit 0
        fi

        input_json="$(cat)"
        prompt="$(printf '%s' "$input_json" | jq -r '.prompt // ""')"
        permission_mode="$(printf '%s' "$input_json" | jq -r '.permission_mode // "default"')"
        prompt_lc="${prompt:l}"
        block_reason=""

        typeset -a context_parts

        if [[ "$prompt_lc" == *"ignore previous instructions"* \\
           || "$prompt_lc" == *"ignore the previous instructions"* \\
           || "$prompt_lc" == *"ignore all previous instructions"* \\
           || "$prompt_lc" == *"forget previous instructions"* \\
           || "$prompt_lc" == *"forget the previous instructions"* \\
           || "$prompt_lc" == *"override the system prompt"* \\
           || "$prompt_lc" == *"ignore system prompt"* \\
           || "$prompt_lc" == *"ignore developer instructions"* \\
           || "$prompt_lc" == *"ignore repo instructions"* \\
           || "$prompt_lc" == *"ignore project instructions"* \\
           || "$prompt_lc" == *"ignore agents.md"* \\
           || "$prompt_lc" == *"disregard agents.md"* \\
           || "$prompt_lc" == *"bypass the guardrails"* \\
           || "$prompt_lc" == *"disable the guardrails"* \\
           || "$prompt_lc" == *"ignore the guardrails"* ]]; then
          block_reason="Cannot ignore higher-priority system, developer, or repo instructions. Rephrase the request within the active guardrails."
        fi

        if [[ "$prompt_lc" == *"skip validation"* \\
           || "$prompt_lc" == *"skip tests"* \\
           || "$prompt_lc" == *"skip test"* \\
           || "$prompt_lc" == *"skip lint"* \\
           || "$prompt_lc" == *"skip typecheck"* \\
           || "$prompt_lc" == *"without tests"* \\
           || "$prompt_lc" == *"no tests"* \\
           || "$prompt_lc" == *"don't validate"* \\
           || "$prompt_lc" == *"do not validate"* \\
           || "$prompt_lc" == *"ship it without validation"* ]]; then
          context_parts+=("If validation is skipped, say so explicitly with a reason in the final handoff.")
        fi

        if [[ "$prompt_lc" == *"rm -rf"* \\
           || "$prompt_lc" == *"reset --hard"* \\
           || "$prompt_lc" == *"checkout --"* \\
           || "$prompt_lc" == *"dangerously skip permissions"* \\
           || "$prompt_lc" == *"--yolo"* \\
           || "$prompt_lc" == *"delete everything"* \\
           || "$prompt_lc" == *"remove everything"* ]]; then
          context_parts+=("The prompt may imply destructive changes; verify scope carefully and protect unrelated edits.")
        fi

        case "$permission_mode" in
          bypassPermissions|dontAsk)
            if (( ${#context_parts[@]} > 0 )); then
              context_parts+=("High-autonomy mode is active, so apply extra caution before destructive or low-verification shortcuts.")
            fi
            ;;
        esac

        additional_context="${(j: :)context_parts}"

        jq -n \\
          --arg additional_context "$additional_context" \\
          --arg block_reason "$block_reason" \\
          '{
            continue: true,
            decision: (if $block_reason == "" then null else "block" end),
            reason: (if $block_reason == "" then null else $block_reason end),
            hookSpecificOutput: (
              if $additional_context == "" then null else {
                hookEventName: "UserPromptSubmit",
                additionalContext: $additional_context
              } end
            )
          } | with_entries(select(.value != null))'
        """
    )


def stop_guard_template() -> str:
    return dedent(
        """\
        #!/bin/zsh

        set -euo pipefail

        if ! command -v jq >/dev/null 2>&1; then
          printf '%s\\n' '{"continue":true,"systemMessage":"jq not found; skipping Stop hook."}'
          exit 0
        fi

        input_json="$(cat)"
        stop_hook_active="$(printf '%s' "$input_json" | jq -r '.stop_hook_active // false')"
        last_message="$(printf '%s' "$input_json" | jq -r '.last_assistant_message // ""')"

        if [[ "$stop_hook_active" == "true" ]]; then
          jq -n '{continue: true}'
          exit 0
        fi

        normalized_message="$(printf '%s' "$last_message" | tr '[:upper:]' '[:lower:]')"

        block_reason=""
        for marker in "todo" "tbd" "fixme" "lorem ipsum" "[insert" "coming soon" "left as an exercise" "not implemented"; do
          if [[ "$normalized_message" == *"$marker"* ]]; then
            block_reason="Rewrite the response before stopping: replace draft marker text like \\"$marker\\" with final content or remove it."
            break
          fi
        done

        if [[ -z "$block_reason" ]] && printf '%s' "$last_message" | grep -Eq '(^|[[:space:]])[-*][[:space:]]\\[[[:space:]]\\]'; then
          block_reason="Rewrite the response before stopping: unresolved checklist items remain in the final message."
        fi

        if [[ -z "$block_reason" ]] && printf '%s' "$normalized_message" | grep -Eq '(did not run|didn.t run|have not run|haven.t run|unable to verify|could not verify|couldn.t verify)'; then
          if ! printf '%s' "$normalized_message" | grep -Eq '(because|due to|since|per your request|as requested)'; then
            block_reason="Rewrite the response before stopping: if validation was skipped, state the reason clearly or run the smallest relevant check."
          fi
        fi

        if [[ -n "$block_reason" ]]; then
          jq -n \\
            --arg reason "$block_reason" \\
            '{
              continue: true,
              decision: "block",
              reason: $reason,
              systemMessage: "Stop hook blocked an incomplete final response."
            }'
        else
          jq -n '{continue: true}'
        fi
        """
    )


def readme_template(config_dir: Path, hooks_dir: Path) -> str:
    return dedent(
        f"""\
        # Codex Hook Pack

        ## Table of Contents
        - [Overview](#overview)
        - [Files](#files)
        - [Install shape](#install-shape)
        - [What this pack does](#what-this-pack-does)
        - [Validation](#validation)

        ## Overview
        This hook pack was scaffolded from `utilities/codex-hooks-builder` and
        targets the currently documented Codex command-hook contract.

        ## Files
        - `{config_dir / "hooks.json"}`
        - `{hooks_dir / "session-start.sh"}`
        - `{hooks_dir / "user-prompt-submit.sh"}`
        - `{hooks_dir / "stop-guard.sh"}`

        ## Install shape
        - active config layer: `{config_dir}`
        - hook scripts folder: `{hooks_dir}`
        - command paths in `hooks.json` are absolute so they keep working from nested working directories

        ## What this pack does
        - `SessionStart` adds concise repo-aware startup context
        - `UserPromptSubmit` blocks obvious instruction-bypass attempts and annotates risky shortcuts
        - `Stop` blocks clearly incomplete final handoffs once, then fails open on retry
        - `PreToolUse` and `PostToolUse` are supported by Codex docs but intentionally not scaffolded in this starter pack unless requested

        ## Validation
        ```bash
        zsh -n {hooks_dir / "session-start.sh"}
        zsh -n {hooks_dir / "user-prompt-submit.sh"}
        zsh -n {hooks_dir / "stop-guard.sh"}
        jq . {config_dir / "hooks.json"}
        ```
        """
    )


def main() -> int:
    args = parse_args()
    target_root = Path(args.target_root).expanduser().resolve()

    if args.scope == "project":
        config_dir = target_root / ".codex"
        hooks_dir = config_dir / "hooks"
    else:
        config_dir = target_root
        hooks_dir = target_root / "hooks"

    session_start_path = hooks_dir / "session-start.sh"
    user_prompt_submit_path = hooks_dir / "user-prompt-submit.sh"
    stop_guard_path = hooks_dir / "stop-guard.sh"
    hooks_json_path = config_dir / "hooks.json"
    readme_path = hooks_dir / "README.md"

    write_text(session_start_path, session_start_template(), args.force)
    write_text(user_prompt_submit_path, user_prompt_submit_template(), args.force)
    write_text(stop_guard_path, stop_guard_template(), args.force)
    write_text(
        hooks_json_path,
        build_hooks_json(
            session_start_path=session_start_path,
            user_prompt_submit_path=user_prompt_submit_path,
            stop_guard_path=stop_guard_path,
            timeout=max(args.timeout, 1),
        ),
        args.force,
    )
    write_text(readme_path, readme_template(config_dir=config_dir, hooks_dir=hooks_dir), args.force)

    for script_path in (session_start_path, user_prompt_submit_path, stop_guard_path):
        script_path.chmod(0o755)

    summary = {
        "schema_version": "1.0",
        "scope": args.scope,
        "target_root": str(target_root),
        "config_dir": str(config_dir),
        "generated_files": [
            str(hooks_json_path),
            str(session_start_path),
            str(user_prompt_submit_path),
            str(stop_guard_path),
            str(readme_path),
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
