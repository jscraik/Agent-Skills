from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_text_tokens import _token_set

def skill_markdown_text(skill_md: Path | None) -> str:
    """Return SKILL.md body text for contract discovery without raising."""
    if not skill_md or not skill_md.is_file():
        return ""
    try:
        return skill_md.read_text(encoding="utf-8")
    except OSError:
        return ""


def markdown_heading_declared(text: str, heading: str) -> bool:
    """Return whether a markdown heading with *heading* exists."""
    target = heading.strip().lower()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        title = stripped.lstrip("#").strip().lower()
        if title == target:
            return True
    return False


def markdown_section_body(text: str, heading: str) -> str:
    """Return the body for a markdown heading without following sibling sections."""
    target = heading.strip().lower()
    collecting = False
    heading_level = 0
    body: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip().lower()
            level = len(stripped) - len(stripped.lstrip("#"))
            if collecting and level <= heading_level:
                break
            if title == target:
                collecting = True
                heading_level = level
                continue
        if collecting:
            body.append(line)
    return "\n".join(body).strip()


def progressive_disclosure_reference_paths(body: str) -> list[str]:
    """Return referenced package paths declared in the progressive-disclosure section."""
    return [raw for raw in body.split("`")[1::2] if raw.startswith("references/")]


def package_local_regular_file(skill_md: Path | None, raw_path: str) -> bool:
    """Return whether a declared package path is a regular file under the skill package."""
    if not skill_md:
        return False
    path = Path(raw_path)
    if path.is_absolute() or "\\" in raw_path or ".." in path.parts:
        return False
    package_root = skill_md.parent
    candidate = package_root / path
    if _path_has_symlink_component(package_root, candidate):
        return False
    try:
        candidate.resolve(strict=True).relative_to(package_root.resolve())
    except (OSError, ValueError):
        return False
    return candidate.is_file()


def package_local_reference_path(raw_path: str) -> bool:
    """Return whether a manifest target path is a package-local reference path."""
    path = Path(raw_path)
    return (
        bool(raw_path.strip())
        and not path.is_absolute()
        and "\\" not in raw_path
        and ".." not in path.parts
        and path.parts[:1] == ("references",)
    )


def _path_has_symlink_component(root: Path, path: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    current = root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def missing_progressive_disclosure_references(
    skill_md: Path | None,
    reference_paths: list[str],
) -> list[str]:
    """Return progressive-disclosure references that are absent from the skill package."""
    return [raw for raw in reference_paths if not package_local_regular_file(skill_md, raw)]


def operating_model_format_contract(skill_md: Path | None, text: str) -> dict[str, Any]:
    """Return whether named workspace artifacts keep first-class format docs."""
    if not skill_md or not text:
        return {
            "artifacts_declared": [],
            "required_format_references": [],
            "present_format_references": [],
            "missing_format_references": [],
            "format_references_ready": False,
            "policy": (
                "Skills that name durable workspace artifacts must preserve their "
                "operating-model docs as package-local references instead of "
                "compressing them into SKILL.md."
            ),
        }

    artifacts: list[str] = []
    required: list[str] = []
    present: list[str] = []
    missing: list[str] = []
    for artifact, needles, reference_path in OPERATING_MODEL_FORMAT_DOCS:
        if not any(needle in text for needle in needles):
            continue
        artifacts.append(artifact)
        required.append(reference_path)
        if package_local_regular_file(skill_md, reference_path):
            present.append(reference_path)
        else:
            missing.append(reference_path)

    return {
        "artifacts_declared": artifacts,
        "required_format_references": required,
        "present_format_references": present,
        "missing_format_references": missing,
        "format_references_ready": bool(artifacts) and not missing,
        "policy": (
            "Skills that name durable workspace artifacts must preserve their "
            "operating-model docs as package-local references instead of "
            "compressing them into SKILL.md."
        ),
    }


def source_operating_model_contract(skill_md: Path | None, progressive_body: str) -> dict[str, Any]:
    """Return whether source operating-model context is preserved as routed references."""
    source_context_path = skill_md.parent / "references" / "source-context.yaml" if skill_md else None
    if not source_context_path or not source_context_path.is_file():
        return {
            "schema_version": "source-operating-model-preservation.v1",
            "status": "not_declared",
            "source_context_declared": False,
            "declared_references": [],
            "present_references": [],
            "missing_references": [],
            "missing_progressive_routes": [],
            "policy": (
                "When source-context declares operating-model source material, "
                "the package must preserve it as package-local references and route "
                "agents to it through Progressive Disclosure."
            ),
        }

    loaded, error = read_structured_reference(source_context_path)
    declared: list[str] = []
    missing: list[str] = []
    missing_routes: list[str] = []
    if error is None and isinstance(loaded, dict):
        references = loaded.get("references")
        if isinstance(references, list):
            for item in references:
                if not isinstance(item, dict):
                    continue
                kind = str(item.get("kind") or "").strip()
                path = str(item.get("path") or "").strip()
                if kind not in SOURCE_OPERATING_MODEL_KINDS or not path:
                    continue
                declared.append(path)
                if not package_local_regular_file(skill_md, path):
                    missing.append(path)
                quoted_path = f"`{path}`"
                if quoted_path not in progressive_body and path not in progressive_body:
                    missing_routes.append(path)
        for path in _source_operating_model_paths_from_text(source_context_path):
            if path in declared:
                continue
            declared.append(path)
            if not package_local_regular_file(skill_md, path):
                missing.append(path)
            quoted_path = f"`{path}`"
            if quoted_path not in progressive_body and path not in progressive_body:
                missing_routes.append(path)
    elif error is not None:
        missing.append("references/source-context.yaml")

    present = [path for path in declared if path not in missing]
    blocked = bool(missing or missing_routes)
    return {
        "schema_version": "source-operating-model-preservation.v1",
        "status": "blocked_validation" if blocked else ("pass" if declared else "not_declared"),
        "source_context_declared": True,
        "source_context_error": error,
        "declared_references": declared,
        "present_references": present,
        "missing_references": missing,
        "missing_progressive_routes": missing_routes,
        "policy": (
            "When source-context declares operating-model source material, "
            "the package must preserve it as package-local references and route "
            "agents to it through Progressive Disclosure."
        ),
    }


def _source_operating_model_paths_from_text(path: Path) -> list[str]:
    """Extract source operating-model paths from source-context.yaml without PyYAML."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    paths: list[str] = []
    current_path: str | None = None
    current_kind: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- path:"):
            if current_path and current_kind in SOURCE_OPERATING_MODEL_KINDS:
                paths.append(current_path)
            current_path = stripped.split(":", 1)[1].strip().strip("'\"")
            current_kind = None
            continue
        if stripped.startswith("kind:"):
            current_kind = stripped.split(":", 1)[1].strip().strip("'\"")
    if current_path and current_kind in SOURCE_OPERATING_MODEL_KINDS:
        paths.append(current_path)
    return [source_path for source_path in paths if source_path]


def progressive_disclosure_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> dict[str, Any]:
    """Return deterministic compaction/progressive-disclosure signals."""
    line_count = len(text.splitlines()) if text else 0
    body = markdown_section_body(text, "Progressive Disclosure")
    reference_paths = progressive_disclosure_reference_paths(body)
    missing = missing_progressive_disclosure_references(skill_md, reference_paths)
    existing_count = len(reference_paths) - len(missing)
    compact_entrypoint = bool(text) and line_count <= 250
    near_threshold_line_limit = 220
    over_near_threshold = bool(text) and line_count > near_threshold_line_limit
    section_declared = bool(body)
    references_declared = existing_count > 0
    operating_model_formats = operating_model_format_contract(skill_md, text)
    format_refs_ready = (
        not operating_model_formats["artifacts_declared"]
        or operating_model_formats["format_references_ready"]
    )
    source_operating_model = source_operating_model_contract(skill_md, body)
    source_operating_model_ready = source_operating_model["status"] in {"pass", "not_declared"}
    return {
        "skill_md_line_count": line_count,
        "skill_md_under_500_lines": line_count <= 500 if text else False,
        "skill_md_under_250_lines": compact_entrypoint,
        "skill_md_near_threshold_line_limit": near_threshold_line_limit,
        "skill_md_over_near_threshold": over_near_threshold,
        "progressive_disclosure_declared": section_declared,
        "progressive_disclosure_reference_count": existing_count,
        "progressive_disclosure_missing_references": missing,
        "progressive_disclosure_ready": (
            compact_entrypoint
            and section_declared
            and references_declared
            and not missing
            and format_refs_ready
            and source_operating_model_ready
        ),
        "operating_model_formats": operating_model_formats,
        "source_operating_model": source_operating_model,
        "progressive_disclosure_policy": (
            "Keep SKILL.md as the compact entrypoint and route task-specific "
            "details and source operating-model docs to existing references."
        ),
        "source_path": repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None,
    }


def package_file_stem_ok(path: Path) -> bool:
    """Return whether a package support filename uses purpose-readable kebab-case."""
    return bool(PACKAGE_FILE_STEM_RE.fullmatch(path.stem))


def text_contains_action_term(text: str) -> bool:
    """Return whether text contains a deterministic natural-action trigger term."""
    tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()}
    return bool(tokens & DESCRIPTION_ACTION_TERMS)


def markdown_has_title(text: str) -> bool:
    """Return whether markdown text declares a top-level title."""
    return any(line.startswith("# ") and line[2:].strip() for line in text.splitlines())


def markdown_title(text: str) -> str:
    """Return the first top-level markdown title."""
    for line in text.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return ""


def markdown_reference_heading_weak(path: Path, text: str) -> bool:
    """Return whether a markdown reference title is too generic to route reliably."""
    title = markdown_title(text)
    if not title:
        return True
    title_tokens = _token_set(title)
    if not title_tokens:
        return True
    if title_tokens.issubset(GENERIC_REFERENCE_HEADING_TERMS):
        return True
    stem_tokens = _token_set(path.stem)
    meaningful_stem_tokens = stem_tokens - GENERIC_REFERENCE_HEADING_TERMS
    meaningful_title_tokens = title_tokens - GENERIC_REFERENCE_HEADING_TERMS
    if meaningful_stem_tokens and not (meaningful_stem_tokens & meaningful_title_tokens):
        return True
    return False


def structured_reference_has_description(path: Path, text: str) -> bool:
    """Return whether a structured reference has a browseable purpose marker."""
    if path.suffix.lower() == ".json":
        return '"description"' in text or '"purpose"' in text or '"schema_version"' in text
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                return False
            if not isinstance(record, dict):
                return False
            return any(str(record.get(field) or "").strip() for field in ("description", "purpose", "schema_version"))
        return False
    return bool(re.search(r"(?m)^(description|purpose|schema_version|name):\s*\S", text))


def script_has_description(text: str) -> bool:
    """Return whether script header comments or docstrings describe purpose/usage."""
    lines = text.splitlines()[:25]
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if not stripped or stripped.startswith("#!"):
            continue
        if stripped.startswith("#") and any(
            marker in stripped for marker in ("description", "purpose", "usage")
        ):
            return True
        if stripped.startswith(("\"\"\"", "'''")) and any(
            marker in _leading_docstring_text(lines[index:]) for marker in ("description", "purpose", "usage")
        ):
            return True
        if stripped.startswith(("import ", "from ", "print(", "def ", "class ")):
            return False
    return False


def _leading_docstring_text(lines: list[str]) -> str:
    quote = lines[0].strip()[:3]
    body: list[str] = []
    for line in lines:
        body.append(line.strip().lower())
        if len(body) > 1 and quote in line:
            break
        if len(body) == 1 and line.strip().lower().count(quote) >= 2:
            break
    return "\n".join(body)


def support_file_has_description(path: Path) -> bool:
    """Return whether a reference or script carries deterministic browseability text."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    suffix = path.suffix.lower()
    if suffix == ".md":
        return markdown_has_title(text)
    if suffix in {".yaml", ".yml", ".json", ".jsonl"}:
        return structured_reference_has_description(path, text)
    if suffix == ".txt":
        return bool(text.strip())
    if path.parts and "scripts" in path.parts:
        return script_has_description(text)
    return False


def iter_support_files(skill_md: Path | None, folder: str) -> list[Path]:
    """Return package support files under references/ or scripts/."""
    if not skill_md:
        return []
    root = skill_md.parent / folder
    if not root.is_dir() or root.is_symlink():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.name not in PACKAGE_IGNORED_FILE_NAMES
        if package_local_regular_file(skill_md, path.relative_to(skill_md.parent).as_posix())
    )


def unsafe_support_files(skill_md: Path | None, folder: str) -> list[Path]:
    """Return support paths that must not be read as package evidence."""
    if not skill_md:
        return []
    root = skill_md.parent / folder
    if root.is_symlink():
        return [root]
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.name not in PACKAGE_IGNORED_FILE_NAMES
        if path.is_symlink()
        or (path.is_file() and not package_local_regular_file(skill_md, path.relative_to(skill_md.parent).as_posix()))
    )


def package_path_label(repo_root: Path | None, path: Path) -> str:
    """Return a repo-relative label without resolving symlink leaves."""
    if repo_root:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def support_file_inventory(
    repo_root: Path | None,
    skill_md: Path | None,
    folder: str,
) -> dict[str, Any]:
    """Return deterministic naming and browseability checks for support files."""
    files = iter_support_files(skill_md, folder)
    unsafe_paths = unsafe_support_files(skill_md, folder)
    bad_names = [path for path in files if not package_file_stem_ok(path)]
    generic_names = [path for path in files if path.stem.lower() in GENERIC_PACKAGE_FILE_STEMS]
    missing_descriptions = [path for path in files if not support_file_has_description(path)]
    weak_headings: list[Path] = []
    if folder == "references":
        for path in files:
            if path.suffix.lower() != ".md":
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                weak_headings.append(path)
                continue
            if markdown_reference_heading_weak(path, text):
                weak_headings.append(path)
    return {
        "count": len(files),
        "filenames_kebab_case": not bad_names,
        "generic_names": [repo_relative_path(repo_root, path) or path.as_posix() for path in generic_names],
        "missing_descriptions": [
            repo_relative_path(repo_root, path) or path.as_posix() for path in missing_descriptions
        ],
        "weak_headings": [
            repo_relative_path(repo_root, path) or path.as_posix() for path in weak_headings
        ],
        "description_coverage_count": len(files) - len(missing_descriptions),
        "ready": (
            not unsafe_paths
            and not bad_names
            and not generic_names
            and not missing_descriptions
            and not weak_headings
        ),
        "bad_names": [repo_relative_path(repo_root, path) or path.as_posix() for path in bad_names],
        "unsafe_paths": [package_path_label(repo_root, path) for path in unsafe_paths],
    }


def skill_identity_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic naming and description signals for a skill package."""
    name = str(frontmatter.get("name") or "").strip()
    description = str(frontmatter.get("description") or "").strip()
    short_description = str(metadata_value(frontmatter, "short_description") or "").strip()
    directory_name = skill_md.parent.name if skill_md else ""
    name_present = bool(name)
    name_kebab_case = bool(PACKAGE_FILE_STEM_RE.fullmatch(name))
    name_matches_directory = bool(name and directory_name and name == directory_name)
    description_present = bool(description)
    description_length_ok = 40 <= len(description) <= 420
    description_no_command_handles = not SKILL_DESCRIPTION_HANDLE_RE.search(description)
    description_has_action_term = text_contains_action_term(description)
    short_description_length_ok = not short_description or len(short_description) <= 80
    return {
        "name": name,
        "directory_name": directory_name,
        "source_path": repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None,
        "name_present": name_present,
        "name_kebab_case": name_kebab_case,
        "name_matches_directory": name_matches_directory,
        "description_present": description_present,
        "description_length_chars": len(description),
        "description_length_ok": description_length_ok,
        "description_no_command_handles": description_no_command_handles,
        "description_has_action_term": description_has_action_term,
        "short_description_length_ok": short_description_length_ok,
        "ready": all(
            (
                name_present,
                name_kebab_case,
                name_matches_directory,
                description_present,
                description_length_ok,
                description_no_command_handles,
                description_has_action_term,
                short_description_length_ok,
            )
        ),
    }


def identity_and_assets_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return SDK advisory checks for skill identity and support asset browseability."""
    skill_identity = skill_identity_contract(repo_root, skill_md, frontmatter)
    references = support_file_inventory(repo_root, skill_md, "references")
    scripts = support_file_inventory(repo_root, skill_md, "scripts")
    return {
        "schema_version": "skill-identity-assets.v1",
        "policy": (
            "Skill names should be stable kebab-case handles; descriptions should use natural "
            "action-trigger language; references and scripts should be purpose-named and browseable."
        ),
        "skill_identity": skill_identity,
        "reference_inventory": references,
        "script_inventory": scripts,
        "ready": skill_identity["ready"] and references["ready"] and scripts["ready"],
    }


def knowledge_capsule_first_party_contract(repo_root: Path | None, skill_md: Path | None, text: str) -> dict[str, Any]:
    """Return whether vendored knowledge capsules are surfaced through first-party skill references."""
    references_dir = skill_md.parent / "references" if skill_md else None
    manifest_path = references_dir / "knowledge-capsule.manifest.yaml" if references_dir else None
    routing_path = references_dir / "knowledge-capsule-routing.md" if references_dir else None
    manifest_declared = bool(manifest_path and (manifest_path.is_file() or manifest_path.is_symlink()))
    manifest_safe = bool(skill_md and package_local_regular_file(skill_md, "references/knowledge-capsule.manifest.yaml"))
    capsule_paths: list[str] = []
    if manifest_safe and manifest_path:
        manifest, error = read_structured_reference(manifest_path)
        if error is None and isinstance(manifest, dict):
            capsules = manifest.get("capsules")
            if isinstance(capsules, list):
                capsule_paths = _knowledge_capsule_target_paths(capsules)
        if not capsule_paths:
            capsule_paths = _knowledge_capsule_target_paths_from_text(manifest_path)
    unsafe_capsule_paths = [path for path in capsule_paths if not package_local_reference_path(path)]
    routing_declared = bool(routing_path and (routing_path.is_file() or routing_path.is_symlink()))
    routing_safe = bool(skill_md and package_local_regular_file(skill_md, "references/knowledge-capsule-routing.md"))
    routing_text = skill_markdown_text(routing_path) if routing_safe and routing_path else ""
    missing_from_routing = [
        path for path in capsule_paths
        if routing_declared and path and path not in routing_text
    ]
    contract_path = skill_md.parent / "references" / "contract.yaml" if skill_md else None
    contract_mentions_routing = (
        bool(contract_path and contract_path.is_file())
        and "knowledge-capsule-routing.md" in skill_markdown_text(contract_path)
    )
    skill_mentions_routing = "knowledge-capsule-routing.md" in text or contract_mentions_routing
    ready = (
        not manifest_declared
        or (
            routing_declared
            and manifest_safe
            and routing_safe
            and skill_mentions_routing
            and bool(capsule_paths)
            and not unsafe_capsule_paths
            and not missing_from_routing
        )
    )
    return {
        "schema_version": "skill-knowledge-capsule-first-party.v1",
        "status": "pass" if ready else "advisory",
        "manifest_declared": manifest_declared,
        "manifest_path": repo_relative_path(repo_root, manifest_path) if repo_root and manifest_path else None,
        "capsule_count": len(capsule_paths),
        "capsule_paths": capsule_paths,
        "unsafe_capsule_paths": unsafe_capsule_paths,
        "first_party_routing_path": (
            repo_relative_path(repo_root, routing_path) if repo_root and routing_path else None
        ),
        "first_party_routing_declared": routing_declared,
        "first_party_routing_safe": routing_safe,
        "manifest_safe": manifest_safe,
        "skill_mentions_first_party_routing": skill_mentions_routing,
        "contract_mentions_first_party_routing": contract_mentions_routing,
        "missing_from_first_party_routing": missing_from_routing,
        "ready": ready,
        "policy": (
            "Knowledge capsule manifests select bounded generated capsules, but capsule use rules should be "
            "promoted into a first-party skill reference so agents see them without relying on buried capsule text."
        ),
    }


def _knowledge_capsule_target_paths(capsules: list[Any]) -> list[str]:
    paths: list[str] = []
    for capsule in capsules:
        if isinstance(capsule, dict) and isinstance(capsule.get("target_path"), str):
            paths.append(capsule["target_path"].strip())
        elif isinstance(capsule, str) and capsule.strip().startswith("target_path:"):
            paths.append(capsule.split(":", 1)[1].strip())
    return [path for path in paths if path]


def _knowledge_capsule_target_paths_from_text(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    paths: list[str] = []
    for match in re.finditer(r"(?m)^\s*target_path:\s*(.+?)\s*$", text):
        paths.append(match.group(1).strip().strip("'\""))
    return [capsule_path for capsule_path in paths if capsule_path]


def skill_eval_paths(repo_root: Path | None, skill_md: Path | None) -> list[str]:
    """Return portable eval declarations adjacent to a skill package."""
    if not skill_md:
        return []
    candidates = [
        skill_md.parent / "evals" / "evals.json",
        skill_md.parent / "evals" / "evals.yaml",
        skill_md.parent / "references" / "evals.yaml",
    ]
    paths: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if repo_root:
            paths.append(repo_relative_path(repo_root, candidate) or candidate.as_posix())
        else:
            paths.append(candidate.as_posix())
    return paths

__all__ = [name for name in globals() if not name.startswith("__")]
