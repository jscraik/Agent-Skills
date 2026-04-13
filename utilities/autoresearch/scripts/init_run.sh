#!/usr/bin/env bash
set -euo pipefail

# usage prints the help message showing the expected CLI format and options: required --tag, required --targets and optional --out.
usage() {
  cat <<'EOF'
Usage:
  bash utilities/autoresearch/scripts/init_run.sh --tag <run-tag> --targets "<path1,path2,...>" [--out <artifacts-root>]

Options:
  --tag       Required run tag (lowercase letters, digits, hyphens)
  --targets   Required comma-separated target paths
  --out       Optional output root under artifacts/autoresearch (default: artifacts/autoresearch)
EOF
}

tag=""
targets_raw=""
out_root="artifacts/autoresearch"
repo_root="$(git rev-parse --show-toplevel)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      tag="${2:-}"
      shift 2
      ;;
    --targets)
      targets_raw="${2:-}"
      shift 2
      ;;
    --out)
      out_root="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$tag" || -z "$targets_raw" ]]; then
  echo "--tag and --targets are required." >&2
  usage >&2
  exit 2
fi

if [[ ! "$tag" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "Invalid tag '$tag'. Use lowercase letters, digits, and hyphens." >&2
  exit 2
fi

normalized_out="$(
python3 - "$repo_root" "$out_root" <<'PY'
from pathlib import Path
import sys

repo_root = Path(sys.argv[1]).resolve()
raw_out = sys.argv[2].strip()

if not raw_out:
    raise SystemExit("Output root cannot be empty.")
if raw_out.startswith("/"):
    raise SystemExit("Output root must be repo-relative, not absolute.")

out_path = (repo_root / raw_out).resolve()
try:
    rel = out_path.relative_to(repo_root)
except ValueError as exc:
    raise SystemExit("Output root resolves outside repo root.") from exc

allowed_root = (repo_root / "artifacts" / "autoresearch").resolve()
if out_path != allowed_root and allowed_root not in out_path.parents:
    raise SystemExit("Output root must stay under artifacts/autoresearch.")

print(rel.as_posix())
PY
)" || {
  echo "$normalized_out" >&2
  exit 2
}

timestamp="$(date +%Y%m%d-%H%M%S)"
run_dir="${normalized_out}/${tag}-${timestamp}"
run_dir_abs="${repo_root}/${run_dir}"
mkdir -p "$run_dir_abs"

results_path="${run_dir_abs}/results.tsv"
targets_path="${run_dir_abs}/targets.txt"
journal_path="${run_dir_abs}/journal.md"

printf "iteration\ttarget\tdecision\tscore\tstatus\tchange_summary\tvalidation_evidence\n" > "$results_path"

IFS=',' read -r -a raw_targets <<<"$targets_raw"
if [[ ${#raw_targets[@]} -eq 0 ]]; then
  echo "No targets provided." >&2
  exit 2
fi

declare -A seen_targets=()
: > "$targets_path"

for target in "${raw_targets[@]}"; do
  trimmed="$(echo "$target" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
  [[ -n "$trimmed" ]] || continue

  normalized_target="$(
  python3 - "$repo_root" "$trimmed" <<'PY'
from pathlib import Path
import sys

repo_root = Path(sys.argv[1]).resolve()
raw_target = sys.argv[2].strip()

if raw_target.startswith("/"):
    raise SystemExit("Target paths must be repo-relative, not absolute.")

resolved = (repo_root / raw_target).resolve()
try:
    rel = resolved.relative_to(repo_root)
except ValueError as exc:
    raise SystemExit(f"Target '{raw_target}' resolves outside repo root.") from exc

rel_posix = rel.as_posix()
if rel_posix.startswith("plugins/cache/"):
    raise SystemExit(f"Target '{raw_target}' is under plugins/cache and is not editable.")
if not resolved.exists():
    raise SystemExit(f"Target '{raw_target}' does not exist.")

print(rel_posix)
PY
  )" || {
    echo "$normalized_target" >&2
    exit 2
  }

  if [[ -z "${seen_targets[$normalized_target]:-}" ]]; then
    printf '%s\n' "$normalized_target" >> "$targets_path"
    seen_targets["$normalized_target"]=1
  fi
done

if [[ ! -s "$targets_path" ]]; then
  echo "No valid targets were parsed from --targets." >&2
  exit 2
fi

cat > "$journal_path" <<EOF
# Autoresearch Journal: ${tag}

- created_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- run_dir: ${run_dir_abs}

## Baseline

- [ ] Record baseline command outcomes for each target

## Iterations

### Iteration 1
- hypothesis:
- change:
- validation:
- decision:
EOF

echo "$run_dir_abs"
