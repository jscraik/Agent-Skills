from __future__ import annotations

import sys
from pathlib import Path


LIB_ROOT = Path(__file__).resolve().parents[1] / "scripts" / "lib"
if str(LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(LIB_ROOT))

from ask.commands.memory import memory_list, memory_read, memory_search


def test_memory_list_reports_total_without_entries() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_list(repo_root, limit=0)

    assert result.status == "success"
    payload = result.data["memory"]
    assert payload["schema_version"] == "memory-provider.v1"
    assert payload["count"] == 0
    assert payload["total_count"] >= 1


def test_memory_list_blocks_blank_source() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_list(repo_root, source_id=" ")

    assert result.status == "error"
    assert result.errors[0].code == "ERR_VALIDATION"


def test_memory_read_accepts_listed_id() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    listed = memory_list(repo_root, limit=1).data["memory"]["entries"][0]

    result = memory_read(repo_root, listed["id"])

    assert result.status == "success"
    entry = result.data["memory"]["entry"]
    assert entry["id"] == listed["id"]
    assert entry["content"]
    assert entry["provenance"]["provider"] == listed["source_id"]
    assert entry["provenance"]["repo_relative_path"] == listed["path"]


def test_memory_read_blocks_unknown_identifier() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_read(repo_root, "not-a-real-memory-entry")

    assert result.status == "error"
    assert result.errors[0].code == "ERR_VALIDATION"
    assert "memory id not found" in result.errors[0].message


def test_memory_search_returns_results_shape() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_search(repo_root, "skill", limit=3)

    assert result.status == "success"
    payload = result.data["memory"]
    assert "results" in payload
    assert payload["count"] <= 3
    if payload["results"]:
        assert "provenance" in payload["results"][0]


def test_memory_search_includes_harness_solutions() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_search(repo_root, "goal-governor", limit=5)

    assert result.status == "success"
    results = result.data["memory"]["results"]
    assert any(entry["source_id"] == "harness-solutions" for entry in results)
    assert any(
        entry["path"] == ".harness/solutions/2026-05-13-agent-skills-goal-governor-smoke-eval-runtime-split-solution.md"
        for entry in results
    )


def test_memory_search_honors_source_filter() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = memory_search(repo_root, "goal-governor", source_id="harness-solutions", limit=3)

    assert result.status == "success"
    results = result.data["memory"]["results"]
    assert results
    assert all(entry["source_id"] == "harness-solutions" for entry in results)
