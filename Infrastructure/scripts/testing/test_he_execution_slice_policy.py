from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HE_ROOT = ROOT / "Plugins/harness-engineering"
CONTRACT = HE_ROOT / "references/execution-slice-contract.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_execution_slice_contract_names_authority_inputs() -> None:
    text = read(CONTRACT)

    for phrase in [
        ".harness/linear/<repo-name>-linear-plan.md",
        ".harness/refactors/<selected-refactor>.md",
        ".harness/decisions/*.md",
        ".harness/core/*.md",
        ".harness/brainstorm/*.md",
        "one milestone",
        "one parent issue",
        "one refactor phase",
        "one execution slice",
    ]:
        assert phrase in text


def test_execution_slice_contract_demotes_secondary_inputs() -> None:
    text = read(CONTRACT)

    for phrase in [
        ".harness/strategy/*.md",
        ".harness/triage/*.md",
        ".harness/review/*.md",
        ".harness/features/*.md",
        "Secondary inputs must not create implementation requirements by themselves",
    ]:
        assert phrase in text


def test_active_he_spec_consumes_approved_execution_slice() -> None:
    text = read(HE_ROOT / "skills/he-spec/SKILL.md")

    for phrase in [
        "bounded implementation spec for one milestone, parent issue, refactor phase, or execution slice",
        ".harness/linear/<repo-name>-linear-plan.md",
        ".harness/refactors/<selected-refactor>.md",
        ".harness/decisions/*.md",
        ".harness/core/*.md",
        ".harness/brainstorm/*.md",
        ".harness/strategy/*.md",
        ".harness/triage/*.md",
        ".harness/review/*.md",
        ".harness/features/*.md",
        "stop if no selected milestone, parent issue, refactor phase, or execution slice is identified",
        "Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route",
        "explicit In Scope and Out of Scope boundaries",
    ]:
        assert phrase in text


def test_downstream_stages_obey_selected_slice_boundary() -> None:
    plan = read(HE_ROOT / "skills/he-plan/SKILL.md")
    work = read(HE_ROOT / "skills/he-work/SKILL.md")

    assert "keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice" in plan
    assert "Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context" in plan
    assert "verify the plan/todo maps to one selected milestone, parent issue, refactor phase, or execution slice before editing" in work
    assert "Pulling unapproved work from secondary review, strategy, triage, or feature docs" in work


def test_shared_contract_is_indexed_and_bridged() -> None:
    index = read(HE_ROOT / "references/deferred-context-index.md")
    bridge = read(HE_ROOT / "references/coding-harness-command-bridge.md")
    lifecycle = read(HE_ROOT / "references/lifecycle-exit-contract.md")

    assert "references/execution-slice-contract.md" in index
    assert "approved execution slice" in bridge
    assert "selected execution slice" in lifecycle
