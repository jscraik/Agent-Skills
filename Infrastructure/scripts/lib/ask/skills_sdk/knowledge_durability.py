from __future__ import annotations

from pathlib import Path
from typing import Any


KNOWLEDGE_DURABILITY_SCHEMA_VERSION = "skills-sdk.knowledge-durability-receipt.v0"
KNOWLEDGE_DURABILITY_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/knowledge-durability-receipt.v0.schema.json"
)
KNOWLEDGE_DURABILITY_ACCEPTANCE_TRACE = ["FR-008", "SA-003", "VP-032"]
KNOWLEDGE_MANIFEST = "references/knowledge-capsule.manifest.yaml"
KNOWLEDGE_ROUTING = "references/knowledge-capsule-routing.md"


def build_knowledge_durability_receipt(repo_root: Path, *, skill: str) -> dict[str, Any]:
    skill_dir = _skill_dir(repo_root, skill)
    durable_dir = _durable_source_for_cache(repo_root, skill_dir)
    cache_owned = durable_dir is not None
    checks = [
        _repo_local_check(repo_root, skill_dir),
        _skill_source_shape_check(skill_dir),
        _knowledge_files_check(skill_dir),
    ]
    if cache_owned:
        assert durable_dir is not None
        checks.append(_durable_source_check(durable_dir))
        checks.append(_knowledge_files_check(durable_dir, check_id="durable_knowledge_files"))
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "pass" if not blockers else "blocked"
    return {
        "schema_version": KNOWLEDGE_DURABILITY_SCHEMA_VERSION,
        "schema_uri": KNOWLEDGE_DURABILITY_SCHEMA_URI,
        "status": status,
        "operation": "knowledge_durability_preview",
        "skill_path": _repo_label(repo_root, skill_dir),
        "cache_owned": cache_owned,
        "durable_source_path": _repo_label(repo_root, durable_dir) if durable_dir else None,
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": KNOWLEDGE_DURABILITY_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Knowledge durability check {status} for {_repo_label(repo_root, skill_dir)}; "
            "cache-owned skill updates require matching durable plugin source evidence."
        ),
    }


def _skill_dir(repo_root: Path, skill: str) -> Path:
    path = Path(skill).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    if path.name == "SKILL.md":
        return path.parent.resolve(strict=False)
    return path.resolve(strict=False)


def _durable_source_for_cache(repo_root: Path, skill_dir: Path) -> Path | None:
    relative = _cache_relative(repo_root, skill_dir)
    if relative is None:
        return None
    parts = relative.parts
    if len(parts) >= 5 and parts[3] == "skills":
        plugin_id = parts[1]
        skill_name = parts[4]
    elif len(parts) >= 4 and parts[2] == "skills":
        plugin_id = parts[0]
        skill_name = parts[3]
    else:
        return None
    return (repo_root / "plugins" / plugin_id / "skills" / skill_name).resolve(strict=False)


def _cache_relative(repo_root: Path, skill_dir: Path) -> Path | None:
    for cache_root in (repo_root / "plugins/cache", repo_root / "Plugins/cache"):
        try:
            return skill_dir.resolve(strict=False).relative_to(cache_root.resolve(strict=False))
        except ValueError:
            continue
    return None


def _repo_local_check(repo_root: Path, skill_dir: Path) -> dict[str, Any]:
    inside = skill_dir.is_relative_to(repo_root.resolve())
    return _check(
        "skill_path_repo_local",
        "pass" if inside else "blocker",
        "Knowledge durability checks only accept repo-local skill paths.",
        [_repo_label(repo_root, skill_dir)],
    )


def _durable_source_check(durable_dir: Path) -> dict[str, Any]:
    return _check(
        "durable_plugin_source_exists",
        "pass" if (durable_dir / "SKILL.md").is_file() else "blocker",
        "Cache-owned plugin skill updates must also exist in durable plugin source.",
        [durable_dir.as_posix()],
    )


def _skill_source_shape_check(skill_dir: Path) -> dict[str, Any]:
    skill_file = skill_dir / "SKILL.md"
    return _check(
        "skill_source_shape",
        "pass" if skill_dir.is_dir() and skill_file.is_file() else "blocker",
        "Knowledge durability checks require an existing skill directory with SKILL.md.",
        [skill_file.as_posix()],
    )


def _knowledge_files_check(skill_dir: Path, *, check_id: str = "knowledge_files_present") -> dict[str, Any]:
    manifest = skill_dir / KNOWLEDGE_MANIFEST
    routing = skill_dir / KNOWLEDGE_ROUTING
    missing = [path for path in (manifest, routing) if not path.is_file()]
    no_knowledge = not manifest.exists() and not routing.exists()
    status = "pass" if no_knowledge or not missing else "blocker"
    evidence = ["knowledge:not_declared"] if no_knowledge else [path.as_posix() for path in missing]
    return _check(
        check_id,
        status,
        "KnowledgeOS packages must carry both manifest and routing files when knowledge is declared.",
        evidence,
    )


def _repo_label(repo_root: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker" if status == "blocker" else "info",
        "message": message,
        "evidence": evidence,
    }
