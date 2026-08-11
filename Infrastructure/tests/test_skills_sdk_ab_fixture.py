from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import sdk_eval  # noqa: E402
from ask.skills_sdk.eval_ab_fixture import AbFixtureStageRequest, stage_ab_fixture  # noqa: E402


def _skill_source(tmp_path: Path) -> Path:
    source = tmp_path / "Skills" / "example"
    references = source / "references"
    references.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example skill.\n---\n\n# Example\n",
        encoding="utf-8",
    )
    (references / "evals.yaml").write_text(
        "cases:\n  - id: happy-path\n    prompt: Preserve this exact scenario prompt.\n",
        encoding="utf-8",
    )
    return source


def _request(operation: str) -> AbFixtureStageRequest:
    return AbFixtureStageRequest(
        skill="Skills/example",
        case_id="happy-path",
        fixture_path=Path(".harness/evidence/handoff/example/fixtures/happy-path.md"),
        operation=operation,  # type: ignore[arg-type]
    )


def test_ab_fixture_stage_preview_derives_the_current_scenario_prompt(tmp_path: Path) -> None:
    source = _skill_source(tmp_path)

    receipt = stage_ab_fixture(tmp_path, source_path=source, request=_request("preview"))

    assert receipt["status"] == "preview"
    assert receipt["mutation_performed"] is False
    assert receipt["fixture"]["path"] == ".harness/evidence/handoff/example/fixtures/happy-path.md"
    assert not (tmp_path / receipt["fixture"]["path"]).exists()


def test_ab_fixture_stage_writes_exact_canonical_prompt_bytes(tmp_path: Path) -> None:
    source = _skill_source(tmp_path)

    receipt = stage_ab_fixture(tmp_path, source_path=source, request=_request("execute"))
    fixture = tmp_path / receipt["fixture"]["path"]

    assert receipt["status"] == "pass"
    assert receipt["mutation_performed"] is True
    assert fixture.read_bytes() == b"Preserve this exact scenario prompt."


def test_ab_fixture_stage_refuses_to_overwrite_an_existing_fixture(tmp_path: Path) -> None:
    source = _skill_source(tmp_path)
    request = _request("execute")
    fixture = tmp_path / request.fixture_path
    fixture.parent.mkdir(parents=True)
    fixture.write_text("stale", encoding="utf-8")

    receipt = stage_ab_fixture(tmp_path, source_path=source, request=request)

    assert receipt["status"] == "blocked"
    assert fixture.read_text(encoding="utf-8") == "stale"
    assert any("already exists" in blocker for blocker in receipt["blockers"])


def test_sdk_eval_registers_the_ab_fixture_stage_command() -> None:
    root = argparse.ArgumentParser()
    subparsers = root.add_subparsers(dest="command", required=True)
    sdk_eval.add_sdk_eval_parser(subparsers, argparse.ArgumentParser(add_help=False))

    parsed = root.parse_args([
        "eval",
        "ab-fixture-stage",
        "--skill",
        "Skills/example",
        "--case",
        "happy-path",
        "--fixture-path",
        ".harness/evidence/handoff/example/fixtures/happy-path.md",
        "--preview",
    ])

    assert parsed.eval_action == "ab-fixture-stage"
    assert parsed.case == "happy-path"
    assert parsed.preview is True
