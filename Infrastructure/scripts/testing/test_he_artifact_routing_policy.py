from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HE_ROOT = ROOT / "Plugins/harness-engineering"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_he_stage_docs_route_to_harness_roots() -> None:
    contract = read(HE_ROOT / "references/artifact-routing-contract.md")
    lifecycle = read(HE_ROOT / "references/lifecycle-exit-contract.md")
    bridge = read(HE_ROOT / "references/coding-harness-command-bridge.md")

    for root in [
        ".harness/ideate/**.md",
        ".harness/brainstorm/**.md",
        ".harness/specs/**.md",
        ".harness/plan/**.md",
    ]:
        assert root in contract
        assert root in lifecycle

    assert ".harness/brainstorm/**.md" in bridge
    assert ".harness/ideate/**.md" in bridge
    assert ".harness/specs/**.md" in bridge
    assert ".harness/plan/**.md" in bridge


def test_active_stage_entrypoints_name_their_durable_roots() -> None:
    expected = {
        "he-brainstorm/SKILL.md": [".harness/brainstorm/**.md", ".harness/ideate/**.md"],
        "he-spec/SKILL.md": [".harness/specs/**.md"],
        "he-plan/SKILL.md": [".harness/plan/**.md"],
    }

    for rel, required_roots in expected.items():
        text = read(HE_ROOT / "skills" / rel)
        for root in required_roots:
            assert root in text


def test_active_templates_do_not_default_to_legacy_doc_roots() -> None:
    active_text = "\n".join(
        read(path)
        for path in [
            HE_ROOT / "skills/he-brainstorm/references/requirements-artifact-guide.md",
            HE_ROOT / "skills/he-spec/references/spec-artifact-contract.md",
            HE_ROOT / "skills/he-plan/references/plan-artifact-contract.md",
            ROOT / "Infrastructure/references/harness-engineering/he-brainstorm-doctrine.md",
        ]
    )

    assert "Default path: `.harness/brainstorm/" in active_text
    assert "Durable spec markdown is written under `.harness/specs/**.md`" in active_text
    assert "Durable plan markdown is written under `.harness/plan/**.md`" in active_text
    assert "Default path: `docs/brainstorms/" not in active_text


def test_artifact_routing_is_listed_in_deferred_index() -> None:
    index = read(HE_ROOT / "references/deferred-context-index.md")

    assert "references/artifact-routing-contract.md" in index
