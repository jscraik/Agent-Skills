from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ask.skills_sdk.schema_validation import validate_payload_against_schema


DEFAULT_REGISTRY_RELATIVE_PATH = Path("Infrastructure/references/lenses/lenses.registry.yaml")
LENS_SCHEMA_RELATIVE_PATH = Path("Infrastructure/references/lenses/schemas/lens.schema.json")
LENS_REGISTRY_SCHEMA_RELATIVE_PATH = Path("Infrastructure/references/lenses/schemas/lens-registry.schema.json")
LENS_SELECTION_SCHEMA_VERSION = "skill-lens-selection.v1"
LENS_CATALOG_VALIDATION_SCHEMA_VERSION = "skill-lens-catalog-validation.v1"
LENS_REGISTRY_SCHEMA_VERSION = "skill-lens-registry.v1"

KNOWN_TASK_INTENTS: tuple[str, ...] = (
    "skill_authoring",
    "documentation_review",
    "reference_design",
    "agent_workflow_design",
    "sdk_contract_review",
    "validation_review",
    "refactor_plan",
    "repo_hygiene",
    "architecture_review",
    "security_review",
    "data_integrity_review",
    "api_contract_review",
    "isolated_bugfix",
    "pure_visual_polish",
    "pure_ui_copy",
)

_LENS_ID_RE = re.compile(r"^lens\.[a-z0-9]+(?:-[a-z0-9]+)*$")
_REQUIRED_LENS_SECTIONS = ("Review Questions", "Failure Modes")
_DEFAULT_MAX_LENSES = 4


class LensCatalogError(ValueError):
    """Raised when the shared SDK lens catalog cannot be loaded."""


def list_lenses(repo_root: Path, *, registry_path: str | Path | None = None) -> dict[str, Any]:
    registry, catalog_dir, _registry_file = _load_registry(repo_root, registry_path=registry_path)
    validation = validate_lens_catalog(repo_root, registry_path=registry_path)
    lenses = []
    for entry in registry["lenses"]:
        lens_path = _safe_catalog_path(catalog_dir, entry["path"])
        frontmatter, _body = _read_frontmatter(lens_path)
        lenses.append(
            {
                "id": entry["id"],
                "title": frontmatter.get("title", entry["id"]),
                "path": _repo_relative(repo_root, lens_path),
                "status": frontmatter.get("status", "unknown"),
                "priority": entry.get("priority", frontmatter.get("priority", 0)),
                "triggers": _normalise_triggers(frontmatter.get("triggers", entry.get("triggers", {}))),
                "strengths": _string_list(frontmatter.get("strengths")),
                "avoid_when": _string_list(frontmatter.get("avoid_when")),
            }
        )
    return {
        "schema_version": LENS_REGISTRY_SCHEMA_VERSION,
        "status": validation["status"],
        "catalog_path": _repo_relative(repo_root, catalog_dir / "lenses.registry.yaml"),
        "summary": validation["summary"],
        "lenses": lenses,
    }


def explain_lens(repo_root: Path, lens_id: str, *, registry_path: str | Path | None = None) -> dict[str, Any]:
    registry, catalog_dir, _registry_file = _load_registry(repo_root, registry_path=registry_path)
    entry = _find_lens_entry(registry, lens_id)
    lens_path = _safe_catalog_path(catalog_dir, entry["path"])
    frontmatter, body = _read_frontmatter(lens_path)
    sections = _markdown_sections(body)
    return {
        "schema_version": "skill-lens-explanation.v1",
        "status": "pass",
        "id": lens_id,
        "title": frontmatter.get("title", lens_id),
        "path": _repo_relative(repo_root, lens_path),
        "lens_type": frontmatter.get("type"),
        "lens_status": frontmatter.get("status"),
        "priority": frontmatter.get("priority", entry.get("priority", 0)),
        "triggers": _normalise_triggers(frontmatter.get("triggers", entry.get("triggers", {}))),
        "strengths": _string_list(frontmatter.get("strengths")),
        "avoid_when": _string_list(frontmatter.get("avoid_when")),
        "pairs_well_with": _string_list(frontmatter.get("pairs_well_with")),
        "sections": sections,
    }


def validate_lens_catalog(repo_root: Path, *, registry_path: str | Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    lenses: list[dict[str, Any]] = []
    try:
        registry, catalog_dir, registry_file = _load_registry(repo_root, registry_path=registry_path)
    except LensCatalogError as exc:
        return _validation_payload(
            repo_root,
            registry_path=registry_path,
            status="fail",
            findings=[
                _finding(
                    severity="error",
                    code="catalog_load_failed",
                    path=str(registry_path or DEFAULT_REGISTRY_RELATIVE_PATH),
                    message=str(exc),
                    fix_suggestion="Fix the lens registry path or YAML shape.",
                )
            ],
            lenses=[],
        )

    registry_ids = [entry.get("id") for entry in registry.get("lenses", []) if isinstance(entry, dict)]
    _validate_registry_schema(
        repo_root=repo_root,
        registry=registry,
        registry_file=registry_file,
        findings=findings,
    )
    duplicate_ids = {lens_id for lens_id in registry_ids if registry_ids.count(lens_id) > 1}
    for lens_id in sorted(duplicate_ids):
        findings.append(
            _finding(
                severity="error",
                code="duplicate_lens_id",
                path=_repo_relative(repo_root, registry_file),
                message=f"Lens id {lens_id!r} appears more than once.",
                fix_suggestion="Use one canonical lens id per shared lens.",
            )
        )

    for entry in registry.get("lenses", []):
        if not isinstance(entry, dict):
            findings.append(
                _finding(
                    severity="error",
                    code="invalid_registry_entry",
                    path=_repo_relative(repo_root, registry_file),
                    message="Every registry lens entry must be a mapping.",
                    fix_suggestion="Replace the malformed entry with id, path, priority, and triggers fields.",
                )
            )
            continue

        lens_id = str(entry.get("id", ""))
        path_value = str(entry.get("path", ""))
        lens_record = {
            "id": lens_id,
            "path": path_value,
            "status": "unknown",
            "priority": entry.get("priority"),
        }
        lenses.append(lens_record)

        if not _LENS_ID_RE.match(lens_id):
            findings.append(
                _finding(
                    severity="error",
                    code="invalid_lens_id",
                    path=_repo_relative(repo_root, registry_file),
                    message=f"Lens id {lens_id!r} must use the lens.<kebab-name> form.",
                    fix_suggestion="Rename the id to a stable lens.<kebab-name> identifier.",
                )
            )

        try:
            lens_path = _safe_catalog_path(catalog_dir, path_value)
        except LensCatalogError as exc:
            findings.append(
                _finding(
                    severity="error",
                    code="unsafe_lens_path",
                    path=_repo_relative(repo_root, registry_file),
                    message=str(exc),
                    fix_suggestion="Keep lens paths inside Infrastructure/references/lenses.",
                )
            )
            continue

        if not lens_path.exists():
            findings.append(
                _finding(
                    severity="error",
                    code="missing_lens_file",
                    path=_repo_relative(repo_root, lens_path),
                    message=f"Registry entry {lens_id!r} points to a missing file.",
                    fix_suggestion="Create the lens file or remove the registry entry.",
                )
            )
            continue

        try:
            frontmatter, body = _read_frontmatter(lens_path)
        except LensCatalogError as exc:
            findings.append(
                _finding(
                    severity="error",
                    code="invalid_lens_frontmatter",
                    path=_repo_relative(repo_root, lens_path),
                    message=str(exc),
                    fix_suggestion="Add YAML frontmatter with the required lens metadata fields.",
                )
            )
            continue

        lens_record["status"] = frontmatter.get("status", "unknown")
        lens_record["priority"] = frontmatter.get("priority", entry.get("priority"))
        _validate_lens_frontmatter(
            repo_root=repo_root,
            lens_id=lens_id,
            lens_path=lens_path,
            frontmatter=frontmatter,
            body=body,
            registry_entry=entry,
            registry_ids=set(str(item) for item in registry_ids),
            findings=findings,
        )

    status = "fail" if any(finding["severity"] == "error" for finding in findings) else "pass"
    return _validation_payload(
        repo_root,
        registry_path=registry_file,
        status=status,
        findings=findings,
        lenses=lenses,
    )


def select_lenses(
    repo_root: Path,
    *,
    prompt: str,
    task_intent: str | None = None,
    repo_files: list[str] | None = None,
    max_lenses: int = _DEFAULT_MAX_LENSES,
    skill: str | None = None,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    if max_lenses < 1:
        raise LensCatalogError("max_lenses must be at least 1.")
    resolved_intent = _normalise_intent(task_intent) if task_intent else infer_task_intent(prompt, repo_files or [])
    registry, catalog_dir, _registry_file = _load_registry(repo_root, registry_path=registry_path)
    validation = validate_lens_catalog(repo_root, registry_path=registry_path)
    if validation["status"] != "pass":
        return {
            "schema_version": LENS_SELECTION_SCHEMA_VERSION,
            "status": "fail",
            "skill": skill,
            "task_intent": resolved_intent,
            "max_lenses": max_lenses,
            "selected_lenses": [],
            "not_selected": [],
            "validation": validation,
        }

    scored: list[dict[str, Any]] = []
    prompt_lower = prompt.lower()
    file_values = [value for value in repo_files or [] if value]
    file_lower = [value.lower() for value in file_values]
    for entry in registry["lenses"]:
        lens_path = _safe_catalog_path(catalog_dir, entry["path"])
        frontmatter, _body = _read_frontmatter(lens_path)
        triggers = _normalise_triggers(frontmatter.get("triggers", entry.get("triggers", {})))
        score, reasons = _score_lens(
            prompt_lower=prompt_lower,
            task_intent=resolved_intent,
            repo_files=file_lower,
            triggers=triggers,
            priority=int(frontmatter.get("priority", entry.get("priority", 0)) or 0),
        )
        status = str(frontmatter.get("status", "stable"))
        row = {
            "id": entry["id"],
            "title": frontmatter.get("title", entry["id"]),
            "path": _repo_relative(repo_root, lens_path),
            "score": score,
            "reasons": reasons,
            "status": status,
        }
        scored.append(row)

    eligible = [row for row in scored if row["status"] != "deprecated" and row["score"] > 0]
    eligible.sort(key=lambda row: (-int(row["score"]), str(row["id"])))
    selected = eligible[:max_lenses]
    selected_ids = {row["id"] for row in selected}
    not_selected = []
    for row in sorted(scored, key=lambda item: str(item["id"])):
        if row["id"] in selected_ids:
            continue
        reason = "score_below_selected_threshold"
        if row["status"] == "deprecated":
            reason = "deprecated"
        elif row["score"] == 0:
            reason = "no_matching_trigger_signal"
        not_selected.append(
            {
                "id": row["id"],
                "path": row["path"],
                "score": row["score"],
                "reason": reason,
            }
        )

    return {
        "schema_version": LENS_SELECTION_SCHEMA_VERSION,
        "status": "pass",
        "skill": skill,
        "task_intent": resolved_intent,
        "max_lenses": max_lenses,
        "selected_lenses": [
            {
                "id": row["id"],
                "path": row["path"],
                "score": row["score"],
                "reasons": row["reasons"],
            }
            for row in selected
        ],
        "not_selected": not_selected,
    }


def infer_task_intent(prompt: str, repo_files: list[str]) -> str:
    text = f"{prompt} {' '.join(repo_files)}".lower()
    if any(signal in text for signal in ("skill.md", "skill ", "heading", "frontmatter", "description")):
        return "skill_authoring"
    if any(signal in text for signal in ("schema", "contract", "sdk", "api", "cli")):
        return "sdk_contract_review"
    if any(signal in text for signal in ("test", "fixture", "pytest", "ci", "eval", "validation")):
        return "validation_review"
    if any(signal in text for signal in ("readme", "docs", "guide", "documentation")):
        return "documentation_review"
    if any(signal in text for signal in ("handoff", "receipt", "proof", "evidence", "closeout")):
        return "agent_workflow_design"
    return "documentation_review"


def _validate_lens_frontmatter(
    *,
    repo_root: Path,
    lens_id: str,
    lens_path: Path,
    frontmatter: dict[str, Any],
    body: str,
    registry_entry: dict[str, Any],
    registry_ids: set[str],
    findings: list[dict[str, Any]],
) -> None:
    schema_path = repo_root / LENS_SCHEMA_RELATIVE_PATH
    if schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(
                _finding(
                    severity="error",
                    code="invalid_lens_schema_json",
                    path=_repo_relative(repo_root, schema_path),
                    message=str(exc),
                    fix_suggestion="Fix the JSON schema before validating lens contracts.",
                )
            )
        else:
            schema_result = validate_payload_against_schema(
                frontmatter,
                schema,
                {"lens.schema.json": schema},
                schema_path=schema_path,
                payload_source=_repo_relative(repo_root, lens_path),
                truth_lane="sdk_lens_catalog",
            )
            for diagnostic in schema_result.diagnostics:
                findings.append(
                    _finding(
                        severity="error",
                        code="lens_schema_invalid",
                        path=diagnostic.payload_source,
                        message=f"{diagnostic.json_path}: {diagnostic.message}",
                        fix_suggestion="Update the lens frontmatter to match schemas/lens.schema.json.",
                    )
                )

    if frontmatter.get("id") != lens_id:
        findings.append(
            _finding(
                severity="error",
                code="lens_id_mismatch",
                path=_repo_relative(repo_root, lens_path),
                message=f"Frontmatter id {frontmatter.get('id')!r} does not match registry id {lens_id!r}.",
                fix_suggestion="Use one stable id in both the registry and lens file.",
            )
        )
    if frontmatter.get("type") != "expert_lens":
        findings.append(
            _finding(
                severity="error",
                code="invalid_lens_type",
                path=_repo_relative(repo_root, lens_path),
                message="Lens type must be expert_lens.",
                fix_suggestion="Set type: expert_lens in the frontmatter.",
            )
        )

    triggers = _normalise_triggers(frontmatter.get("triggers", registry_entry.get("triggers", {})))
    if not triggers["keywords"] or not triggers["task_intents"]:
        findings.append(
            _finding(
                severity="error",
                code="weak_lens_triggers",
                path=_repo_relative(repo_root, lens_path),
                message="Lens triggers must include at least one keyword and one task intent.",
                fix_suggestion="Add concrete activation keywords and task_intents.",
            )
        )
    unknown_intents = sorted(set(triggers["task_intents"]) - set(KNOWN_TASK_INTENTS))
    if unknown_intents:
        findings.append(
            _finding(
                severity="warning",
                code="unknown_task_intent",
                path=_repo_relative(repo_root, lens_path),
                message=f"Lens uses task intents not registered in SDK vocabulary: {unknown_intents}.",
                fix_suggestion="Add the intent to KNOWN_TASK_INTENTS or use an existing generic intent.",
            )
        )

    for paired_id in _string_list(frontmatter.get("pairs_well_with")):
        if paired_id not in registry_ids:
            findings.append(
                _finding(
                    severity="warning",
                    code="unknown_paired_lens",
                    path=_repo_relative(repo_root, lens_path),
                    message=f"pairs_well_with references unknown lens {paired_id!r}.",
                    fix_suggestion="Register the paired lens or remove the stale reference.",
                )
            )

    headings = _markdown_headings(body)
    h1_headings = [heading for level, heading in headings if level == 1]
    if len(h1_headings) != 1:
        findings.append(
            _finding(
                severity="error",
                code="missing_single_h1",
                path=_repo_relative(repo_root, lens_path),
                message="Lens body must contain exactly one H1 heading.",
                fix_suggestion="Add one top-level heading matching the lens title.",
            )
        )
    for required in _REQUIRED_LENS_SECTIONS:
        if not any(level == 2 and heading == required for level, heading in headings):
            findings.append(
                _finding(
                    severity="error",
                    code="missing_required_lens_section",
                    path=_repo_relative(repo_root, lens_path),
                    message=f"Lens body is missing required section: {required}.",
                    fix_suggestion=f"Add a ## {required} section.",
                )
            )


def _validate_registry_schema(
    *,
    repo_root: Path,
    registry: dict[str, Any],
    registry_file: Path,
    findings: list[dict[str, Any]],
) -> None:
    schema_path = repo_root / LENS_REGISTRY_SCHEMA_RELATIVE_PATH
    if not schema_path.exists():
        findings.append(
            _finding(
                severity="warning",
                code="missing_registry_schema",
                path=_repo_relative(repo_root, schema_path),
                message="Lens registry schema file is missing.",
                fix_suggestion="Restore schemas/lens-registry.schema.json so registry shape is deterministic.",
            )
        )
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(
            _finding(
                severity="error",
                code="invalid_registry_schema_json",
                path=_repo_relative(repo_root, schema_path),
                message=str(exc),
                fix_suggestion="Fix the JSON schema before validating the lens registry.",
            )
        )
        return
    schema_result = validate_payload_against_schema(
        registry,
        schema,
        {"lens-registry.schema.json": schema},
        schema_path=schema_path,
        payload_source=_repo_relative(repo_root, registry_file),
        truth_lane="sdk_lens_registry",
    )
    for diagnostic in schema_result.diagnostics:
        findings.append(
            _finding(
                severity="error",
                code="lens_registry_schema_invalid",
                path=diagnostic.payload_source,
                message=f"{diagnostic.json_path}: {diagnostic.message}",
                fix_suggestion="Update the registry to match schemas/lens-registry.schema.json.",
            )
        )


def _score_lens(
    *,
    prompt_lower: str,
    task_intent: str,
    repo_files: list[str],
    triggers: dict[str, list[str]],
    priority: int,
) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if task_intent in triggers["task_intents"]:
        score += 50
        reasons.append(f"task_intent:{task_intent}")
    for keyword in triggers["keywords"]:
        keyword_lower = keyword.lower()
        if keyword_lower and keyword_lower in prompt_lower:
            score += 10
            reasons.append(f"keyword:{keyword}")
    for file_signal in triggers["file_signals"]:
        file_signal_lower = file_signal.lower()
        if any(_file_signal_matches(file_signal_lower, repo_file) for repo_file in repo_files):
            score += 8
            reasons.append(f"file_signal:{file_signal}")
    if score > 0:
        priority_bonus = max(0, min(priority, 100)) // 10
        score += priority_bonus
        reasons.append(f"priority_bonus:{priority_bonus}")
    return score, reasons


def _file_signal_matches(file_signal: str, repo_file: str) -> bool:
    if file_signal.endswith("/"):
        return file_signal in repo_file or repo_file.startswith(file_signal)
    return repo_file.endswith(file_signal) or file_signal in repo_file


def _validation_payload(
    repo_root: Path,
    *,
    registry_path: str | Path | None,
    status: str,
    findings: list[dict[str, Any]],
    lenses: list[dict[str, Any]],
) -> dict[str, Any]:
    by_severity: dict[str, int] = {}
    for finding in findings:
        severity = str(finding.get("severity", "unknown"))
        by_severity[severity] = by_severity.get(severity, 0) + 1
    if isinstance(registry_path, Path):
        catalog_path = _repo_relative(repo_root, registry_path)
    else:
        catalog_path = str(registry_path or DEFAULT_REGISTRY_RELATIVE_PATH)
    return {
        "schema_version": LENS_CATALOG_VALIDATION_SCHEMA_VERSION,
        "status": status,
        "catalog_path": catalog_path,
        "summary": {
            "lens_count": len(lenses),
            "finding_count": len(findings),
            "by_severity": by_severity,
        },
        "findings": findings,
        "lenses": lenses,
    }


def _finding(
    *,
    severity: str,
    code: str,
    path: str,
    message: str,
    fix_suggestion: str,
) -> dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "path": path,
        "message": message,
        "fix_suggestion": fix_suggestion,
    }


def _load_registry(repo_root: Path, *, registry_path: str | Path | None = None) -> tuple[dict[str, Any], Path, Path]:
    registry_file = _resolve_repo_path(repo_root, registry_path or DEFAULT_REGISTRY_RELATIVE_PATH)
    if not registry_file.exists():
        raise LensCatalogError(f"Lens registry does not exist: {registry_file}")
    loaded = _load_yaml_mapping(registry_file)
    lenses = loaded.get("lenses")
    if not isinstance(lenses, list):
        raise LensCatalogError("Lens registry must contain a top-level lenses list.")
    for entry in lenses:
        if not isinstance(entry, dict):
            raise LensCatalogError("Lens registry entries must be mappings.")
        for key in ("id", "path", "triggers"):
            if key not in entry:
                raise LensCatalogError(f"Lens registry entry is missing required key: {key}")
    return loaded, registry_file.parent, registry_file


def _find_lens_entry(registry: dict[str, Any], lens_id: str) -> dict[str, Any]:
    for entry in registry["lenses"]:
        if entry["id"] == lens_id:
            return entry
    raise LensCatalogError(f"Unknown lens id: {lens_id}")


def _read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise LensCatalogError("Lens file must start with YAML frontmatter.")
    _start, frontmatter_text, body = text.split("---", 2)
    return _load_yaml_text_mapping(frontmatter_text, source=path), body.lstrip("\n")


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    return _load_yaml_text_mapping(path.read_text(encoding="utf-8"), source=path)


def _load_yaml_text_mapping(text: str, *, source: Path | str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        loaded = _parse_minimal_yaml(text)
    else:
        loaded = yaml.safe_load(text) or {}
    if not isinstance(loaded, dict):
        raise LensCatalogError(f"Expected YAML mapping in {source}.")
    return loaded


def _parse_minimal_yaml(text: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    def parent_for(indent: int) -> Any:
        while stack and stack[-1][0] >= indent:
            stack.pop()
        return stack[-1][1]

    for index, line in enumerate(lines):
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        parent = parent_for(indent)
        if stripped.startswith("- "):
            if not isinstance(parent, list):
                raise LensCatalogError("Minimal YAML parser only supports list items under list keys.")
            item_text = stripped[2:].strip()
            if ":" in item_text:
                key, value = item_text.split(":", 1)
                item: dict[str, Any] = {key.strip(): _parse_yaml_scalar(value.strip())}
                parent.append(item)
                stack.append((indent, item))
            else:
                parent.append(_parse_yaml_scalar(item_text))
            continue
        if ":" not in stripped:
            raise LensCatalogError("Minimal YAML parser found an unsupported line.")
        key, value = stripped.split(":", 1)
        target = parent
        if not isinstance(target, dict):
            raise LensCatalogError("Minimal YAML parser found a mapping under a scalar list.")
        clean_key = key.strip()
        clean_value = value.strip()
        if clean_value:
            target[clean_key] = _parse_yaml_scalar(clean_value)
            continue
        next_container: list[Any] | dict[str, Any] = [] if _next_nonempty_is_list(lines, index) else {}
        target[clean_key] = next_container
        stack.append((indent, next_container))
    return root


def _next_nonempty_is_list(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    return lines[index + 1].lstrip().startswith("- ")


def _parse_yaml_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [
            item.strip().strip("\"'")
            for item in value[1:-1].split(",")
            if item.strip()
        ]
    if value in {"true", "false"}:
        return value == "true"
    if value.isdigit():
        return int(value)
    return value.strip("\"'")


def _resolve_repo_path(repo_root: Path, path: str | Path) -> Path:
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.resolve()
    return (repo_root / path_obj).resolve()


def _safe_catalog_path(catalog_dir: Path, relative_path: str) -> Path:
    if not relative_path:
        raise LensCatalogError("Lens path cannot be empty.")
    resolved = (catalog_dir / relative_path).resolve()
    try:
        resolved.relative_to(catalog_dir.resolve())
    except ValueError as exc:
        raise LensCatalogError(f"Lens path escapes catalog directory: {relative_path}") from exc
    return resolved


def _normalise_intent(task_intent: str) -> str:
    value = task_intent.strip().replace("-", "_")
    if value not in KNOWN_TASK_INTENTS:
        raise LensCatalogError(f"Unknown task intent: {task_intent}")
    return value


def _normalise_triggers(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {"keywords": [], "task_intents": [], "file_signals": []}
    return {
        "keywords": _string_list(value.get("keywords")),
        "task_intents": [_normalise_task_intent_value(item) for item in _string_list(value.get("task_intents"))],
        "file_signals": _string_list(value.get("file_signals")),
    }


def _normalise_task_intent_value(value: str) -> str:
    return value.strip().replace("-", "_")


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _markdown_headings(body: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        marker, _, title = stripped.partition(" ")
        if marker and set(marker) == {"#"}:
            headings.append((len(marker), title.strip()))
    return headings


def _markdown_sections(body: str) -> list[dict[str, Any]]:
    return [
        {"level": level, "title": title}
        for level, title in _markdown_headings(body)
    ]


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)
