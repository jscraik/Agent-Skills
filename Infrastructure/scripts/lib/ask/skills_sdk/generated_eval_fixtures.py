from __future__ import annotations

import re
from pathlib import Path


FIXTURE_FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z ]+):\s*(.*)$")
GENERIC_GENERATED_SHOULD = (
    "Expose package instructions or references that encode the reviewed behavior "
    "under test, preserve safety boundaries, and name the next verifiable action."
)


def safe_scenario_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-").lower()
    return slug or "scenario"


def _fixture_fields(text: str) -> tuple[str, dict[str, str]]:
    title = ""
    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        match = FIXTURE_FIELD_RE.match(line)
        if match:
            current_key = match.group(1).strip().lower().replace(" ", "_")
            fields[current_key] = match.group(2).strip()
            continue
        if current_key and line.strip() and not line.startswith(("-", "#")):
            fields[current_key] = f"{fields[current_key]} {line.strip()}".strip()
    return title, fields


def _fixture_acceptance(good: str, bad: str) -> list[dict[str, str]]:
    acceptance: list[dict[str, str]] = [
        {"type": "expected_signal", "value": f"The skill package instructs agents to {good}"},
        {
            "type": "expected_signal",
            "value": "The skill package names the proof or validation boundary and cites observable package evidence.",
        },
        {
            "type": "expected_signal",
            "value": "The skill package avoids the expected failure mode and blocks readiness overclaims when proof is missing.",
        },
    ]
    if bad:
        acceptance.append({"type": "not_contains", "value": f"The skill package encourages or permits this failure mode: {bad}"})
    return acceptance


def _fixture_prompt(_given: str) -> str:
    return "\n".join([
        "Evaluate whether the installed skill package covers the reviewed operator boundary case described by the hidden checklist.",
        "Score the package instructions and references, not a freshly generated chat response. Look for the safest next action, the boundary that must be preserved, and the proof or check that would make the next step reliable.",
    ])


def _fixture_identity(title: str, fixture_path: Path) -> tuple[str, str, str]:
    raw_id = title.split(":", 1)[0].strip() if title else fixture_path.stem
    case_id = f"generated-{safe_scenario_slug(raw_id)}"
    display_name = title.split(":", 1)[1].strip() if ":" in title else raw_id
    return case_id, raw_id, display_name


def _fixture_case(case_id: str, raw_id: str, display_name: str, relative_path: str, fields: dict[str, str]) -> dict[str, object]:
    given = fields["given"]
    should = fields["should"]
    good = fields["good"]
    bad = fields.get("bad", "")
    return {
        "id": case_id,
        "category": "pressure" if "pressure" in relative_path or "feedback" in relative_path else "edge",
        "eval_modes": ["release"],
        "realistic": True,
        "why_realistic": "Reviewed generated fixture imported into the skill package for private Tessl assessment and SDK scenario-quality parity.",
        "prompt": _fixture_prompt(given),
        "unit": display_name or raw_id,
        "given": given,
        "should": GENERIC_GENERATED_SHOULD,
        "hidden_expected_behavior": should,
        "hidden_review_focus": fields.get("behavior") or should,
        "expected_artifact": relative_path,
        "actual_artifact": "installed skill package instructions and references",
        "reproduce": relative_path,
        "claim_ids": ["generated_fixture.behavior"],
        "deterministic_checks": {"forbidden_commands": ["curl", "wget", "rm -rf", "git push", "tessl publish"]},
        "acceptance": _fixture_acceptance(good, bad),
        "tessl": {"generated": True, "reviewed_fixture": relative_path, "source": "references/evals/*.md"},
        "source": relative_path,
        "source_kind": "generated_fixture",
    }


def parse_generated_eval_fixture(fixture_path: Path, source_root: Path) -> dict[str, object] | None:
    """Convert a reviewed markdown eval fixture into a Tessl/SDK case row."""
    title, fields = _fixture_fields(fixture_path.read_text(encoding="utf-8"))
    fields["good"] = fields.get("expected_agent_move") or fields.get("good_answer_patterns") or fields.get("should", "")
    fields["bad"] = fields.get("expected_failure") or fields.get("bad_answer_patterns") or fields.get("failure_mode", "")
    fields["behavior"] = fields.get("behavior_under_test") or fields.get("knowledge_claim") or fields.get("should", "")
    if not fields.get("given") or not fields.get("should") or not fields.get("good"):
        return None
    relative_path = fixture_path.relative_to(source_root).as_posix()
    case_id, raw_id, display_name = _fixture_identity(title, fixture_path)
    return _fixture_case(case_id, raw_id, display_name, relative_path, fields)


def parse_generated_eval_fixtures(source_root: Path) -> list[dict[str, object]]:
    fixture_root = source_root / "references" / "evals"
    if not fixture_root.is_dir():
        return []
    cases: list[dict[str, object]] = []
    for fixture_path in sorted(fixture_root.glob("*.md")):
        parsed = parse_generated_eval_fixture(fixture_path, source_root)
        if parsed is not None:
            cases.append(parsed)
    return cases
