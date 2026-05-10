#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT_DIR="${ROOT_DIR}/.harness/session-evidence/jsc-246-fresh-agent-golden-path"

run_step() {
  local name="$1"
  shift
  local stdout_path="${OUT_DIR}/${name}.stdout.json"
  local stderr_path="${OUT_DIR}/${name}.stderr.txt"
  local exit_path="${OUT_DIR}/${name}.exit"

  (
    cd "${ROOT_DIR}" &&
      "$@"
  ) >"${stdout_path}" 2>"${stderr_path}"
  local exit_code=$?
  printf '%s\n' "${exit_code}" >"${exit_path}"
  printf '%s %s\n' "${name}" "${exit_code}"
  return "${exit_code}"
}

run_step "01-repo-doctor" ./bin/ask repo doctor --json --robot
run_step "02-repo-surface" ./bin/ask repo surface --json --robot
jq '{
  status,
  trace_id,
  metadata,
  data: {
    strict: .data.strict,
    repo_surface: {
      schema_version: .data.repo_surface.schema_version,
      status: .data.repo_surface.status,
      summary: .data.repo_surface.summary,
      metadata: .data.repo_surface.metadata
    }
  },
  telemetry,
  errors
}' "${OUT_DIR}/02-repo-surface.stdout.json" > "${OUT_DIR}/02-repo-surface.stdout.summary.json"
mv "${OUT_DIR}/02-repo-surface.stdout.summary.json" "${OUT_DIR}/02-repo-surface.stdout.json"
run_step "03-skills-improve-pr-review" ./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot
run_step "04-skills-improve-linear-spec" ./bin/ask skills improve "write a Linear-backed HE spec" --json --robot
run_step "05-skills-improve-heartbeat" ./bin/ask skills improve "monitor a long-running HE work phase" --json --robot
run_step "06-skills-improve-code-review" ./bin/ask skills improve "review this implementation against the spec" --json --robot
run_step "07-skills-improve-fix-blockers" ./bin/ask skills improve "fix validation blockers after review" --json --robot
run_step "08-skills-explain-he-spec" ./bin/ask skills explain he-spec --json --robot
run_step "09-skills-proof-he-spec" ./bin/ask skills proof he-spec --json --robot
run_step "10-skills-prove-he-spec" ./bin/ask skills prove he-spec --json --robot
run_step "11-repo-closeout-changed" ./bin/ask repo closeout --changed --json --robot
