from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import body_without_frontmatter


DETERMINISM_AUDIT_SCHEMA_VERSION = "skill-determinism-audit.v1"

DEFAULT_SKILL_ROOTS: tuple[str, ...] = (
    "Skills",
    "Plugins/skill-factory/skills",
    "skills-system",
)

_EXCLUDED_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "cache",
    "fixtures",
    "budget-archive",
    "node_modules",
}

_OLD_LENS_REFERENCES = (
    "software-literature-expert-lens-pack.md",
    "software-literature-skill-expertise-map.md",
    "openai-cookbook-expert-lens-pack.md",
    "openai-cookbook-skill-expertise-map.md",
    "coding_lens",
    "testing_lens",
)

_STRUCTURED_OUTPUT_SIGNALS = (
    "schema_version",
    "structured output",
    "structured outputs",
    "output_contract",
    "schema-bound",
    "return schema",
)

_VALIDATION_SIGNALS = (
    "run validation",
    "rerun validation",
    "validation evidence",
    "validate with",
    "must pass",
)


def audit_skill_determinism(
    repo_root: Path,
    *,
    scope: str = "skills",
    paths: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    skill_files = _resolve_skill_files(repo_root, scope=scope, paths=paths)
    candidates: list[dict[str, Any]] = []
    for skill_path in skill_files:
        text = skill_path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(text)
        body = body_without_frontmatter(text)
        relative_path = _repo_relative(repo_root, skill_path)
        candidates.extend(_description_candidates(relative_path, frontmatter))
        candidates.extend(_lens_candidates(relative_path, text))
        candidates.extend(_structured_output_candidates(relative_path, text))
        candidates.extend(_validation_command_candidates(relative_path, text))
        candidates.extend(_progressive_disclosure_candidates(repo_root, skill_path, body))

    candidates.sort(key=lambda item: (_priority_rank(item["priority"]), item["skill_path"], item["area"]))
    if limit is not None:
        candidates = candidates[:limit]

    by_area: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for candidate in candidates:
        by_area[candidate["area"]] = by_area.get(candidate["area"], 0) + 1
        by_priority[candidate["priority"]] = by_priority.get(candidate["priority"], 0) + 1

    return {
        "schema_version": DETERMINISM_AUDIT_SCHEMA_VERSION,
        "status": "pass",
        "scope": scope,
        "summary": {
            "skills_scanned": len(skill_files),
            "candidate_count": len(candidates),
            "by_area": by_area,
            "by_priority": by_priority,
        },
        "candidates": candidates,
    }


def _resolve_skill_files(repo_root: Path, *, scope: str, paths: list[str] | None) -> list[Path]:
    if paths:
        result: list[Path] = []
        for raw_path in paths:
            path = (repo_root / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
            if path.is_dir():
                candidate = path / "SKILL.md"
                if candidate.exists():
                    result.append(candidate)
                continue
            if path.name == "SKILL.md" and path.exists():
                result.append(path)
        return sorted(set(result))
    if scope != "skills":
        raise ValueError(f"Unsupported determinism audit scope: {scope}")
    skill_files: list[Path] = []
    for root_name in DEFAULT_SKILL_ROOTS:
        root = repo_root / root_name
        if not root.exists():
            continue
        for skill_path in root.rglob("SKILL.md"):
            if _is_excluded(skill_path.relative_to(repo_root)):
                continue
            skill_files.append(skill_path.resolve())
    return sorted(skill_files)


def _description_candidates(skill_path: str, frontmatter: dict[str, str]) -> list[dict[str, Any]]:
    description = frontmatter.get("description", "")
    if not description:
        return [
            _candidate(
                skill_path=skill_path,
                area="description_trigger_contract",
                priority="high",
                current_surface="missing",
                recommended_mechanism="frontmatter_validator",
                evidence=["frontmatter.description missing"],
                message="Skill has no description, so routing cannot be deterministically checked.",
            )
        ]
    candidates: list[dict[str, Any]] = []
    description_lower = description.lower()
    if "use this skill when" not in description_lower and "use when" not in description_lower:
        candidates.append(
            _candidate(
                skill_path=skill_path,
                area="description_trigger_contract",
                priority="high",
                current_surface="prompt_only",
                recommended_mechanism="frontmatter_validator",
                evidence=["frontmatter.description"],
                message="Description does not include an explicit trigger phrase such as 'Use this skill when'.",
            )
        )
    if "do not use" not in description_lower and "do not use for" not in description_lower:
        candidates.append(
            _candidate(
                skill_path=skill_path,
                area="description_boundary_contract",
                priority="medium",
                current_surface="prompt_only",
                recommended_mechanism="frontmatter_validator",
                evidence=["frontmatter.description"],
                message="Description does not declare an explicit boundary such as 'Do not use for'.",
            )
        )
    if len(description) > 250:
        candidates.append(
            _candidate(
                skill_path=skill_path,
                area="description_budget_contract",
                priority="medium",
                current_surface="prompt_only",
                recommended_mechanism="frontmatter_validator",
                evidence=[f"frontmatter.description length={len(description)}"],
                message="Description exceeds the 250-character routing budget candidate.",
            )
        )
    return candidates


def _lens_candidates(skill_path: str, text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for signal in _OLD_LENS_REFERENCES:
        if signal in text:
            candidates.append(
                _candidate(
                    skill_path=skill_path,
                    area="lens_migration_contract",
                    priority="medium",
                    current_surface="skill_local_reference",
                    recommended_mechanism="sdk_lens_registry",
                    evidence=[signal],
                    message="Skill directly references a lens pack or lens token that can move behind the shared SDK lens selector.",
                )
            )
            break
    return candidates


def _structured_output_candidates(skill_path: str, text: str) -> list[dict[str, Any]]:
    text_lower = text.lower()
    has_signal = any(signal in text_lower for signal in _STRUCTURED_OUTPUT_SIGNALS)
    if not has_signal:
        return []
    has_schema_ref = "schema.json" in text_lower or "schemas/" in text_lower or "contract.yaml" in text_lower
    if has_schema_ref:
        return []
    return [
        _candidate(
            skill_path=skill_path,
            area="output_schema_contract",
            priority="high",
            current_surface="prompt_only",
            recommended_mechanism="schema_or_fixture_validator",
            evidence=["structured output signal without schema reference"],
            message="Skill asks for structured output but does not point to a machine-checkable schema or contract.",
        )
    ]


def _validation_command_candidates(skill_path: str, text: str) -> list[dict[str, Any]]:
    text_lower = text.lower()
    if not any(signal in text_lower for signal in _VALIDATION_SIGNALS):
        return []
    has_exact_command = bool(re.search(r"\x60(?:\.\/|python3 |uv |bash |npm |pnpm |yarn |bun )[^\x60]+\x60", text))
    if has_exact_command:
        return []
    return [
        _candidate(
            skill_path=skill_path,
            area="validation_command_contract",
            priority="high",
            current_surface="prompt_only",
            recommended_mechanism="command_validator",
            evidence=["validation prose without exact command"],
            message="Skill references validation but does not include an exact command for agents to run or verify.",
        )
    ]


def _progressive_disclosure_candidates(repo_root: Path, skill_path: Path, body: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    relative_path = _repo_relative(repo_root, skill_path)
    line_count = len(body.splitlines())
    if line_count > 220:
        candidates.append(
            _candidate(
                skill_path=relative_path,
                area="progressive_disclosure_budget",
                priority="medium",
                current_surface="prompt_only",
                recommended_mechanism="skill_size_validator",
                evidence=[f"body_lines={line_count}"],
                message="Skill entrypoint is large enough that detail may belong in references with explicit links.",
            )
        )
    for link in _markdown_links(body):
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (skill_path.parent / link).resolve()
        if not target.exists():
            candidates.append(
                _candidate(
                    skill_path=relative_path,
                    area="reference_integrity_contract",
                    priority="high",
                    current_surface="prompt_only",
                    recommended_mechanism="reference_link_validator",
                    evidence=[link],
                    message="Skill links to a local reference path that does not exist.",
                )
            )
    return candidates


def _candidate(
    *,
    skill_path: str,
    area: str,
    priority: str,
    current_surface: str,
    recommended_mechanism: str,
    evidence: list[str],
    message: str,
) -> dict[str, Any]:
    return {
        "skill_path": skill_path,
        "area": area,
        "priority": priority,
        "current_surface": current_surface,
        "recommended_mechanism": recommended_mechanism,
        "evidence": evidence,
        "autofix_safe": False,
        "message": message,
    }


def _parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        _start, frontmatter_text, _body = text.split("---", 2)
    except ValueError:
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_simple_frontmatter(frontmatter_text)
    loaded = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(loaded, dict):
        return {}
    return {str(key): _normalise_scalar(value) for key, value in loaded.items()}


def _parse_simple_frontmatter(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    current_key: str | None = None
    folded: list[str] = []
    for line in text.splitlines():
        if current_key and (line.startswith(" ") or line.startswith("\t")):
            folded.append(line.strip())
            continue
        if current_key:
            values[current_key] = " ".join(folded).strip()
            current_key = None
            folded = []
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", "|"}:
            current_key = key
            folded = []
        else:
            values[key] = value.strip("\"'")
    if current_key:
        values[current_key] = " ".join(folded).strip()
    return values


def _normalise_scalar(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    return str(value)


def _markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def _is_excluded(path: Path) -> bool:
    return any(part in _EXCLUDED_PATH_PARTS for part in path.parts)


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _priority_rank(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)
