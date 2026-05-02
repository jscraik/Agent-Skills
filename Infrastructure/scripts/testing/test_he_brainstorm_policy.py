from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/he-brainstorm"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
AGENT_METADATA = SKILL_DIR / "agents/openai.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_he_brainstorm_active_contract_stays_context_budgeted() -> None:
    text = _read(SKILL)

    assert len(text.splitlines()) <= 120
    assert "Context preservation" in text
    assert "scope_tier" in text
    assert "Stated" in text
    assert "Inferred" in text
    assert "Out of scope" in text
    assert "warrant" in text.lower()
    assert "he-spec" in text
    assert "he-plan" in text
    assert "he-work" in text


def test_he_brainstorm_references_are_present() -> None:
    required = {
        "requirements-artifact-guide.md",
        "brainstorm-workflow-details.md",
        "discovery-interview.md",
        "visual-communication.md",
        "document-review-pass.md",
        "contract.yaml",
        "evals.yaml",
        "task-profile.json",
    }

    present = {path.name for path in REFERENCES.iterdir() if path.is_file()}

    assert required <= present


def test_he_brainstorm_keeps_current_he_stage_names() -> None:
    combined = "\n".join(
        _read(path)
        for path in [SKILL, *REFERENCES.glob("*.md"), REFERENCES / "contract.yaml", REFERENCES / "evals.yaml"]
    )

    assert "ce-spec" not in combined
    assert "ce-plan" not in combined
    assert "ce-work" not in combined


def test_he_brainstorm_evals_cover_hardening_scenarios() -> None:
    evals = _read(REFERENCES / "evals.yaml")

    for case_id in [
        "missing-subject-gate",
        "synthesis-before-artifact",
        "warranted-ideation",
        "visual-communication-needed",
        "deep-product-scope",
        "direct-spec-request",
        "direct-plan-request",
        "direct-work-request",
        "clear-qa-defect-request",
    ]:
        assert case_id in evals

    assert evals.count("should_trigger: false") >= 4


def test_he_brainstorm_metadata_has_complete_routing_description() -> None:
    metadata = _read(AGENT_METADATA)

    assert "Use when..." not in metadata
    assert "before spec, plan, work, or bug routing" in metadata
