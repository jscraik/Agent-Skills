from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/he-work"
SKILL = SKILL_DIR / "SKILL.md"
EVALS = SKILL_DIR / "references/evals.yaml"
CONTRACT = SKILL_DIR / "references/contract.yaml"
INDEX = ROOT / "Plugins/harness-engineering/references/deferred-context-index.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_active_skill_keeps_required_work_contracts() -> None:
    text = read(SKILL)

    for phrase in [
        "Harness Engineering",
        "`update_plan` is live checklist only",
        "current active state",
        "Explore first, ask second",
        "dirty worktrees",
        "external-delegate",
        "he-code-review mode:autofix",
    ]:
        assert phrase in text
    assert (SKILL_DIR / "assets/icon-small.png").exists()


def test_active_skill_uses_plugin_owned_references() -> None:
    text = read(SKILL)
    index = read(INDEX)
    expected = [
        "references/work-execution-contract.md",
        "references/codex-execution-lessons.md",
        "references/handoff-and-shipping.md",
        "references/execution-modes.md",
    ]

    assert "fixtures/preserved-context" not in text
    for rel in expected:
        assert (SKILL_DIR / rel).exists()
        assert f"Plugins/harness-engineering/skills/he-work/{rel}" in index


def test_contract_has_operational_readiness_keys() -> None:
    text = read(CONTRACT)

    for phrase in [
        "schema_version: 1",
        "observability:",
        "rollback_procedure:",
        "traceability evidence",
        "dirty worktree damage",
    ]:
        assert phrase in text


def test_eval_matrix_has_no_ce_naming_and_sufficient_coverage() -> None:
    text = read(EVALS)
    cases = text.count("\n  - id:")
    deterministic = text.count("deterministic_checks:")

    assert cases >= 20
    assert deterministic / cases >= 0.70
    assert 'last_updated: "2026-05-02"' in text
    assert "explicit Harness Engineering work stage" in text
    assert "ce work stage" not in text.lower()
    assert "ce-work" not in text
    assert "x_common: &common {eval_modes: [smoke, release]" in text
    assert "x_negative: &negative {eval_modes: [smoke, release]" in text


def test_examples_are_concrete() -> None:
    text = read(SKILL)

    assert "JSC-246" in text
    assert "delegate mode" in text
    assert "verified slices" in text
