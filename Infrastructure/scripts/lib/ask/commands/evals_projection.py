from .evals_quality import *  # noqa: F403

def _tessl_case_source(case: dict[str, object]) -> str:
    return str(case.get("source") or "references/evals.yaml")


def _tessl_criteria_from_case(case: dict[str, object]) -> dict:
    checklist: list[dict[str, object]] = []
    source = _tessl_case_source(case)
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for index, item in enumerate(acceptance, start=1):
            if not isinstance(item, dict):
                continue
            normalized_item = _normalize_tessl_acceptance_item(item)
            criterion_type = str(normalized_item.get("type") or "acceptance").strip().lower()
            value = _tessl_acceptance_description(normalized_item, case, source_item=item)
            category = "MUST_NOT" if criterion_type.startswith(("forbidden", "must_not")) else "INTENT"
            criterion = {
                "name": _safe_slug(f"{criterion_type}-{index}"),
                "description": value,
                "max_score": 1,
                "category": category,
                "source": source,
            }
            if criterion_type.startswith("text_field_"):
                criterion["metadata"] = {
                    "acceptance": {
                        key: normalized_item[key]
                        for key in sorted(normalized_item)
                        if key in {"type", "field", "fields", "value", "values", "expected", "expected_values"}
                    }
                }
            checklist.append({
                **criterion,
            })

    if not checklist:
        checklist.append({
            "name": "task-satisfaction",
            "description": "The agent response satisfies task.md and the skill contract.",
            "max_score": 1,
            "category": "INTENT",
            "source": source,
        })
    criteria_obligation_hash = hashlib.sha256(
        json.dumps(checklist, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    return {
        "context": f"Evaluation criteria adapted from {source} for {case.get('id') or 'unknown'}.",
        "type": "weighted_checklist",
        "checklist": checklist,
        "metadata": {
            "schema_version": "ask-tessl-criteria-adapter.v1",
            "source_case_id": str(case.get("id") or "unknown"),
            "source": source,
            "criteria_obligation_hash": criteria_obligation_hash,
            "source_kind": case.get("source_kind") or "skill_owned",
            "riteway": {
                "unit": case.get("unit"),
                "given": case.get("given"),
                "should": case.get("should"),
                "actual_artifact": case.get("actual_artifact"),
                "expected_artifact": case.get("expected_artifact"),
                "reproduce": case.get("reproduce"),
            },
            "agent_eval_artifacts": {
                "raw_response": case.get("raw_response_artifact"),
                "judge_details": case.get("judge_detail_artifact"),
                "judge_raw_output": case.get("judge_raw_output_artifact")
                or case.get("raw_response_artifact"),
                "judge_parse_error": case.get("judge_parse_error_artifact"),
                "judge_schema_error": case.get("judge_schema_error_artifact"),
            },
            "calibration_examples": {
                "positive": case.get("positive_example_artifact"),
                "negative": case.get("negative_example_artifact"),
            },
            "judge_failure_outcomes": {
                "parse_error": "judge_parse_error",
                "schema_error": "judge_schema_error",
                "semantic_fail": "judge_semantic_fail",
                "pass": "judge_pass",
            },
            "guardrail_output_contract": {
                "sentence_results": "required",
                "overall_verdict": "required",
                "failure_reason": "required",
                "source_references": "required_for_pass_decisions",
                "unsupported_factual_claim": "fail_closed",
                "fail_rationale": "separate_from_pass_reference",
            },
            "synthetic_case": {
                "enabled": case.get("synthetic"),
                "label": case.get("label"),
                "risk_dimension": case.get("risk_dimension"),
                "source_policy_artifact": case.get("source_policy_artifact"),
            },
            "judge_sampling": {
                "temperature": case.get("judge_temperature"),
                "runs": case.get("judge_runs"),
                "sample_count": case.get("sample_count"),
            },
            "pass_rate_policy": {
                "threshold": case.get("pass_rate_threshold"),
                "calibration_artifact": case.get("pass_rate_calibration_artifact"),
                "gate_status": "calibrated_gate" if case.get("pass_rate_calibration_artifact") else "advisory",
            },
        },
    }


def _write_tessl_live_evals_from_references(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    evals_path = source_root / "references" / "evals.yaml"
    base_cases = [
        case for case in _parse_tessl_eval_cases(evals_path)
        if _case_tessl_enabled(case, lane="live_private")
    ]
    cases, scenario_manifest = _merge_tessl_cases_with_generated_fixtures(
        source_root,
        base_cases,
        require_generated=True,
    )
    _assert_tessl_eval_quality(cases, source=evals_path)
    if (
        not scenario_manifest.get("structure_only_exception")
        and len(cases) < TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    ):
        raise ValueError(
            "Tessl live-private evals require at least "
            f"{TESSL_LIVE_PRIVATE_MIN_SCENARIOS} gold-standard structured scenarios for behavioral skills. "
            f"Found {len(cases)}. Add bespoke generated scenarios, review/import them into references/evals.yaml "
            "or references/evals/*.md, then rerun the dry-run staging lane before using Tessl live runs."
        )
    from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: PLC0415

    evals_payload = _yaml_safe_load(evals_path.read_text(encoding="utf-8"))
    release_case_ids = release_scenario_set_case_ids(evals_payload)
    cases = _select_default_tessl_live_cases(
        base_cases,
        cases,
        scenario_manifest,
        release_case_ids,
    )
    scenario_manifest["min_scenarios_required"] = TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    scenario_manifest["target_scenarios"] = TESSL_LIVE_PRIVATE_TARGET_SCENARIOS
    scenario_manifest["max_scenarios_allowed"] = TESSL_LIVE_PRIVATE_MAX_SCENARIOS
    scenario_manifest["meets_min_scenarios"] = len(cases) >= TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    scenario_manifest["run_limit_policy"] = {
        "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
        "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
        "preflight_required": True,
    }
    scenario_manifest_path = staged_root / "scenario-sources.json"
    scenario_manifest_path.write_text(json.dumps(scenario_manifest, indent=2) + "\n", encoding="utf-8")
    copied.append(str(scenario_manifest_path.relative_to(staged_root)))
    for case in cases:
        case_id = _tessl_eval_case_id(str(case["id"]))
        case_root = staged_root / "evals" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        task_path = case_root / "task.md"
        task_path.write_text(_tessl_task_markdown(case), encoding="utf-8")
        criteria_path = case_root / "criteria.json"
        criteria_path.write_text(json.dumps(_tessl_criteria_from_case(case), indent=2) + "\n", encoding="utf-8")
        copied.extend([
            str(task_path.relative_to(staged_root)),
            str(criteria_path.relative_to(staged_root)),
        ])
    return copied


def _write_tessl_live_project_marker(staged_root: Path, workspace: str, tile_slug: str) -> list[str]:
    marker_path = staged_root / "tessl.json"
    marker_path.write_text(
        json.dumps({"name": f"{workspace}/{tile_slug}", "mode": "managed", "dependencies": {}}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _tessl_live_tile_slug(source_root: Path) -> str:
    return _tessl_project_slug(source_root)


def _write_tessl_live_plugin_manifest(source_root: Path, staged_root: Path, workspace: str) -> list[str]:
    tile_slug = _tessl_live_tile_slug(source_root)
    tile_version = _skill_tessl_tile_version(source_root)
    summary = f"Private live eval plugin for {source_root.name}."
    tessl_plugin_manifest = staged_root / ".tessl-plugin" / "plugin.json"
    tessl_plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
    tessl_plugin_payload = {
        "schema_version": 1,
        "name": f"{workspace}/{tile_slug}",
        "version": tile_version,
        "description": summary,
        "private": True,
        "skills": "./skills/",
    }
    tessl_plugin_manifest.write_text(json.dumps(tessl_plugin_payload, indent=2) + "\n", encoding="utf-8")
    return [
        ".tessl-plugin/plugin.json",
        *_write_tessl_live_project_marker(staged_root, workspace, tile_slug),
    ]


def _write_tessl_registry_readme(source_root: Path, staged_root: Path, workspace: str) -> list[str]:
    source_readme = source_root / "README.md"
    readme_target = staged_root / "README.md"
    tile_slug = _tessl_live_tile_slug(source_root)
    if source_readme.exists():
        _reject_tessl_staging_symlink(source_root, source_readme)
        shutil.copy2(source_readme, readme_target)
        _append_tessl_registry_readme_section(readme_target, workspace, tile_slug)
    else:
        readme_target.write_text(
            (
                f"# {source_root.name}\n\n"
                f"Registry presentation for the private Tessl package `{workspace}/{tile_slug}`.\n\n"
                "Agent runtime instructions live in `skills/` and `SKILL.md`; this README is "
                "for registry presentation and should not be treated as agent context.\n\n"
                "## GitHub Badge\n\n"
                "When this package is public in the Tessl registry, paste the registry-provided "
                "GitHub badge Markdown here so repository readers can see the current Tessl score.\n\n"
                "## Score Improvement And CI Gate\n\n"
                "Use `tessl skill review --optimize` to improve a weak registry score before "
                "promotion. Use `tessl review run` in CI when the package needs a score "
                "threshold gate.\n"
            ),
            encoding="utf-8",
        )
    return ["README.md"]


def _append_tessl_registry_readme_section(readme_target: Path, workspace: str, tile_slug: str) -> None:
    text = readme_target.read_text(encoding="utf-8")
    required = ("GitHub Badge", "Tessl registry", "tessl skill review --optimize", "tessl review run")
    if all(phrase in text for phrase in required):
        return
    suffix = (
        "\n\n## Tessl Registry Presentation\n\n"
        f"Registry presentation for the private Tessl package `{workspace}/{tile_slug}`. "
        "Agent runtime instructions live in `skills/` and `SKILL.md`; this README is "
        "for registry presentation and should not be treated as agent context.\n\n"
        "### GitHub Badge\n\n"
        "When this package is public in the Tessl registry, paste the registry-provided "
        "GitHub badge Markdown here so repository readers can see the current Tessl score.\n\n"
        "### Score Improvement And CI Gate\n\n"
        "Use `tessl skill review --optimize` to improve a weak registry score before "
        "promotion. Use `tessl review run` in CI when the package needs a score threshold gate.\n"
    )
    readme_target.write_text(text.rstrip() + suffix, encoding="utf-8")


def _write_tesslignore(staged_root: Path) -> list[str]:
    tesslignore = staged_root / ".tesslignore"
    tesslignore.write_text(
        (
            "# Generated by Skills SDK Tessl staging.\n"
            "# Agent host context is project-local and not plugin package context.\n"
            "AGENTS.md\n"
            "CLAUDE.md\n"
            "GEMINI.md\n"
            "notes.md\n"
            "TODO.md\n"
            "*.draft.md\n"
            "test-data/\n"
            ".harness/\n"
            ".agents/\n"
            ".codex/\n"
            ".tessl/\n"
            "dist/\n"
        ),
        encoding="utf-8",
    )
    return [".tesslignore"]


def _validate_tessl_live_private_manifest(plugin_path: Path, workspace: str, project_slug: str | None = None) -> None:
    manifest = _load_json_object_file(plugin_path, label="staged Tessl plugin manifest")
    plugin_name = manifest.get("name")
    if not isinstance(plugin_name, str) or not plugin_name.startswith(f"{workspace}/"):
        raise ValueError("Staged Tessl plugin name must use workspace/plugin-name format for the requested workspace.")
    if project_slug is not None and plugin_name != f"{workspace}/{project_slug}":
        raise ValueError(
            "Staged Tessl plugin name must match the requested workspace/project "
            f"{workspace}/{project_slug}."
        )
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Staged Tessl plugin manifest must include a non-empty description.")
    if manifest.get("private") is not True:
        raise ValueError("Staged Tessl plugin manifest must set private: true.")
    version = manifest.get("version")
    if not isinstance(version, str) or not TESSL_TILE_VERSION_RE.fullmatch(version):
        raise ValueError("Staged Tessl plugin manifest must include a SemVer version.")
    skills = manifest.get("skills")
    if skills != "./skills/":
        raise ValueError('Staged Tessl plugin manifest skills must be "./skills/".')
    if "rules" in manifest:
        raise ValueError(
            "Skills SDK Tessl skill projections must keep skill support context in references/, not map it to Tessl rules/."
        )
    if "mcpServers" in manifest and manifest["mcpServers"] not in (".mcp.json", "./.mcp.json"):
        raise ValueError("Staged Tessl plugin manifest mcpServers must point to .mcp.json or ./.mcp.json.")


def _load_json_object_file(path: Path, *, label: str) -> dict[str, object]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to read {label}: {e}") from e
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return loaded


def _validate_tessl_bundled_mcp(staged_root: Path, manifest: dict[str, object]) -> None:
    mcp_path = staged_root / ".mcp.json"
    if "mcpServers" in manifest and not mcp_path.is_file():
        raise ValueError("Staged Tessl plugin manifest declares mcpServers but .mcp.json is missing.")
    if not mcp_path.exists():
        return
    mcp_payload = _load_json_object_file(mcp_path, label="staged Tessl bundled .mcp.json")
    servers = mcp_payload.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        raise ValueError("Staged Tessl bundled .mcp.json must contain a non-empty top-level mcpServers map.")
    for server_name, server_config in servers.items():
        if not isinstance(server_name, str) or not isinstance(server_config, dict):
            raise ValueError("Staged Tessl bundled .mcp.json server entries must be named objects.")
        server_type = server_config.get("type")
        if server_type == "stdio":
            command = server_config.get("command")
            if not isinstance(command, str) or not command.strip():
                raise ValueError("Staged Tessl stdio MCP servers must declare a command.")
        elif server_type == "http":
            url = server_config.get("url")
            if not isinstance(url, str) or not re.fullmatch(r"https?://.+", url):
                raise ValueError("Staged Tessl http MCP servers must declare an http or https url.")
        else:
            raise ValueError("Staged Tessl bundled .mcp.json server type must be stdio or http.")


def _validate_tessl_registry_readme(staged_root: Path) -> None:
    readme_path = staged_root / "README.md"
    try:
        text = readme_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Failed to read staged Tessl README.md: {e}") from e
    required = (
        "GitHub Badge",
        "Tessl registry",
        "tessl skill review --optimize",
        "tessl review run",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ValueError(
            "Staged Tessl README.md must document registry presentation, badge placement, "
            f"score optimization, and CI review gating; missing: {', '.join(missing)}"
        )


def _validate_tessl_project_marker(staged_root: Path, workspace: str, project_slug: str) -> None:
    marker = _load_json_object_file(staged_root / "tessl.json", label="staged Tessl project marker")
    name = marker.get("name")
    expected_name = f"{workspace}/{project_slug}"
    if name != expected_name:
        raise ValueError(
            "Staged Tessl tessl.json must include the exact workspace/project name "
            f"{expected_name}."
        )
    if marker.get("mode") not in ("managed", "vendored"):
        raise ValueError("Staged Tessl tessl.json must declare mode as managed or vendored.")


def _validate_tesslignore(staged_root: Path) -> None:
    ignore_path = staged_root / ".tesslignore"
    try:
        text = ignore_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Failed to read staged Tessl .tesslignore: {e}") from e
    required = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".harness/", ".agents/", ".codex/", "dist/")
    missing = [entry for entry in required if entry not in text]
    if missing:
        raise ValueError("Staged Tessl .tesslignore is missing required exclusions: " + ", ".join(missing))
    forbidden = ("skills", "skills/", "rules", "rules/", "docs", "docs/")
    active_lines = {line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")}
    blocked_entrypoints = sorted(entry for entry in forbidden if entry in active_lines)
    if blocked_entrypoints:
        raise ValueError(
            "Staged Tessl .tesslignore must not ignore manifest entrypoints: "
            + ", ".join(blocked_entrypoints)
        )


def _validate_tessl_eval_directories(staged_root: Path, *, require_evals: bool) -> None:
    evals_root = staged_root / "evals"
    if require_evals and not evals_root.is_dir():
        raise ValueError("Staged Tessl package must include evals/<case-id>/task.md and criteria.json.")
    if not evals_root.exists():
        return
    case_dirs = [path for path in evals_root.iterdir() if path.is_dir()]
    if require_evals and not case_dirs:
        raise ValueError("Staged Tessl package evals/ must contain at least one case directory.")
    missing: list[str] = []
    for case_dir in sorted(case_dirs):
        for filename in ("task.md", "criteria.json"):
            if not (case_dir / filename).is_file():
                missing.append(str((case_dir / filename).relative_to(staged_root)))
    if missing:
        raise ValueError("Staged Tessl eval cases are missing required files: " + ", ".join(missing))


def _validate_tessl_projection_shape(
    staged_root: Path,
    *,
    skill_name: str,
    workspace: str,
    project_slug: str,
    require_evals: bool,
) -> None:
    _validate_tessl_workspace(workspace)
    required_paths = [
        ".tessl-plugin/plugin.json",
        "README.md",
        ".tesslignore",
        "tessl.json",
        f"skills/{skill_name}/SKILL.md",
    ]
    missing = [relative for relative in required_paths if not (staged_root / relative).is_file()]
    if missing:
        raise ValueError("Staged Tessl package is missing required projection files: " + ", ".join(missing))
    if (staged_root / "rules").exists():
        raise ValueError(
            "Skills SDK Tessl skill projections must not place skill support context in root rules/; use references/."
        )
    manifest_path = staged_root / ".tessl-plugin" / "plugin.json"
    _validate_tessl_live_private_manifest(manifest_path, workspace, project_slug)
    manifest = _load_json_object_file(manifest_path, label="staged Tessl plugin manifest")
    _validate_tessl_bundled_mcp(staged_root, manifest)
    _validate_tessl_registry_readme(staged_root)
    _validate_tessl_project_marker(staged_root, workspace, project_slug)
    _validate_tesslignore(staged_root)
    _validate_tessl_eval_directories(staged_root, require_evals=require_evals)


def _copy_tessl_live_reference_support_files(
    source_root: Path,
    staged_root: Path,
    already_copied: set[str],
) -> list[str]:
    references_root = source_root / "references"
    if not references_root.exists():
        return []

    copied: list[str] = []
    for source_file in sorted(references_root.rglob("*")):
        if not source_file.is_file():
            continue
        relative_path = source_file.relative_to(source_root).as_posix()
        if relative_path in already_copied:
            continue
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
        already_copied.add(relative_path)
    return copied


def _copy_tessl_live_skill_package(source_root: Path, staged_root: Path) -> list[str]:
    skill_package_root = f"skills/{source_root.name}"
    copied: list[str] = []
    copied.extend(_copy_tree_files_to_relative_root(source_root, "agents", staged_root, skill_package_root))
    copied.extend(_copy_tree_files_to_relative_root(source_root, "assets", staged_root, skill_package_root))
    copied.extend(_copy_tree_files_to_relative_root(source_root, "references", staged_root, skill_package_root))

    skill_source = source_root / "SKILL.md"
    if skill_source.exists():
        _reject_tessl_staging_symlink(source_root, skill_source)
        skill_target = staged_root / skill_package_root / "SKILL.md"
        skill_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_source, skill_target)
        copied.append(f"{skill_package_root}/SKILL.md")
    return copied


def _stable_tessl_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stable_tessl_live_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stable_tessl_local_install_workspace(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-local-install" / f"{safe_name}-{digest}"


def _tessl_archive_suffix() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _unique_archive_dir(archive_root: Path, label: str) -> Path:
    archive_root.mkdir(parents=True, exist_ok=True)
    safe_label = _safe_slug(label)
    archive_dir = archive_root / f"{_tessl_archive_suffix()}-{safe_label}"
    while archive_dir.exists():
        archive_dir = archive_root / f"{_tessl_archive_suffix()}-{safe_label}"
    return archive_dir


def _sanitize_tessl_archive_ingestable_dirs(archive_root: Path) -> None:
    if not archive_root.exists():
        return
    for child in sorted((path for path in archive_root.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True):
        if child.name not in {"evals", "scenarios"}:
            continue
        target = child.with_name(f"archived-{child.name}")
        suffix = 1
        while target.exists():
            target = child.with_name(f"archived-{child.name}-{suffix}")
            suffix += 1
        shutil.move(str(child), target)


def _archive_stage_children(stage_root: Path, label: str) -> Path | None:
    if not stage_root.exists():
        return None
    archive_root = stage_root.parent / f"{stage_root.name}-evidence-archive"
    legacy_archive_root = stage_root / "evidence-archive"
    if legacy_archive_root.exists():
        legacy_archive_dir = _unique_archive_dir(archive_root, "legacy-evidence-archive")
        legacy_archive_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy_archive_root), legacy_archive_dir)
    _sanitize_tessl_archive_ingestable_dirs(archive_root)
    children = list(stage_root.iterdir())
    if not children:
        return None
    archive_dir = _unique_archive_dir(archive_root, label)
    archive_dir.mkdir()
    for child in children:
        archived_name = f"archived-{child.name}" if child.name in {"evals", "scenarios"} else child.name
        shutil.move(str(child), archive_dir / archived_name)
    _sanitize_tessl_archive_ingestable_dirs(archive_root)
    return archive_dir


def _archive_stage_directory(stage_dir: Path, label: str) -> Path | None:
    if not stage_dir.exists() or not any(stage_dir.iterdir()):
        return None
    archive_dir = _unique_archive_dir(stage_dir.parent / "evidence-archive", label)
    shutil.move(str(stage_dir), archive_dir)
    return archive_dir


def _json_or_text(text_value: str) -> object:
    try:
        return json.loads(text_value)
    except json.JSONDecodeError:
        return text_value


def _tessl_json_status(process: subprocess.CompletedProcess[str]) -> str | None:
    parsed = _json_or_text(process.stdout.strip()) if process.stdout.strip() else None
    if isinstance(parsed, dict):
        status = parsed.get("status") or parsed.get("outcome")
        if isinstance(status, str):
            return status.lower()
    return None


def _tessl_process_succeeded(process: subprocess.CompletedProcess[str]) -> bool:
    if process.returncode != 0:
        return False
    return _tessl_json_status(process) != "error"

__all__ = [name for name in globals() if not name.startswith("__")]
