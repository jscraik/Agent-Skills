#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/spreadsheet_workflows.sh deps-check
  Infrastructure/scripts/spreadsheet_workflows.sh print-install core|charting|render
  Infrastructure/scripts/spreadsheet_workflows.sh paths
USAGE
}

cmd="${1:-}"
if [[ -z "$cmd" ]]; then
  usage
  exit 2
fi
shift || true

check_python_module() {
  local module="$1"
  python3 - <<PY >/dev/null 2>&1
import importlib
import sys
sys.exit(0 if importlib.util.find_spec("${module}") else 1)
PY
}

case "$cmd" in
  deps-check)
    python_bin="$(command -v python3 || true)"
    uv_bin="$(command -v uv || true)"
    soffice_bin="$(command -v soffice || true)"
    pdftoppm_bin="$(command -v pdftoppm || true)"

    echo "python3=${python_bin:-missing}"
    echo "uv=${uv_bin:-missing}"
    echo "soffice=${soffice_bin:-missing}"
    echo "pdftoppm=${pdftoppm_bin:-missing}"

    if check_python_module openpyxl; then
      echo "python_module_openpyxl=installed"
    else
      echo "python_module_openpyxl=missing"
    fi

    if check_python_module pandas; then
      echo "python_module_pandas=installed"
    else
      echo "python_module_pandas=missing"
    fi

    if check_python_module matplotlib; then
      echo "python_module_matplotlib=installed"
    else
      echo "python_module_matplotlib=missing"
    fi
    ;;

  print-install)
    target="${1:-}"
    case "$target" in
      core)
        echo "uv pip install openpyxl pandas"
        ;;
      charting)
        echo "uv pip install matplotlib"
        ;;
      render)
        echo "brew install libreoffice poppler"
        ;;
      *)
        echo "unknown install target: ${target:-<empty>}" >&2
        usage
        exit 2
        ;;
    esac
    ;;

  paths)
    echo "tmp_dir=tmp/spreadsheets"
    echo "output_dir=output/spreadsheet"
    ;;

  *)
    echo "unknown command: $cmd" >&2
    usage
    exit 2
    ;;
esac
