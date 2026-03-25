#!/bin/zsh

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"continue":true,"systemMessage":"jq not found; skipping UserPromptSubmit hook."}'
  exit 0
fi

input_json="$(cat)"
prompt="$(printf '%s' "$input_json" | jq -r '.prompt // ""')"
permission_mode="$(printf '%s' "$input_json" | jq -r '.permission_mode // "default"')"
prompt_lc="${prompt:l}"
block_reason=""

typeset -a context_parts

if [[ "$prompt_lc" == *"ignore previous instructions"* \
   || "$prompt_lc" == *"ignore the previous instructions"* \
   || "$prompt_lc" == *"ignore all previous instructions"* \
   || "$prompt_lc" == *"forget previous instructions"* \
   || "$prompt_lc" == *"forget the previous instructions"* \
   || "$prompt_lc" == *"override the system prompt"* \
   || "$prompt_lc" == *"ignore system prompt"* \
   || "$prompt_lc" == *"ignore developer instructions"* \
   || "$prompt_lc" == *"ignore repo instructions"* \
   || "$prompt_lc" == *"ignore project instructions"* \
   || "$prompt_lc" == *"ignore agents.md"* \
   || "$prompt_lc" == *"disregard agents.md"* \
   || "$prompt_lc" == *"bypass the guardrails"* \
   || "$prompt_lc" == *"disable the guardrails"* \
   || "$prompt_lc" == *"ignore the guardrails"* ]]; then
  block_reason="Cannot ignore higher-priority system, developer, or repo instructions. Rephrase the request within the active guardrails."
fi

if [[ "$prompt_lc" == *"skip validation"* \
   || "$prompt_lc" == *"skip tests"* \
   || "$prompt_lc" == *"skip test"* \
   || "$prompt_lc" == *"skip lint"* \
   || "$prompt_lc" == *"skip typecheck"* \
   || "$prompt_lc" == *"without tests"* \
   || "$prompt_lc" == *"no tests"* \
   || "$prompt_lc" == *"don't validate"* \
   || "$prompt_lc" == *"do not validate"* \
   || "$prompt_lc" == *"ship it without validation"* ]]; then
  context_parts+=("If validation is skipped, say so explicitly with a reason in the final handoff.")
fi

if [[ "$prompt_lc" == *"rm -rf"* \
   || "$prompt_lc" == *"reset --hard"* \
   || "$prompt_lc" == *"checkout --"* \
   || "$prompt_lc" == *"dangerously skip permissions"* \
   || "$prompt_lc" == *"--yolo"* \
   || "$prompt_lc" == *"delete everything"* \
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

jq -n \
  --arg additional_context "$additional_context" \
  --arg block_reason "$block_reason" \
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
