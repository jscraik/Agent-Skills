from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from ask.skills_sdk.contracts import read_skill_frontmatter_fields
from ask.skills_sdk.risk import build_risk_classification


SKILL_IR_SCHEMA_VERSION = "skills-sdk.skill-ir.v0"
SKILL_IR_SCHEMA_URI = "https://jscraik.local/agent-skills/schemas/skills-sdk/skill-ir.v0.schema.json"
SKILL_IR_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"]

_HEADING_RE = re.compile(r"^#+\s+")


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _skill_root_for(source_path: Path) -> Path:
    return source_path.parent if source_path.name == "SKILL.md" else source_path


def _iter_files(root: Path, dirname: str, repo_root: Path) -> list[str]:
    base = root / dirname
    if not base.is_dir():
        return []
    return sorted(
        _repo_relative(repo_root, path)
        for path in base.rglob("*")
        if path.is_file()
    )


def _body_without_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def _first_paragraph(body: str) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if _HEADING_RE.match(line):
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs[0] if paragraphs else "No procedure summary declared."


def _normalized_list(value: Any) -> list[str]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return sorted(str(item) for item in value if str(item).strip())
    return [str(value)]


def _identity_from_frontmatter(frontmatter: dict[str, Any], skill_root: Path) -> dict[str, str]:
    name = str(frontmatter.get("name") or skill_root.name).strip() or skill_root.name
    version = str(frontmatter.get("version") or frontmatter.get("metadata", {}).get("version") or "0.1.0").strip()
    return {
        "id": name,
        "name": name,
        "version": version or "0.1.0",
    }


def _filesystem_permission(runtime_needs: list[str]) -> str:
    return "write" if any("write" in item.lower() for item in runtime_needs) else "read"


def _network_permission(normalized_runtime_needs: list[str], body: str) -> str:
    body_lower = body.lower()
    has_restricted_signal = (
        "http://" in body_lower
        or "https://" in body_lower
        or any(item == "network" or item.startswith("network:") for item in normalized_runtime_needs)
    )
    if any(item in {"network:open", "network:unrestricted"} for item in normalized_runtime_needs):
        return "open"
    return "restricted" if has_restricted_signal else "none"


def _secrets_permission(runtime_needs: list[str], body: str) -> str:
    if any("raw_secret" in item.lower() for item in runtime_needs):
        return "raw"
    body_lower = body.lower()
    return "handles" if "secret" in body_lower or "credential" in body_lower else "none"


def _permissions(frontmatter: dict[str, Any], body: str, scripts: list[str]) -> dict[str, Any]:
    runtime_needs = _normalized_list(frontmatter.get("runtime_needs"))
    normalized_runtime_needs = [item.lower().replace("_", ":") for item in runtime_needs]
    tools = sorted({
        *runtime_needs,
        *_normalized_list(frontmatter.get("tools")),
        *_normalized_list(frontmatter.get("commands")),
    })
    return {
        "filesystem": _filesystem_permission(runtime_needs),
        "network": _network_permission(normalized_runtime_needs, body),
        "secrets": _secrets_permission(runtime_needs, body),
        "tools": tools,
    }


def _risk_tier(source_kind: str) -> str:
    return {
        "docs_only": "local",
        "referenced": "team",
        "scripted": "scripted",
        "external": "privileged",
        "placeholder": "draft",
    }.get(source_kind, "draft")


def _source_block(repo_root: Path, skill_root: Path, source: Path) -> tuple[dict[str, Any], dict[str, list[str]]]:
    files = {
        "references": _iter_files(skill_root, "references", repo_root),
        "scripts": _iter_files(skill_root, "scripts", repo_root),
        "assets": _iter_files(skill_root, "assets", repo_root),
        "evals": _iter_files(skill_root, "evals", repo_root),
    }
    block = {
        "root": _repo_relative(repo_root, skill_root),
        "skill_md": _repo_relative(repo_root, source),
        "readme": _repo_relative(repo_root, skill_root / "README.md") if (skill_root / "README.md").is_file() else None,
        **files,
    }
    return block, files


def _behavior_block(frontmatter: dict[str, Any], body: str, query: str) -> dict[str, Any]:
    description = str(frontmatter.get("description") or query).strip() or query
    return {
        "trigger": description,
        "inputs": _normalized_list(frontmatter.get("inputs")),
        "outputs": _normalized_list(frontmatter.get("outputs")),
        "procedure_summary": _first_paragraph(body),
    }


def _risk_block(source: Path, frontmatter: dict[str, Any], body: str) -> dict[str, Any]:
    risk = build_risk_classification(source, frontmatter, body)
    source_kind = str(risk["source_kind"])
    return {
        "tier": _risk_tier(source_kind),
        "reasons": [f"source_kind:{source_kind}"],
        "source_kind": source_kind,
    }


def build_skill_ir(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    """Build the read-only SkillIR.v0 spine for a canonical skill source."""
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    skill_root = _skill_root_for(source)
    text = source.read_text(encoding="utf-8")
    body = _body_without_frontmatter(text)
    frontmatter = read_skill_frontmatter_fields(source)
    source_block, files = _source_block(repo_root, skill_root, source)

    return {
        "schema_version": SKILL_IR_SCHEMA_VERSION,
        "schema_uri": SKILL_IR_SCHEMA_URI,
        "identity": _identity_from_frontmatter(frontmatter, skill_root),
        "source": source_block,
        "behavior": _behavior_block(frontmatter, body, query),
        "permissions": _permissions(frontmatter, body, files["scripts"]),
        "risk": _risk_block(source, frontmatter, body),
        "evidence": {
            "checks": [f"./bin/ask sdk ir build {query} --json --robot"],
            "receipts": [],
        },
        "mutation_performed": False,
        "acceptance_trace": SKILL_IR_ACCEPTANCE_TRACE,
    }
