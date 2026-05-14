from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HE_ROOT = ROOT / "Plugins/harness-engineering"
CONTRACT = HE_ROOT / "references/execution-slice-contract.md"


def read(path: Path) -> str:
    """
    Read the entire text contents of the file at the given path using UTF-8 encoding.
    
    Returns:
        str: The file contents as a Unicode string.
    """
    return path.read_text(encoding="utf-8")


def test_execution_slice_contract_names_authority_inputs() -> None:
    """
    Check that the execution-slice contract names the required authority input file path patterns and the permitted selection concepts.
    
    Asserts that the contract text includes authority input patterns such as harness linear plans, reframes, decisions, core, and brainstorm documents, and that it requires selecting exactly one of: milestone, parent issue, reframe phase, or execution slice.
    """
    text = read(CONTRACT)

    for phrase in [
        ".harness/linear/*.md",
        ".harness/reframes/<selected-reframe>.md",
        ".harness/decisions/*.md",
        ".harness/core/*.md",
        ".harness/brainstorm/*.md",
        "one milestone",
        "one parent issue",
        "one reframe phase",
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
        "execution slice",
        ".harness/linear/",
        "In Scope",
        "Out of Scope",
    ]:
        assert phrase in text


def test_downstream_stages_obey_selected_slice_boundary() -> None:
    plan = read(HE_ROOT / "skills/he-plan/SKILL.md")
    work = read(HE_ROOT / "skills/he-work/SKILL.md")

    assert "execution slice" in plan
    assert "execution slice" in work
    assert "secondary review" in work or "secondary inputs" in work


def test_shared_contract_is_indexed_and_bridged() -> None:
    """
    Verify that the execution-slice contract is referenced and referenced terms are bridged across HE reference documents.
    
    Checks that the deferred-context index references the execution-slice contract, the coding-harness command bridge mentions "approved execution slice", and the lifecycle exit contract mentions "selected execution slice".
    """
    index = read(HE_ROOT / "references/deferred-context-index.md")
    bridge = read(HE_ROOT / "references/coding-harness-command-bridge.md")
    lifecycle = read(HE_ROOT / "references/lifecycle-exit-contract.md")

    assert "references/execution-slice-contract.md" in index
    assert "approved execution slice" in bridge
    assert "selected execution slice" in lifecycle
