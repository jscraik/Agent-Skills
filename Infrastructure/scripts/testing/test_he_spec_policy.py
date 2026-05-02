from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/he-spec"
SKILL = SKILL_DIR / "SKILL.md"
EVALS = SKILL_DIR / "references/evals.yaml"
CONTRACT = SKILL_DIR / "references/contract.yaml"
INDEX = ROOT / "Plugins/harness-engineering/references/deferred-context-index.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_active_skill_keeps_required_spec_contracts() -> None:
    text = read(SKILL)

    for phrase in [
        "schema_version: 1",
        "Explore first and ask second",
        "session-collector evidence",
        "current-vs-latest spec status",
        "Linear Acceptance Traceability",
        "complete replacement spec section",
        "assets/icon-small.png",
        "Plugins/harness-engineering/references/he-spec-doctrine.md",
    ]:
        assert phrase in text


def test_plugin_owned_references_are_present_and_indexed() -> None:
    expected = [
        "references/autoresearch-2026-05-02.md",
        "references/codex-and-session-evidence.md",
        "references/spec-artifact-contract.md",
        "references/spec-mode-rules.md",
    ]
    index = read(INDEX)

    assert (ROOT / "Plugins/harness-engineering/references/he-spec-doctrine.md").exists()
    for rel in expected:
        assert (SKILL_DIR / rel).exists()
        assert f"Plugins/harness-engineering/skills/he-spec/{rel}" in index
    assert "Plugins/harness-engineering/references/he-spec-doctrine.md" in index


def test_contract_has_operational_readiness_keys() -> None:
    text = read(CONTRACT)

    for phrase in [
        "schema_version: 1",
        "observability:",
        "rollback_procedure:",
        "source-parity notes",
        "session-collector output",
    ]:
        assert phrase in text


def test_eval_matrix_has_enough_deterministic_coverage() -> None:
    text = read(EVALS)

    cases = text.count("\n  - id:")
    deterministic = text.count("deterministic_checks:")

    assert cases >= 18
    assert deterministic / cases >= 0.30
    assert "session-collector-evidence" in text
    assert "current-vs-latest-spec" in text
    assert 'last_updated: "2026-05-02"' in text


def test_examples_are_concrete() -> None:
    text = read(SKILL)

    assert "JSC-246" in text
    assert "QA report" in text
    assert "account settings flow" in text
