from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_human_lane_card.py"
)
SPEC = importlib.util.spec_from_file_location("validate_human_lane_card", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_human_lane_card = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_human_lane_card
SPEC.loader.exec_module(validate_human_lane_card)


def test_accepts_human_task_and_pr_title() -> None:
    findings = validate_human_lane_card.validate_payload(
        {
            "schema_version": "worker-packet-set/v1",
            "human_task_name": "Agent-Skills: Add PM Model Routing And Bounded Lane Guards",
            "human_pr_title": "Add PM model routing and bounded lane guards",
        }
    )

    assert findings == []


def test_rejects_opaque_primary_task_name() -> None:
    findings = validate_human_lane_card.validate_payload(
        {
            "schema_version": "worker-packet-set/v1",
            "human_task_name": "chief-flow-ratchets-worker-02a",
            "human_pr_title": "Add PM model routing and bounded lane guards",
        }
    )

    assert any(finding.code == "opaque_primary_display_name" for finding in findings)


def test_rejects_opaque_worker_human_name() -> None:
    findings = validate_human_lane_card.validate_payload(
        {
            "schema_version": "worker-packet-set/v1",
            "worker_packets": [
                {
                    "worker_id": "chief-flow-ratchets-worker-02a-human-lane-card-validator",
                    "human_name": "chief-flow-ratchets-worker-02a-human-lane-card-validator",
                }
            ],
        }
    )

    assert any(finding.path == "worker_packets.0.human_name" for finding in findings)


def test_rejects_uppercase_opaque_lane_ids() -> None:
    findings = validate_human_lane_card.validate_payload(
        {
            "schema_version": "worker-packet-set/v1",
            "worker_packets": [
                {"human_name": "JSC-worker-02"},
                {"human_name": "codex-PR-123"},
                {"human_name": "chief-flow-ratchets-worker-02A"},
            ],
        }
    )

    opaque_paths = {
        finding.path
        for finding in findings
        if finding.code == "opaque_primary_display_name"
    }
    assert "worker_packets.0.human_name" in opaque_paths
    assert "worker_packets.1.human_name" in opaque_paths
    assert "worker_packets.2.human_name" in opaque_paths


def test_accepts_worker_human_name() -> None:
    findings = validate_human_lane_card.validate_payload(
        {
            "schema_version": "worker-packet-set/v1",
            "worker_packets": [
                {
                    "worker_id": "chief-flow-ratchets-worker-02a-human-lane-card-validator",
                    "human_name": "Agent-Skills: Add Human Lane Card Validator",
                }
            ],
        }
    )

    assert findings == []


def test_cli_reports_bad_fixture(tmp_path: Path, capsys) -> None:
    fixture = tmp_path / "bad.json"
    fixture.write_text(
        json.dumps(
            {
                "schema_version": "worker-packet-set/v1",
                "human_task_name": "chief-flow-ratchets-worker-02a",
                "human_pr_title": "codex-pr-123",
            }
        ),
        encoding="utf-8",
    )

    exit_code = validate_human_lane_card.main([fixture.as_posix(), "--json"])

    assert exit_code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "fail"
