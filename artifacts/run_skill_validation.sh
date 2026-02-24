#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  run_skill_validation.sh [skill-list-file]

Environment:
  PYTHON_BIN  Python interpreter for validation scripts
TXT
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == --* || "${1:-}" == -?* ]]; then
  echo "ERROR: unknown option: ${1:-}" >&2
  usage >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_list="${1:-artifacts/skill-validation-skill_files.txt}"
results_tsv="artifacts/skill-validation-results.tsv"
log_file="artifacts/skill-validation-log.txt"

if [[ ! -f "$skill_list" ]]; then
  echo "ERROR: skill list not found: $skill_list" >&2
  exit 1
fi

python_bin="${PYTHON_BIN:-$HOME/.venvs/pyyaml/bin/python}"
if [[ ! -x "$python_bin" ]]; then
  python_bin="$(command -v python3 || true)"
fi
if [[ -z "$python_bin" ]]; then
  echo "ERROR: no Python interpreter found (set PYTHON_BIN)." >&2
  exit 1
fi

rm -f "$results_tsv" "$log_file"
touch "$results_tsv" "$log_file"

printf 'skill\tquick_validate\tskill_gate\topenclaw_guard\n' > "$results_tsv"

total="$(wc -l < "$skill_list" | tr -d " ")"
i=0

while IFS= read -r skill_md; do
  i=$((i + 1))
  skill_dir="$(dirname "$skill_md")"
  echo "[$i/$total] $skill_dir" | tee -a "$log_file"

  qv="PASS"
  sg="PASS"
  oc="PASS"

  "$python_bin" utilities/skill-creator/scripts/quick_validate.py "$skill_dir" >> "$log_file" 2>&1 || qv="FAIL"
  "$python_bin" utilities/skill-creator/scripts/skill_gate.py "$skill_dir" >> "$log_file" 2>&1 || sg="FAIL"
  "$python_bin" utilities/skill-creator/scripts/openclaw_skill_guard.py "$skill_dir" --mode both >> "$log_file" 2>&1 || oc="FAIL"

  printf '%s\t%s\t%s\t%s\n' "$skill_dir" "$qv" "$sg" "$oc" >> "$results_tsv"
done < "$skill_list"

echo "DONE" | tee -a "$log_file"
