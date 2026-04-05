#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

python_bin="${PYTHON_BIN:-$HOME/.venvs/pyyaml/bin/python}"
if [[ ! -x "$python_bin" ]]; then
  python_bin="python3"
fi

skill_dirs=(
  "utilities/skill-builder"
  "skills-system/skill-creator"
  "skills-system/skill-installer"
  "skills-system/plugin-creator"
)

assert_security_eval_contract() {
  local skill_dir="$1"
  local report_file
  report_file="$(mktemp "${TMPDIR:-/tmp}/skill-authoring-family-gate.XXXXXX")"
  trap 'rm -f "$report_file"' RETURN

  if ! "$python_bin" utilities/skill-builder/scripts/skill_gate.py "$skill_dir" \
    --require-security-evals \
    --pi-high-fail \
    --require-fail-fast \
    --format json >"$report_file"; then
    # skill_gate can return non-zero for non-contract style findings.
    # We still parse JSON and fail only on contract/eval/security benchmark findings.
    :
  fi

  "$python_bin" - "$report_file" "$skill_dir" <<'PY'
import json
import sys

report_path = sys.argv[1]
skill_dir = sys.argv[2]

try:
    with open(report_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
except Exception as exc:  # noqa: BLE001
    print(f"[family-gate] skill_gate did not emit valid JSON for {skill_dir}: {exc}")
    sys.exit(1)

findings = payload.get("findings") or []
blocking = []

for finding in findings:
    level = str(finding.get("level", "")).upper()
    code = str(finding.get("code", ""))
    if level == "FAIL" and (
        code.startswith("CONTRACT_")
        or code.startswith("EVALS_")
        or code.startswith("SEC_EVALS_")
        or code.startswith("PI_")
        or code.startswith("SCRIPT_SECURITY_")
        or code == "WF_FAIL_FAST_REQUIRED"
    ):
        blocking.append(finding)
    if code == "SEC_EVALS_PARSE":
        blocking.append(finding)

if blocking:
    print(f"[family-gate] contract/eval/security benchmark failures: {skill_dir}")
    for finding in blocking:
        level = str(finding.get("level", "")).upper()
        code = str(finding.get("code", ""))
        message = str(finding.get("message", ""))
        print(f"  - {level} {code}: {message}")
    sys.exit(1)

print(f"[family-gate] contract/eval/security benchmarks passed: {skill_dir}")
PY
  trap - RETURN
}

echo "[family-gate] using python: $python_bin"
echo "[family-gate] validating ${#skill_dirs[@]} skill authoring family members"
if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
  if [[ "${SKILL_FAMILY_LIVE_EVALS_TRUSTED:-0}" != "1" ]]; then
    echo "[family-gate] refusing live eval mode without explicit trusted-lane acknowledgement"
    echo "[family-gate] set SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 only for trusted branches/jobs"
    exit 1
  fi
  echo "[family-gate] live eval mode enabled (trusted lane): smoke + release"
else
  echo "[family-gate] live eval mode disabled: structural eval contract checks only (smoke+release case listings)"
fi

"$python_bin" scripts/validate_skill_authoring_family_benchmarks.py

for skill_dir in "${skill_dirs[@]}"; do
  echo
  echo "[family-gate] === $skill_dir ==="

  "$python_bin" utilities/skill-builder/scripts/quick_validate.py "$skill_dir" --mode compat

  assert_security_eval_contract "$skill_dir"

  if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --runner codex \
      --eval-mode smoke
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --runner codex \
      --eval-mode release
  else
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --list-cases \
      --eval-mode smoke
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --list-cases \
      --eval-mode release
  fi

  "$python_bin" utilities/skill-builder/scripts/openclaw_skill_guard.py "$skill_dir" \
    --mode both \
    --format text

  "$python_bin" utilities/skill-builder/scripts/analyze_skill.py "$skill_dir" \
    --min-pass 60 \
    --no-emoji

done

echo
if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
  echo "[family-gate] pass: all authoring-family skills met equivalent eval/security benchmarks"
else
  echo "[family-gate] pass: all authoring-family skills met structural contract/security checks"
fi
