#!/usr/bin/env bash
set -euo pipefail

changed_files=()
changed_files_mode=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --changed-files)
      changed_files_mode=1
      shift
      while [[ $# -gt 0 ]]; do
        if [[ "$1" == --* ]]; then
          break
        fi
        changed_files+=("${1#./}")
        shift
      done
      continue
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh [--changed-files <file>...]

  --changed-files
      Optional repo-relative file list used to scope expensive unit-test selections.
EOF
      exit 0
      ;;
    *)
      echo "[family-gate] ERROR: unknown argument: $1"
      exit 2
      ;;
  esac
  shift
done

# changed_files_match returns success when any provided changed file matches the supplied glob.
changed_files_match() {
  local pattern="$1"
  local changed_file=""
  for changed_file in "${changed_files[@]}"; do
    # shellcheck disable=SC2053
    if [[ "$changed_file" == $pattern ]]; then
      return 0
    fi
  done
  return 1
}

# Run repo preflight before any path-sensitive operations
preflight_mode="${SKILL_FAMILY_LOCAL_MEMORY_MODE:-optional}"
if [[ "$preflight_mode" != "required" && "$preflight_mode" != "optional" ]]; then
  echo "[family-gate] ERROR: SKILL_FAMILY_LOCAL_MEMORY_MODE must be 'required' or 'optional' (got '$preflight_mode')"
  exit 1
fi

# Keep preflight path checks lightweight for this family gate. The script only needs
# the scripts tree at this stage; broader repo checks run elsewhere in validate_all.
_preflight_paths="scripts"
if [[ -f "scripts/codex-preflight.sh" ]]; then
  bash scripts/codex-preflight.sh --stack auto --mode "$preflight_mode" --bins "git,bash,sed,jq,curl,python3" --paths "$_preflight_paths"
elif [[ -f "$(dirname "${BASH_SOURCE[0]}")/codex-preflight.sh" ]]; then
  bash "$(dirname "${BASH_SOURCE[0]}")/codex-preflight.sh" --stack auto --mode "$preflight_mode" --bins "git,bash,sed,jq,curl,python3" --paths "$_preflight_paths"
else
  echo "WARNING: codex-preflight.sh not found, skipping preflight"
fi

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir/../.." rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd -P "$script_dir/../.." && pwd -P)"
fi
cd "$repo_root"

python_cmd=(python3)
python_cmd_display="python3"
pyyaml_venv_python="$HOME/.venvs/pyyaml/bin/python"

use_pyyaml_venv_python() {
  [[ -x "$pyyaml_venv_python" ]] || return 1
  "$pyyaml_venv_python" -c "import yaml, jsonschema" >/dev/null 2>&1 || return 1
  python_cmd=("$pyyaml_venv_python")
  python_cmd_display="$pyyaml_venv_python"
  return 0
}

if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_cmd=("$PYTHON_BIN")
  python_cmd_display="$PYTHON_BIN"
elif command -v mise >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
  if mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python -c "import yaml, jsonschema" >/dev/null 2>&1; then
    python_cmd=(mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python)
    python_cmd_display="mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python"
  elif uv run --python 3.12 --with pyyaml --with jsonschema python -c "import yaml, jsonschema" >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 --with pyyaml --with jsonschema python)
    python_cmd_display="uv run --python 3.12 --with pyyaml --with jsonschema python"
    echo "[family-gate] WARN: Python launcher fallback engaged (mise probe failed); using uv directly"
  elif use_pyyaml_venv_python; then
    echo "[family-gate] WARN: Python launcher probes failed; using PyYAML venv fallback"
  else
    echo "[family-gate] WARN: Python launcher probes failed; using python3 fallback"
  fi
elif command -v uv >/dev/null 2>&1; then
  if uv run --python 3.12 --with pyyaml --with jsonschema python -c "import yaml, jsonschema" >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 --with pyyaml --with jsonschema python)
    python_cmd_display="uv run --python 3.12 --with pyyaml --with jsonschema python"
  elif use_pyyaml_venv_python; then
    echo "[family-gate] WARN: uv Python launcher probe failed; using PyYAML venv fallback"
  else
    echo "[family-gate] WARN: uv Python launcher probe failed; using python3 fallback"
  fi
elif use_pyyaml_venv_python; then
  :
else
  python_cmd=(python3)
  python_cmd_display="python3"
fi

preserved_context_dir="Plugins/harness-engineering/fixtures/preserved-context"
legacy_context_alias="Plugins/harness-engineering/fixtures/skill-archive"
echo "[family-gate] validating Harness Engineering preserved-context alias"
if [[ ! -d "$preserved_context_dir" ]]; then
  echo "[family-gate] ERROR: missing canonical preserved context dir: $preserved_context_dir" >&2
  exit 1
fi
if [[ ! -L "$legacy_context_alias" ]]; then
  echo "[family-gate] ERROR: legacy context alias must be a symlink: $legacy_context_alias" >&2
  exit 1
fi
"${python_cmd[@]}" - "$preserved_context_dir" "$legacy_context_alias" <<'PY'
from pathlib import Path
import sys

canonical = Path(sys.argv[1])
alias = Path(sys.argv[2])
if canonical.resolve() != alias.resolve():
    raise SystemExit(
        f"[family-gate] ERROR: {alias} resolves to {alias.resolve()}, expected {canonical.resolve()}"
    )
PY
echo "[family-gate] Harness Engineering preserved-context alias passed"

echo "[family-gate] validating Harness Engineering subagent routing"
he_subagent_manifest="Plugins/harness-engineering/fixtures/subagent-routing-manifest.fixture.json"
"${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_he_subagent_routing.py \
  --manifest "$he_subagent_manifest"
echo "[family-gate] Harness Engineering subagent routing passed"

skill_dirs=(
  "Plugins/skill-factory/skills/code_quality_review/skill-builder"
  "Plugins/skill-factory/skills/scaffolding_templates/skill-creator"
  "Plugins/skill-factory/skills/infrastructure_ops/skill-installer"
  "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator"
)
skill_builder_dir_candidates=(
  "Plugins/skill-factory/skills/code_quality_review/skill-builder"
  "Plugins/skill-factory/skills/skill-builder"
  "plugins/skill-factory/skills/code_quality_review/skill-builder"
  "plugins/skill-factory/skills/skill-builder"
)
skill_builder_scripts_dir=""
for candidate in "${skill_builder_dir_candidates[@]}"; do
  if [[ -f "${candidate}/scripts/skill_gate.py" ]]; then
    skill_builder_scripts_dir="${candidate}/scripts"
    break
  fi
done

if [[ ! -d "$skill_builder_scripts_dir" ]]; then
  echo "[family-gate] ERROR: missing skill-builder scripts directory: $skill_builder_scripts_dir"
  exit 1
fi

# run_skill_builder_script runs a skill-builder Python script from the discovered skill_builder_scripts_dir using the selected python_cmd and forwards any additional arguments to that script.
run_skill_builder_script() {
  local script_name="$1"
  shift
  "${python_cmd[@]}" "${skill_builder_scripts_dir}/${script_name}" "$@"
}

he_work_skill="Plugins/harness-engineering/skills/he-work/SKILL.md"
ce_shared_approval_doc="Plugins/harness-engineering/skills/shared/references/approval-flow.md"
ce_shared_approval_ref="../shared/references/approval-flow.md"
ce_shared_approval_repo_ref="repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md"

# ---------------------------------------------------------------------------
# Runner selection — override via SKILL_FAMILY_RUNNER (default: codex)
# ---------------------------------------------------------------------------
runner_name="${SKILL_FAMILY_RUNNER:-codex}"
runner_args=(--runner "$runner_name")

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

  if ! run_skill_builder_script skill_gate.py "$skill_dir" \
    --require-security-evals \
    --pi-high-fail \
    --require-fail-fast \
    --format json >"$report_file"; then
    # skill_gate can return non-zero for findings that this family gate
    # classifies below. Parse JSON so we can print precise blocking evidence.
    :
  fi

  "${python_cmd[@]}" -c '
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
        or code.startswith("SEC_")
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
' "$report_file" "$skill_dir"
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

echo "[family-gate] using python: $python_cmd_display"

echo "[family-gate] validating he-work approval-flow linkage"
if [[ ! -f "$ce_shared_approval_doc" ]]; then
  echo "[family-gate] ERROR: missing shared approval flow document: $ce_shared_approval_doc"
  exit 1
fi

if [[ ! -f "$he_work_skill" ]]; then
  echo "[family-gate] ERROR: missing HE skill doc: $he_work_skill"
  exit 1
fi

if ! grep -Fq "$ce_shared_approval_ref" "$he_work_skill" && ! grep -Fq "$ce_shared_approval_repo_ref" "$he_work_skill"; then
  echo "[family-gate] ERROR: $he_work_skill must reference $ce_shared_approval_ref or $ce_shared_approval_repo_ref"
  exit 1
fi

if grep -Fq "continue without re-asking" "$he_work_skill" || \
   grep -Fq "ask a focused blocker question only when ambiguity would change scope, interface, architecture, or shipping risk" "$he_work_skill"; then
  echo "[family-gate] ERROR: $he_work_skill still contains inline approval-flow text; use shared reference"
  exit 1
fi
echo "[family-gate] he-work approval-flow linkage passed"

echo "[family-gate] validating harness-engineering progressive-disclosure contract"
bash Infrastructure/scripts/validation-and-linting/validate_he_progressive_disclosure.sh
echo "[family-gate] harness-engineering progressive-disclosure contract passed"

echo "[family-gate] validating authoring context-preservation contract"
bash Infrastructure/scripts/validation-and-linting/validate_authoring_context_preservation.sh
echo "[family-gate] authoring context-preservation contract passed"

echo "[family-gate] validating he-improve example spec yaml fixtures"
"${python_cmd[@]}" - <<'PY'
from pathlib import Path
import yaml

paths = [
    Path("Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-improve/references/example-hard-spec.yaml"),
    Path("Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-improve/references/example-judge-spec.yaml"),
    Path("Plugins/harness-engineering/fixtures/budget-archive/2026-04-21/skills/team_automation/he-improve/references/example-hard-spec.yaml"),
    Path("Plugins/harness-engineering/fixtures/budget-archive/2026-04-21/skills/team_automation/he-improve/references/example-judge-spec.yaml"),
]
missing = [str(path) for path in paths if not path.exists()]
if missing:
    raise SystemExit(
        "[family-gate] ERROR: missing he-improve example spec yaml fixtures:\n  - "
        + "\n  - ".join(missing)
    )
for path in paths:
    with path.open("r", encoding="utf-8") as handle:
        yaml.safe_load(handle.read())
print("[family-gate] he-improve example spec yaml fixtures passed")
PY

# ---------------------------------------------------------------------------
# P1.2: shellcheck gate — lint all gate/validation shell scripts
# ---------------------------------------------------------------------------
if command -v shellcheck >/dev/null 2>&1; then
  echo "[family-gate] running shellcheck on gate scripts..."
  gate_scripts=()
  while IFS= read -r -d '' f; do
    gate_scripts+=("$f")
  done < <(
    find scripts/ -maxdepth 1 -name "*.sh" -print0 2>/dev/null
    find Infrastructure/scripts/validation-and-linting -name "*.sh" -print0 2>/dev/null
  )
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
    Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py
    Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py
    "${skill_builder_scripts_dir}/yaml_frontmatter.py"
    "${skill_builder_scripts_dir}/skill_gate.py"
    "${skill_builder_scripts_dir}/analyze_skill.py"
    "${skill_builder_scripts_dir}/upgrade_skill.py"
    "${skill_builder_scripts_dir}/quick_validate.py"
    "${skill_builder_scripts_dir}/run_skill_evals.py"
    "${skill_builder_scripts_dir}/ci_skill_quality_gate.py"
    "${skill_builder_scripts_dir}/openclaw_skill_guard.py"
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
  echo "[family-gate] WARN: ruff not found; skipping Python lint (install via: uv tool install ruff, uv pip install ruff, or brew install ruff)"
fi

echo "[family-gate] validating ${#skill_dirs[@]} skill authoring family members"
if [[ "$changed_files_mode" -eq 1 ]]; then
  echo "[family-gate] changed-files scope active (${#changed_files[@]} file(s))"
fi
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

"${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py

# ---------------------------------------------------------------------------
# P1.x: pytest unit gate — run validator unit tests
# ---------------------------------------------------------------------------
pytest_cmd=()
uv_pytest_env=()
uv_pytest_cache_dir=""

if command -v uv >/dev/null 2>&1; then
  uv_pytest_cache_dir="${SKILL_FAMILY_UV_CACHE_DIR:-${UV_CACHE_DIR:-${TMPDIR:-/tmp}/agent-skills-uv-cache}}"
  mkdir -p "$uv_pytest_cache_dir"
  uv_pytest_env=(env "UV_CACHE_DIR=$uv_pytest_cache_dir")
fi

if "${python_cmd[@]}" -m pytest --version >/dev/null 2>&1; then
  pytest_cmd=("${python_cmd[@]}" -m pytest)
elif [[ ${#uv_pytest_env[@]} -gt 0 ]] && "${uv_pytest_env[@]}" uv run --python 3.12 --with pytest --with pyyaml --with jsonschema python -m pytest --version >/dev/null 2>&1; then
  pytest_cmd=("${uv_pytest_env[@]}" uv run --python 3.12 --with pytest --with pyyaml --with jsonschema python -m pytest)
  echo "[family-gate] using uv ephemeral pytest runner (UV_CACHE_DIR=$uv_pytest_cache_dir)"
elif [[ ${#uv_pytest_env[@]} -gt 0 ]] && "${uv_pytest_env[@]}" uv run --python 3.12 pytest --version >/dev/null 2>&1; then
  pytest_cmd=("${uv_pytest_env[@]}" uv run --python 3.12 pytest)
  echo "[family-gate] using uv project pytest command (UV_CACHE_DIR=$uv_pytest_cache_dir)"
elif [[ ${#uv_pytest_env[@]} -gt 0 ]] && "${uv_pytest_env[@]}" uv run --python 3.12 python -m pytest --version >/dev/null 2>&1; then
  pytest_cmd=("${uv_pytest_env[@]}" uv run --python 3.12 python -m pytest)
  echo "[family-gate] using uv project pytest runner (UV_CACHE_DIR=$uv_pytest_cache_dir)"
fi

run_skill_gate_unittest=1
run_family_benchmark_pytest=1
run_projection_pytest=1
run_plugin_hooks_pytest=1
run_first_principles_gate_pytest=1
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  run_skill_gate_unittest=0
  run_family_benchmark_pytest=0
  run_projection_pytest=0
  run_plugin_hooks_pytest=0
  run_first_principles_gate_pytest=0

  if changed_files_match "Plugins/skill-factory/skills/code_quality_review/skill-builder/*" || \
     changed_files_match "Plugins/skill-factory/skills/scaffolding_templates/skill-creator/*" || \
     changed_files_match "Plugins/skill-factory/skills/infrastructure_ops/skill-installer/*" || \
     changed_files_match "Plugins/plugin-factory/skills/code_quality_review/plugin-builder/*" || \
     changed_files_match "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/*" || \
     changed_files_match "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh" || \
     changed_files_match "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py" || \
     changed_files_match "Infrastructure/scripts/testing/test_validate_skill_authoring_family_benchmarks.py" || \
     changed_files_match "Infrastructure/tests/test_plugin_bundled_hooks_contract.py"; then
    run_skill_gate_unittest=1
    run_family_benchmark_pytest=1
    run_plugin_hooks_pytest=1
  fi

  if changed_files_match "Plugins/skill-factory/skills/*" || \
     changed_files_match "Plugins/plugin-factory/skills/*" || \
     changed_files_match "Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py" || \
     changed_files_match "Infrastructure/scripts/testing/test_validate_first_principles_gate.py" || \
     changed_files_match "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh"; then
    run_first_principles_gate_pytest=1
  fi

  if changed_files_match "Infrastructure/scripts/lifecycle-and-sync/*" || \
     changed_files_match "Infrastructure/scripts/validate_projection_integrity.sh" || \
     changed_files_match "Infrastructure/scripts/testing/test_projection_integrity.py"; then
    run_projection_pytest=1
  fi
fi

selected_pytest_targets=()
if [[ "$run_family_benchmark_pytest" -eq 1 ]]; then
  selected_pytest_targets+=(Infrastructure/scripts/testing/test_validate_skill_authoring_family_benchmarks.py)
fi
if [[ "$run_projection_pytest" -eq 1 ]]; then
  selected_pytest_targets+=(Infrastructure/scripts/testing/test_projection_integrity.py)
fi
if [[ "$run_plugin_hooks_pytest" -eq 1 ]]; then
  selected_pytest_targets+=(Infrastructure/tests/test_plugin_bundled_hooks_contract.py)
fi
if [[ "$run_first_principles_gate_pytest" -eq 1 ]]; then
  selected_pytest_targets+=(Infrastructure/scripts/testing/test_validate_first_principles_gate.py)
fi

first_principles_gate_files=()
if [[ "$changed_files_mode" -eq 1 && ${#changed_files[@]} -gt 0 ]]; then
  for changed_file in "${changed_files[@]}"; do
    if [[ "$changed_file" == Plugins/skill-factory/skills/* ]] || \
       [[ "$changed_file" == Plugins/plugin-factory/skills/* ]]; then
      first_principles_gate_files+=("$changed_file")
    fi
  done
fi

if [[ ${#first_principles_gate_files[@]} -gt 0 ]]; then
  echo "[family-gate] validating first-principles factory gate evidence (warning-first)"
  "${python_cmd[@]}" Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py "${first_principles_gate_files[@]}"
else
  echo "[family-gate] first-principles factory gate validation skipped: no active factory output/readiness paths selected"
fi

if [[ "$run_skill_gate_unittest" -eq 1 ]]; then
  echo "[family-gate] running skill_gate unit-test shim..."
  skill_gate_unittest_path="$(cd "$skill_builder_scripts_dir" && pwd -P)/test_skill_gate.py"
  if [[ ! -f "$skill_gate_unittest_path" ]]; then
    echo "[family-gate] ERROR: missing skill-gate unit-test target"
    exit 2
  fi
  if ! "${python_cmd[@]}" "$skill_gate_unittest_path"; then
    echo "[family-gate] ERROR: skill_gate unit tests failed — fix before proceeding"
    exit 2
  fi
fi

if [[ ${#selected_pytest_targets[@]} -gt 0 ]]; then
  if [[ ${#pytest_cmd[@]} -gt 0 ]]; then
    echo "[family-gate] running pytest unit tests (${#selected_pytest_targets[@]} target(s))..."
    if "${pytest_cmd[@]}" "${selected_pytest_targets[@]}" -q --tb=short; then
      echo "[family-gate] pytest passed"
    else
      echo "[family-gate] ERROR: pytest found test failures — fix before proceeding"
      exit 2
    fi
  else
    if [[ "${SKILL_FAMILY_ALLOW_PYTEST_SKIP:-0}" == "1" ]]; then
      echo "[family-gate] WARN: pytest not found; skipping selected pytest targets due to SKILL_FAMILY_ALLOW_PYTEST_SKIP=1"
    else
      echo "[family-gate] ERROR: pytest not found; selected unit tests are required for this gate"
      echo "[family-gate] install via: uv run --python 3.12 --with pytest ... , uv pip install pytest, or brew install python"
      echo "[family-gate] set SKILL_FAMILY_ALLOW_PYTEST_SKIP=1 only for emergency lanes with explicit approval"
      exit 2
    fi
  fi
else
  echo "[family-gate] pytest scope: no matching changed paths; skipping pytest targets"
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
    skill_evidence_paths_ordered[idx]="$path"
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
    skill_outcomes_ordered[idx]="$outcome"
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

# run_structural_skill_suite runs the structural checks for one skill without live model evals.
run_structural_skill_suite() {
  local skill_dir="$1"
  run_skill_builder_script quick_validate.py "$skill_dir" --mode compat
  assert_security_eval_contract "$skill_dir"
  # One standard listing replaces two mode-specific list passes.
  run_skill_builder_script run_skill_evals.py "$skill_dir" \
    --list-cases \
    --eval-mode standard
  run_skill_builder_script openclaw_skill_guard.py "$skill_dir" \
    --mode both \
    --format text
  run_skill_builder_script analyze_skill.py "$skill_dir" \
    --min-pass 60 \
    --no-emoji
  run_skill_builder_script upgrade_skill.py "$skill_dir" \
    --format text
}

structural_pids=()
structural_skills=()
structural_logs=()
structural_failures=0

flush_oldest_structural_batch() {
  local pid="${structural_pids[0]}"
  local skill="${structural_skills[0]}"
  local log_file="${structural_logs[0]}"

  if wait "$pid"; then
    cat "$log_file"
    _set_outcome "$skill" "structural-only"
  else
    cat "$log_file"
    _set_outcome "$skill" "failed"
    structural_failures=1
    echo "[family-gate] ERROR: structural checks failed for ${skill}"
  fi

  rm -f "$log_file"
  structural_pids=("${structural_pids[@]:1}")
  structural_skills=("${structural_skills[@]:1}")
  structural_logs=("${structural_logs[@]:1}")
}

if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
  for skill_dir in "${skill_dirs[@]}"; do
    echo
    echo "[family-gate] === $skill_dir ==="

    run_skill_builder_script quick_validate.py "$skill_dir" --mode compat
    assert_security_eval_contract "$skill_dir"

    skill_slug="${skill_dir//\//-}"
    skill_eval_failed=0
    if [[ "$release_ready" == "1" ]]; then
      skill_evidence_path="${evidence_run_dir}/${skill_slug}"
      _set_evidence_path "$skill_dir" "$skill_evidence_path"
      run_skill_builder_script run_skill_evals.py "$skill_dir" \
        "${runner_args[@]}" \
        --eval-mode smoke \
        --reports-dir "$skill_evidence_path" \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}" || skill_eval_failed=1
      run_skill_builder_script run_skill_evals.py "$skill_dir" \
        "${runner_args[@]}" \
        --eval-mode release \
        --reports-dir "$skill_evidence_path" \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}" || skill_eval_failed=1
      run_skill_builder_script ci_skill_quality_gate.py \
        "$skill_evidence_path" \
        --tier2-mode warn \
        --format text || skill_eval_failed=1
    else
      run_skill_builder_script run_skill_evals.py "$skill_dir" \
        "${runner_args[@]}" \
        --eval-mode smoke \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}" || skill_eval_failed=1
      run_skill_builder_script run_skill_evals.py "$skill_dir" \
        "${runner_args[@]}" \
        --eval-mode release \
        "${codex_profile_args[@]+"${codex_profile_args[@]}"}" || skill_eval_failed=1
    fi
    if [[ "$skill_eval_failed" == "0" ]]; then
      _set_outcome "$skill_dir" "passed"
    else
      _set_outcome "$skill_dir" "failed"
      echo "[family-gate] WARN: live evals had failures for $skill_dir — recording outcome as failed"
    fi

    run_skill_builder_script openclaw_skill_guard.py "$skill_dir" \
      --mode both \
      --format text
    run_skill_builder_script analyze_skill.py "$skill_dir" \
      --min-pass 60 \
      --no-emoji
    run_skill_builder_script upgrade_skill.py "$skill_dir" \
      --format text
  done
else
  structural_batch_jobs="${SKILL_FAMILY_BATCH_JOBS:-2}"
  if ! [[ "$structural_batch_jobs" =~ ^[0-9]+$ ]] || [[ "$structural_batch_jobs" -lt 1 ]]; then
    structural_batch_jobs=1
  fi
  if [[ "$structural_batch_jobs" -gt 4 ]]; then
    structural_batch_jobs=4
  fi
  echo "[family-gate] structural batch size: ${structural_batch_jobs}"

  for skill_dir in "${skill_dirs[@]}"; do
    echo
    echo "[family-gate] === $skill_dir ==="
    skill_slug="${skill_dir//\//-}"
    skill_log="$(mktemp "${TMPDIR:-/tmp}/skill-family-${skill_slug}.log.XXXXXX")"

    (
      run_structural_skill_suite "$skill_dir"
    ) >"$skill_log" 2>&1 &

    structural_pids+=("$!")
    structural_skills+=("$skill_dir")
    structural_logs+=("$skill_log")

    if [[ ${#structural_pids[@]} -ge "$structural_batch_jobs" ]]; then
      flush_oldest_structural_batch
    fi
  done

  while [[ ${#structural_pids[@]} -gt 0 ]]; do
    flush_oldest_structural_batch
  done

  if [[ "$structural_failures" -ne 0 ]]; then
    exit 2
  fi
fi

# ---------------------------------------------------------------------------
# Write evidence index for release-ready runs
# ---------------------------------------------------------------------------
if [[ "$release_ready" == "1" ]] && [[ -n "$evidence_run_dir" ]]; then
  index_path="${evidence_run_dir}/evidence-index.json"

  runner_label="${SKILL_FAMILY_RUNNER:-codex}"
  codex_profile_label="${SKILL_FAMILY_CODEX_PROFILE:-default}"

  # Build skills JSON array safely with jq
  skills_json_array="[]"
  for skill_dir in "${skill_dirs[@]}"; do
    outcome=$(_get_outcome "$skill_dir")
    evpath=$(_get_evidence_path "$skill_dir")
    skills_json_array=$(echo "$skills_json_array" | jq \
      --arg skill "$skill_dir" \
      --arg outcome "$outcome" \
      --arg evpath "$evpath" \
      '. + [{skill: $skill, outcome: $outcome, evidence_path: $evpath}]')
  done

  # Write entire index with jq to safely escape all values
  jq -n \
    --arg ts "$run_timestamp" \
    --arg branch "$git_branch" \
    --arg sha "$git_sha" \
    --arg runner "$runner_label" \
    --arg profile "$codex_profile_label" \
    --arg dir "$evidence_run_dir" \
    --argjson skills "$skills_json_array" \
    '{
      schema_version: 1,
      generated_at: $ts,
      branch: $branch,
      commit_sha: $sha,
      runner: $runner,
      freshness_window_days: 7,
      mode: "release-ready",
      codex_profile: $profile,
      evidence_dir: $dir,
      skill_coverage: $skills,
      degraded_mode_policy: "runner failures block closeout; retry-limited reruns are required before marking release-ready; one successful trusted rerun per skill is the minimum evidence standard",
      note: "This index satisfies the P1 trusted live eval release gate. Stale artifacts older than freshness_window_days or from non-descendant commits must be rejected at closeout time."
    }' > "$index_path"
  echo "[family-gate] evidence index written: ${index_path}"
  echo "[family-gate] lineage: branch=${git_branch} sha=${git_sha}"
fi

# ---------------------------------------------------------------------------
# Quarterly review date freshness check
# ---------------------------------------------------------------------------
# Parse the criteria.md file and check if quarterly review is overdue
if [[ -f ".harness/quality/criteria.md" ]]; then
  # Look for pattern like "quarterly (90 days from last review)" or similar
  # Extract any explicit dates and check if they're in the past
  if grep -qE 'next due.*20[0-9]{2}-[0-9]{2}-[0-9]{2}' .harness/quality/criteria.md 2>/dev/null; then
    next_due=$(grep -oE 'next due.*20[0-9]{2}-[0-9]{2}-[0-9]{2}' .harness/quality/criteria.md | grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' | head -1)
    if [[ -n "$next_due" ]]; then
      # Compare date (works on macOS and Linux)
      next_due_epoch=$(date -j -f "%Y-%m-%d" "$next_due" +%s 2>/dev/null || date -d "$next_due" +%s 2>/dev/null || echo "")
      today_epoch=$(date +%s)
      if [[ -n "$next_due_epoch" && "$today_epoch" -gt "$next_due_epoch" ]]; then
        echo "[family-gate] WARN: Quarterly review date ($next_due) is overdue"
        echo "[family-gate]        Update .harness/quality/criteria.md with new review date"
        # Non-blocking: warn only, don't exit 1
      fi
    fi
  fi
fi

echo
# Compute overall outcome from per-skill results
any_failed=0
for skill_dir in "${skill_dirs[@]}"; do
  outcome=$(_get_outcome "$skill_dir")
  if [[ "$outcome" == "failed" ]]; then
    any_failed=1
  fi
done

if [[ "${SKILL_FAMILY_LIVE_EVALS:-0}" == "1" ]]; then
  if [[ "$any_failed" == "0" ]]; then
    if [[ "$release_ready" == "1" ]]; then
      echo "[family-gate] pass (release-ready): all authoring-family skills met trusted live eval/security benchmarks"
      echo "[family-gate] evidence artifacts: ${evidence_run_dir}"
    else
      echo "[family-gate] pass: all authoring-family skills met equivalent eval/security benchmarks"
    fi
  else
    echo "[family-gate] FAIL: one or more skills had live eval failures"
    echo "[family-gate] evidence artifacts: ${evidence_run_dir}"
    echo "[family-gate] review evidence-index.json for per-skill outcomes"
    exit 2
  fi
else
  echo "[family-gate] pass: all authoring-family skills met structural contract/security checks"
fi
