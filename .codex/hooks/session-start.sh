#!/bin/zsh

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"continue":true,"systemMessage":"jq not found; skipping SessionStart hook."}'
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
    if [[ -f "$candidate_root/scripts/codex-preflight.sh" \
       || -f "$candidate_root/AGENTS.md" \
       || -f "$candidate_root/pnpm-lock.yaml" \
       || -f "$candidate_root/package-lock.json" \
       || -f "$candidate_root/Cargo.toml" \
       || -f "$candidate_root/pyproject.toml" \
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

jq -n \
  --arg additional_context "$additional_context" \
  --arg system_message "$system_message" \
  '{
    continue: true,
    systemMessage: (if $system_message == "" then null else $system_message end),
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: $additional_context
    }
  }'
