import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure/scripts/validation-and-linting"))

from verify_selection_gate_severity import _build_payload, _validate_against_schema  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/selection-gate-severity.v1.schema.json"


def test_selection_gate_schema_accepts_truthful_skipped_result() -> None:
    payload = {
        "schema_version": "selection-gate-severity.v1",
        "run_id": "changed-files-fixture",
        "generated_at": "2026-07-09T00:00:00Z",
        "all_required_passed": True,
        "checks": [
            {
                "name": "runtime-separation-manifest",
                "mode": "required",
                "result": "skipped",
                "rationale": "check skipped; outside validation scope",
                "log_file": "/tmp/runtime-separation-manifest.log",
            }
        ],
    }

    assert _validate_against_schema(payload, SCHEMA_PATH) == []
    assert _build_payload("changed-files-fixture", payload["checks"])["all_required_passed"] is True
