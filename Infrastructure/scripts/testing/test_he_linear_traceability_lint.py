from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "he_linear_traceability_lint.py"
)
SPEC = importlib.util.spec_from_file_location("he_linear_traceability_lint", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["he_linear_traceability_lint"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_valid_plan_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Progress

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-224 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert result.passed


def test_traceability_required_without_issue_fails() -> None:
    markdown = """---
schema_version: 1
linear_status: Todo
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: pending

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| pending | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert "frontmatter linear_issue must contain a Linear issue key like JSC-224" in result.errors


def test_missing_plan_traceability_columns_fail() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement |
| --- | --- |
| JSC-224 | R1 |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("Linear / Spec / Plan / PR Traceability table" in error for error in result.errors)


def test_valid_spec_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Spec

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Progress

## 17.9 Linear Acceptance Traceability

| Linear issue | Source requirement | Acceptance IDs | Planning handoff |
| --- | --- | --- | --- |
| JSC-224 | Requirement 1 | SA1, SA2 | PLAN-P0 |
"""

    result = MODULE.lint_markdown(Path("spec.md"), markdown)

    assert result.passed


def test_valid_pr_traceability_passes() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Review
traceability_required: true
---

# Pull Request

## Linear Work Item Contract

- Linear issue: JSC-224
- Current Linear status: In Review

## PR Traceability

| Linear issue | Acceptance IDs | Validation |
| --- | --- | --- |
| JSC-224 | AC1, AC2 | pytest passed |
"""

    result = MODULE.lint_markdown(Path("pr.md"), markdown)

    assert result.passed


def test_traceability_table_must_match_frontmatter_issue() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-224

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-999 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("frontmatter linear_issue JSC-224" in error for error in result.errors)


def test_traceability_table_requires_exact_issue_key_match() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-22
linear_status: In Progress
traceability_required: true
---

# Plan

## Linear Work Item Contract

- Linear issue: JSC-22

## Linear / Spec / Plan / PR Traceability

| Linear issue | Requirement | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- | --- |
| JSC-224 | R1 | SA1 | P0 | AC1 | pending |
"""

    result = MODULE.lint_markdown(Path("plan.md"), markdown)

    assert not result.passed
    assert any("frontmatter linear_issue JSC-22" in error for error in result.errors)


def test_pr_traceability_requires_validation_column() -> None:
    markdown = """---
schema_version: 1
linear_issue: JSC-224
linear_status: In Review
traceability_required: true
---

# Pull Request

## Linear Work Item Contract

- Linear issue: JSC-224

## PR Traceability

| Linear issue | Acceptance IDs |
| --- | --- |
| JSC-224 | AC1 |
"""

    result = MODULE.lint_markdown(Path("pr.md"), markdown)

    assert not result.passed
    assert any("PR Traceability table must include columns: Validation" in error for error in result.errors)
