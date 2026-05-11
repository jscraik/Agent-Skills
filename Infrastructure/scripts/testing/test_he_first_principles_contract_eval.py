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


# ---------------------------------------------------------------------------
# Module paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]

_IDENTITY_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_artifact_identity_lint.py"
)
_SAFETY_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_frontmatter_safety_lint.py"
)


def _load(name: str, script: Path):
    spec = importlib.util.spec_from_file_location(name, script)
    assert spec is not None, f"Could not locate module at {script}"
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IDENTITY = _load("he_artifact_identity_lint", _IDENTITY_SCRIPT)
SAFETY = _load("he_frontmatter_safety_lint", _SAFETY_SCRIPT)

# ---------------------------------------------------------------------------
# Path to the changed eval artifact
# ---------------------------------------------------------------------------

EVAL_FILE = REPO_ROOT / ".harness" / "evals" / "2026-05-09-agent-skills-first-principles-contract-eval.md"

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

EVAL_PATH = Path(".harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md")

# ---------------------------------------------------------------------------
# Content-level tests: the key change in this PR
# ---------------------------------------------------------------------------


def test_eval_yaml_parse_gate_uses_portable_python3_command() -> None:
    """The Eval YAML parse gate evidence must use the portable ``python3``
    command, not a hardcoded user-specific virtualenv path.

    This is the exact change introduced in this PR (line 298 of the eval file).
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

    # The new portable command must be present.
    assert "python3 -c" in text, (
        "Expected 'python3 -c' in the Eval YAML parse gate evidence section, "
        "but it was not found."
    )


def test_eval_yaml_parse_gate_does_not_contain_hardcoded_user_path() -> None:
    """No evidence line in the eval should reference a hardcoded user-specific
    virtualenv path (e.g. /Users/<username>/.venvs/...).

    The PR replaced '/Users/<username>/.venvs/pyyaml/bin/python' with
    'python3', making the evidence portable.
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

    assert "/Users/" not in text, (
        "The eval file still contains a hardcoded '/Users/' path. "
        "The evidence command must use the portable 'python3' form."
    )


def test_eval_yaml_parse_gate_does_not_contain_venv_path() -> None:
    """The evidence command must not reference a .venvs virtualenv path.

    Regression guard: ensures the old '/Users/<username>/.venvs/pyyaml/bin/python'
    form (or any .venvs variant) cannot creep back into the evidence section.
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

    assert ".venvs" not in text, (
        "The eval file references a '.venvs' path in an evidence command. "
        "Evidence commands must use the portable 'python3' executable."
    )


def test_eval_yaml_parse_gate_evidence_targets_expected_yaml_files() -> None:
    """The python3 command in the Eval YAML parse gate must reference both
    expected YAML eval file paths.

    Ensures the command content was not accidentally altered when the Python
    executable path was updated.
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

    assert (
        "Plugins/skill-factory/skills/code_quality_review/skill-builder/references/evals.yaml"
        in text
    ), "skill-factory evals.yaml path is missing from the Eval YAML parse gate evidence."

    assert (
        "Plugins/plugin-factory/skills/code_quality_review/plugin-builder/references/evals.yaml"
        in text
    ), "plugin-factory evals.yaml path is missing from the Eval YAML parse gate evidence."


def test_eval_yaml_parse_gate_evidence_prints_ok() -> None:
    """The python3 command in the gate evidence must include the 'print('ok')'
    verification step, confirming the script asserts success.
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

    assert "print('ok')" in text, (
        "The Eval YAML parse gate evidence command is missing the print('ok') "
        "verification step."
    )


# ---------------------------------------------------------------------------
# Frontmatter identity-lint tests
# ---------------------------------------------------------------------------


def test_first_principles_eval_frontmatter_passes_identity_lint() -> None:
    """The canonical frontmatter for the changed eval file must pass
    he_artifact_identity_lint validation.
    """
    result = IDENTITY.lint_markdown(EVAL_PATH, EVAL_FRONTMATTER)

    assert result.passed, f"Identity lint errors: {result.errors}"


def test_first_principles_eval_real_file_passes_identity_lint() -> None:
    """The actual eval file on disk must pass identity lint after the PR change."""
    text = EVAL_FILE.read_text(encoding="utf-8")

    result = IDENTITY.lint_markdown(EVAL_PATH, text)

    assert result.passed, f"Identity lint errors on real file: {result.errors}"


# ---------------------------------------------------------------------------
# Frontmatter safety-lint tests
# ---------------------------------------------------------------------------


def test_first_principles_eval_frontmatter_passes_safety_lint() -> None:
    """The canonical frontmatter for the changed eval file must pass
    he_frontmatter_safety_lint validation.
    """
    result = SAFETY.lint_markdown(EVAL_PATH, EVAL_FRONTMATTER)

    assert result.passed, f"Safety lint errors: {result.errors}"


def test_first_principles_eval_real_file_passes_safety_lint() -> None:
    """The actual eval file on disk must pass safety lint after the PR change."""
    text = EVAL_FILE.read_text(encoding="utf-8")

    result = SAFETY.lint_markdown(EVAL_PATH, text)

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
    """The Eval YAML parse gate section must contain the word 'python3',
    not a non-portable interpreter reference.

    Boundary test: ensures that even if the gate prose is updated, the
    portable executable keyword is always present.
    """
    text = EVAL_FILE.read_text(encoding="utf-8")

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
