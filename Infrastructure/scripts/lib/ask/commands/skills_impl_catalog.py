from __future__ import annotations

from types import MappingProxyType

from .skills_impl_core import *  # noqa: F403

def _completed_process_payload(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """Return stable JSON data for a validation subprocess result."""
    return {
        "command": list(proc.args) if isinstance(proc.args, list) else proc.args,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _call_result_payload(result: CallResult) -> dict[str, Any]:
    """Return a JSON-serializable in-process command result."""
    return {
        "status": result.status,
        "trace_id": result.trace_id,
        "metadata": result.metadata,
        "data": result.data,
        "telemetry": result.telemetry,
        "errors": [error.__dict__ for error in result.errors],
    }


def _package_verify_rule_evidence(verification: dict[str, Any]) -> list[str]:
    """Return compact, replay-friendly rule evidence strings for package verification."""
    evidence: list[str] = []
    checks = verification.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            name = str(check.get("name") or "unknown")
            status = str(check.get("status") or "unknown")
            value = "true" if status == "pass" else "false" if status in {"fail", "blocked"} else status
            evidence.append(f"{name}:{value}")
            if name == "trusted_provenance":
                evidence.append(f"provenance_trusted:{value}")
            check_evidence = check.get("evidence") if isinstance(check.get("evidence"), dict) else {}
            for member in check_evidence.get("unsafe_members") or []:
                if isinstance(member, dict) and member.get("name"):
                    evidence.append(f"unsafe_member:{member['name']}")
            for member in check_evidence.get("unsafe_links") or []:
                if isinstance(member, dict) and member.get("name"):
                    evidence.append(f"symlink_escape:{member['name']}")
        return evidence

    rule_results = verification.get("rule_results")
    if isinstance(rule_results, list):
        blocker_ids = {str(item.get("rule_id")) for item in rule_results if isinstance(item, dict)}
        contract = verification.get("contract") if isinstance(verification.get("contract"), dict) else {}
        missing = contract.get("required_fields", {}).get("missing", []) if contract else []
        evidence.append(f"package_metadata_complete:{str(not missing).lower()}")
        provenance = verification.get("provenance_identity")
        trusted = provenance.get("trusted") if isinstance(provenance, dict) else False
        evidence.append(f"provenance_trusted:{str(bool(trusted)).lower()}")
        if "digest_mismatch" in blocker_ids:
            evidence.append("digest_match:false")
        mutation = verification.get("mutation_status")
        evidence.append(f"no_runtime_mutation:{str(mutation == 'not_mutated').lower()}")
        for blocker in rule_results:
            if not isinstance(blocker, dict):
                continue
            if blocker.get("path"):
                evidence.append(f"{blocker.get('rule_id')}:{blocker.get('path')}")
                if blocker.get("rule_id") in {"absolute_archive_path", "archive_path_traversal"}:
                    evidence.append(f"unsafe_member:{blocker.get('path')}")
                if blocker.get("rule_id") == "archive_symlink_escape":
                    evidence.append(f"symlink_escape:{blocker.get('path')}")
            else:
                evidence.append(str(blocker.get("rule_id") or "blocked_validation"))
    return evidence


def _package_verify_blockers(verification: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = verification.get("blockers")
    if isinstance(blockers, list):
        return [
            {**item, "class": item.get("class") or item.get("rule_id")}
            for item in blockers
            if isinstance(item, dict)
        ]
    rule_results = verification.get("rule_results")
    if isinstance(rule_results, list):
        return [
            {**item, "class": item.get("class") or item.get("rule_id")}
            for item in rule_results
            if isinstance(item, dict)
        ]
    return []


def _package_verify_mutation_status(verification: dict[str, Any]) -> dict[str, Any]:
    runtime_mutation = verification.get("runtime_mutation")
    runtime_mutated = False
    if isinstance(runtime_mutation, dict):
        runtime_mutated = runtime_mutation.get("status") == "fail" or bool(runtime_mutation.get("mutations"))
    mutation_status = verification.get("mutation_status")
    mutation_payload = mutation_status if isinstance(mutation_status, dict) else {}
    status_value = mutation_payload.get("status") if mutation_payload else mutation_status
    return {
        "mutated": runtime_mutated
        or bool(mutation_payload.get("mutated"))
        or status_value not in {None, "not_mutated", "pass"},
        "runtime_roots_mutated": runtime_mutated or bool(mutation_payload.get("runtime_roots_mutated")),
        "install_attempted": bool(mutation_payload.get("install_attempted")),
        "archive_extracted": bool(mutation_payload.get("archive_extracted")),
        "network_used": bool(mutation_payload.get("network_used")),
        "raw": mutation_status or runtime_mutation or "not_mutated",
    }


def _normalize_package_verification(
    *,
    query: str,
    validation_command: str,
    verification: dict[str, Any],
    strict: bool,
) -> dict[str, Any]:
    archive = verification.get("archive")
    archive_identity = verification.get("archive_identity")
    if isinstance(archive, dict):
        archive_identity = {
            "path": archive.get("path"),
            "sha256": archive.get("sha256"),
            "type": archive.get("type"),
            "member_count": archive.get("member_count"),
        }
    target_kind = verification.get("target_kind") or ("archive" if archive_identity else "skill_directory")
    target_path = verification.get("target_path") or (archive.get("path") if isinstance(archive, dict) else query)
    provenance_identity = verification.get("provenance_identity")
    if not isinstance(provenance_identity, dict):
        provenance = verification.get("provenance")
        source = provenance.get("source") if isinstance(provenance, dict) else None
        provenance_identity = {
            "trusted": "trusted_provenance:true" in _package_verify_rule_evidence(verification),
            "source": source,
        }

    blockers = _package_verify_blockers(verification)
    next_command: str | None = None
    if verification.get("status") == "blocked" and strict and target_kind == "skill_directory":
        next_command = _skills_validation_command("package", query, "--strict")
    elif verification.get("status") == "blocked" and target_kind == "skill_directory":
        source_root = Path(str(target_path)).parent.as_posix()
        next_command = _skills_validation_command("audit", source_root, "--level", "strict")
    elif verification.get("status") == "blocked":
        next_command = _ask_validation_command("sdk", "start", query)
    elif verification.get("status") == "pass" and strict and target_kind == "skill_directory":
        next_command = _skills_validation_command("prove", query)

    normalized = {
        **verification,
        "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
        "query": query,
        "strict": strict,
        "status": verification.get("status", "blocked"),
        "target_identity": {
            "kind": target_kind,
            "path": target_path,
            "query": query,
        },
        "archive_identity": archive_identity,
        "provenance_identity": provenance_identity,
        "rule_evidence": _package_verify_rule_evidence(verification),
        "blockers": blockers,
        "mutation_status": _package_verify_mutation_status(verification),
        "rollback_hint": verification.get("rollback_hint")
        or "No rollback is required because verification did not install, extract, or mutate runtime roots.",
        "validation_commands": [validation_command],
        "next_command": next_command,
    }
    normalized["agent_summary"] = (
        f"Package verification blocked: {normalized['blockers'][0].get('message', 'validation failed')}"
        if normalized["status"] == "blocked" and normalized["blockers"]
        else "Package verification passed without install, extraction, or runtime-root mutation."
    )
    return normalized


def _apply_strict_package_readiness(
    repo_root: Path,
    query: str,
    verification: dict[str, Any],
) -> dict[str, Any]:
    """Attach the existing strict package-readiness result to verification."""
    readiness_result = skills_package(repo_root, query, strict=True)
    readiness = readiness_result.data.get("skill_package")
    if not isinstance(readiness, dict):
        return verification
    if readiness.get("status") != "blocked":
        return {**verification, "strict_package_readiness": readiness}

    blocker = {
        "rule_id": "strict_package_readiness_blocked",
        "status": "blocked",
        "message": readiness.get("agent_summary", "Strict package readiness failed."),
        "path": readiness.get("canonical_source_path"),
        "evidence": readiness,
    }
    return {
        **verification,
        "status": "blocked",
        "strict_package_readiness": readiness,
        "blockers": [*verification.get("blockers", []), blocker],
        "rule_results": [*verification.get("rule_results", []), blocker],
    }


def _run_captured_tool(
    *,
    repo_root: Path,
    command: list[str],
    timeout_seconds: int = 120,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a local validation tool with bounded runtime and captured output."""
    env = _subprocess_env_with_uv_cache()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_seconds,
    )


def _safe_tessl_skill_key(raw_name: str) -> str:
    """Return a conservative tile skill key for a temporary Tessl wrapper."""
    key = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
    return key or "skill"


def _write_tessl_staged_json(path: Path, payload: dict[str, Any], staging_root_real: str, label: str) -> None:
    safe_path = _safe_tessl_staging_path(path, staging_root_real, label)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    _write_tessl_staged_text(
        safe_path,
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        staging_root_real,
        label,
    )


def _write_tessl_staged_text(path: Path, value: str, staging_root_real: str, label: str) -> None:
    safe_path = _safe_tessl_staging_path(path, staging_root_real, label)
    if safe_path.is_symlink():
        raise ValueError(f"Tessl review staging {label} path must not be a symlink.")
    with safe_path.open("w", encoding="utf-8") as handle:
        handle.write(value)


def _safe_tessl_staging_path(path: Path, staging_root_real: str, label: str) -> Path:
    parent_real = os.path.realpath(path.parent)
    if os.path.commonpath([staging_root_real, parent_real]) != staging_root_real:
        raise ValueError(f"Tessl review staging {label} parent escaped the staging root.")
    target_real = os.path.realpath(path)
    if os.path.commonpath([staging_root_real, target_real]) != staging_root_real:
        raise ValueError(f"Tessl review staging {label} path escaped the staging root.")
    return Path(target_real)


def _raise_if_tessl_support_tree_has_symlink(support_dir: Path, label: str) -> None:
    for path in [support_dir, *support_dir.rglob("*")]:
        if path.is_symlink():
            raise ValueError(f"Tessl review staging refuses symlinked support path: {label}")


def _write_tessl_plugin_wrapper(repo_root: Path, audit_target_path: str, stable_parent: Path) -> tuple[Path, dict[str, str]]:
    """Create a stable Tessl plugin-shaped evidence wrapper for a SKILL.md-first local skill."""
    source_skill_dir = repo_root / audit_target_path
    source_skill = source_skill_dir / "SKILL.md"
    if source_skill.is_symlink():
        raise ValueError(f"Tessl review staging refuses symlinked skill source: {audit_target_path}/SKILL.md")
    fields = _read_skill_frontmatter_fields(source_skill)
    skill_key = _safe_tessl_skill_key(fields.get("name") or Path(audit_target_path).name)
    temp_root = stable_parent / "current"
    if temp_root.exists():
        archive_root = stable_parent / "evidence-archive"
        archive_root.mkdir(parents=True, exist_ok=True)
        archive_name = f"plugin-review-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        archive_path = archive_root / archive_name
        counter = 1
        while archive_path.exists():
            counter += 1
            archive_path = archive_root / f"{archive_name}-{counter}"
        shutil.move(str(temp_root), str(archive_path))
    temp_root.mkdir(parents=True, exist_ok=True)
    staged_skill_dir = temp_root / "skills" / skill_key
    staged_skill_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_skill, staged_skill_dir / "SKILL.md")
    for support_dir_name in ("references", "scripts", "assets", "evals"):
        support_dir = source_skill_dir / support_dir_name
        if support_dir.is_dir():
            _raise_if_tessl_support_tree_has_symlink(
                support_dir,
                f"{audit_target_path}/{support_dir_name}",
            )
            shutil.copytree(support_dir, staged_skill_dir / support_dir_name)

    plugin = {
        "schema_version": 1,
        "name": f"local/{skill_key}",
        "description": fields.get("description") or f"Local validation wrapper for {skill_key}.",
        "version": "0.0.0-local",
        "private": True,
        "skills": "./skills/",
    }
    stable_parent_real = os.path.realpath(stable_parent)
    plugin_path = temp_root / ".tessl-plugin" / "plugin.json"
    _write_tessl_staged_json(plugin_path, plugin, stable_parent_real, "manifest")
    tessl_marker_path = temp_root / "tessl.json"
    _write_tessl_staged_json(
        tessl_marker_path,
        {"name": f"agent-skills-{skill_key}", "version": "0.0.0-local"},
        stable_parent_real,
        "marker",
    )
    return temp_root, {
        "plugin_manifest": str(plugin_path),
        "tessl_project_marker": str(tessl_marker_path),
        "staging_root": str(temp_root),
        "review_path": str(staged_skill_dir),
        "skill_key": skill_key,
        "source_skill": audit_target_path,
        "evidence_retention": "stable_tmp_directory_left_for_post-run_inspection",
        "archive_policy": "previous_current_staging_moved_to_evidence_archive_before_refresh",
    }


def _stable_tessl_review_root(audit_target_path: str) -> Path:
    safe_name = audit_target_path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(audit_target_path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-reviews" / f"{safe_name}-{digest}"


def _parse_tessl_review_output(stdout: str, status: str = "") -> dict[str, Any]:
    json_start = stdout.find("{")
    if json_start >= 0:
        try:
            parsed = json.loads(stdout[json_start:])
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            nested_review = parsed.get("review")
            score = parsed.get("reviewScore") or parsed.get("review_score") or parsed.get("score")
            if score is None and isinstance(nested_review, dict):
                score = nested_review.get("reviewScore") or nested_review.get("review_score") or nested_review.get("score")
            return {
                "review_score": score,
                "minimum_score": TESSL_REVIEW_MIN_SCORE,
                "target_score": TESSL_REVIEW_TARGET_SCORE,
                "score_acceptable": isinstance(score, (int, float)) and score >= TESSL_REVIEW_MIN_SCORE,
                "status": status or "reported",
                "raw": parsed,
            }
    parsed_human = _parse_tessl_review(stdout, status)
    parsed_human["minimum_score"] = TESSL_REVIEW_MIN_SCORE
    parsed_human["target_score"] = TESSL_REVIEW_TARGET_SCORE
    parsed_human["score_acceptable"] = parsed_human.get("review_score", 0) >= TESSL_REVIEW_MIN_SCORE
    return parsed_human


@dataclass(frozen=True)
class _RouterSkill:
    name: str
    description: str
    skill_path: str


STARTER_ARCHETYPES = MappingProxyType({
    "general": (
        "autofix",
        "testing",
        "simplify",
        "improve-codebase-architecture",
        "technical-writer",
        "context7",
    ),
    "delivery": ("pr-green-sweep", "testing", "autofix", "coding-harness", "technical-writer"),
    "review": ("improve-codebase-architecture", "he-code-review", "autofix", "testing"),
    "docs": ("agents-md", "technical-writer", "context7", "openai-docs"),
})


_SKILL_INSTALLER_SCRIPT_CANDIDATES = (
    "skills-system/skill-installer/scripts/install-skill-from-github.py",
)

_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES = (
    "Plugins/skill-factory/scripts/skill-builder",
    "plugins/skill-factory/scripts/skill-builder",
)


def _resolve_skill_installer_script(repo_root: Path) -> str:
    for rel in _SKILL_INSTALLER_SCRIPT_CANDIDATES:
        candidate = repo_root / rel
        if candidate.is_file():
            return rel
    # Keep canonical path in the error payload for predictable operator guidance.
    return _SKILL_INSTALLER_SCRIPT_CANDIDATES[0]


def _resolve_skill_builder_script(repo_root: Path, module_name: str) -> str:
    filename = f"{module_name}.py"
    for rel_dir in _SKILL_BUILDER_SCRIPT_DIR_CANDIDATES:
        candidate = repo_root / rel_dir / filename
        if candidate.is_file():
            return f"{rel_dir}/{filename}"
    return f"{_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES[0]}/{filename}"


# Explicitly load builder-specific logic using absolute paths to avoid namespace collisions
def _load_builder_module(repo_root: Path, module_name: str):
    """Load a skill-builder module from this repository, if its script exists."""
    module_rel = _resolve_skill_builder_script(repo_root, module_name)
    module_path = repo_root / module_rel
    if not module_path.exists():
        return None
    scripts_dir = module_path.parent

    internal_name = f"ask_builder_{module_name}"
    if internal_name in sys.modules:
        return sys.modules[internal_name]

    scripts_dir_str = str(scripts_dir)
    inserted = False
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(internal_name, str(module_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[internal_name] = mod  # Register BEFORE exec
            loaded = False
            try:
                spec.loader.exec_module(mod)
                loaded = True
            finally:
                if not loaded:
                    sys.modules.pop(internal_name, None)
            return mod
    finally:
        if inserted and scripts_dir_str in sys.path:
            sys.path.remove(scripts_dir_str)
    return None

def _canonical_entries(
    repo_root: Path,
    *,
    source: str = "auto",
    visibility: str = "default",
) -> list:
    """
    Filter discovered skill entries to those whose source directory is inside the repository root.

    Parameters:
        repo_root (Path): Repository root used to determine whether an entry's `source_dir` is inside the repository.

    Returns:
        entries (list): Discovered skill entries whose `source_dir` is relative to `repo_root`.
    """
    return [
        entry
        for entry in discover_skill_entries(source=source, visibility=visibility)
        if entry.source_dir.is_relative_to(repo_root)
    ]


def _starter_entries(entries: list, archetype: str, limit: int) -> list:
    """
    Selects a deterministic subset of skill entries for starter mode.

    Prefers skills listed in the chosen archetype (in archetype order) and, if needed, appends additional entries from the provided list until a bounded minimum of 1 up to `limit` items is reached. Unknown archetype keys fall back to the "general" archetype.

    Parameters:
        entries (list): Iterable of skill entry objects; each must expose a `name` attribute.
        archetype (str): Archetype key whose ordered starter names guide preferred selection.
        limit (int): Maximum number of entries to return; values below 1 are treated as 1.

    Returns:
        list: Ordered list of selected entries (length >= 1 and <= `limit`), preferring archetype-specified names first and then remaining entries in input order.
    """
    bounded_limit = max(1, int(limit))
    archetype_key = archetype if archetype in STARTER_ARCHETYPES else "general"
    preferred = list(STARTER_ARCHETYPES[archetype_key])
    by_name = {entry.name: entry for entry in entries}
    selected = [by_name[name] for name in preferred if name in by_name]
    if len(selected) >= bounded_limit:
        return selected[:bounded_limit]

    seen = {item.name for item in selected}
    for entry in entries:
        if entry.name in seen:
            continue
        selected.append(entry)
        if len(selected) >= bounded_limit:
            break
    return selected


def _sdk_handle_owner_index(repo_root: Path) -> dict[str, str]:
    """Return SDK skill owners keyed by handle name."""
    try:
        records = build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")
    except (OSError, ValueError) as exc:
        print(f"warning: failed to load SDK skill owner index: {exc}", file=sys.stderr)
        return {}
    owner_by_handle = {}
    for record in records:
        handle = record.handle.strip()
        owner = record.owner.strip()
        if handle and owner:
            owner_by_handle[handle] = owner
    return owner_by_handle


def _entry_matches_category(entry, category_token: str, owner_by_handle: dict[str, str], repo_root: Path) -> bool:
    """Match a skill-list category against path/category plus SDK ownership."""
    searchable = [
        str(getattr(entry, "category", "")),
        str(getattr(entry, "name", "")),
        str(getattr(entry, "description", "")),
        owner_by_handle.get(str(getattr(entry, "name", "")), ""),
    ]
    source_dir = getattr(entry, "source_dir", None)
    if isinstance(source_dir, Path):
        searchable.append(source_dir.as_posix())
        if source_dir.is_relative_to(repo_root):
            searchable.append(source_dir.relative_to(repo_root).as_posix())
    return any(category_token in value.lower() for value in searchable if value)


def _entry_visible_for_picker(entry, repo_root: Path) -> bool:
    """Return whether an entry belongs in the narrow picker-visible inventory."""
    source_dir = getattr(entry, "source_dir", None)
    if not isinstance(source_dir, Path):
        return False
    try:
        rel_parts = source_dir.relative_to(repo_root).parts
    except ValueError:
        return False
    lower_parts = tuple(part.lower() for part in rel_parts)
    if len(lower_parts) >= 4 and lower_parts[0] == "plugins" and lower_parts[2] == "skills":
        return lower_parts[1] == lower_parts[3]
    return True


def _refresh_catalog_projections(repo_root: Path, dry_run: bool = False) -> list[str]:
    """
    Regenerate root catalog projections from the default catalog surface.

    Parameters:
        repo_root (Path): Repository root containing `README.md` and `SKILL.md`.
        dry_run (bool): When `True`, do not write files and only describe planned changes.

    Returns:
        list[str]: Human-readable log lines describing projection updates.
    """
    entries = [
        entry
        for entry in discover_catalog_entries(source="repo")
        if entry.source_dir.is_relative_to(repo_root)
    ]
    catalog_count = len(entries)
    logs: list[str] = []

    skill_index_path = repo_root / "SKILL.md"
    rendered_index = render_index(entries, source="catalog", visibility="default") + "\n"
    existing_index = skill_index_path.read_text(encoding="utf-8") if skill_index_path.exists() else None
    if dry_run:
        if existing_index != rendered_index:
            logs.append(f"Would refresh catalog index: {skill_index_path}")
    elif existing_index != rendered_index:
        skill_index_path.write_text(rendered_index, encoding="utf-8")
        logs.append(f"Refreshed catalog index: {skill_index_path}")

    readme_path = repo_root / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        sdk_owner_counts: dict[str, int] = {}
        for record in build_sdk_skill_records(repo_root_path=repo_root):
            if record.source_path.startswith("Skills/"):
                sdk_owner_counts[record.owner] = sdk_owner_counts.get(record.owner, 0) + 1

        updated_readme, replacements = re.subn(
            r"A governed repository of \*\*\d+(?: canonical)? skills\*\* for AI coding agents",
            f"A governed repository of **{catalog_count} skills** for AI coding agents",
            readme_content,
            count=1,
        )
        if replacements == 0:
            updated_readme, replacements = re.subn(
                r"A governed repository of AI coding skills\.",
                f"A governed repository of **{catalog_count} skills** for AI coding agents.",
                updated_readme,
                count=1,
            )
        updated_readme = re.sub(
            r"A governed repository of \*\*skills\*\* for AI coding agents",
            f"A governed repository of **{catalog_count} skills** for AI coding agents",
            updated_readme,
            count=1,
        )
        updated_readme = re.sub(
            r"A governed \*\*Agent Skills Kit\*\* repository(?: of \*\*\d+(?: canonical)? skills\*\*)? for Codex and AI coding agents",
            "A governed **Agent Skills Kit** repository for Codex and AI coding agents",
            updated_readme,
            count=1,
        )
        updated_readme = re.sub(
            r"(?:A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\. Author skills once, validate quality, expose `\$`[^.\n]+, and sync routed skills and plugins into runtime projections through the `ask` CLI\.\n\n)+(?=A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\.\nAuthor skills once)",
            "",
            updated_readme,
        )
        updated_readme = re.sub(
            r"This repository currently exposes \*\*\d+ skills\*\* in the default catalog",
            f"This repository currently exposes **{catalog_count} skills** in the default catalog",
            updated_readme,
            count=1,
        )
        if sdk_owner_counts:
            preferred_order = (
                "agent-ops",
                "backend-platform",
                "content-publishing",
                "frontend-ui",
                "mobile-native",
                "product-strategy",
                "security-ops",
            )
            source_counts = sdk_owner_counts
            cluster_counts = {
                name: count for name, count in source_counts.items() if name in preferred_order
            }
            if cluster_counts:
                first_party_handle_count = sum(cluster_counts.values())
                cluster_summary = ", ".join(
                    f"{name}: {cluster_counts[name]}"
                    for name in preferred_order
                    if name in cluster_counts
                )
                updated_readme = re.sub(
                    r"(?:including \*\*\d+ first-party SDK skill names\*\* backed by canonical skill source|including \*\*\d+ first-party handles\*\* backed by canonical skill source|backed by first-party canonical skill\s+source) across \d+ topic clusters \([^)]*\)",
                    (
                        f"including **{first_party_handle_count} first-party SDK skill names** backed by canonical "
                        f"skill source across {len(cluster_counts)} topic clusters ({cluster_summary})"
                    ),
                    updated_readme,
                    count=1,
                    flags=re.DOTALL,
                )
                for name, count in cluster_counts.items():
                    updated_readme = re.sub(
                        rf"(\| {re.escape(name)}\s+\|)\s*\d+(\s+\|)",
                        lambda match, count=count: f"{match.group(1)} {count}{match.group(2)}",
                        updated_readme,
                        count=1,
                    )
                    updated_readme = re.sub(
                        rf"(\|\s+\|-- {re.escape(name)}/\s+#\s*)\d+(\s+skills?:)",
                        lambda match, count=count: f"{match.group(1)}{count}{match.group(2)}",
                        updated_readme,
                        count=1,
                    )
        updated_readme = re.sub(
            r"currently expects \*\*\d+\*\* skills",
            f"currently expects **{catalog_count}** skills",
            updated_readme,
            count=1,
        )
        if dry_run:
            if updated_readme != readme_content:
                logs.append(f"Would refresh README skill count: {readme_path}")
        elif updated_readme != readme_content:
            readme_path.write_text(updated_readme, encoding="utf-8")
            logs.append(f"Refreshed README skill count: {readme_path}")

    return logs

__all__ = [name for name in globals() if not name.startswith("__")]
