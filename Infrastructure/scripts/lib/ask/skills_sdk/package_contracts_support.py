from .package_contracts_core import *  # noqa: F403
from .package_contracts_rubric import *  # noqa: F403

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


def skill_package_file_path(
    repo_root: Path | None,
    skill_md: Path | None,
    relative_path: str,
) -> str | None:
    """Return a repo-relative package file path when present."""
    if not skill_md:
        return None
    candidate = skill_md.parent / relative_path
    if not candidate.is_file():
        return None
    if repo_root:
        return repo_relative_path(repo_root, candidate) or candidate.as_posix()
    return candidate.as_posix()


def skillflow_contract(repo_root: Path | None, skill_md: Path | None, reference_contract: dict[str, Any]) -> dict[str, Any]:
    """Return optional deterministic workflow contract metadata for one skill package."""
    workflow_decl = reference_contract.get("workflow")
    if not isinstance(workflow_decl, dict):
        workflow_decl = {}
    execution_mode = str(
        reference_contract.get("execution_mode") or workflow_decl.get("execution_mode") or "prose"
    )
    workflow_path_value = str(workflow_decl.get("path") or "workflows/skillflow.json")
    required = bool(workflow_decl.get("required") or execution_mode in {"deterministic_flow", "hybrid"})
    path = None
    rel_path = None
    if skill_md:
        path = skill_md.parent / workflow_path_value
        rel_path = repo_relative_path(repo_root, path) if repo_root else path.as_posix()
    exists = bool(path and path.is_file())
    checks: list[dict[str, Any]] = [
        {
            "name": "execution_mode_declared",
            "status": "pass" if execution_mode in SKILLFLOW_EXECUTION_MODES else "blocked_validation",
            "value": execution_mode,
            "allowed_values": sorted(SKILLFLOW_EXECUTION_MODES),
        },
        {
            "name": "workflow_file_presence",
            "status": "pass" if exists else ("blocked_validation" if required else "not_applicable"),
            "path": rel_path,
            "required": required,
        },
    ]
    blockers: list[dict[str, Any]] = []
    if execution_mode not in SKILLFLOW_EXECUTION_MODES:
        blockers.append(
            {
                "rule_id": "skillflow_execution_mode_invalid",
                "path": "references/contract.yaml",
                "message": f"execution_mode must be one of: {', '.join(sorted(SKILLFLOW_EXECUTION_MODES))}.",
            }
        )
    if required and not exists:
        blockers.append(
            {
                "rule_id": "skillflow_required_file_missing",
                "path": rel_path,
                "message": "Package declares deterministic workflow behavior but workflows/skillflow.json is missing.",
            }
        )

    node_count = 0
    side_effecting_nodes = 0
    human_gate_count = 0
    output_names: list[str] = []
    if exists and path:
        loaded, error = read_structured_reference(path)
        checks.append(
            {
                "name": "skillflow_parse",
                "status": "pass" if error is None and isinstance(loaded, dict) else "blocked_validation",
                "path": rel_path,
            }
        )
        if error is not None or not isinstance(loaded, dict):
            blockers.append(
                {
                    "rule_id": "skillflow_unparseable",
                    "path": rel_path,
                    "message": error or "skillflow must parse to an object.",
                }
            )
        else:
            schema_version = loaded.get("schema_version")
            nodes = loaded.get("nodes")
            inputs = loaded.get("inputs")
            outputs = loaded.get("outputs")
            checks.append(
                {
                    "name": "skillflow_schema_version",
                    "status": "pass" if schema_version == SKILLFLOW_SCHEMA_VERSION else "blocked_validation",
                    "expected": SKILLFLOW_SCHEMA_VERSION,
                    "actual": schema_version,
                }
            )
            if schema_version != SKILLFLOW_SCHEMA_VERSION:
                blockers.append(
                    {
                        "rule_id": "skillflow_schema_version_invalid",
                        "path": rel_path,
                        "message": f"schema_version must be {SKILLFLOW_SCHEMA_VERSION}.",
                    }
                )
            checks.append(
                {
                    "name": "skillflow_typed_inputs_outputs",
                    "status": "pass" if isinstance(inputs, dict) and isinstance(outputs, dict) else "blocked_validation",
                    "inputs_declared": isinstance(inputs, dict),
                    "outputs_declared": isinstance(outputs, dict),
                }
            )
            if not isinstance(inputs, dict) or not isinstance(outputs, dict):
                blockers.append(
                    {
                        "rule_id": "skillflow_inputs_outputs_missing",
                        "path": rel_path,
                        "message": "skillflow must declare typed inputs and outputs objects.",
                    }
                )
            if isinstance(outputs, dict):
                output_names = sorted(str(name) for name in outputs)
            if not isinstance(nodes, list) or not nodes:
                checks.append(
                    {
                        "name": "skillflow_nodes_declared",
                        "status": "blocked_validation",
                        "node_count": 0,
                    }
                )
                blockers.append(
                    {
                        "rule_id": "skillflow_nodes_missing",
                        "path": rel_path,
                        "message": "skillflow must declare at least one node.",
                    }
                )
            else:
                node_count = len(nodes)
                node_ids: list[str] = []
                duplicate_ids: set[str] = set()
                invalid_nodes: list[str] = []
                for node in nodes:
                    if not isinstance(node, dict):
                        invalid_nodes.append("<non-object>")
                        continue
                    node_id = str(node.get("id") or "")
                    node_type = str(node.get("type") or "")
                    if node_id in node_ids:
                        duplicate_ids.add(node_id)
                    if node_id:
                        node_ids.append(node_id)
                    if node_type not in SKILLFLOW_NODE_TYPES:
                        invalid_nodes.append(node_id or "<missing-id>")
                    if node.get("side_effect") or node.get("side_effecting"):
                        side_effecting_nodes += 1
                    if node_type == "human_gate":
                        human_gate_count += 1
                checks.append(
                    {
                        "name": "skillflow_nodes_declared",
                        "status": "pass",
                        "node_count": node_count,
                    }
                )
                checks.append(
                    {
                        "name": "skillflow_node_ids_unique",
                        "status": "pass" if not duplicate_ids else "blocked_validation",
                        "duplicates": sorted(duplicate_ids),
                    }
                )
                if duplicate_ids:
                    blockers.append(
                        {
                            "rule_id": "skillflow_duplicate_node_ids",
                            "path": rel_path,
                            "message": f"Duplicate node ids: {', '.join(sorted(duplicate_ids))}.",
                        }
                    )
                checks.append(
                    {
                        "name": "skillflow_node_types_allowed",
                        "status": "pass" if not invalid_nodes else "blocked_validation",
                        "invalid_nodes": invalid_nodes,
                        "allowed_types": sorted(SKILLFLOW_NODE_TYPES),
                    }
                )
                if invalid_nodes:
                    blockers.append(
                        {
                            "rule_id": "skillflow_node_type_invalid",
                            "path": rel_path,
                            "message": f"Invalid or missing node type on nodes: {', '.join(invalid_nodes)}.",
                        }
                    )
    status = "blocked_validation" if blockers else ("pass" if exists else "not_declared")
    return {
        "schema_version": "skillflow-contract.v1",
        "skillflow_schema_version": SKILLFLOW_SCHEMA_VERSION,
        "skillflow_schema_path": SKILLFLOW_SCHEMA_PATH,
        "status": status,
        "execution_mode": execution_mode,
        "required": required,
        "declared": exists,
        "path": rel_path,
        "node_count": node_count,
        "side_effecting_node_count": side_effecting_nodes,
        "human_gate_count": human_gate_count,
        "outputs": output_names,
        "adapt_policy": workflow_decl.get("adapt_policy")
        or {
            "retry_failed_node": "allowed",
            "choose_declared_branch": "allowed",
            "fill_typed_hole": "allowed",
            "add_node": "forbidden",
            "rewire_edge": "forbidden",
        },
        "amend_policy": workflow_decl.get("amend_policy") or "reviewed",
        "checks": checks,
        "blockers": blockers,
        "what_this_proves": [
            "workflow_contract_shape",
            "declared_node_graph_resolves_structurally",
        ] if exists and not blockers else [],
        "what_this_does_not_prove": [
            "workflow_runtime_execution",
            "llm_node_quality",
            "side_effect_idempotency",
        ],
    }
__all__ = [name for name in globals() if not name.startswith("__")]
