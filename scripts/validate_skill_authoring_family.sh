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

# ---------------------------------------------------------------------------
# Release-readiness mode validation
# ---------------------------------------------------------------------------
# SKILL_FAMILY_RELEASE_READY=1 enforces:
#   - SKILL_FAMILY_LIVE_EVALS=1 and SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 must be set
#   - Evidence artifacts are captured with branch + commit SHA metadata
#   - An evidence index is written to SKILL_FAMILY_EVIDENCE_DIR (default: artifacts/validation/family-gate)
#   - Freshness constraint: evidence is produced from the current run; stale pre-existing artifacts are not accepted
#   - Degraded-mode handling: runner failures block closeout; retry-limited reruns are documented in evidence index
# ---------------------------------------------------------------------------
release_ready="${SKILL_FAMILY_RELEASE_READY:-0}"
if [[ "$release_ready" == "1" ]]; then
  if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" != "1" ]] || [[ "${SKILL_FAMILY_LIVE_EVALS_TRUSTED:-0}" != "1" ]]; then
    echo "[family-gate] ERROR: SKILL_FAMILY_RELEASE_READY=1 requires both:"
    echo "[family-gate]   SKILL_FAMILY_LIVE_EVALS=1"
    echo "[family-gate]   SKILL_FAMILY_LIVE_EVALS_TRUSTED=1"
    echo "[family-gate] These must be set only for trusted branches and CI jobs with authenticated runners."
    echo "[family-gate] Release-grade readiness claims require trusted live execution proof, not structural listing alone."
    exit 1
  fi
fi

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

# ---------------------------------------------------------------------------
# Codex profile for live eval runs
# ---------------------------------------------------------------------------
# Set SKILL_FAMILY_CODEX_PROFILE to pass --profile <name> to run_skill_evals.py.
# Example: SKILL_FAMILY_CODEX_PROFILE=fast uses the [profiles.fast] config (gpt-5.3-codex-spark).
# Leave unset to use the default Codex profile from config.toml.
codex_profile_args=()
if [[ -n "${SKILL_FAMILY_CODEX_PROFILE:-}" ]]; then
  codex_profile_args=(--profile "${SKILL_FAMILY_CODEX_PROFILE}")
fi

# ---------------------------------------------------------------------------
# Release-readiness evidence setup
# ---------------------------------------------------------------------------
evidence_dir="${SKILL_FAMILY_EVIDENCE_DIR:-artifacts/validation/family-gate}"
run_timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
git_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
git_sha="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
evidence_run_dir=""
if [[ "$release_ready" == "1" ]]; then
  evidence_run_dir="${evidence_dir}/${run_timestamp}"
  mkdir -p "$evidence_run_dir"
  echo "[family-gate] release-ready mode: evidence will be captured at ${evidence_run_dir}"
  echo "[family-gate] branch: ${git_branch} | sha: ${git_sha}"
  if [[ -n "${SKILL_FAMILY_CODEX_PROFILE:-}" ]]; then
    echo "[family-gate] codex profile: ${SKILL_FAMILY_CODEX_PROFILE}"
  fi
fi

echo "[family-gate] using python: $python_bin"

# ---------------------------------------------------------------------------
# P1.2: shellcheck gate — lint all gate/validation shell scripts
# ---------------------------------------------------------------------------
if command -v shellcheck >/dev/null 2>&1; then
  echo "[family-gate] running shellcheck on gate scripts..."
  gate_scripts=()
  while IFS= read -r -d '' f; do
    gate_scripts+=("$f")
  done < <(find scripts/ -maxdepth 1 -name "*.sh" -print0 2>/dev/null)
  if [[ ${#gate_scripts[@]} -gt 0 ]]; then
    if shellcheck --severity=error "${gate_scripts[@]}"; then
      echo "[family-gate] shellcheck passed"
    else
      echo "[family-gate] ERROR: shellcheck found errors in gate scripts — fix before proceeding"
      exit 2
    fi
  fi
else
  echo "[family-gate] WARN: shellcheck not found; skipping shell script lint (install via: brew install shellcheck)"
fi

# ---------------------------------------------------------------------------
# P3.7: ruff lint gate — lint Python validator scripts
# ---------------------------------------------------------------------------
ruff_bin="${RUFF_BIN:-ruff}"
if command -v "$ruff_bin" >/dev/null 2>&1; then
  echo "[family-gate] running ruff on validator scripts..."
  # Lint only the family validator scripts; legacy utility scripts in scripts/
  # are excluded to avoid pre-existing E401 violations in unrelated tooling.
  family_py_scripts=(
    scripts/validate_skill_authoring_family_benchmarks.py
    utilities/skill-builder/scripts/yaml_frontmatter.py
    utilities/skill-builder/scripts/skill_gate.py
    utilities/skill-builder/scripts/analyze_skill.py
    utilities/skill-builder/scripts/upgrade_skill.py
    utilities/skill-builder/scripts/quick_validate.py
    utilities/skill-builder/scripts/run_skill_evals.py
    utilities/skill-builder/scripts/ci_skill_quality_gate.py
    utilities/skill-builder/scripts/openclaw_skill_guard.py
  )
  existing_py_scripts=()
  for f in "${family_py_scripts[@]}"; do
    [[ -f "$f" ]] && existing_py_scripts+=("$f")
  done
  if "$ruff_bin" check \
      --select E,F,W \
      --ignore E501 \
      --quiet \
      "${existing_py_scripts[@]}"; then
    echo "[family-gate] ruff passed"
  else
    echo "[family-gate] ERROR: ruff found issues in validator scripts — fix before proceeding"
    exit 2
  fi
else
  echo "[family-gate] WARN: ruff not found; skipping Python lint (install via: pip install ruff or brew install ruff)"
fi

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

# ---------------------------------------------------------------------------
# P1.x: pytest unit gate — run validator unit tests
# ---------------------------------------------------------------------------
if "$python_bin" -m pytest --version >/dev/null 2>&1; then
  echo "[family-gate] running pytest unit tests..."
  if "$python_bin" -m pytest utilities/skill-builder/scripts/test_skill_gate.py \
      -q --tb=short; then
    echo "[family-gate] pytest passed"
  else
    echo "[family-gate] ERROR: pytest found test failures — fix before proceeding"
    exit 2
  fi
else
  echo "[family-gate] WARN: pytest not found; skipping unit tests (install via: pip install pytest or brew install python)"
fi

# Track per-skill evidence for the release-ready index
# Using parallel indexed arrays for Bash 3.2+ compatibility (avoid associative arrays)
skill_dirs_ordered=()
skill_evidence_paths_ordered=()
skill_outcomes_ordered=()

# Helper: get index of skill_dir in ordered array (or -1 if not found)
_get_skill_index() {
  local target="$1"
  local i
  for i in "${!skill_dirs_ordered[@]}"; do
    if [[ "${skill_dirs_ordered[$i]}" == "$target" ]]; then
      echo "$i"
      return
    fi
  done
  echo "-1"
}

# Helper: set evidence path for skill_dir
_set_evidence_path() {
  local skill="$1"
  local path="$2"
  local idx
  idx=$(_get_skill_index "$skill")
  if [[ "$idx" == "-1" ]]; then
    skill_dirs_ordered+=("$skill")
    skill_evidence_paths_ordered+=("$path")
    skill_outcomes_ordered+=("")
  else
    skill_evidence_paths_ordered[$idx]="$path"
  fi
}

# Helper: set outcome for skill_dir
_set_outcome() {
  local skill="$1"
  local outcome="$2"
  local idx
  idx=$(_get_skill_index "$skill")
  if [[ "$idx" == "-1" ]]; then
    skill_dirs_ordered+=("$skill")
    skill_evidence_paths_ordered+=("")
    skill_outcomes_ordered+=("$outcome")
  else
    skill_outcomes_ordered[$idx]="$outcome"
  fi
}

# Helper: get evidence path for skill_dir (returns empty if not found)
_get_evidence_path() {
  local skill="$1"
  local idx
  idx=$(_get_skill_index "$skill")
  if [[ "$idx" == "-1" ]]; then
    echo ""
  else
    echo "${skill_evidence_paths_ordered[$idx]}"
  fi
}

# Helper: get outcome for skilldir (returns "unknown" if not found)
_get_outcome() {
  local skill="$1"
  local idx
  idx=$(_get_skill_index "$skill")
  if [[ "$idx" == "-1" ]]; then
    echo "unknown"
  else
    echo "${skill_outcomes_ordered[$idx]:-unknown}"
  fi
}

for skill_dir in "${skill_dirs[@]}"; do
  echo
  echo "[family-gate] === $skill_dir ==="

  "$python_bin" utilities/skill-builder/scripts/quick_validate.py "$skill_dir" --mode compat

  assert_security_eval_contract "$skill_dir"

  if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
    skill_slug="${skill_dir//\//-}"
    if [[ "$release_ready" == "1" ]]; then
      skill_evidence_path="${evidence_run_dir}/${skill_slug}"
      _set_evidence_path "$skill_dir" "$skill_evidence_path"
      "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
        --runner codex \
        --eval-mode smoke \
        --reports-dir "$skill_evidence_path" \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}"
      "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
        --runner codex \
        --eval-mode release \
        --reports-dir "$skill_evidence_path" \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}"
      "$python_bin" utilities/skill-builder/scripts/ci_skill_quality_gate.py \
        "$skill_evidence_path" \
        --tier2-mode warn \
        --format text
    else
      "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
        --runner codex \
        --eval-mode smoke \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}"
      "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
        --runner codex \
        --eval-mode release \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}"
    fi
    _set_outcome "$skill_dir" "passed"
  else
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --list-cases \
      --eval-mode smoke
    "$python_bin" utilities/skill-builder/scripts/run_skill_evals.py "$skill_dir" \
      --list-cases \
      --eval-mode release
    _set_outcome "$skill_dir" "structural-only"
  fi

  "$python_bin" utilities/skill-builder/scripts/openclaw_skill_guard.py "$skill_dir" \
    --mode both \
    --format text

  "$python_bin" utilities/skill-builder/scripts/analyze_skill.py "$skill_dir" \
    --min-pass 60 \
    --no-emoji

  "$python_bin" utilities/skill-builder/scripts/upgrade_skill.py "$skill_dir" \
    --format text

done

# ---------------------------------------------------------------------------
# Write evidence index for release-ready runs
# ---------------------------------------------------------------------------
if [[ "$release_ready" == "1" ]] && [[ -n "$evidence_run_dir" ]]; then
  index_path="${evidence_run_dir}/evidence-index.json"

  # Build skills JSON array
  skills_json="["
  first=1
  for skill_dir in "${skill_dirs[@]}"; do
    [[ "$first" == "0" ]] && skills_json+=","
    first=0
    outcome=$(_get_outcome "$skill_dir")
    evpath=$(_get_evidence_path "$skill_dir")
    skills_json+="{\"skill\":\"${skill_dir}\",\"outcome\":\"${outcome}\",\"evidence_path\":\"${evpath}\"}"
  done
  skills_json+="]"

  codex_profile_label="${SKILL_FAMILY_CODEX_PROFILE:-default}"

  cat >"$index_path" <<EOF
{
  "schema_version": 1,
  "generated_at": "${run_timestamp}",
  "branch": "${git_branch}",
  "commit_sha": "${git_sha}",
  "freshness_window_days": 7,
  "mode": "release-ready",
  "codex_profile": "${codex_profile_label}",
  "evidence_dir": "${evidence_run_dir}",
  "skill_coverage": ${skills_json},
  "degraded_mode_policy": "runner failures block closeout; retry-limited reruns are required before marking release-ready; one successful trusted rerun per skill is the minimum evidence standard",
  "note": "This index satisfies the P1 trusted live eval release gate. Stale artifacts older than freshness_window_days or from non-descendant commits must be rejected at closeout time."
}
EOF
  echo "[family-gate] evidence index written: ${index_path}"
  echo "[family-gate] lineage: branch=${git_branch} sha=${git_sha}"
fi

echo
if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
  if [[ "$release_ready" == "1" ]]; then
    echo "[family-gate] pass (release-ready): all authoring-family skills met trusted live eval/security benchmarks"
    echo "[family-gate] evidence artifacts: ${evidence_run_dir}"
  else
    echo "[family-gate] pass: all authoring-family skills met equivalent eval/security benchmarks"
  fi
else
  echo "[family-gate] pass: all authoring-family skills met structural contract/security checks"
fi
