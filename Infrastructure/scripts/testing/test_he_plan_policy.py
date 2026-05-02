from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/he-plan"
SKILL = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"
DOCTRINE = ROOT / "Plugins/harness-engineering/references/he-plan-doctrine.md"
OPENAI = SKILL_DIR / "agents/openai.yaml"
EVALS = REFS / "evals.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_active_skill_is_compact_and_preserves_plan_mode_contract() -> None:
    text = read(SKILL)
    assert len(text.splitlines()) <= 130
    for phrase in [
        "Explore first, ask second",
        "non-mutating inspection",
        "update_plan",
        "durable plan",
        "complete replacement plan",
        "Linear/spec/plan/PR traceability matrix",
        "repo-relative file paths",
        "product blockers",
    ]:
        assert phrase in text


def test_references_exist_and_retain_imported_context() -> None:
    expected = [
        "codex-plan-mode.md",
        "plan-artifact-contract.md",
        "planning-depth.md",
        "deepening-review.md",
        "test-strategy.md",
        "visual-communication.md",
    ]
    for name in expected:
        path = REFS / name
        assert path.exists(), name
        assert "Plugins/harness-engineering/references/he-plan-doctrine.md" in read(path)

    doctrine = read(DOCTRINE)
    for phrase in [
        "Live `/Users/jamiecraik/dev/codex` and codex-repo MCP",
        "Plan Mode",
        "Synthesis",
        "Deepening",
        "Testing Guidance",
        "Visual Guidance",
    ]:
        assert phrase in doctrine


def test_eval_matrix_covers_hardening_scenarios() -> None:
    text = read(EVALS)
    for case_id in [
        "explicit-plan-stage",
        "explore-before-asking",
        "codex-plan-mode-distinction",
        "tracked-work-requires-linear",
        "plan-revision-complete-replacement",
        "testing-anti-patterns",
        "visual-communication-needed",
        "pressure-skip-traceability",
        "pressure-prompt-injection",
    ]:
        assert f"id: {case_id}" in text

    for case_id in {
        "direct-implementation-request",
        "brainstorm-request",
        "review-request",
    }:
        assert re.search(rf"id: {case_id}\b[\s\S]*?should_trigger: false", text)

    smoke_cases = re.findall(r"id: ([^\n]+)\n[\s\S]*?eval_modes: \[smoke, release\]", text)
    assert smoke_cases == ["explicit-plan-stage"]


def test_metadata_description_is_complete() -> None:
    text = read(OPENAI)
    assert "into an..." not in text
    assert "traceable Harness Engineering delivery plans" in text


def test_deferred_index_points_to_plan_context() -> None:
    index = read(ROOT / "Plugins/harness-engineering/references/deferred-context-index.md")
    assert "## Plan Preserved Context" in index
    assert "Plugins/harness-engineering/references/he-plan-doctrine.md" in index
    assert (ROOT / "Plugins/harness-engineering/references/he-plan-doctrine.md").exists()
    for name in [
        "codex-plan-mode.md",
        "plan-artifact-contract.md",
        "planning-depth.md",
        "deepening-review.md",
        "test-strategy.md",
        "visual-communication.md",
    ]:
        path = f"Plugins/harness-engineering/skills/he-plan/references/{name}"
        assert path in index
        assert (ROOT / path).exists()
