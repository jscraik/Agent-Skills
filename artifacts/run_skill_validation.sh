#!/usr/bin/env bash
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_list="artifacts/skill-validation-skill_files.txt"
results_tsv="artifacts/skill-validation-results.tsv"
log_file="artifacts/skill-validation-log.txt"

rm -f "$results_tsv" "$log_file"
touch "$results_tsv" "$log_file"

echo -e "skill\tquick_validate\tskill_gate\topenclaw_guard" > "$results_tsv"

total="$(wc -l < "$skill_list" | tr -d " ")"
i=0

while IFS= read -r skill_md; do
  i=$((i + 1))
  skill_dir="$(dirname "$skill_md")"
  echo "[$i/$total] $skill_dir" | tee -a "$log_file"

  qv="PASS"
  sg="PASS"
  oc="PASS"

  ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py "$skill_dir" >> "$log_file" 2>&1 || qv="FAIL"
  ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py "$skill_dir" >> "$log_file" 2>&1 || sg="FAIL"
  ~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/openclaw_skill_guard.py "$skill_dir" --mode both >> "$log_file" 2>&1 || oc="FAIL"

  echo -e "${skill_dir}\t${qv}\t${sg}\t${oc}" >> "$results_tsv"
done < "$skill_list"

echo "DONE" | tee -a "$log_file"

