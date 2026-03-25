#!/bin/zsh

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"continue":true,"systemMessage":"jq not found; skipping Stop hook."}'
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
    block_reason="Rewrite the response before stopping: replace draft marker text like \"$marker\" with final content or remove it."
    break
  fi
done

if [[ -z "$block_reason" ]] && printf '%s' "$last_message" | grep -Eq '(^|[[:space:]])[-*][[:space:]]\[[[:space:]]\]'; then
  block_reason="Rewrite the response before stopping: unresolved checklist items remain in the final message."
fi

if [[ -z "$block_reason" ]] && printf '%s' "$normalized_message" | grep -Eq '(did not run|didn.t run|have not run|haven.t run|unable to verify|could not verify|couldn.t verify)'; then
  if ! printf '%s' "$normalized_message" | grep -Eq '(because|due to|since|per your request|as requested)'; then
    block_reason="Rewrite the response before stopping: if validation was skipped, state the reason clearly or run the smallest relevant check."
  fi
fi

if [[ -n "$block_reason" ]]; then
  jq -n \
    --arg reason "$block_reason" \
    '{
      continue: true,
      decision: "block",
      reason: $reason,
      systemMessage: "Stop hook blocked an incomplete final response."
    }'
else
  jq -n '{continue: true}'
fi
