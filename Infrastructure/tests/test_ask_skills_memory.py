from __future__ import annotations

import sys
from pathlib import Path


LIB_ROOT = Path(__file__).resolve().parents[1] / "scripts" / "lib"
if str(LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(LIB_ROOT))

from ask.commands.skills_impl import skills_memory


def test_skills_memory_list_wraps_provider_payload() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "list", limit=0)

    assert result.status == "success"
    payload = result.data["skill_memory"]
    assert payload["schema_version"] == "skill-memory-provider.v1"
    assert payload["memory_provider_schema"] == "memory-provider.v1"
    assert payload["contract_schemas"]["memory"] == "skill-memory-provider.v1"
    assert payload["contract_schemas"]["provider"] == "memory-provider.v1"
    assert payload["entry_count"] == 0
    assert payload["total_count"] >= 1
    assert payload["entry_summary"]["returned_count"] == 0
    assert payload["source_summary"]["source_count"] >= 1
    assert payload["roots"]


def test_skills_memory_search_preserves_entry_provenance() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "search", query="projection", limit=1)

    assert result.status == "success"
    payload = result.data["skill_memory"]
    assert payload["entry_count"] == 1
    assert payload["entry_summary"]["returned_count"] == 1
    assert payload["entry_summary"]["total_count"] >= 1
    entry = payload["entries"][0]
    assert entry["provenance"]["provider"] == entry["source_id"]
    assert entry["provenance"]["repo_relative_path"] == entry["path"]


def test_skills_memory_search_preserves_source_filter() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "search", query="goal-governor", source_id="harness-solutions", limit=3)

    assert result.status == "success"
    payload = result.data["skill_memory"]
    assert payload["entry_count"] >= 1
    assert all(entry["source_id"] == "harness-solutions" for entry in payload["entries"])


def test_skills_memory_search_requires_query() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "search", query="")

    assert result.status == "error"
    assert result.data["skill_memory"]["status"] == "blocked"
    assert result.errors[0].code == "ERR_VALIDATION"


def test_skills_memory_list_passes_source_filter_validation() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "list", source_id=" ")

    assert result.status == "error"
    assert result.data["skill_memory"]["status"] == "blocked"
    assert result.errors[0].code == "ERR_VALIDATION"


def test_skills_memory_read_blocks_unknown_identifier() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    result = skills_memory(repo_root, "read", query="not-a-real-memory-entry")

    assert result.status == "error"
    payload = result.data["skill_memory"]
    assert payload["status"] == "blocked"
    assert payload["mode"] == "read"
    assert payload["requested"] == "not-a-real-memory-entry"
    assert result.errors[0].code == "ERR_VALIDATION"
