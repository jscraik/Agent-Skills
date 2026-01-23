#!/usr/bin/env bash
# Ralph Loop for Anthropic Claude Code (claude -p)
#
# Goals:
# - Fresh Claude context each iteration (new `claude -p` process)
# - State persists in files + git, not in the model context
# - Keep prompts small; rely on file references ("pin" + "plan" + "guardrails")
#
# Supports two task modes:
#   1) Checkbox mode via RALPH_TASK.md
#   2) Optional PRD mode via prd.json (stories w/ passes=false/true)

set -euo pipefail

# -----------------------
# Defaults (overridable)
# -----------------------
WORKSPACE="${RALPH_WORKSPACE:-.}"
MAX_ITERATIONS="${MAX_ITERATIONS:-25}"

# Claude behavior
CLAUDE_MODEL="${RALPH_MODEL:-sonnet}"                 # alias or full model name
CLAUDE_MAX_TURNS="${RALPH_MAX_TURNS:-25}"             # agentic turns per iteration
CLAUDE_PERMISSION_MODE="${RALPH_PERMISSION_MODE:-acceptEdits}"
CLAUDE_TOOLS="${RALPH_TOOLS:-Read,Edit,Grep,Glob}"
CLAUDE_ALLOWED_TOOLS="${RALPH_ALLOWED_TOOLS:-Read,Edit,Grep,Glob}"
CLAUDE_DANGEROUS_SKIP_PERMISSIONS="${RALPH_DANGEROUS_SKIP_PERMISSIONS:-false}"  # true|false

# Output handling
OUTPUT_FORMAT="${RALPH_OUTPUT_FORMAT:-text}"          # text|json
STRUCTURED_OUTPUT="${RALPH_STRUCTURED_OUTPUT:-off}"  # auto|on|off
ITERATION_SCHEMA_FILE="${RALPH_ITERATION_SCHEMA_FILE:-.ralph/iteration.schema.json}"

# Task files
TASK_FILE="${RALPH_TASK_FILE:-RALPH_TASK.md}"
PRD_FILE="${RALPH_PRD_FILE:-prd.json}"

# State files
RALPH_DIR="${RALPH_STATE_DIR:-.ralph}"
PIN_FILE="${RALPH_PIN_FILE:-$RALPH_DIR/pin.md}"
PLAN_FILE="${RALPH_PLAN_FILE:-$RALPH_DIR/plan.md}"
GUARDRAILS_FILE="${RALPH_GUARDRAILS_FILE:-$RALPH_DIR/guardrails.md}"
PROGRESS_FILE="${RALPH_PROGRESS_FILE:-$RALPH_DIR/progress.md}"
ADDENDUM_FILE="${RALPH_ADDENDUM_FILE:-scripts/ralph/prompt.md}"

# Git
BRANCH="${RALPH_BRANCH:-}"
PUSH="${RALPH_PUSH:-false}"                      # true|false
COMMIT_MODE="${RALPH_COMMIT_MODE:-green}"        # green|always|never
GIT_NO_VERIFY="${RALPH_GIT_NO_VERIFY:-false}"    # true|false
REQUIRE_CLEAN_TREE="${RALPH_REQUIRE_CLEAN_TREE:-false}" # true|false
ARCHIVE_PER_BRANCH="${RALPH_ARCHIVE_PER_BRANCH:-true}"  # true|false

# Check commands
TEST_CMD="${RALPH_TEST_CMD:-}"
TYPECHECK_CMD="${RALPH_TYPECHECK_CMD:-}"
LINT_CMD="${RALPH_LINT_CMD:-}"

# Failure handling
CHECK_FAILURE_STREAK_LIMIT="${RALPH_CHECK_FAILURE_STREAK_LIMIT:-3}"
AGENT_FAILURE_STREAK_LIMIT="${RALPH_AGENT_FAILURE_STREAK_LIMIT:-3}"
SLEEP_SECONDS="${RALPH_SLEEP_SECONDS:-0}"

# Logging
LOGS_DIR="$RALPH_DIR/logs"
ACTIVITY_LOG="$RALPH_DIR/activity.log"
ERROR_LOG="$RALPH_DIR/errors.log"

# -----------------------
# Helpers
# -----------------------
die() { echo "ERROR: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<'EOF'
Usage:
  ./scripts/ralph/ralph-claude.sh [options]

Options:
  -w, --workspace DIR           Working directory (default: .)
  -n, --iterations N            Max outer-loop iterations (default: 25)

Claude flags (passed to `claude -p`):
  -m, --model NAME              Model alias/full name (default: sonnet)
      --max-turns N             Max agent turns per iteration (default: 25)
      --permission-mode MODE    default|acceptEdits|plan|dontAsk|bypassPermissions (default: acceptEdits)
      --tools LIST              Restrict tools (default: Read,Edit,Grep,Glob)
      --allowed-tools LIST      Auto-approve tools (default: Read,Edit,Grep,Glob)
      --dangerously-skip-permissions true|false (default: false)

Structured output:
      --structured MODE         auto|on|off (default: auto)
      --iteration-schema FILE   JSON schema file (default: .ralph/iteration.schema.json)
      --output-format FMT       text|json (default: text). In structured mode, json is recommended.

Task / state files:
      --task FILE               Task file (default: RALPH_TASK.md)
      --prd FILE                PRD file (default: prd.json)
      --pin FILE                Pin/spec anchor file (default: .ralph/pin.md)
      --plan FILE               Plan file (default: .ralph/plan.md)
      --guardrails FILE         Guardrails file (default: .ralph/guardrails.md)
      --progress FILE           Progress log (default: .ralph/progress.md)
      --addendum FILE           Optional prompt addendum (default: scripts/ralph/prompt.md)

Git:
      --branch NAME             Checkout/create branch before looping
      --push BOOL               true|false (push after commits)
      --commit MODE             green|always|never (default: green)
      --no-verify BOOL          true|false (skip commit hooks; default false)
      --require-clean-tree BOOL true|false (default false)
      --archive-per-branch BOOL true|false (default true)

Checks:
      --test-cmd CMD            Override test command
      --typecheck-cmd CMD       Override typecheck command
      --lint-cmd CMD            Override lint command

Failure handling:
      --check-fail-limit N      Stop after N consecutive failing check runs (default: 3)
      --agent-fail-limit N      Stop after N consecutive claude failures (default: 3)
      --sleep SECONDS           Sleep between iterations (default: 0)

  -h, --help                    Show help
EOF
}

log_activity() {
  local msg="$1"
  mkdir -p "$(dirname "$ACTIVITY_LOG")"
  printf "[%s] %s\n" "$(date +"%Y-%m-%dT%H:%M:%S%z")" "$msg" | tee -a "$ACTIVITY_LOG" >/dev/null
}

log_error() {
  local msg="$1"
  mkdir -p "$(dirname "$ERROR_LOG")"
  printf "[%s] %s\n" "$(date +"%Y-%m-%dT%H:%M:%S%z")" "$msg" | tee -a "$ERROR_LOG" >/dev/null
}

ensure_file() {
  local path="$1"
  local header="$2"
  if [[ ! -f "$path" ]]; then
    mkdir -p "$(dirname "$path")"
    printf "%s\n" "$header" > "$path"
  fi
}

# Extract YAML frontmatter key from a file that starts with '---' ... '---'
frontmatter_get() {
  local key="$1"
  local file="$2"
  [[ -f "$file" ]] || return 0
  awk -v k="$key" '
    BEGIN { in=0 }
    /^---[ \t]*$/ { if (in==0) { in=1; next } else { exit } }
    in==1 {
      if ($0 ~ "^[ \t]*" k ":[ \t]*") {
        sub("^[ \t]*" k ":[ \t]*", "", $0)
        gsub(/^[ \t"]+|[ \t"]+$/, "", $0)
        print $0
        exit
      }
    }
  ' "$file"
}

count_unchecked_boxes() {
  local file="$1"
  [[ -f "$file" ]] || { echo "0"; return 0; }
  grep -E "^\s*([-*]|\d+[.)])?\s*\[\s\]\s+" "$file" 2>/dev/null | wc -l | tr -d ' '
}

prd_tasks_key() {
  local file="$1"
  jq -r '
    if (.userStories | type) == "array" then "userStories"
    elif (.stories | type) == "array" then "stories"
    elif (.tasks | type) == "array" then "tasks"
    else "" end
  ' "$file"
}

prd_next_index() {
  local file="$1"
  local key="$2"
  jq -r --arg k "$key" '
    (.[$k] // [])
    | to_entries
    | map(select(.value.passes != true))
    | sort_by([(.value.priority // 9999), .key])
    | (.[0].key // "")
  ' "$file"
}

prd_story_json() {
  local file="$1"
  local key="$2"
  local idx="$3"
  jq -c --arg k "$key" --argjson i "$idx" '.[$k][$i]' "$file"
}

story_id_from_json() { jq -r '.id // .key // .slug // .title // .name // "story"' <<<"$1"; }
story_title_from_json() { jq -r '.title // .name // .summary // .id // "Untitled story"' <<<"$1"; }

run_checks() {
  local iter="$1"
  local checks_log="$LOGS_DIR/iter-$(printf "%04d" "$iter").checks.log"
  mkdir -p "$LOGS_DIR"

  local ok=0

  if [[ -n "$TYPECHECK_CMD" ]]; then
    echo "== TYPECHECK: $TYPECHECK_CMD" | tee -a "$checks_log"
    if ! bash -lc "$TYPECHECK_CMD" 2>&1 | tee -a "$checks_log"; then ok=1; fi
    echo "" | tee -a "$checks_log"
  fi

  if [[ -n "$LINT_CMD" ]]; then
    echo "== LINT: $LINT_CMD" | tee -a "$checks_log"
    if ! bash -lc "$LINT_CMD" 2>&1 | tee -a "$checks_log"; then ok=1; fi
    echo "" | tee -a "$checks_log"
  fi

  if [[ -n "$TEST_CMD" ]]; then
    echo "== TEST: $TEST_CMD" | tee -a "$checks_log"
    if ! bash -lc "$TEST_CMD" 2>&1 | tee -a "$checks_log"; then ok=1; fi
    echo "" | tee -a "$checks_log"
  fi

  return "$ok"
}

git_is_repo() { git rev-parse --is-inside-work-tree >/dev/null 2>&1; }

git_dirty() {
  git_is_repo || return 1
  [[ -n "$(git status --porcelain)" ]]
}

git_current_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null || echo ""
}

git_checkout_branch() {
  local branch="$1"
  [[ -n "$branch" ]] || return 0
  git_is_repo || { log_error "Not a git repo; --branch ignored"; return 0; }

  local current
  current="$(git_current_branch)"
  if [[ "$current" == "$branch" ]]; then
    return 0
  fi

  if git show-ref --verify --quiet "refs/heads/$branch"; then
    git checkout "$branch"
  else
    git checkout -b "$branch"
  fi
}

archive_ephemeral_state_if_branch_changed() {
  [[ "$ARCHIVE_PER_BRANCH" == "true" ]] || return 0
  git_is_repo || return 0

  local cur prev branch_file archive_dir ts safe_prev
  cur="$(git_current_branch)"
  branch_file="$RALPH_DIR/last_branch.txt"

  if [[ -f "$branch_file" ]]; then
    prev="$(cat "$branch_file" 2>/dev/null || true)"
  else
    prev=""
  fi

  if [[ -n "$prev" && "$prev" != "$cur" ]]; then
    ts="$(date +"%Y%m%dT%H%M%S")"
    safe_prev="${prev//\//_}"
    archive_dir="$RALPH_DIR/archive/${ts}-${safe_prev}"
    mkdir -p "$archive_dir"

    shopt -s nullglob
    if [[ -d "$LOGS_DIR" ]]; then mv "$LOGS_DIR" "$archive_dir/" 2>/dev/null || true; fi
    for f in "$RALPH_DIR"/prompt.iter-*.md "$RALPH_DIR"/last_result.iter-*.json "$RALPH_DIR"/iter-*.raw.txt; do
      [[ -f "$f" ]] && mv "$f" "$archive_dir/" 2>/dev/null || true
    done
    [[ -f "$ACTIVITY_LOG" ]] && mv "$ACTIVITY_LOG" "$archive_dir/" 2>/dev/null || true
    [[ -f "$ERROR_LOG" ]] && mv "$ERROR_LOG" "$archive_dir/" 2>/dev/null || true
    shopt -u nullglob

    log_activity "Archived ephemeral state for branch '$prev' to $archive_dir"
  fi

  printf "%s" "$cur" > "$branch_file"
}

git_maybe_commit() {
  local iter="$1"
  local msg="$2"
  local allow="$3"

  git_is_repo || return 0
  [[ "$COMMIT_MODE" == "never" ]] && return 0
  [[ "$allow" != "true" && "$COMMIT_MODE" == "green" ]] && return 0

  if git diff --quiet && git diff --cached --quiet; then
    return 0
  fi

  git add -A

  local commit_args=(-m "$msg")
  if [[ "$GIT_NO_VERIFY" == "true" ]]; then
    commit_args+=(--no-verify)
  fi

  if git commit "${commit_args[@]}" >/dev/null 2>&1; then
    log_activity "Committed: $msg"
  else
    true
  fi

  if [[ "$PUSH" == "true" ]]; then
    local cur
    cur="$(git_current_branch)"
    git push -u origin "$cur" >/dev/null 2>&1 || log_error "git push failed (ignored)"
  fi
}

prd_mark_passes_true() {
  local file="$1"
  local key="$2"
  local idx="$3"
  local tmp
  tmp="$(mktemp)"
  jq --arg k "$key" --argjson i "$idx" '.[$k][$i].passes = true' "$file" > "$tmp"
  mv "$tmp" "$file"
}

append_progress_note() {
  local iter="$1"
  local mode="$2"
  local status="$3"
  local story_id="${4:-}"
  local checks_ran="$5"
  local checks_ok="$6"
  local summary="$7"

  local ts
  ts="$(date +"%Y-%m-%dT%H:%M:%S%z")"

  local checks_str="checks=SKIP"
  if [[ "$checks_ran" == "true" ]]; then
    if [[ "$checks_ok" == "true" ]]; then checks_str="checks=PASS"; else checks_str="checks=FAIL"; fi
  fi

  local label="iter $iter mode=$mode status=$status $checks_str"
  if [[ -n "$story_id" ]]; then
    label="$label story=$story_id"
  fi

  summary="$(echo "$summary" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g' | cut -c1-200)"
  printf -- "- [%s] %s — %s\n" "$ts" "$label" "$summary" >> "$PROGRESS_FILE" 2>/dev/null || true
}

# -----------------------
# Parse args
# -----------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -w|--workspace) WORKSPACE="$2"; shift 2;;
    -n|--iterations) MAX_ITERATIONS="$2"; shift 2;;

    -m|--model) CLAUDE_MODEL="$2"; shift 2;;
    --max-turns) CLAUDE_MAX_TURNS="$2"; shift 2;;
    --permission-mode) CLAUDE_PERMISSION_MODE="$2"; shift 2;;
    --tools) CLAUDE_TOOLS="$2"; shift 2;;
    --allowed-tools) CLAUDE_ALLOWED_TOOLS="$2"; shift 2;;
    --dangerously-skip-permissions) CLAUDE_DANGEROUS_SKIP_PERMISSIONS="$2"; shift 2;;

    --structured) STRUCTURED_OUTPUT="$2"; shift 2;;
    --iteration-schema) ITERATION_SCHEMA_FILE="$2"; shift 2;;
    --output-format) OUTPUT_FORMAT="$2"; shift 2;;

    --task) TASK_FILE="$2"; shift 2;;
    --prd) PRD_FILE="$2"; shift 2;;
    --pin) PIN_FILE="$2"; shift 2;;
    --plan) PLAN_FILE="$2"; shift 2;;
    --guardrails) GUARDRAILS_FILE="$2"; shift 2;;
    --progress) PROGRESS_FILE="$2"; shift 2;;
    --addendum) ADDENDUM_FILE="$2"; shift 2;;

    --branch) BRANCH="$2"; shift 2;;
    --push) PUSH="$2"; shift 2;;
    --commit) COMMIT_MODE="$2"; shift 2;;
    --no-verify) GIT_NO_VERIFY="$2"; shift 2;;
    --require-clean-tree) REQUIRE_CLEAN_TREE="$2"; shift 2;;
    --archive-per-branch) ARCHIVE_PER_BRANCH="$2"; shift 2;;

    --test-cmd) TEST_CMD="$2"; shift 2;;
    --typecheck-cmd) TYPECHECK_CMD="$2"; shift 2;;
    --lint-cmd) LINT_CMD="$2"; shift 2;;

    --check-fail-limit) CHECK_FAILURE_STREAK_LIMIT="$2"; shift 2;;
    --agent-fail-limit) AGENT_FAILURE_STREAK_LIMIT="$2"; shift 2;;
    --sleep) SLEEP_SECONDS="$2"; shift 2;;

    -h|--help) usage; exit 0;;
    *) die "Unknown option: $1";;
  esac
done

# -----------------------
# Init
# -----------------------
have claude || die "claude CLI not found in PATH"
cd "$WORKSPACE"

mkdir -p "$RALPH_DIR" "$LOGS_DIR"

ensure_file "$RALPH_DIR/.gitignore" "# Ralph loop artifacts\nlogs/\narchive/\nprompt.iter-*.md\nlast_result.iter-*.json\niter-*.raw.txt\nstate.json\n"

ensure_file "$PIN_FILE" "# Ralph Pin (spec anchor)\n\n- Purpose:\n- Non-goals:\n- Constraints:\n- Conventions:\n- Known system areas / links:\n"
ensure_file "$PLAN_FILE" "# Ralph Plan (linkage-oriented)\n\n- Link to spec sections and code locations.\n- Keep each item small enough for one loop iteration.\n"
ensure_file "$GUARDRAILS_FILE" "# Guardrails (Signs)\n\nAdd short, reusable rules learned from failures.\n\nExample:\n## Sign: Don't duplicate imports\n- Trigger: adding imports\n- Instruction: check existing imports first\n- Added after: iter X\n"
ensure_file "$PROGRESS_FILE" "# Progress (append-only)\n\nWrite short notes per iteration: what changed, what failed, what to do next.\n"

# Iteration schema file (optional)
if [[ ! -f "$ITERATION_SCHEMA_FILE" ]]; then
  ensure_file "$ITERATION_SCHEMA_FILE" "$(cat <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RalphIterationResult",
  "type": "object",
  "properties": {
    "status": { "type": "string", "enum": ["CONTINUE", "DONE", "GUTTER"] },
    "summary": { "type": "string" }
  },
  "required": ["status", "summary"],
  "additionalProperties": true
}
JSON
)"
fi

# Task template if missing
if [[ ! -f "$TASK_FILE" ]]; then
  cat > "$TASK_FILE" <<'EOF'
---
task: "Describe the task here"
test_command: ""
typecheck_command: ""
lint_command: ""
---

# Ralph Task

## Success Criteria (checkboxes)

1. [ ] Define concrete, testable outcomes
2. [ ] Add/adjust tests for the outcomes
3. [ ] Implement the feature
4. [ ] All checks pass
EOF
fi

# Auto-discover checks from frontmatter
if [[ -z "$TEST_CMD" ]]; then TEST_CMD="$(frontmatter_get "test_command" "$TASK_FILE" || true)"; fi
if [[ -z "$TYPECHECK_CMD" ]]; then TYPECHECK_CMD="$(frontmatter_get "typecheck_command" "$TASK_FILE" || true)"; fi
if [[ -z "$LINT_CMD" ]]; then LINT_CMD="$(frontmatter_get "lint_command" "$TASK_FILE" || true)"; fi

# PRD may define checks too
HAS_JQ="false"
have jq && HAS_JQ="true"

if [[ -f "$PRD_FILE" && "$HAS_JQ" == "true" ]]; then
  if [[ -z "$TEST_CMD" ]]; then TEST_CMD="$(jq -r '(.testCommand // .test_command // .commands.test // .quality.test // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
  if [[ -z "$TYPECHECK_CMD" ]]; then TYPECHECK_CMD="$(jq -r '(.typecheckCommand // .typecheck_command // .commands.typecheck // .quality.typecheck // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
  if [[ -z "$LINT_CMD" ]]; then LINT_CMD="$(jq -r '(.lintCommand // .lint_command // .commands.lint // .quality.lint // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
fi

# Git branch setup
if [[ -n "$BRANCH" ]]; then
  git_checkout_branch "$BRANCH"
fi

archive_ephemeral_state_if_branch_changed

if [[ "$REQUIRE_CLEAN_TREE" == "true" && "$(git_is_repo && echo yes || echo no)" == "yes" ]]; then
  if git_dirty; then
    git status --porcelain >&2
    die "Refusing to start: git working tree is not clean (set --require-clean-tree false to override)."
  fi
fi

# Structured output decision
USE_STRUCTURED="false"
if [[ "$STRUCTURED_OUTPUT" == "on" ]]; then
  [[ "$HAS_JQ" == "true" ]] || die "--structured on requires jq"
  USE_STRUCTURED="true"
elif [[ "$STRUCTURED_OUTPUT" == "auto" ]]; then
  [[ "$HAS_JQ" == "true" ]] && USE_STRUCTURED="true"
elif [[ "$STRUCTURED_OUTPUT" == "off" ]]; then
  USE_STRUCTURED="false"
else
  die "Invalid --structured value: $STRUCTURED_OUTPUT (expected auto|on|off)"
fi

# If structured is enabled, json output makes parsing easier.
if [[ "$USE_STRUCTURED" == "true" && "$HAS_JQ" == "true" ]]; then
  OUTPUT_FORMAT="json"
fi

log_activity "Starting Ralph Claude loop in $(pwd) (model=$CLAUDE_MODEL, max_turns=$CLAUDE_MAX_TURNS, structured=$USE_STRUCTURED)"

# -----------------------
# Main loop
# -----------------------
check_fail_streak=0
agent_fail_streak=0

for ((iter=1; iter<=MAX_ITERATIONS; iter++)); do
  log_activity "Iteration $iter start"

  local_mode="checkbox"
  if [[ -f "$PRD_FILE" && "$HAS_JQ" == "true" ]]; then
    key="$(prd_tasks_key "$PRD_FILE" 2>/dev/null || true)"
    if [[ -n "${key:-}" ]]; then
      local_mode="prd"
    fi
  fi

  iter_prompt="$RALPH_DIR/prompt.iter-$(printf "%04d" "$iter").md"
  iter_raw="$RALPH_DIR/iter-$(printf "%04d" "$iter").raw.txt"
  iter_stdout="$LOGS_DIR/iter-$(printf "%04d" "$iter").stdout.log"
  iter_result="$RALPH_DIR/last_result.iter-$(printf "%04d" "$iter").json"

  objective_block=""
  prd_key=""
  prd_idx=""
  story_id=""
  story_title=""

  if [[ "$local_mode" == "checkbox" ]]; then
    remaining="$(count_unchecked_boxes "$TASK_FILE")"
    if [[ "$remaining" == "0" ]]; then
      log_activity "Checkbox mode complete (0 unchecked boxes). Exiting."
      break
    fi

    unchecked_list="$(grep -E "^\s*([-*]|\d+[.)])?\s*\[\s\]\s+" "$TASK_FILE" | head -n 20 || true)"

    objective_block=$(cat <<EOF
MODE: CHECKBOX
Unchecked boxes remaining: $remaining

Work on ONE checkbox (the highest-leverage next step). When you complete it, change [ ] -> [x].
Unchecked items (first 20):
$unchecked_list
EOF
)
  else
    prd_key="$(prd_tasks_key "$PRD_FILE")"
    prd_idx="$(prd_next_index "$PRD_FILE" "$prd_key")"
    if [[ -z "$prd_idx" ]]; then
      log_activity "PRD mode complete (all stories pass). Exiting."
      break
    fi

    story="$(prd_story_json "$PRD_FILE" "$prd_key" "$prd_idx")"
    story_id="$(story_id_from_json "$story")"
    story_title="$(story_title_from_json "$story")"

    objective_block=$(cat <<EOF
MODE: PRD
PRD file: $PRD_FILE
Stories array key: $prd_key
Selected story index: $prd_idx
Selected story id: $story_id
Selected story title: $story_title

Your single objective this iteration is to make this story pass.
Do NOT edit other stories. Keep changes minimal and linked to the pin/plan.
EOF
)
  fi

  instruction_files=()
  [[ -f "AGENTS.md" ]] && instruction_files+=("AGENTS.md")
  [[ -f "CLAUDE.md" ]] && instruction_files+=("CLAUDE.md")
  [[ -f ".github/copilot-instructions.md" ]] && instruction_files+=(".github/copilot-instructions.md")

  cat >"$iter_prompt" <<EOF
# Ralph Loop — Claude Code

Iteration: $iter
Workspace: $(pwd)

## Read these files first (anchors + rails)
1) $PIN_FILE
2) $PLAN_FILE
3) $GUARDRAILS_FILE
4) $PROGRESS_FILE
EOF

  if [[ "${#instruction_files[@]}" -gt 0 ]]; then
    echo "" >>"$iter_prompt"
    echo "## Also read (repo instructions)" >>"$iter_prompt"
    for f in "${instruction_files[@]}"; do
      echo "- $f" >>"$iter_prompt"
    done
  fi

  if [[ "$local_mode" == "checkbox" ]]; then
    echo "" >>"$iter_prompt"
    echo "## Task file" >>"$iter_prompt"
    echo "- $TASK_FILE" >>"$iter_prompt"
  else
    echo "" >>"$iter_prompt"
    echo "## PRD file" >>"$iter_prompt"
    echo "- $PRD_FILE" >>"$iter_prompt"
  fi

  cat >>"$iter_prompt" <<EOF

## Operating rules
- Keep context minimal: use targeted search (Grep/Glob) to find relevant files; avoid reading huge files end-to-end.
- Work on ONE objective only (single checkbox OR the single PRD story provided).
- Prefer linkage over invention: before changing code, cite the relevant spec section and file(s) you will edit.
- Follow existing conventions in the repo (style, linting, tests, i18n, etc).
- Add/adjust tests where appropriate.
- Keep changes small and incremental; do not do broad refactors unless required by the pin/spec.
- If something fails repeatedly, add a short reusable "Sign" to guardrails.md.

EOF

  if [[ -f "$ADDENDUM_FILE" ]]; then
    echo "## Prompt addendum (project-specific)" >>"$iter_prompt"
    cat "$ADDENDUM_FILE" >>"$iter_prompt"
    echo "" >>"$iter_prompt"
  fi

  echo "## Current objective" >>"$iter_prompt"
  echo "$objective_block" >>"$iter_prompt"
  echo "" >>"$iter_prompt"

  if [[ "$USE_STRUCTURED" == "true" ]]; then
    cat >>"$iter_prompt" <<EOF
## Output format (MANDATORY)
Return ONLY a single JSON object matching this JSON Schema:
- $ITERATION_SCHEMA_FILE

Rules:
- No surrounding markdown.
- No backticks.
- Keys must be double-quoted (valid JSON).
- status must be one of: CONTINUE | DONE | GUTTER

Example:
{"status":"CONTINUE","summary":"Added a failing test; next fix the handler."}
EOF
  else
    cat >>"$iter_prompt" <<'EOF'
## Signals (print exactly one at the end)
- If you believe the objective is done and checks are green: <ralph>DONE</ralph>
- If you are blocked after 2 serious attempts: <ralph>GUTTER</ralph>
EOF
  fi

  query="Read $iter_prompt and follow it exactly. End with the required output format."
  claude_args=(claude -p "$query" --output-format "$OUTPUT_FORMAT" --model "$CLAUDE_MODEL" --max-turns "$CLAUDE_MAX_TURNS" --permission-mode "$CLAUDE_PERMISSION_MODE" --tools "$CLAUDE_TOOLS" --allowed-tools "$CLAUDE_ALLOWED_TOOLS")

  if [[ "$CLAUDE_DANGEROUS_SKIP_PERMISSIONS" == "true" ]]; then
    claude_args+=(--dangerously-skip-permissions)
  fi

  log_activity "Iteration $iter claude start (mode=$local_mode, output=$OUTPUT_FORMAT)"
  set +e
  "${claude_args[@]}" 2>&1 | tee "$iter_stdout" | tee "$iter_raw" >/dev/null
  claude_exit="${PIPESTATUS[0]}"
  set -e
  log_activity "Iteration $iter claude exit=$claude_exit"

  if [[ $claude_exit -ne 0 ]]; then
    agent_fail_streak=$((agent_fail_streak+1))
    log_error "Iteration $iter claude failed (streak=$agent_fail_streak). See $iter_stdout"
    if [[ $agent_fail_streak -ge $AGENT_FAILURE_STREAK_LIMIT ]]; then
      log_error "Agent failure streak reached limit ($AGENT_FAILURE_STREAK_LIMIT). Stopping."
      break
    fi
  else
    agent_fail_streak=0
  fi

  # Extract assistant message from raw output
  iter_msg=""
  if [[ "$OUTPUT_FORMAT" == "json" && "$HAS_JQ" == "true" ]]; then
    # Claude JSON output format: { "result": "...", ... }
    iter_msg="$(cat "$iter_raw" | jq -r '.result // empty' 2>/dev/null || true)"
  else
    iter_msg="$(cat "$iter_raw")"
  fi

  status="CONTINUE"
  summary="(no summary)"

  if [[ "$USE_STRUCTURED" == "true" && "$HAS_JQ" == "true" ]]; then
    if jq -e . >/dev/null 2>&1 <<<"$iter_msg"; then
      printf "%s\n" "$iter_msg" > "$iter_result" 2>/dev/null || true
      status="$(jq -r '.status // "CONTINUE"' <<<"$iter_msg" 2>/dev/null || echo "CONTINUE")"
      summary="$(jq -r '.summary // "(no summary)"' <<<"$iter_msg" 2>/dev/null || echo "(no summary)")"
    else
      # Fallback tags
      if grep -q "<ralph>GUTTER</ralph>" <<<"$iter_msg"; then status="GUTTER"; fi
      if grep -q "<ralph>DONE</ralph>" <<<"$iter_msg"; then status="DONE"; fi
      summary="$(printf "%s" "$iter_msg" | head -n 1 | tr -d '\r' | cut -c1-200)"
    fi
  else
    if grep -q "<ralph>GUTTER</ralph>" <<<"$iter_msg"; then status="GUTTER"; fi
    if grep -q "<ralph>DONE</ralph>" <<<"$iter_msg"; then status="DONE"; fi
    summary="$(printf "%s" "$iter_msg" | head -n 1 | tr -d '\r' | cut -c1-200)"
  fi

  if [[ "$status" == "GUTTER" ]]; then
    log_error "Iteration $iter signalled GUTTER. Stopping loop."
    append_progress_note "$iter" "$local_mode" "$status" "$story_id" "false" "false" "$summary"
    break
  fi

  # Checks
  checks_ran="false"
  checks_ok="true"
  if [[ -n "$TEST_CMD" || -n "$TYPECHECK_CMD" || -n "$LINT_CMD" ]]; then
    checks_ran="true"
    if run_checks "$iter"; then
      checks_ok="true"
      log_activity "Iteration $iter checks PASS"
      check_fail_streak=0
    else
      checks_ok="false"
      check_fail_streak=$((check_fail_streak+1))
      log_error "Iteration $iter checks FAIL (streak=$check_fail_streak) (see $LOGS_DIR/iter-$(printf "%04d" "$iter").checks.log)"
      if [[ $check_fail_streak -ge $CHECK_FAILURE_STREAK_LIMIT ]]; then
        log_error "Check failure streak reached limit ($CHECK_FAILURE_STREAK_LIMIT). Stopping."
        append_progress_note "$iter" "$local_mode" "GUTTER" "$story_id" "$checks_ran" "$checks_ok" "Repeated failing checks; update pin/plan/guardrails."
        break
      fi
    fi
  else
    check_fail_streak=0
  fi

  append_progress_note "$iter" "$local_mode" "$status" "$story_id" "$checks_ran" "$checks_ok" "$summary"

  # PRD marking
  if [[ "$local_mode" == "prd" && "$status" == "DONE" ]]; then
    if [[ "$checks_ran" == "false" || "$checks_ok" == "true" ]]; then
      prd_mark_passes_true "$PRD_FILE" "$prd_key" "$prd_idx"
      log_activity "Marked story passes=true (id=$story_id, idx=$prd_idx)"
    else
      log_error "Agent said DONE but checks failed; not marking passes=true (id=$story_id)"
    fi
  fi

  # Commit
  commit_msg="ralph: iter $iter"
  if [[ "$local_mode" == "prd" && -n "$story_id" ]]; then
    commit_msg="ralph: iter $iter ($story_id)"
  fi

  allow_commit="false"
  if [[ "$COMMIT_MODE" == "always" ]]; then
    allow_commit="true"
  elif [[ "$COMMIT_MODE" == "green" ]]; then
    if [[ "$checks_ran" == "false" || "$checks_ok" == "true" ]]; then
      allow_commit="true"
    fi
  fi
  git_maybe_commit "$iter" "$commit_msg" "$allow_commit"

  # Completion check for checkbox mode
  if [[ "$local_mode" == "checkbox" ]]; then
    remaining_after="$(count_unchecked_boxes "$TASK_FILE")"
    if [[ "$remaining_after" == "0" ]]; then
      log_activity "Checkbox mode complete (0 unchecked boxes). Exiting."
      break
    fi
  fi

  log_activity "Iteration $iter end"
  if [[ "$SLEEP_SECONDS" != "0" ]]; then
    sleep "$SLEEP_SECONDS" || true
  fi
done

log_activity "Ralph loop finished."
