from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

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


def test_expected_signal_rejects_scorer_boilerplate() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "scorer-boilerplate-signal",
            "unit": "AGENTS router audit",
            "given": "A user wants root and nested AGENTS.md files reviewed.",
            "should": "Recommend keep, move, or delete decisions with file evidence.",
            "prompt": "Review AGENTS.md routing in the current repository.",
            "actual_artifact": "artifacts/agents-router-audit.md",
            "eval_modes": ["smoke", "release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": (
                        "Semantically covers the scenario-specific evidence and decision "
                        "signals: keep, move, delete."
                    ),
                }
            ],
        }
    ])

    assert "scorer_boilerplate_expected_signal" in {finding["code"] for finding in findings}


def test_expected_signal_rejects_generated_template_fragments() -> None:
    findings = tessl_eval_quality_findings([
        {
            "id": "generated-template-fragments",
            "unit": "agent-native evidence boundary",
            "given": "A maintainer asks whether branch provenance proves validation passed.",
            "should": "Separate provenance from validation proof and name missing commands.",
            "prompt": "Review the supplied scenario and return a concise maintainer assessment.",
            "actual_artifact": "artifacts/generated-template-fragments.md",
            "eval_modes": ["release"],
            "acceptance": [
                {
                    "type": "expected_signal",
                    "value": "failure class, failure category, failure mode, classif.",
                },
                {
                    "type": "expected_signal",
                    "value": "evidence boundary, proof boundary, claim boundary, skill-local evidence, capsule evidence.",
                },
            ],
        }
    ])

    assert "generated_boilerplate_expected_signal" in {finding["code"] for finding in findings}


def test_improve_agent_native_evals_do_not_reintroduce_scorer_boilerplate() -> None:
    evals_text = (
        REPO_ROOT
        / "Skills"
        / "agent-ops"
        / "improve-agent-native"
        / "references"
        / "evals.yaml"
    ).read_text(encoding="utf-8")

    assert "Semantically covers the scenario-specific evidence and decision signals" not in evals_text


def test_improve_agent_native_evals_do_not_reintroduce_generated_template_fragments() -> None:
    evals_text = (
        REPO_ROOT
        / "Skills"
        / "agent-ops"
        / "improve-agent-native"
        / "references"
        / "evals.yaml"
    ).read_text(encoding="utf-8")

    forbidden_fragments = [
        "failure class, failure category, failure",
        "evidence boundary, proof boundary, claim",
        "evidence _- boundary, proof _- boundary",
        "durable, mechanism, validator, check",
        "pass, fail, blocked, not_run_with_reason",
    ]
    assert not any(fragment in evals_text for fragment in forbidden_fragments)


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
