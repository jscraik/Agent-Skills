from run_skill_evals_preflight import *  # noqa: F403

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Builds and returns the command-line argument parser for run_skill_evals.py.

    The parser includes options for selecting cases and runners, eval suite mode and categories,
    timeout and runtime configuration, Codex/Codex/OpenAI CLI overrides and extra flags,
    JSONL capture and reporting paths, and tier2 gating behavior.

    Returns:
        argparse.ArgumentParser: A parser configured with the script's CLI options.
    """
    p = argparse.ArgumentParser(
        prog="run_skill_evals.py",
        description="Run skill evals using Codex, Codex (Kimi/Zai), and/or OpenAI CLI runners.",
    )
    p.add_argument("path", help="Path to a skill directory or SKILL.md.")
    p.add_argument(
        "--list-cases",
        action="store_true",
        help="List available eval cases (respects --case/--category filters) and exit.",
    )

    p.add_argument("--runner", choices=_RUNNER_CHOICES, default="codex", help="Single-run mode runner.")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Shortcut for `--runner discovery-smoke` for fast contract-level discovery smoke checks.",
    )
    p.add_argument(
        "--runners",
        action="append",
        default=[],
        help=(
            "Explicit runner list (repeatable or comma-separated). "
            "Examples: --runners codex,codex-kimi --runners openai"
        ),
    )
    p.add_argument("--dual-run", action="store_true", help="Run both Codex and Codex-Kimi for every eval case.")
    p.add_argument(
        "--case",
        action="append",
        default=[],
        help=(
            "Run only matching eval case ids/names (repeatable or comma-separated). "
            "Substring match against case id and name."
        ),
    )
    p.add_argument(
        "--eval-mode",
        choices=_EVAL_MODE_CHOICES,
        default="standard",
        help=(
            "Eval suite mode. `standard` preserves current behavior, "
            "`smoke` runs a faster contract/regression subset, and `release` runs the full release-grade suite."
        ),
    )
    p.add_argument(
        "--category",
        action="append",
        default=[],
        help=(
            "Run only evals in matching category (repeatable or comma-separated). "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        ),
    )

    p.add_argument("--workspace", default=None, help="Workspace root to run commands in (defaults to repo root guess).")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--ask-for-approval",
        default=None,
        choices=["untrusted", "on-request", "never"],
        help=(
            "Legacy Codex approval mode flag. Prefer configuring approval policy via profile/config; "
            "ignored when the active Codex CLI does not support --ask-for-approval."
        ),
    )
    p.add_argument(
        "--timeout-sec",
        type=float,
        default=None,
        help="Per-runner subprocess timeout in seconds. Overrides env vars and timeout profile.",
    )
    p.add_argument(
        "--timeout-profile",
        choices=_TIMEOUT_PROFILE_CHOICES,
        default="default",
        help=(
            "Timeout preset. `codex-heavy` raises the default timeout for slow Codex startup paths; "
            "`discovery-heavy` is a longer preset for interview/discovery prompts."
        ),
    )
    p.add_argument("--model", default=None, help="Override model for codex exec.")
    p.add_argument("--profile", default=None, help="Codex config profile name.")
    p.add_argument(
        "--codex-fallback-profile",
        default="d",
        help=(
            "Auto-retry profile for Codex when active profile/model rejects reasoning.summary "
            "(default: d). Set empty string to disable."
        ),
    )
    p.add_argument(
        "--codex-home",
        default=None,
        help="Set CODEX_HOME. This replaces the full Codex home; live Codex runs need authenticated state in the selected home.",
    )
    p.add_argument("--codex-bin", default=None, help="Override codex CLI path.")
    p.add_argument("--openai-bin", default=None, help="Override openai CLI path.")
    p.add_argument(
        "--codex-output-format",
        choices=["text", "json"],
        default="text",
        help="Codex output format (default: text).",
    )
    p.add_argument(
        "--openai-output-format",
        choices=["text", "json", "stream-json"],
        default="text",
        help="OpenAI output format (default: text).",
    )
    p.add_argument(
        "--codex-settings",
        default=None,
        help="DEPRECATED: plain `codex` runner was removed. Use --codex-kimi-settings / --codex-zai-settings.",
    )
    p.add_argument(
        "--codex-kimi-settings",
        default="kimi_settings.json",
        help="Settings JSON used by runner `codex-kimi` (default: kimi_settings.json).",
    )
    p.add_argument(
        "--codex-zai-settings",
        default="zai_settings.json",
        help="Settings JSON used by runner `codex-zai` (default: zai_settings.json).",
    )
    p.add_argument(
        "--codex-kimi-command",
        default="codex-kimi",
        help="Interactive shell command used for runner `codex-kimi` (default: codex-kimi).",
    )
    p.add_argument(
        "--codex-zai-command",
        default="codex-zai",
        help="Interactive shell command used for runner `codex-zai` (default: codex-zai).",
    )
    p.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra flag to pass to codex CLI (repeatable; supports `--codex-arg --flag`).",
    )
    p.add_argument(
        "--openai-arg",
        action="append",
        default=[],
        help="Extra flag to pass to openai CLI (repeatable; supports `--openai-arg --flag`).",
    )
    p.add_argument(
        "--capture-jsonl",
        action="store_true",
        help="Capture Codex JSONL event stream (--json). Auto-enabled when deterministic checks or budgets are present; required for --dual-run.",
    )
    p.add_argument("--reports-dir", default="Infrastructure/artifacts/skills", help="Base directory for eval reports.")
    p.add_argument("--scorecard-out", default=None, help="Optional explicit path for merged scorecard JSON.")
    p.add_argument("--junit-out", default=None, help="Optional explicit path for JUnit XML output (default: <run>/junit.xml).")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--tier2-mode",
        choices=["warn", "fail", "off"],
        default="warn",
        help="How to treat tier-2 findings (rubric/efficiency budgets).",
    )
    return p


def _guess_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


def _resolve_path(path_like: str, *, base: Path) -> Path:
    p = Path(path_like).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (base / p).resolve()


def _make_relative(path: Optional[Path], base: Path) -> str:
    """Convert absolute path to relative path from base, or return as-is if not possible."""
    if path is None:
        return ""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


WORKFLOW_CLOSEOUT_SCHEMA_VERSION = "skills-sdk.eval-closeout.v1"


def _case_status_from_summary(case: Dict[str, Any]) -> str:
    if case.get("blocked") is True:
        return "blocked"
    if case.get("passed") is True:
        return "pass"
    return "fail"


def _case_closeout_from_summary(case: Dict[str, Any]) -> Dict[str, Any]:
    status = _case_status_from_summary(case)
    entry: Dict[str, Any] = {
        "id": str(case.get("id") or case.get("name") or "unknown"),
        "status": status,
    }
    if case.get("dir"):
        entry["result_path"] = str(case.get("dir"))
    blocker_classes = case.get("blocker_classes")
    if status == "blocked" and isinstance(blocker_classes, list) and blocker_classes:
        entry["blocker_class"] = str(blocker_classes[0])
    if status != "pass":
        failures = case.get("tier1_failures")
        if isinstance(failures, list) and failures:
            entry["failures"] = [str(item) for item in failures]
        blocked_reasons = case.get("blocked_reasons")
        if isinstance(blocked_reasons, list) and blocked_reasons:
            entry["blocked_reasons"] = [str(item) for item in blocked_reasons]
    return entry


def _case_closeout_from_artifact_dir(case_dir: Path, workspace_root: Path) -> Dict[str, Any]:
    case_id = re.sub(r"^\d+-", "", case_dir.name)
    result_path = case_dir / "result.json"
    if result_path.is_file():
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, dict):
            return _case_closeout_from_summary(payload)
    actual_artifacts = [
        path.relative_to(case_dir).as_posix()
        for path in sorted(case_dir.rglob("*"))
        if path.is_file()
    ]
    return {
        "id": case_id,
        "status": "blocked",
        "blocker_class": "blocked_missing_artifact",
        "expected_artifacts": ["result.json"],
        "actual_artifacts": actual_artifacts,
        "result_path": _make_relative(case_dir, workspace_root),
    }


def _workflow_closeout_validation(closeout: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    required = {
        "schema_version",
        "status",
        "skill_path",
        "mode",
        "runner",
        "cases",
        "mutation_allowed",
        "registry_update_allowed",
        "next_reproduce_command",
    }
    missing = sorted(required - set(closeout))
    checks.append({
        "id": "required_fields_present",
        "status": "blocker" if missing else "pass",
        "message": "workflow-closeout/v1 receipts must include required contract fields.",
        "evidence": missing,
    })
    schema_version = closeout.get("schema_version")
    checks.append({
        "id": "schema_version_valid",
        "status": "pass" if schema_version == WORKFLOW_CLOSEOUT_SCHEMA_VERSION else "blocker",
        "message": "workflow-closeout receipt must use skills-sdk.eval-closeout.v1.",
        "evidence": [] if schema_version == WORKFLOW_CLOSEOUT_SCHEMA_VERSION else [str(schema_version)],
    })
    cases = closeout.get("cases")
    case_list = cases if isinstance(cases, list) else []
    checks.append({
        "id": "cases_array_valid",
        "status": "pass" if isinstance(cases, list) else "blocker",
        "message": "workflow-closeout receipt must carry cases as an array.",
        "evidence": [] if isinstance(cases, list) else [type(cases).__name__],
    })
    status = str(closeout.get("status") or "")
    blocked_cases = [
        str(case.get("id") or index)
        for index, case in enumerate(case_list, start=1)
        if isinstance(case, dict) and str(case.get("status") or "") == "blocked"
    ]
    checks.append({
        "id": "blocked_cases_block_suite",
        "status": "blocker" if blocked_cases and status != "blocked" else "pass",
        "message": "Any blocked case must make the suite closeout status blocked.",
        "evidence": blocked_cases if blocked_cases and status != "blocked" else [],
    })
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": "skills-sdk.eval-closeout-validation.v1",
        "status": "blocked" if blockers else "pass",
        "checks": checks,
        "blockers": blockers,
    }


def _write_workflow_closeout(
    *,
    reports_base: Path,
    workspace_root: Path,
    skill_dir: Path,
    eval_mode: str,
    runner_mode: str,
    status: str,
    cases: List[Dict[str, Any]],
    blocker_class: Optional[str],
    missing_suite_artifacts: bool,
    next_reproduce_command: str,
) -> Path:
    closeout: Dict[str, Any] = {
        "schema_version": WORKFLOW_CLOSEOUT_SCHEMA_VERSION,
        "status": status,
        "skill_path": _make_relative(skill_dir, workspace_root),
        "mode": eval_mode,
        "runner": runner_mode,
        "report_dir": _make_relative(reports_base, workspace_root),
        "cases_expected": [str(case.get("id") or "unknown") for case in cases],
        "cases": cases,
        "blocker_class": blocker_class,
        "mutation_allowed": status == "pass",
        "registry_update_allowed": status == "pass" and eval_mode == "release",
        "raw_output_present": False,
        "raw_error_present": False,
        "missing_suite_artifacts": missing_suite_artifacts,
        "case_evidence_present": bool(cases),
        "next_reproduce_command": next_reproduce_command,
    }
    closeout["closeout_validation"] = _workflow_closeout_validation(closeout)
    path = reports_base / "workflow-closeout.json"
    path.write_text(json.dumps(closeout, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_provisional_workflow_closeout(
    *,
    reports_base: Path,
    workspace_root: Path,
    skill_dir: Path,
    eval_mode: str,
    runner_mode: str,
    next_reproduce_command: str,
) -> Path:
    case_dirs = [
        path
        for path in sorted(reports_base.iterdir())
        if path.is_dir() and re.match(r"^\d+-", path.name)
    ]
    cases = [_case_closeout_from_artifact_dir(path, workspace_root) for path in case_dirs]
    return _write_workflow_closeout(
        reports_base=reports_base,
        workspace_root=workspace_root,
        skill_dir=skill_dir,
        eval_mode=eval_mode,
        runner_mode=runner_mode,
        status="blocked",
        cases=cases,
        blocker_class="blocked_missing_artifact",
        missing_suite_artifacts=True,
        next_reproduce_command=next_reproduce_command,
    )


def _release_dependency_scan_roots(skill_dir: Path) -> List[Path]:
    roots = [skill_dir]
    parts = skill_dir.parts
    if "Plugins" in parts:
        idx = parts.index("Plugins")
        if len(parts) > idx + 2 and "skills" in parts[idx + 2 :]:
            plugin_root = Path(*parts[: idx + 2])
            if plugin_root not in roots:
                roots.append(plugin_root)
    return roots


def _is_snyk_manifest(path: Path) -> bool:
    return path.name in SNYK_MANIFEST_NAMES or path.name.endswith(SNYK_MANIFEST_SUFFIXES)


def _dependency_manifest_paths(skill_dir: Path, *, limit: int = 25) -> List[Path]:
    manifests: List[Path] = []
    seen: Set[Path] = set()
    for root in _release_dependency_scan_roots(skill_dir):
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file() or not _is_snyk_manifest(candidate):
                continue
            relative_parts = candidate.relative_to(root).parts[:-1]
            if any(part in SNYK_MANIFEST_EXCLUDED_DIRS for part in relative_parts):
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            manifests.append(candidate)
            if len(manifests) >= limit:
                return manifests
    return manifests


def _snyk_release_gate(
    *,
    skill_dir: Path,
    workspace_root: Path,
    timeout_seconds: int = 180,
) -> Dict[str, Any]:
    scan_roots = _release_dependency_scan_roots(skill_dir)
    scan_target = scan_roots[-1]
    manifests = _dependency_manifest_paths(skill_dir)
    gate: Dict[str, Any] = {
        "schema_version": "skill-release-snyk-gate.v1",
        "required": bool(manifests),
        "status": "not_applicable",
        "reason": "No supported dependency manifest found under the skill package.",
        "manifest_paths": [_make_relative(path, workspace_root) for path in manifests],
        "command": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
    }
    if not manifests:
        return gate

    snyk_bin = shutil.which("snyk")
    if not snyk_bin:
        gate.update({
            "status": "blocked_missing_binary",
            "reason": "Snyk CLI is required for release evals of manifest-backed skill packages.",
            "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
        })
        return gate

    command = [
        snyk_bin,
        "test",
        "--all-projects",
        "--detection-depth=6",
        "--severity-threshold=high",
        "--exclude=node_modules,cache,artifacts,tmp,fixtures,budget-archive",
        "--json",
        str(scan_target),
    ]
    gate["command"] = command
    try:
        proc = sp.run(command, cwd=str(workspace_root), capture_output=True, text=True, timeout=timeout_seconds)
    except sp.TimeoutExpired as exc:
        gate.update({
            "status": "timeout",
            "reason": f"Snyk timed out after {timeout_seconds} seconds.",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        })
        return gate

    gate.update({"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    combined_output = f"{proc.stdout}\n{proc.stderr}".lower()
    if proc.returncode == 0:
        gate["status"] = "success"
        gate["reason"] = "Snyk dependency screening passed for the manifest-backed skill package."
    elif (
        "use snyk auth" in combined_output
        or "not authenticated" in combined_output
        or "authentication required" in combined_output
        or "snyk_token" in combined_output
    ):
        gate["status"] = "blocked_auth"
        gate["reason"] = "Snyk authentication is required for release evals of manifest-backed skill packages."
    elif "could not detect supported target files" in combined_output or "no supported files" in combined_output:
        gate["status"] = "blocked_no_supported_projects"
        gate["reason"] = "Dependency manifests were present, but Snyk did not detect a supported project."
    elif proc.returncode == 1:
        gate["status"] = "advisory"
        gate["reason"] = "Snyk reported high-severity dependency advisories."
    else:
        gate["status"] = "error"
        gate["reason"] = "Snyk failed during release dependency screening."
    return gate


def _snyk_release_gate_passed(gate: Dict[str, Any]) -> bool:
    if not gate.get("required"):
        return True
    return gate.get("status") == "success"


def _extract_min_rubric_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    if not budgets:
        return None
    v = budgets.get("min_rubric_score")
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _extract_min_expected_signal_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    return parse_min_expected_signal_score(budgets)


def _extract_require_overall_pass(budgets: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not budgets:
        return None
    v = budgets.get("require_overall_pass")
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        text = v.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def _extract_bool_budget(budgets: Optional[Dict[str, Any]], key: str) -> Optional[bool]:
    if not budgets:
        return None
    value = budgets.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def _extract_min_skill_lift(budgets: Optional[Dict[str, Any]]) -> Optional[int]:
    if not budgets:
        return None
    value = budgets.get("min_skill_lift")
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _print_case_listing(cases: Sequence[EvalCase]) -> None:
    print("Available eval cases:")
    for case in cases:
        category = case.category or "uncategorized"
        smoke = case.smoke_mode or "-"
        eval_modes = ",".join(case.eval_modes) if case.eval_modes else "auto"
        timeout_profile = case.timeout_profile or "-"
        timeout_sec = (
            f"{case.timeout_sec:g}" if isinstance(case.timeout_sec, (int, float)) else "-"
        )
        print(
            f"- {case.id} [{category}] "
            f"(prepend_skill={str(case.prepend_skill).lower()}, smoke_mode={smoke}, eval_modes={eval_modes}, "
            f"timeout_profile={timeout_profile}, timeout_sec={timeout_sec})"
        )
        print(f"  name: {case.name}")

__all__ = [name for name in globals() if not name.startswith("__")]
