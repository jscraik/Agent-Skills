"""Tests for .harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md.

These tests cover the changes introduced in the PR that replaced a hardcoded
user-specific virtualenv Python path with the portable ``python3`` command in
the Eval YAML parse gate evidence section.

Scope: only the changed/added content in this PR is exercised.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import yaml


# ---------------------------------------------------------------------------
# Module paths
# ---------------------------------------------------------------------------

repo_root = Path(__file__).resolve().parents[3]

_identity_script = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_artifact_identity_lint.py"
)
_safety_script = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_frontmatter_safety_lint.py"
)


def _load(name: str, script: Path) -> ModuleType:
    """
    Load a Python module from the given filesystem path and insert it into sys.modules.
    
    Parameters:
        name (str): Module name to register in sys.modules.
        script (Path): Filesystem path to the Python source file to load.
    
    Returns:
        ModuleType: The loaded module object.
    
    Raises:
        AssertionError: If a module spec cannot be created for the given path or if the spec has no loader.
    """
    spec = importlib.util.spec_from_file_location(name, script)
    assert spec is not None, f"Could not locate module at {script}"
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


identity = _load("he_artifact_identity_lint", _identity_script)
safety = _load("he_frontmatter_safety_lint", _safety_script)

# ---------------------------------------------------------------------------
# Path to the changed eval artifact
# ---------------------------------------------------------------------------

eval_file = repo_root / ".harness" / "evals" / "2026-05-09-agent-skills-first-principles-contract-eval.md"

# ---------------------------------------------------------------------------
# Canonical frontmatter for the changed eval (matches the actual file header)
# ---------------------------------------------------------------------------

EVAL_FRONTMATTER = """---
schema_version: 1
artifact_id: agent-skills-first-principles-contract-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-first-principles-contract
title: First-Principles Contract Eval
harness_stage: he-eval-report
status: accepted
date: 2026-05-09
traceability_required: false
origin: .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md
linear_issue: not_created
linear_milestone: HE First-Principles Gate (proposed)
---

# First-Principles Contract Eval
"""

eval_path = Path(".harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md")

# ---------------------------------------------------------------------------
# Content-level tests: the key change in this PR
# ---------------------------------------------------------------------------


def test_eval_yaml_parse_gate_uses_portable_python3_command() -> None:
    """
    Assert the Eval YAML parse gate evidence uses a portable python3 command.

    Checks that the target eval markdown contains the substring "python3 -c", ensuring the evidence uses a portable command rather than a user-specific virtualenv path.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Find the "Eval YAML parse" gate section
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' gate in eval file."

    # Find the Evidence section within this gate
    evidence_start = text.find("Evidence:", gate_start)
    assert evidence_start != -1, "Could not find Evidence section in Eval YAML parse gate."

    # Extract evidence content (up to next blank line or next section)
    evidence_end = text.find("\n\n", evidence_start)
    if evidence_end == -1:
        evidence_end = len(text)

    gate_evidence = text[evidence_start:evidence_end]

    # The new portable command must be present.
    assert "python3 -c" in gate_evidence, (
        "Expected 'python3 -c' in the Eval YAML parse gate evidence section, "
        "but it was not found."
    )


def test_eval_yaml_parse_gate_does_not_contain_hardcoded_user_path() -> None:
    """
    Ensure the "Gate: Eval YAML parse." evidence does not contain hardcoded user-specific paths.
    
    This test asserts that the gate's Evidence section does not include substrings like "/Users/" which indicate a user-specific virtualenv path, ensuring the evidence uses a portable command form.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Extract the YAML frontmatter and parse it
    if text.startswith("---\n"):
        # Find the closing frontmatter delimiter
        end_frontmatter = text.find("\n---\n", 4)
        if end_frontmatter != -1:
            # Parse the frontmatter (not used but validates structure)
            frontmatter_text = text[4:end_frontmatter]
            yaml.safe_load(frontmatter_text)

    # Find the "Eval YAML parse" gate section
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' gate in eval file."

    # Find the Evidence section within this gate
    evidence_start = text.find("Evidence:", gate_start)
    assert evidence_start != -1, "Could not find Evidence section in Eval YAML parse gate."

    # Extract evidence content (up to next blank line or next section)
    evidence_end = text.find("\n\n", evidence_start)
    if evidence_end == -1:
        evidence_end = len(text)

    gate_evidence = text[evidence_start:evidence_end]

    assert "/Users/" not in gate_evidence, (
        "The Eval YAML parse gate evidence still contains a hardcoded '/Users/' path. "
        "The evidence command must use the portable 'python3' form."
    )


def test_eval_yaml_parse_gate_does_not_contain_venv_path() -> None:
    """
    Ensure the Eval YAML parse gate's Evidence section does not reference a `.venvs` virtualenv path.
    
    Raises:
        AssertionError: If the file is missing the gate or Evidence section, or if the extracted Evidence contains the substring `.venvs`.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Extract the YAML frontmatter and parse it
    if text.startswith("---\n"):
        # Find the closing frontmatter delimiter
        end_frontmatter = text.find("\n---\n", 4)
        if end_frontmatter != -1:
            # Parse the frontmatter (not used but validates structure)
            frontmatter_text = text[4:end_frontmatter]
            yaml.safe_load(frontmatter_text)

    # Find the "Eval YAML parse" gate section
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' gate in eval file."

    # Find the Evidence section within this gate
    evidence_start = text.find("Evidence:", gate_start)
    assert evidence_start != -1, "Could not find Evidence section in Eval YAML parse gate."

    # Extract evidence content (up to next blank line or next section)
    evidence_end = text.find("\n\n", evidence_start)
    if evidence_end == -1:
        evidence_end = len(text)

    gate_evidence = text[evidence_start:evidence_end]

    assert ".venvs" not in gate_evidence, (
        "The Eval YAML parse gate evidence references a '.venvs' path. "
        "Evidence commands must use the portable 'python3' executable."
    )


def test_eval_yaml_parse_gate_evidence_targets_expected_yaml_files() -> None:
    """The python3 command in the Eval YAML parse gate must reference both
    expected YAML eval file paths.

    Ensures the command content was not accidentally altered when the Python
    executable path was updated.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Find the "Eval YAML parse" gate section
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' gate in eval file."

    # Find the Evidence section within this gate
    evidence_start = text.find("Evidence:", gate_start)
    assert evidence_start != -1, "Could not find Evidence section in Eval YAML parse gate."

    # Extract evidence content (up to next blank line or next section)
    evidence_end = text.find("\n\n", evidence_start)
    if evidence_end == -1:
        evidence_end = len(text)

    gate_evidence = text[evidence_start:evidence_end]

    assert (
        "Plugins/skill-factory/skills/code_quality_review/skill-builder/references/evals.yaml"
        in gate_evidence
    ), "skill-factory evals.yaml path is missing from the Eval YAML parse gate evidence."

    assert (
        "Plugins/plugin-factory/skills/code_quality_review/plugin-builder/references/evals.yaml"
        in gate_evidence
    ), "plugin-factory evals.yaml path is missing from the Eval YAML parse gate evidence."


def test_eval_yaml_parse_gate_evidence_prints_ok() -> None:
    """The python3 command in the gate evidence must include the 'print('ok')'
    verification step, confirming the script asserts success.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Find the "Eval YAML parse" gate section
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' gate in eval file."

    # Find the Evidence section within this gate
    evidence_start = text.find("Evidence:", gate_start)
    assert evidence_start != -1, "Could not find Evidence section in Eval YAML parse gate."

    # Extract evidence content (up to next blank line or next section)
    evidence_end = text.find("\n\n", evidence_start)
    if evidence_end == -1:
        evidence_end = len(text)

    gate_evidence = text[evidence_start:evidence_end]

    assert "print('ok')" in gate_evidence, (
        "The Eval YAML parse gate evidence command is missing the print('ok') "
        "verification step."
    )


# ---------------------------------------------------------------------------
# Frontmatter identity-lint tests
# ---------------------------------------------------------------------------


def test_first_principles_EVAL_FRONTMATTER_passes_identity_lint() -> None:
    """The canonical frontmatter for the changed eval file must pass
    he_artifact_identity_lint validation.
    """
    result = identity.lint_markdown(eval_path, EVAL_FRONTMATTER)

    assert result.passed, f"Identity lint errors: {result.errors}"


def test_first_principles_eval_real_file_passes_identity_lint() -> None:
    """The actual eval file on disk must pass identity lint after the PR change."""
    text = eval_file.read_text(encoding="utf-8")

    result = identity.lint_markdown(eval_path, text)

    assert result.passed, f"Identity lint errors on real file: {result.errors}"


# ---------------------------------------------------------------------------
# Frontmatter safety-lint tests
# ---------------------------------------------------------------------------


def test_first_principles_EVAL_FRONTMATTER_passes_safety_lint() -> None:
    """
    Verify that the canonical frontmatter for the eval file passes the safety frontmatter lint.
    """
    result = safety.lint_markdown(eval_path, EVAL_FRONTMATTER)

    assert result.passed, f"Safety lint errors: {result.errors}"


def test_first_principles_eval_real_file_passes_safety_lint() -> None:
    """The actual eval file on disk must pass safety lint after the PR change."""
    text = eval_file.read_text(encoding="utf-8")

    result = safety.lint_markdown(eval_path, text)

    assert result.passed, f"Safety lint errors on real file: {result.errors}"


# ---------------------------------------------------------------------------
# Negative/boundary tests
# ---------------------------------------------------------------------------


def test_frontmatter_with_hardcoded_user_path_is_detectable() -> None:
    """Verify that a document containing the old hardcoded user path is
    distinguishable from one with the portable python3 form.

    This is a boundary/regression test: if the old path were re-introduced,
    the content-level assertion would catch it.
    """
    old_evidence = (
        "`/Users/<username>/.venvs/pyyaml/bin/python "
        "-c \"import pathlib,yaml; print('ok')\"` -> pass."
    )
    new_evidence = (
        "`python3 "
        "-c \"import pathlib,yaml; print('ok')\"` -> pass."
    )

    assert "/Users/" in old_evidence, "Old path format should contain /Users/."
    assert "/Users/" not in new_evidence, "New portable form must not contain /Users/."
    assert "python3" in new_evidence, "New form must use python3."
    assert "python3" not in old_evidence.split()[0], (
        "Old form must not start with the bare python3 command."
    )


def test_eval_file_gate_section_contains_portability_marker() -> None:
    """
    Verify the "Gate: Eval YAML parse." section contains the portable "python3" marker and does not include hardcoded user paths.
    
    Checks an 800-character window starting at the gate header for the substring "python3" and asserts that "/Users/" is not present.
    """
    text = eval_file.read_text(encoding="utf-8")

    # Find the Eval YAML parse gate block
    gate_start = text.find("Gate: Eval YAML parse.")
    assert gate_start != -1, "Could not find 'Gate: Eval YAML parse.' section in eval file."

    gate_block = text[gate_start : gate_start + 800]

    assert "python3" in gate_block, (
        "The 'Gate: Eval YAML parse.' section does not contain 'python3'. "
        "The evidence command must use the portable python3 form."
    )
    assert "/Users/" not in gate_block, (
        "The 'Gate: Eval YAML parse.' section still contains a '/Users/' path. "
        "This hardcoded path should have been replaced with 'python3'."
    )
