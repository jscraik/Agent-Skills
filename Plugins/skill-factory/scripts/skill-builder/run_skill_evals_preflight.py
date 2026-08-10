from functools import lru_cache

from run_skill_evals_runners import *  # noqa: F403

def _filter_cases(
    cases: List[EvalCase],
    *,
    case_filters: Sequence[str],
    categories: Sequence[str],
    exact_case_ids: bool = False,
) -> List[EvalCase]:
    """
    Filter eval cases by case id/name substring and by category.

    Parameters:
        case_filters (Sequence[str]): Terms used to match case ids or names. An empty sequence disables id/name filtering.
        categories (Sequence[str]): Category names to include (case-insensitive). An empty sequence disables category filtering.
        exact_case_ids (bool): When true, case filters must match the exact case id. Release scenario-set
            expansion uses this to prevent substring leakage into generated fixture ids.

    Returns:
        List[EvalCase]: The subset of `cases` that match all provided filters.

    Raises:
        ValueError: If any provided category is not in the allowed set, or if no cases match the supplied filters.
    """
    if not case_filters and not categories:
        return cases

    category_set = {c.lower() for c in categories if c}
    invalid_categories = sorted(category_set - _VALID_CATEGORIES)
    if invalid_categories:
        raise ValueError(
            f"Unknown category filter(s): {', '.join(invalid_categories)}. "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        )

    case_terms = [term.lower() for term in case_filters if term]
    filtered: List[EvalCase] = []
    for case in cases:
        haystack = f"{case.id} {case.name}".lower()
        if exact_case_ids:
            match_case = not case_terms or case.id.lower() in case_terms
        else:
            match_case = not case_terms or any(term in haystack for term in case_terms)
        match_category = not category_set or ((case.category or "").lower() in category_set)
        if match_case and match_category:
            filtered.append(case)

    if not filtered:
        available = ", ".join(f"{c.id}({c.category or 'uncategorized'})" for c in cases)
        raise ValueError(
            "No eval cases matched the supplied filters. "
            f"Available cases: {available}"
        )

    return filtered


def _codex_cli_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Builds the command prefix to invoke the Codex CLI, preferring a bundled `node` executable when present.

    Parameters:
        codex_bin (Optional[Path]): Path to a specific `codex` binary. If `None`, the system `codex` command name is used.

    Returns:
        List[str]: Sequence of command tokens to run the CLI:
            - `["node", "<codex_bin>"]` if a sibling `node` executable exists next to `codex_bin`,
            - `["<codex_bin>"]` if `codex_bin` is provided without a sibling `node`,
            - `["codex"]` if `codex_bin` is `None`.
    """
    effective_codex_bin = codex_bin or _mise_codex_bin()
    if effective_codex_bin:
        node_bin = effective_codex_bin.parent / "node"
        if not node_bin.exists() and _is_node_launcher(effective_codex_bin):
            node_bin = _mise_repo_node_bin()
        if node_bin and node_bin.exists():
            return [str(node_bin), str(effective_codex_bin)]
        return [str(effective_codex_bin)]
    return ["codex"]


def _is_node_launcher(path: Path) -> bool:
    try:
        first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except (OSError, IndexError):
        return False
    return "node" in first_line and first_line.startswith("#!")


def _mise_codex_bin() -> Optional[Path]:
    codex_bin = Path.home() / ".local" / "share" / "mise" / "installs" / "npm-openai-codex" / "latest" / "bin" / "codex"
    return codex_bin.resolve() if codex_bin.exists() else None


def _mise_repo_node_bin() -> Optional[Path]:
    version = _repo_mise_node_version()
    if not version:
        return None
    node_bin = Path.home() / ".local" / "share" / "mise" / "installs" / "node" / version / "bin" / "node"
    return node_bin if node_bin.exists() else None


def _repo_mise_node_version() -> Optional[str]:
    config_path = WORKSPACE_ROOT / ".mise.toml"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except OSError:
        return None
    except tomllib.TOMLDecodeError:
        return None
    tools = config.get("tools")
    if not isinstance(tools, dict):
        return None
    value = tools.get("node")
    return value if isinstance(value, str) and value.strip() else None


def _codex_exec_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Build the command token prefix for invoking the Codex CLI `exec` subcommand.

    Parameters:
        codex_bin (Optional[Path]): Optional path to a specific `codex` binary to prefer; if `None` the default resolver is used.

    Returns:
        List[str]: A list of command tokens forming the prefix (e.g. `["codex", "exec"]` or `["node", "...", "codex", "exec"]`).
    """
    return [*_codex_cli_prefix(codex_bin), "exec"]


def _effective_codex_home(codex_home: Optional[Path]) -> Path:
    """
    Resolve the effective CODEX_HOME directory to use for Codex operations.

    If `codex_home` is provided, it is used; otherwise the `CODEX_HOME` environment variable is used if set; if neither is present, defaults to `~/.codex`. The returned Path is expanded and resolved to an absolute path.

    Parameters:
        codex_home (Optional[Path]): Optional override path for CODEX_HOME.

    Returns:
        Path: Absolute, expanded, resolved path to the Codex home directory.
    """
    raw = str(codex_home) if codex_home else (os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    return Path(raw).expanduser().resolve()


def _copy_codex_home_file(source_home: Path, target_home: Path, name: str) -> Optional[str]:
    source = source_home / name
    if not source.exists():
        return None
    target = target_home / name
    try:
        if name == "config.toml":
            target.write_text(_scrub_mcp_servers_from_toml(source.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(source, target)
    except OSError as exc:
        return f"Could not copy {source} into isolated Codex eval home: {exc}"
    return None


def _scrub_mcp_servers_from_toml(text: str) -> str:
    """
    Remove MCP server tables from copied Codex eval config.

    Live evals verify skill behavior through prompts and filesystem artifacts.
    Inheriting the operator's MCP servers can make unrelated remote OAuth
    failures look like skill failures, so isolated eval homes keep ordinary
    Codex config but drop all [mcp_servers.*] tables.
    """
    kept: List[str] = []
    skipping_mcp = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("["):
            section_name = stripped.lstrip("[").rstrip("]").strip()
            skipping_mcp = section_name == "mcp_servers" or section_name.startswith("mcp_servers.")
        if not skipping_mcp:
            kept.append(line)
    return "".join(kept)


def _isolated_codex_home_for_eval(
    profile: Optional[str] = None,
    *,
    source_home: Optional[Path] = None,
) -> Tuple[Path, List[str]]:
    """
    Build a temporary CODEX_HOME for live eval runs.

    Codex evals need authenticated state, but they should not write sessions into
    the operator's real ~/.codex tree. The temporary home receives only the small
    auth/config files needed to run `codex exec`; sessions and logs stay isolated.
    """
    warnings: List[str] = []
    source_home = _effective_codex_home(source_home)
    temp_home_ctx = tempfile.TemporaryDirectory(prefix="skill-evals-codex-home-")
    atexit.register(temp_home_ctx.cleanup)
    target_home = Path(temp_home_ctx.name).resolve()

    for child in ("sessions", "logs", "worktrees"):
        (target_home / child).mkdir(parents=True, exist_ok=True)

    if source_home.exists():
        profile_config = f"{profile}.config.toml" if profile else None
        if profile == "oss-cloud" and profile_config:
            required = ("config.toml", profile_config)
            missing = [name for name in required if not (source_home / name).is_file()]
            if missing:
                missing_names = ", ".join(missing)
                raise ValueError(
                    "oss-cloud eval requires both config.toml and oss-cloud.config.toml "
                    f"in CODEX_HOME; missing: {missing_names} ({source_home})"
                )
            names = ("auth.json", "config.toml", profile_config)
        else:
            names = ("auth.json", profile_config) if profile_config and (source_home / profile_config).is_file() else (
                "auth.json", "config.toml", "oss-local.config.toml", "oss-cloud.config.toml"
            )
        for name in names:
            warning = _copy_codex_home_file(source_home, target_home, name)
            if warning:
                warnings.append(warning)
    else:
        warnings.append(f"Default Codex home does not exist, using empty isolated eval home: {source_home}")

    warnings.append(f"Using isolated CODEX_HOME for live eval session writes: {target_home}")
    return target_home, warnings


def _codex_env(*, codex_bin: Optional[Path], codex_home: Optional[Path]) -> Dict[str, str]:
    """
    Builds an environment mapping configured for running the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary; when provided, its parent directory is prepended to the `PATH`.
        codex_home (Optional[Path]): Desired Codex home directory; when `None` an effective home is resolved via `_effective_codex_home`.

    Returns:
        Dict[str, str]: A copy of the current environment with `CODEX_HOME` set and `PATH` modified if `codex_bin` was provided.
    """
    env = os.environ.copy()
    effective_home = _effective_codex_home(codex_home)
    env["CODEX_HOME"] = str(effective_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"
    return env


def _codex_auth_env_keys(env: Dict[str, str]) -> List[str]:
    """
    Return the Codex authentication environment variable names that are present and non-empty in the provided environment mapping.

    Parameters:
        env (Dict[str, str]): Mapping of environment variable names to their values (typically os.environ).

    Returns:
        List[str]: Keys from `_CODEX_AUTH_ENV_VARS` whose corresponding value in `env` is non-empty after trimming.
    """
    return [key for key in _CODEX_AUTH_ENV_VARS if str(env.get(key) or "").strip()]


def _codex_login_status(
    *,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[int, str, str]:
    """
    Check the Codex CLI authentication status by running `codex login status`.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to use; if None the system PATH is used.
        codex_home (Optional[Path]): Codex home directory to set via the `CODEX_HOME` environment variable.

    Returns:
        Tuple[int, str, str]: A tuple of `(exit_code, stdout, stderr)`.
            - `exit_code`: the subprocess return code; `127` if the Codex CLI was not found, `124` if the command timed out.
            - `stdout`: the command's standard output as a string (empty string if none).
            - `stderr`: the command's standard error as a string (contains a user-facing message when CLI is missing or timed out).
    """
    cmd = [*_codex_cli_prefix(codex_bin), "login", "status"]
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=120)
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except sp.TimeoutExpired:
        return 124, "", "codex login status timed out after 120 seconds."
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _preflight_codex_live_runner(
    *,
    workspace_root: Path,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[List[str], List[str]]:
    """
    Validate that the configured Codex home/bin provide authenticated state required for live `codex exec` runs.

    Performs checks for the existence of the effective CODEX_HOME, presence of an auth.json file or auth-related environment variables, and attempts a short `codex login status` probe. Collects any blocking error messages and non-blocking warnings but does not raise exceptions.

    Parameters:
        workspace_root (Path): Repository/workspace root used to detect repo-local `.codex`.
        codex_bin (Optional[Path]): Optional path to a Codex binary to use for login status probing.
        codex_home (Optional[Path]): Optional explicit Codex home directory; if omitted an effective default is used.

    Returns:
        Tuple[List[str], List[str]]: A pair (errors, warnings).
            - errors: blocking issues that should prevent live Codex execution (e.g., missing home or missing authentication).
            - warnings: non-blocking diagnostics or guidance (e.g., env-based auth present despite login status).
    """
    errors: List[str] = []
    warnings: List[str] = []
    effective_home = _effective_codex_home(codex_home)
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    auth_env_keys = _codex_auth_env_keys(env)
    auth_file = effective_home / "auth.json"
    default_home = (Path.home() / ".codex").resolve()
    default_auth_file = default_home / "auth.json"
    repo_local_home = (workspace_root / ".codex").resolve()

    if not effective_home.exists():
        errors.append(f"Selected Codex home does not exist: {effective_home}")
        return errors, warnings

    if not auth_file.exists() and not auth_env_keys:
        message = (
            f"Selected Codex home is missing authenticated Codex state for live Codex runs: {effective_home}. "
            "`--codex-home` replaces CODEX_HOME for `codex exec`."
        )
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is provisioned with authenticated Codex state."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += (
                f" The default home {default_home} has auth.json, but the selected home does not inherit it."
            )
        message += " Use an authenticated Codex home for `--runner codex`, or omit `--codex-home` to use the default home."
        errors.append(message)
        return errors, warnings

    status_code, status_stdout, status_stderr = _codex_login_status(codex_bin=codex_bin, codex_home=effective_home)
    status_text = " ".join(part.strip() for part in (status_stdout, status_stderr) if part.strip()).strip()
    if status_code == 0:
        return errors, warnings

    if "not logged in" in status_text.lower():
        if auth_env_keys:
            warnings.append(
                "Codex login status reported 'Not logged in', but auth environment variables are present "
                f"({', '.join(auth_env_keys)}). Live exec may still work if this environment intentionally uses env-based auth."
            )
            return errors, warnings

        message = f"Selected Codex home is not logged in for live Codex runs: {effective_home}."
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is authenticated."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += f" The default home {default_home} has auth.json, but the selected home does not inherit it."
        message += (
            " Run `CODEX_HOME=<that-home> codex login` for the selected home, or omit `--codex-home` to use the default authenticated home."
        )
        errors.append(message)
        return errors, warnings

    warnings.append(
        f"Unable to confirm Codex login status for {effective_home}: {status_text or f'exit code {status_code}'}"
    )
    return errors, warnings


@lru_cache(maxsize=None)
def _codex_help_text(codex_bin: Optional[Path]) -> Optional[str]:
    """
    Retrieve and cache the combined help text for the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to query. If omitted, the system "codex" command will be used.

    Returns:
        Optional[str]: Combined stdout and stderr produced by running the help command, or `None` if the executable is not available or the help invocation failed.
    """
    cmd = _codex_exec_prefix(codex_bin) + ["--help"]
    env = os.environ.copy()
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=10, start_new_session=True)
    except (OSError, sp.SubprocessError):
        return None

    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return text


def _codex_supports_exec_flag(codex_bin: Optional[Path], flag: str) -> Optional[bool]:
    help_text = _codex_help_text(codex_bin)
    if help_text is None:
        return None
    return flag in help_text


def _is_codex_untrusted_repo_error(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("not inside a trusted directory" in low) and ("skip-git-repo-check" in low)


def _is_runner_runtime_blocked(*, output_text: str, stdout_text: str, stderr_text: str) -> bool:
    return _classify_runner_blocker(
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
    ) is not None


def _classify_runner_blocker(
    *,
    output_text: str,
    stdout_text: str,
    stderr_text: str,
    exit_code: Optional[int] = None,
) -> Optional[str]:
    """
    Determine whether a runner's combined output indicates a runtime blocker and return its blocker taxonomy key.

    Scans the concatenated output, stdout, and stderr for known marker phrases and maps matches to one of:
    - "blocked_user_input" — runner is awaiting user input.
    - "blocked_auth" — authentication/login is required.
    - "timeout_partial_output" or "timeout_no_output" — process timed out (exit_code == 124); chosen depending on whether any output text is present.
    - "blocked_runtime" — sandbox/permission/capacity/runtime failures were detected.

    Parameters:
        output_text (str): Final output text or last message from the runner.
        stdout_text (str): Captured standard output from the runner process.
        stderr_text (str): Captured standard error from the runner process.
        exit_code (Optional[int]): Process exit code; when equal to 124 it is treated as a timeout.

    Returns:
        Optional[str]: One of the blocker keys listed above, or `None` if no blocker markers are found.
    """
    if exit_code == 124:
        runner_text = "\n".join([output_text or "", stdout_text or ""])
        return "timeout_partial_output" if runner_text.strip() else "timeout_no_output"

    process_text = "\n".join([stdout_text or "", stderr_text or ""])
    low = process_text.lower()

    hard_runtime_markers = [
        "ran out of room in the model's context window",
        "selected model is at capacity",
        "model is at capacity",
        "you've hit your usage limit",
        "you have hit your usage limit",
        "usage limit for",
        "switch to another model",
    ]
    conditional_runtime_markers = [
        "sandbox_apply: operation not permitted",
        "host_execution_untrusted",
        "sandbox-exec",
        "operation not permitted",
        "blocked_runtime",
    ]
    model_refresh_runtime_markers = [
        "failed to refresh available models",
        "error sending request for url (http://localhost:11434",
        "stream disconnected before completion",
    ]
    weak_runtime_markers = ["try again at", "start a new thread"]
    usage_context_markers = [
        "usage limit",
        "model is at capacity",
        "selected model is at capacity",
        "context window",
    ]
    if any(marker in low for marker in hard_runtime_markers):
        return "blocked_runtime"
    if (exit_code != 0 or not (output_text or "").strip()) and any(
        marker in low for marker in model_refresh_runtime_markers
    ):
        return "blocked_runtime"
    if any(marker in low for marker in weak_runtime_markers) and any(
        marker in low for marker in usage_context_markers
    ):
        return "blocked_runtime"

    if exit_code == 0 and (output_text or "").strip():
        return None

    text = "\n".join([output_text or "", process_text])
    low = text.lower()
    tool_schema_markers = [
        "failed to parse function arguments",
        "tool exec invoked with incompatible payload",
        "unknown input item type",
        "no last agent message",
        "wrote empty content to",
    ]
    if not (output_text or "").strip() and any(marker in low for marker in tool_schema_markers):
        return "blocked_runtime"
    if any(marker in low for marker in hard_runtime_markers):
        return "blocked_runtime"
    if any(marker in low for marker in conditional_runtime_markers):
        return "blocked_runtime"
    if (exit_code != 0 or not (output_text or "").strip()) and any(
        marker in low for marker in model_refresh_runtime_markers
    ):
        return "blocked_runtime"
    if any(marker in low for marker in weak_runtime_markers) and any(
        marker in low for marker in usage_context_markers
    ):
        return "blocked_runtime"

    user_input_markers = [
        "user_input_requested_during_turn",
        "request_user_input",
        "requested user input",
        "waiting on user",
        "needs user input",
        "blocked_user_input",
    ]
    if any(marker in low for marker in user_input_markers):
        return "blocked_user_input"

    auth_markers = [
        "not logged in",
        "/login",
        "unauthenticated",
        "authentication required",
        "invalid_grant",
        "tokenrefreshfailed",
        "invalid refresh token",
        "missing authenticated codex state",
        "blocked_auth",
    ]
    if any(marker in low for marker in auth_markers):
        return "blocked_auth"

    return None


def _is_codex_reasoning_summary_unsupported(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("unsupported parameter" in low) and ("reasoning.summary" in low)


def _has_skip_git_repo_check(extra_codex_args: Optional[Sequence[str]]) -> bool:
    if not extra_codex_args:
        return False
    return any(arg.strip() == "--skip-git-repo-check" for arg in extra_codex_args if isinstance(arg, str))

__all__ = [name for name in globals() if not name.startswith("__")]
