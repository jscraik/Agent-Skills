#!/usr/bin/env bash
# Ralph Loop for OpenAI Codex CLI (codex exec)
#
# Goals:
# - Fresh Codex context each iteration (new codex exec process)
# - State persists in files + git, not in the model context
# - Keep prompts small; rely on file references ("pin" + "plan" + "guardrails")
#
# Supports two task modes:
#   1) Checkbox mode via RALPH_TASK.md
#   2) PRD mode via prd.json (stories w/ passes=false/true)
#
# Usage:
#   ./scripts/ralph/ralph-codex.sh [options]
#
# Recommended:
#   - Start attended: -a on-request
#   - Run on a branch: --branch ralph/<topic>
#   - Keep .ralph/pin.md small and authoritative

set -euo pipefail

# ----------------------------
# Defaults (override via env)
# ----------------------------
WORKSPACE="${RALPH_WORKSPACE:-$(pwd)}"
MAX_ITERATIONS="${MAX_ITERATIONS:-20}"

MODEL="${RALPH_MODEL:-gpt-5-codex}"

# Codex safety knobs
SANDBOX="${RALPH_SANDBOX:-workspace-write}"        # read-only | workspace-write | danger-full-access
ASK_APPROVAL="${RALPH_ASK_APPROVAL:-never}"        # untrusted | on-failure | on-request | never
ENABLE_SEARCH="${RALPH_ENABLE_SEARCH:-false}"      # true | false

# Task sources
TASK_FILE="${RALPH_TASK_FILE:-RALPH_TASK.md}"
PRD_FILE="${RALPH_PRD_FILE:-prd.json}"

# "Pin" + state files (kept small; treated as authoritative)
STATE_DIR="${RALPH_STATE_DIR:-.ralph}"
PIN_FILE="${RALPH_PIN_FILE:-$STATE_DIR/pin.md}"
PLAN_FILE="${RALPH_PLAN_FILE:-$STATE_DIR/plan.md}"
GUARDRAILS_FILE="${RALPH_GUARDRAILS_FILE:-$STATE_DIR/guardrails.md}"
PROGRESS_FILE="${RALPH_PROGRESS_FILE:-$STATE_DIR/progress.md}"

# Prompt template (static addendum)
PROMPT_ADDENDUM_FILE="${RALPH_PROMPT_ADDENDUM_FILE:-scripts/ralph/prompt.md}"

# Structured iteration result (optional)
STRUCTURED_OUTPUT="${RALPH_STRUCTURED_OUTPUT:-off}"   # auto|on|off
ITERATION_SCHEMA_FILE="${RALPH_ITERATION_SCHEMA_FILE:-$STATE_DIR/iteration.schema.json}"

# Logging
LOG_DIR="${RALPH_LOG_DIR:-$STATE_DIR/logs}"
ACTIVITY_LOG="${RALPH_ACTIVITY_LOG:-$STATE_DIR/activity.log}"
ERRORS_LOG="${RALPH_ERRORS_LOG:-$STATE_DIR/errors.log}"

# Git / workflow
BRANCH="${RALPH_BRANCH:-}"              # if set, checkout/create branch before looping
PUSH="${RALPH_PUSH:-false}"             # true | false
COMMIT_MODE="${RALPH_COMMIT_MODE:-green}"  # green | always | never
GIT_NO_VERIFY="${RALPH_GIT_NO_VERIFY:-false}" # true|false (skip commit hooks)
REQUIRE_CLEAN_TREE="${RALPH_REQUIRE_CLEAN_TREE:-false}" # true|false (recommended true for unattended)
ARCHIVE_PER_BRANCH="${RALPH_ARCHIVE_PER_BRANCH:-true}"  # true|false

# Checks (optional; discovered from frontmatter or prd.json)
TEST_CMD="${RALPH_TEST_CMD:-}"
TYPECHECK_CMD="${RALPH_TYPECHECK_CMD:-}"
LINT_CMD="${RALPH_LINT_CMD:-}"

# Failure handling
CHECK_FAILURE_STREAK_LIMIT="${RALPH_CHECK_FAILURE_STREAK_LIMIT:-3}"   # stop after N consecutive failing check runs
AGENT_FAILURE_STREAK_LIMIT="${RALPH_AGENT_FAILURE_STREAK_LIMIT:-3}"   # stop after N consecutive codex exec failures
SLEEP_SECONDS="${RALPH_SLEEP_SECONDS:-0}"                              # sleep between iterations (seconds)

# ----------------------------
# Helpers
# ----------------------------
die() { echo "ERROR: $*" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<'EOF'
Ralph Loop for Codex CLI

Runs Codex in a loop until:
  - Checkbox mode: all [ ] in RALPH_TASK.md are checked
  - PRD mode: all stories in prd.json have passes=true

Options:
  -C, --cd PATH                 Workspace root (default: cwd)
  -n, --iterations N            Max iterations (default: 20)
  -m, --model MODEL             Codex model (default: gpt-5-codex)
  -s, --sandbox POLICY          read-only|workspace-write|danger-full-access
  -a, --ask-for-approval MODE   untrusted|on-failure|on-request|never
      --search BOOL             true|false (enable web search tool in Codex)

Task / state:
      --task-file FILE          Checkbox task file (default: RALPH_TASK.md)
      --prd FILE                PRD JSON file (default: prd.json)
      --pin FILE                Pin/spec anchor file (default: .ralph/pin.md)
      --plan FILE               Plan file (default: .ralph/plan.md)
      --guardrails FILE         Guardrails file (default: .ralph/guardrails.md)
      --progress FILE           Progress log (default: .ralph/progress.md)
      --prompt-addendum FILE    Optional repo-specific addendum (default: scripts/ralph/prompt.md)

Structured output:
      --structured MODE         auto|on|off (default: auto)
      --iteration-schema FILE   JSON schema file (default: .ralph/iteration.schema.json)

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
      --agent-fail-limit N      Stop after N consecutive codex exec failures (default: 3)
      --sleep SECONDS           Sleep between iterations (default: 0)

  -h, --help                    Show help

Environment variables mirror the flags (prefix RALPH_...).

Examples:
  # Attended "screwdriver" run (may prompt)
  ./scripts/ralph/ralph-codex.sh -a on-request

  # Unattended loop on a dedicated branch
  ./scripts/ralph/ralph-codex.sh --branch ralph/feature-x -a never -s workspace-write --require-clean-tree true
EOF
}

log_activity() {
  local msg="$1"
  mkdir -p "$(dirname "$ACTIVITY_LOG")"
  printf "[%s] %s\n" "$(date +"%Y-%m-%dT%H:%M:%S%z")" "$msg" | tee -a "$ACTIVITY_LOG" >/dev/null
}

log_error() {
  local msg="$1"
  mkdir -p "$(dirname "$ERRORS_LOG")"
  printf "[%s] %s\n" "$(date +"%Y-%m-%dT%H:%M:%S%z")" "$msg" | tee -a "$ERRORS_LOG" >/dev/null
}

ensure_file() {
  local path="$1"
  local header="$2"
  if [[ ! -f "$path" ]]; then
    mkdir -p "$(dirname "$path")"
    printf "%s\n" "$header" > "$path"
  fi
}

# Minimal YAML frontmatter getter (top-of-file --- ... ---). Supports:
#   key: value
#   key: "value"
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

# Checkbox helper: count unchecked boxes in a markdown file
count_unchecked_boxes() {
  local file="$1"
  [[ -f "$file" ]] || { echo "0"; return 0; }
  grep -E "^\s*([-*]|\d+[.)])?\s*\[\s\]\s+" "$file" 2>/dev/null | wc -l | tr -d ' '
}

# PRD mode: detect task array key
prd_tasks_key() {
  local file="$1"
  jq -r '
    if (.userStories | type) == "array" then "userStories"
    elif (.stories | type) == "array" then "stories"
    elif (.tasks | type) == "array" then "tasks"
    else "" end
  ' "$file"
}

# PRD mode: choose next failing story index (priority asc, then index asc)
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

# Run checks (returns 0 if all pass, 1 otherwise)
run_checks() {
  local iter="$1"
  local checks_log="$LOG_DIR/iter-$(printf "%04d" "$iter").checks.log"
  mkdir -p "$LOG_DIR"

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
  branch_file="$STATE_DIR/last_branch.txt"

  if [[ -f "$branch_file" ]]; then
    prev="$(cat "$branch_file" 2>/dev/null || true)"
  else
    prev=""
  fi

  if [[ -n "$prev" && "$prev" != "$cur" ]]; then
    ts="$(date +"%Y%m%dT%H%M%S")"
    safe_prev="${prev//\//_}"
    archive_dir="$STATE_DIR/archive/${ts}-${safe_prev}"
    mkdir -p "$archive_dir"

    # Move ephemeral logs/prompt artifacts to archive
    shopt -s nullglob
    if [[ -d "$LOG_DIR" ]]; then mv "$LOG_DIR" "$archive_dir/" 2>/dev/null || true; fi
    for f in "$STATE_DIR"/prompt.iter-*.md "$STATE_DIR"/last_message.iter-*.md "$STATE_DIR"/last_result.iter-*.json; do
      [[ -f "$f" ]] && mv "$f" "$archive_dir/" 2>/dev/null || true
    done
    [[ -f "$ACTIVITY_LOG" ]] && mv "$ACTIVITY_LOG" "$archive_dir/" 2>/dev/null || true
    [[ -f "$ERRORS_LOG" ]] && mv "$ERRORS_LOG" "$archive_dir/" 2>/dev/null || true
    shopt -u nullglob

    log_activity "Archived ephemeral state for branch '$prev' to $archive_dir"
  fi

  printf "%s" "$cur" > "$branch_file"
}

git_maybe_commit() {
  local iter="$1"
  local msg="$2"
  local allow="$3"  # "true" or "false"

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

# Append a short harness note to progress.md (keeps state outside model context).
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

  # Keep it one line
  summary="$(echo "$summary" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g' | cut -c1-200)"

  printf -- "- [%s] %s — %s\n" "$ts" "$label" "$summary" >> "$PROGRESS_FILE" 2>/dev/null || true
}

# Determine whether codex supports a flag (best effort).
codex_supports_flag() {
  local flag="$1"
  set +e
  local help
  help="$(codex exec --help 2>&1)"
  local rc=$?
  set -e
  [[ $rc -eq 0 ]] || return 1
  grep -q -- "$flag" <<<"$help"
}

# ----------------------------
# Parse args
# ----------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -C|--cd) WORKSPACE="$2"; shift 2;;
    -n|--iterations) MAX_ITERATIONS="$2"; shift 2;;
    -m|--model) MODEL="$2"; shift 2;;
    -s|--sandbox) SANDBOX="$2"; shift 2;;
    -a|--ask-for-approval) ASK_APPROVAL="$2"; shift 2;;
    --search) ENABLE_SEARCH="$2"; shift 2;;

    --task-file) TASK_FILE="$2"; shift 2;;
    --prd) PRD_FILE="$2"; shift 2;;
    --pin) PIN_FILE="$2"; shift 2;;
    --plan) PLAN_FILE="$2"; shift 2;;
    --guardrails) GUARDRAILS_FILE="$2"; shift 2;;
    --progress) PROGRESS_FILE="$2"; shift 2;;
    --prompt-addendum) PROMPT_ADDENDUM_FILE="$2"; shift 2;;

    --structured) STRUCTURED_OUTPUT="$2"; shift 2;;
    --iteration-schema) ITERATION_SCHEMA_FILE="$2"; shift 2;;

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
    *) die "Unknown option: $1 (use --help)";;
  esac
done

# ----------------------------
# Preconditions / init
# ----------------------------
have codex || die "codex CLI not found in PATH"
cd "$WORKSPACE"

mkdir -p "$STATE_DIR" "$LOG_DIR"

# Local .gitignore inside .ralph (safe, non-invasive)
ensure_file "$STATE_DIR/.gitignore" "# Ralph loop artifacts\nlogs/\narchive/\nprompt.iter-*.md\nlast_message.iter-*.md\nlast_result.iter-*.json\nstate.json\n"

# Core state files
ensure_file "$PIN_FILE" "# Ralph Pin (spec anchor)\n\n- Purpose:\n- Non-goals:\n- Constraints:\n- Conventions:\n- Known system areas / links:\n"
ensure_file "$PLAN_FILE" "# Ralph Plan (linkage-oriented)\n\n- Link to spec sections and code locations.\n- Keep each item small enough for one loop iteration.\n"
ensure_file "$GUARDRAILS_FILE" "# Guardrails (Signs)\n\nAdd short, reusable rules learned from failures.\n\nExample:\n## Sign: Don't duplicate imports\n- Trigger: adding imports\n- Instruction: check existing imports first\n- Added after: iter X\n"
ensure_file "$PROGRESS_FILE" "# Progress (append-only)\n\nWrite short notes per iteration: what changed, what failed, what to do next.\n"

# Iteration schema file (optional; used for structured output)
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

# If checkbox mode file missing, create a template
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

## Context / Constraints

- Add constraints here (languages, frameworks, style, security).
- Keep each checkbox small enough to complete in 1-2 iterations.
EOF
fi

# Auto-discover check commands if unset
if [[ -z "$TEST_CMD" ]]; then TEST_CMD="$(frontmatter_get "test_command" "$TASK_FILE" || true)"; fi
if [[ -z "$TYPECHECK_CMD" ]]; then TYPECHECK_CMD="$(frontmatter_get "typecheck_command" "$TASK_FILE" || true)"; fi
if [[ -z "$LINT_CMD" ]]; then LINT_CMD="$(frontmatter_get "lint_command" "$TASK_FILE" || true)"; fi

# PRD mode may define commands too (best-effort)
if [[ -f "$PRD_FILE" && "$(have jq && echo yes || echo no)" == "yes" ]]; then
  if [[ -z "$TEST_CMD" ]]; then TEST_CMD="$(jq -r '(.testCommand // .test_command // .commands.test // .quality.test // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
  if [[ -z "$TYPECHECK_CMD" ]]; then TYPECHECK_CMD="$(jq -r '(.typecheckCommand // .typecheck_command // .commands.typecheck // .quality.typecheck // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
  if [[ -z "$LINT_CMD" ]]; then LINT_CMD="$(jq -r '(.lintCommand // .lint_command // .commands.lint // .quality.lint // empty)' "$PRD_FILE" 2>/dev/null || true)"; fi
fi

# Branch setup (optional)
if [[ -n "$BRANCH" ]]; then
  git_checkout_branch "$BRANCH"
fi

# Archive ephemeral state if we switched branches since last run
archive_ephemeral_state_if_branch_changed

# Safety: require clean tree if enabled
if [[ "$REQUIRE_CLEAN_TREE" == "true" && "$(git_is_repo && echo yes || echo no)" == "yes" ]]; then
  if git_dirty; then
    git status --porcelain >&2
    die "Refusing to start: git working tree is not clean (set --require-clean-tree false to override)."
  fi
fi

# Structured output decision
HAS_JQ="false"
have jq && HAS_JQ="true"

USE_STRUCTURED="false"
USE_OUTPUT_SCHEMA="false"
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

if [[ "$USE_STRUCTURED" == "true" ]]; then
  if codex_supports_flag "--output-schema"; then
    USE_OUTPUT_SCHEMA="true"
  else
    USE_OUTPUT_SCHEMA="false"
  fi
fi

log_activity "Starting Ralph Codex loop in $(pwd) (model=$MODEL, sandbox=$SANDBOX, approvals=$ASK_APPROVAL, max=$MAX_ITERATIONS, structured=$USE_STRUCTURED, output_schema=$USE_OUTPUT_SCHEMA)"

# ----------------------------
# Main loop
# ----------------------------
check_fail_streak=0
agent_fail_streak=0

for ((iter=1; iter<=MAX_ITERATIONS; iter++)); do
  log_activity "Iteration $iter start"

  # Optional: compile prd.json from latest .spec/spec-*.md each iteration
  if [[ "${COMPILE_PRD_EACH_ITER:-true}" == "true" ]]; then
    SPEC_DIR="${RALPH_SPEC_DIR:-.spec}"
    SPEC_FILE="${RALPH_SPEC_FILE:-}"
    COMPILER="${RALPH_SPEC_COMPILER:-scripts/ralph/spec_to_prd.py}"
    STRICT="${RALPH_SPEC_STRICT:-true}"
    if [[ -z "$SPEC_FILE" ]]; then
      if [[ -d "$SPEC_DIR" ]]; then
        # pick newest spec by mtime
        SPEC_FILE="$(ls -t "$SPEC_DIR"/spec-*.md 2>/dev/null | head -n 1 || true)"
      fi
    fi
    if [[ -n "$SPEC_FILE" && -f "$SPEC_FILE" && -f "$COMPILER" ]]; then
      log_activity "Compiling PRD from spec: $SPEC_FILE -> $PRD_FILE"
      if [[ "$STRICT" == "true" ]]; then
        python3 "$COMPILER" --spec "$SPEC_FILE" --out "$PRD_FILE" --strict >>"$LOG_DIR/compiler.log" 2>&1 || {
          log_error "spec_to_prd compiler failed (strict). See $LOG_DIR/compiler.log";
          agent_fail_streak=$((agent_fail_streak+1));
          if [[ "$agent_fail_streak" -ge "$AGENT_FAIL_LIMIT" ]]; then log_error "Agent/compile fail limit reached ($AGENT_FAIL_LIMIT). Stopping."; exit 2; fi;
        }
      else
        python3 "$COMPILER" --spec "$SPEC_FILE" --out "$PRD_FILE" >>"$LOG_DIR/compiler.log" 2>&1 || true
      fi
    else
      log_activity "PRD compile skipped (missing spec/compiler). SPEC_FILE=$SPEC_FILE COMPILER=$COMPILER"
    fi
  fi

  local_mode="checkbox"
  if [[ -f "$PRD_FILE" && "$HAS_JQ" == "true" ]]; then
    key="$(prd_tasks_key "$PRD_FILE" 2>/dev/null || true)"
    if [[ -n "${key:-}" ]]; then
      local_mode="prd"
    fi
  fi

  prompt_file="$STATE_DIR/prompt.iter-$(printf "%04d" "$iter").md"
  last_msg_file="$STATE_DIR/last_message.iter-$(printf "%04d" "$iter").md"
  last_result_file="$STATE_DIR/last_result.iter-$(printf "%04d" "$iter").json"
  stdout_log="$LOG_DIR/iter-$(printf "%04d" "$iter").stdout.log"

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

  # Extra instruction files if present (kept optional; do not create unless you want them)
  instruction_files=()
  [[ -f "AGENTS.md" ]] && instruction_files+=("AGENTS.md")
  [[ -f "CLAUDE.md" ]] && instruction_files+=("CLAUDE.md")
  [[ -f ".github/copilot-instructions.md" ]] && instruction_files+=(".github/copilot-instructions.md")

  # Build prompt
  cat > "$prompt_file" <<EOF
# Ralph Loop — Codex CLI

Iteration: $iter
Workspace: $(pwd)

## Read these files first (anchors + rails)
1) $PIN_FILE
2) $PLAN_FILE
3) $GUARDRAILS_FILE
4) $PROGRESS_FILE
EOF

  if [[ "${#instruction_files[@]}" -gt 0 ]]; then
    echo "" >>"$prompt_file"
    echo "## Also read (repo instructions)" >>"$prompt_file"
    for f in "${instruction_files[@]}"; do
      echo "- $f" >>"$prompt_file"
    done
  fi

  if [[ "$local_mode" == "checkbox" ]]; then
    echo "" >>"$prompt_file"
    echo "## Task file" >>"$prompt_file"
    echo "- $TASK_FILE" >>"$prompt_file"
  else
    echo "" >>"$prompt_file"
    echo "## PRD file" >>"$prompt_file"
    echo "- $PRD_FILE" >>"$prompt_file"
  fi

  cat >> "$prompt_file" <<EOF

## Operating rules
- Keep context minimal: use targeted search (ripgrep) to find relevant files; avoid reading huge files end-to-end.
- Work on ONE objective only (single checkbox OR the single PRD story provided).
- Prefer linkage over invention: before changing code, cite the relevant spec section and file(s) you will edit.
- Follow existing conventions in the repo (style, linting, tests, i18n, etc).
- Add/adjust tests where appropriate; run checks.
- Keep changes small and incremental; do not do broad refactors unless required by the pin/spec.
- If something fails repeatedly, add a short reusable "Sign" to guardrails.md.

EOF

  if [[ -f "$PROMPT_ADDENDUM_FILE" ]]; then
    echo "## Prompt addendum (project-specific)" >> "$prompt_file"
    cat "$PROMPT_ADDENDUM_FILE" >> "$prompt_file"
    echo "" >> "$prompt_file"
  fi

  echo "## Current objective" >> "$prompt_file"
  echo "$objective_block" >> "$prompt_file"
  echo "" >> "$prompt_file"

  if [[ "$USE_STRUCTURED" == "true" ]]; then
    cat >> "$prompt_file" <<EOF
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
    cat >> "$prompt_file" <<'EOF'
## Signals (print exactly one at the end)
- If you believe the objective is done and checks are green: <ralph>DONE</ralph>
- If you are blocked after 2 serious attempts: <ralph>GUTTER</ralph>
EOF
  fi

  # Run codex exec
  codex_args=(exec --cd "$WORKSPACE" --model "$MODEL" --sandbox "$SANDBOX" --ask-for-approval "$ASK_APPROVAL" --color never --output-last-message "$last_msg_file")

  if [[ "$ENABLE_SEARCH" == "true" ]]; then
    codex_args+=(--search true)
  else
    codex_args+=(--search false)
  fi

  if [[ "$USE_OUTPUT_SCHEMA" == "true" ]]; then
    codex_args+=(--output-schema "$ITERATION_SCHEMA_FILE")
  fi

  log_activity "Iteration $iter codex exec start (mode=$local_mode)"
  set +e
  codex "${codex_args[@]}" - < "$prompt_file" 2>&1 | tee "$stdout_log"
  codex_exit="${PIPESTATUS[0]}"
  set -e
  log_activity "Iteration $iter codex exec exit=$codex_exit"

  if [[ $codex_exit -ne 0 ]]; then
    agent_fail_streak=$((agent_fail_streak+1))
    log_error "Iteration $iter codex exec failed (streak=$agent_fail_streak). See $stdout_log"
    if [[ $agent_fail_streak -ge $AGENT_FAILURE_STREAK_LIMIT ]]; then
      log_error "Agent failure streak reached limit ($AGENT_FAILURE_STREAK_LIMIT). Stopping."
      break
    fi
  else
    agent_fail_streak=0
  fi

  # Determine status + summary
  status="CONTINUE"
  summary="(no summary)"

  if [[ -f "$last_msg_file" ]]; then
    if [[ "$USE_STRUCTURED" == "true" && "$HAS_JQ" == "true" ]]; then
      if jq -e . "$last_msg_file" >/dev/null 2>&1; then
        cp "$last_msg_file" "$last_result_file" 2>/dev/null || true
        status="$(jq -r '.status // "CONTINUE"' "$last_msg_file" 2>/dev/null || echo "CONTINUE")"
        summary="$(jq -r '.summary // "(no summary)"' "$last_msg_file" 2>/dev/null || echo "(no summary)")"
      else
        # Fallback to tags
        if grep -q "<ralph>GUTTER</ralph>" "$last_msg_file"; then status="GUTTER"; fi
        if grep -q "<ralph>DONE</ralph>" "$last_msg_file"; then status="DONE"; fi
        summary="$(head -n 1 "$last_msg_file" | tr -d '\r' | cut -c1-200)"
      fi
    else
      if grep -q "<ralph>GUTTER</ralph>" "$last_msg_file"; then status="GUTTER"; fi
      if grep -q "<ralph>DONE</ralph>" "$last_msg_file"; then status="DONE"; fi
      summary="$(head -n 1 "$last_msg_file" | tr -d '\r' | cut -c1-200)"
    fi
  fi

  if [[ "$status" == "GUTTER" ]]; then
    log_error "Iteration $iter signalled GUTTER. Stopping loop."
    append_progress_note "$iter" "$local_mode" "$status" "$story_id" "false" "false" "$summary"
    break
  fi

  # Run checks (optional)
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
      log_error "Iteration $iter checks FAIL (streak=$check_fail_streak) (see $LOG_DIR/iter-$(printf "%04d" "$iter").checks.log)"
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

  # PRD pass marking (only if DONE + checks_ok)
  if [[ "$local_mode" == "prd" && -f "$last_msg_file" && "$status" == "DONE" ]]; then
    if [[ "$checks_ran" == "false" || "$checks_ok" == "true" ]]; then
      prd_mark_passes_true "$PRD_FILE" "$prd_key" "$prd_idx"
      log_activity "Marked story passes=true (id=$story_id, idx=$prd_idx)"
    else
      log_error "Agent said DONE but checks failed; not marking passes=true (id=$story_id)"
    fi
  fi

  # Commit (based on COMMIT_MODE)
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

  # Completion check (checkbox mode)
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
