from __future__ import annotations

from ask.skills_sdk.tessl_eval_quality import tessl_eval_quality_findings


def test_side_effect_detection_reads_task_field() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "side-effect-task",
            "task": "Write output.md with the generated documentation.",
            "acceptance": [{"type": "expected_signal", "value": "Creates docs/output.md"}],
        }
    ])

    assert any(finding["code"] == "read_only_file_artifact_side_effect" for finding in findings)
