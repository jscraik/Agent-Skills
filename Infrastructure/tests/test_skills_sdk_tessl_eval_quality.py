from __future__ import annotations

from ask.skills_sdk.tessl_eval_quality import tessl_eval_quality_findings


def test_no_invention_scenarios_need_broad_negative_acceptance() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "narrow-no-invention",
            "unit": "service docs",
            "given": "A supplied runbook excerpt has missing recovery and owner evidence.",
            "should": "Mark missing evidence as blocked instead of inventing operational details.",
            "prompt": (
                "Use only the supplied excerpt. Do not invent support channels, setup "
                "commands, validation commands, owner names, dates, recovery paths, or "
                "acceptance criteria. If tools fail, ask in Slack."
            ),
            "actual_artifact": "artifacts/narrow-no-invention.md",
            "eval_modes": ["release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "Uses blocked placeholders for missing owner, recovery path, and acceptance criteria.",
                },
                {
                    "type": "not_regex",
                    "value": "(?i)(#agent.?skills.?support|\\./bin/ask setup)",
                },
            ],
        }
    ])

    assert "narrow_no_invention_negative_acceptance" in {finding["code"] for finding in findings}


def test_no_invention_scenarios_accept_broad_negative_acceptance() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "broad-no-invention",
            "unit": "service docs",
            "given": "A supplied runbook excerpt has missing recovery and owner evidence.",
            "should": "Mark missing evidence as blocked instead of inventing operational details.",
            "prompt": (
                "Use only the supplied excerpt. Do not invent support channels, setup "
                "commands, validation commands, owner names, dates, recovery paths, or "
                "acceptance criteria. If tools fail, ask in Slack."
            ),
            "actual_artifact": "artifacts/broad-no-invention.md",
            "eval_modes": ["release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "Uses blocked placeholders for missing owner, recovery path, and acceptance criteria.",
                },
                {
                    "type": "regex",
                    "value": "(?i)(\\[BLOCKED: missing owner\\]|\\[BLOCKED: missing recovery path\\]|\\[BLOCKED: missing acceptance criteria\\])",
                },
                {
                    "type": "not_regex",
                    "value": "(?i)(#[a-z0-9_-]+|Slack channel|Slack support|pytest|uv|mise|\\./bin/ask|setup command|validation command)",
                },
            ],
        }
    ])

    assert "narrow_no_invention_negative_acceptance" not in {finding["code"] for finding in findings}


def test_no_invention_scenarios_accept_plain_slack_channel_negative() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "plain-channel-no-invention",
            "unit": "service docs",
            "given": "A supplied runbook excerpt has missing recovery and owner evidence.",
            "should": "Mark missing evidence as blocked instead of inventing operational details.",
            "prompt": (
                "Use only the supplied excerpt. Do not invent support channels, setup "
                "commands, validation commands, owner names, dates, recovery paths, or "
                "acceptance criteria. If tools fail, ask in Slack."
            ),
            "actual_artifact": "artifacts/plain-channel-no-invention.md",
            "eval_modes": ["release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "Uses blocked placeholders for missing owner, recovery path, and acceptance criteria.",
                },
                {
                    "type": "not_regex",
                    "value": r"(?i)(#support|#deploy-help|pytest|uv|mise|\./bin/ask|setup command|validation command)",
                },
            ],
        }
    ])

    assert "narrow_no_invention_negative_acceptance" not in {finding["code"] for finding in findings}


def test_no_invention_guardrail_does_not_self_trigger_from_acceptance_text() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "command-only-no-invention",
            "unit": "architecture note",
            "given": "A staged excerpt has missing command proof.",
            "should": "Mark missing command proof as blocked instead of inventing it.",
            "prompt": "Use only the supplied excerpt. Do not invent setup commands or validation commands.",
            "actual_artifact": "artifacts/command-only-no-invention.md",
            "eval_modes": ["release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "Blocks invented command evidence.",
                },
                {
                    "type": "not_regex",
                    "value": "(?i)(Slack channel|Slack support|pytest|uv|mise|\\./bin/ask|setup command|validation command)",
                },
            ],
        }
    ])

    assert "narrow_no_invention_negative_acceptance" not in {finding["code"] for finding in findings}


def test_side_effect_detection_reads_task_field() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "side-effect-task",
            "task": "Write output.md with the generated documentation.",
            "acceptance": [{"type": "expected_signal", "value": "Creates docs/output.md"}],
        }
    ])

    assert any(finding["code"] == "read_only_file_artifact_side_effect" for finding in findings)
