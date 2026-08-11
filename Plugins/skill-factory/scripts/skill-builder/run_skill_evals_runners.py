from run_skill_evals_assertions import *  # noqa: F403

from dataclasses import dataclass


@dataclass(frozen=True)
class CodexExecRequest:
    workspace_root: Path
    prompt: str
    output_last_message_path: Path
    output_schema_path: Optional[Path]
    sandbox: str
    ask_for_approval: Optional[str]
    model: Optional[str]
    profile: Optional[str]
    codex_home: Optional[Path]
    jsonl_path: Optional[Path]
    codex_bin: Optional[Path]
    timeout_sec: Optional[float]
    timeout_profile: str
    extra_codex_args: Optional[List[str]] = None
    fallback_profile: Optional[str] = None


@dataclass(frozen=True)
class AltCodexExecRequest:
    workspace_root: Path
    prompt: str
    output_last_message_path: Path
    codex_bin: Optional[Path]
    output_format: str
    settings_path: Optional[Path]
    cli_command: Optional[str]
    timeout_sec: Optional[float]
    timeout_profile: str
    extra_codex_args: Optional[List[str]] = None


@dataclass(frozen=True)
class OpenAiExecRequest:
    workspace_root: Path
    prompt: str
    output_last_message_path: Path
    openai_bin: Optional[Path]
    output_format: str
    timeout_sec: Optional[float]
    timeout_profile: str
    extra_openai_args: Optional[List[str]] = None


@dataclass
class _CodexExecContext:
    request: CodexExecRequest
    env: dict[str, str]
    timeout: float
    warnings: List[str]


def _codex_exec_context(request: CodexExecRequest) -> _CodexExecContext:
    env = os.environ.copy()
    if request.codex_home:
        env["CODEX_HOME"] = str(request.codex_home)
    if request.codex_bin:
        env["PATH"] = f"{request.codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"
    timeout = _eval_timeout_seconds(
        timeout_sec=request.timeout_sec,
        timeout_profile=request.timeout_profile,
    )
    return _CodexExecContext(request=request, env=env, timeout=timeout, warnings=[])


def _validate_oss_cloud_exec(request: CodexExecRequest) -> None:
    if request.sandbox != "read-only":
        raise ValueError("oss-cloud execution requires the read-only sandbox")
    if request.ask_for_approval not in (None, "on-request"):
        raise ValueError("oss-cloud execution requires on-request approval")
    if request.model and request.model != OSS_CLOUD_MODEL:
        raise ValueError(f"oss-cloud execution requires model {OSS_CLOUD_MODEL}")
    if request.output_schema_path is not None:
        raise ValueError("oss-cloud execution does not support an output schema")
    if request.extra_codex_args:
        raise ValueError("oss-cloud execution does not accept ad hoc Codex arguments")


def _oss_cloud_exec_command(context: _CodexExecContext) -> list[str]:
    request = context.request
    _validate_oss_cloud_exec(request)
    env_file = actual_opaque_env_path()
    if env_file is None:
        raise ValueError("oss-cloud execution requires an operator-approved opaque environment stream")
    resolved_output = request.output_last_message_path.resolve()
    resolved_root = request.workspace_root.resolve()
    try:
        relative_output = resolved_output.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            "run_skill_evals: oss-cloud execution requires output_last_message_path inside the workspace root "
            f"({resolved_output} is outside {resolved_root})"
        ) from exc
    logical_command = [
        "codex", "exec", "--profile", "oss-cloud", "-c", 'approval_policy="on-request"',
        "--cd", ".", "--sandbox", "read-only", "--output-last-message",
        relative_output.as_posix(), "--json", "-",
    ]
    with configs_auth_backed_invocation(env_file) as invocation:
        return invocation.runtime_argv(configs_oss_cloud_exec_command(logical_command))


def _add_codex_profile_isolation_args(
    cmd: list[str],
    context: _CodexExecContext,
    effective_profile: Optional[str],
) -> None:
    request = context.request
    ignore_user_config_support = _codex_supports_exec_flag(request.codex_bin, "--ignore-user-config")
    if effective_profile and ignore_user_config_support is not False:
        cmd.append("--ignore-user-config")
        context.warnings.append(
            "Ignored base Codex user config while preserving the explicit --profile for noninteractive eval subprocesses."
        )
    elif effective_profile:
        context.warnings.append(
            "Codex CLI does not support --ignore-user-config; profile eval subprocess may inherit base user config."
        )
    elif ignore_user_config_support is not False:
        cmd.append("--ignore-user-config")
    else:
        context.warnings.append("Codex CLI does not support --ignore-user-config; eval runner continued without it.")
    if effective_profile:
        disable_support = _codex_supports_exec_flag(request.codex_bin, "--disable")
        if disable_support is not False:
            cmd.extend(["--disable", "apps"])
            context.warnings.append("Disabled Codex apps for noninteractive profile eval subprocesses.")
        else:
            context.warnings.append("Codex CLI does not support --disable; eval runner could not disable apps.")


def _standard_codex_exec_command(
    context: _CodexExecContext,
    effective_profile: Optional[str],
) -> list[str]:
    request = context.request
    cmd = _codex_exec_prefix(request.codex_bin)
    _add_codex_profile_isolation_args(cmd, context, effective_profile)
    cmd.extend(["--sandbox", request.sandbox])
    if request.ask_for_approval and _codex_supports_exec_flag(request.codex_bin, "--ask-for-approval") is not False:
        cmd.extend(["--ask-for-approval", request.ask_for_approval])
    cmd.extend(["--output-last-message", str(request.output_last_message_path)])
    if request.extra_codex_args:
        cmd.extend(request.extra_codex_args)
    if effective_profile:
        cmd.extend(["--profile", effective_profile])
    if request.model:
        cmd.extend(["--model", request.model])
    if request.output_schema_path:
        cmd.extend(["--output-schema", str(request.output_schema_path)])
    if request.jsonl_path:
        cmd.append("--json")
    cmd.append("-")
    return cmd


def _write_codex_jsonl(path: Optional[Path], stdout: str) -> None:
    if path and stdout:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(stdout, encoding="utf-8")
        except OSError:
            pass


def _codex_timeout_result(context: _CodexExecContext, exc: sp.TimeoutExpired) -> Tuple[int, str, str]:
    stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
    stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
    _write_codex_jsonl(context.request.jsonl_path, stdout)
    timeout_message = f"codex exec timed out after {context.timeout} seconds."
    return 124, stdout, f"{stderr.rstrip()}\n{timeout_message}".strip()


def _invoke_codex_exec(
    context: _CodexExecContext,
    effective_profile: Optional[str],
) -> Tuple[int, str, str]:
    request = context.request
    try:
        cmd = _oss_cloud_exec_command(context) if effective_profile == "oss-cloud" else _standard_codex_exec_command(context, effective_profile)
        proc = sp.run(
            cmd, input=request.prompt, text=True, capture_output=True, env=context.env,
            cwd=request.workspace_root, timeout=context.timeout, start_new_session=True,
        )
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except (OSError, ValueError) as exc:
        return 2, "", str(exc)
    except sp.TimeoutExpired as exc:
        return _codex_timeout_result(context, exc)
    _write_codex_jsonl(request.jsonl_path, proc.stdout)
    return proc.returncode, proc.stdout, proc.stderr


def _has_last_message_artifact(path: Path) -> bool:
    """Check whether a last-message artifact exists and contains non-empty content."""
    try:
        content = path.read_text(encoding="utf-8").strip()
        return bool(content)
    except OSError:
        return False


def _retry_empty_timeout(
    context: _CodexExecContext,
    profile: Optional[str],
    result: Tuple[int, str, str],
) -> Tuple[int, str, str]:
    rc, stdout, stderr = result
    request = context.request
    if rc != 124 or stdout.strip() or _has_last_message_artifact(request.output_last_message_path):
        return result
    if not stderr.startswith("codex exec timed out after "):
        return result
    context.warnings.append("Codex timed out without output; retrying once with a fresh exec process.")
    if request.output_last_message_path.exists():
        try:
            if not request.output_last_message_path.read_text(encoding="utf-8").strip():
                request.output_last_message_path.unlink()
        except OSError as exc:
            context.warnings.append(f"Could not read {request.output_last_message_path} before retry: {exc}")
            try:
                request.output_last_message_path.unlink(missing_ok=True)
            except OSError as unlink_exc:
                context.warnings.append(f"Could not remove {request.output_last_message_path}: {unlink_exc}")
    if request.jsonl_path and request.jsonl_path.exists():
        try:
            request.jsonl_path.unlink()
        except OSError as exc:
            context.warnings.append(f"Could not remove {request.jsonl_path}: {exc}")
    return _invoke_codex_exec(context, profile)


def _apply_codex_fallback(
    context: _CodexExecContext,
    profile: Optional[str],
    result: Tuple[int, str, str],
) -> Tuple[int, str, str]:
    rc, stdout, stderr = result
    fallback_profile = context.request.fallback_profile
    if rc == 0 or not fallback_profile or fallback_profile == profile:
        return result
    if not _is_codex_reasoning_summary_unsupported(f"{stderr}\n{stdout}"):
        return result
    if profile == "oss-cloud":
        context.warnings.append(
            "Codex rejected reasoning.summary for oss-cloud; skipped cross-profile fallback "
            "to preserve the authenticated Configs transport and requested provider identity."
        )
        return result
    context.warnings.append(
        "Codex rejected reasoning.summary for the active profile/model; "
        f"retrying with fallback profile `{fallback_profile}`."
    )
    return _invoke_codex_exec(context, fallback_profile)


def _run_codex_exec(request: CodexExecRequest) -> Tuple[int, str, str, List[str]]:
    """
    Run the Codex CLI `exec` command with the provided prompt and capture outputs and warnings.

    Parameters:
        workspace_root (Path): Working directory for the Codex subprocess.
        prompt (str): Prompt text supplied to Codex via stdin.
        output_last_message_path (Path): File path where the CLI's "last message" output will be written.
        output_schema_path (Optional[Path]): Path to an output schema file to pass via `--output-schema` (if any).
        sandbox (str): Sandbox name to pass via `--sandbox`.
        ask_for_approval (Optional[str]): Legacy value for `--ask-for-approval` when supported by the Codex CLI.
        model (Optional[str]): Model name to pass via `--model`.
        profile (Optional[str]): Active Codex profile name to pass via `--profile`.
        codex_home (Optional[Path]): Directory to set as `CODEX_HOME` in the subprocess environment.
        jsonl_path (Optional[Path]): When provided, the raw CLI stdout is written to this path as JSONL.
        codex_bin (Optional[Path]): Path to a Codex binary; its parent directory is prepended to `PATH`.
        timeout_sec (Optional[float]): Explicit timeout in seconds for the subprocess; if omitted, resolved from profile/env.
        timeout_profile (str): Timeout profile name used when `timeout_sec` is not provided.
        extra_codex_args (Optional[List[str]]): Additional CLI arguments appended to the command.
        fallback_profile (Optional[str]): If the first run fails due to unsupported reasoning.summary, retry with this profile.

    Returns:
        Tuple[int, str, str, List[str]]: A tuple of `(exit_code, stdout, stderr, warnings)`. `exit_code` may be
        127 when the Codex CLI is not found and 124 on timeout. `stdout` and `stderr` are the subprocess outputs;
        `warnings` contains non-fatal diagnostics (e.g., unsupported flags, automatic fallback retries).
    """
    context = _codex_exec_context(request)
    result = _invoke_codex_exec(context, request.profile)
    result = _retry_empty_timeout(context, request.profile, result)
    result = _apply_codex_fallback(context, request.profile, result)
    return *result, context.warnings


def run_codex_exec(
    request: CodexExecRequest | None = None,
    *,
    workspace_root: Path | None = None,
    prompt: str | None = None,
    output_last_message_path: Path | None = None,
    output_schema_path: Path | None = None,
    sandbox: str | None = None,
    ask_for_approval: str | None = None,
    model: str | None = None,
    profile: str | None = None,
    codex_home: Path | None = None,
    jsonl_path: Path | None = None,
    codex_bin: Path | None = None,
    timeout_sec: float | None = None,
    timeout_profile: str | None = None,
    extra_codex_args: list[str] | None = None,
    fallback_profile: str | None = None,
) -> Tuple[int, str, str, List[str]]:
    """
    Run Codex from a typed request; accept legacy keyword arguments during migration.

    DEPRECATION: The legacy keyword argument interface is deprecated and will be removed
    in a future version. Use CodexExecRequest dataclass instead.
    """
    if request is not None and any([
        workspace_root, prompt, output_last_message_path, output_schema_path, sandbox,
        ask_for_approval, model, profile, codex_home, jsonl_path, codex_bin,
        timeout_sec is not None, timeout_profile, extra_codex_args, fallback_profile,
    ]):
        raise TypeError("pass either CodexExecRequest or legacy keyword arguments, not both")
    if request is None:
        if workspace_root is None or prompt is None or output_last_message_path is None or sandbox is None or timeout_profile is None:
            raise TypeError("legacy keyword arguments require workspace_root, prompt, output_last_message_path, sandbox, and timeout_profile")
        resolved = CodexExecRequest(
            workspace_root=workspace_root,
            prompt=prompt,
            output_last_message_path=output_last_message_path,
            output_schema_path=output_schema_path,
            sandbox=sandbox,
            ask_for_approval=ask_for_approval,
            model=model,
            profile=profile,
            codex_home=codex_home,
            jsonl_path=jsonl_path,
            codex_bin=codex_bin,
            timeout_sec=timeout_sec,
            timeout_profile=timeout_profile,
            extra_codex_args=extra_codex_args,
            fallback_profile=fallback_profile,
        )
    else:
        resolved = request
    return _run_codex_exec(resolved)


def _alt_codex_command(request: AltCodexExecRequest) -> tuple[list[str], bool, str]:
    command_name = (request.cli_command or "").strip() or "codex"
    use_shell_function = command_name != "codex"
    base_args = [command_name, "-p"]
    if request.settings_path:
        base_args.extend(["--settings", str(request.settings_path)])
    base_args.extend(["--output-format", request.output_format])
    if request.extra_codex_args:
        base_args.extend(request.extra_codex_args)
    if use_shell_function:
        return ["zsh", "-ic", " ".join(shlex.quote(arg) for arg in base_args)], True, command_name
    if request.codex_bin:
        return [str(request.codex_bin), *base_args[1:]], False, command_name
    return base_args, False, command_name


def _run_alt_codex_process(
    request: AltCodexExecRequest,
    cmd: list[str],
    *,
    use_shell_function: bool,
    command_name: str,
) -> Tuple[int, str, str]:
    timeout = _eval_timeout_seconds(
        timeout_sec=request.timeout_sec,
        timeout_profile=request.timeout_profile,
    )
    try:
        proc = sp.run(
            cmd, input=request.prompt, text=True, capture_output=True,
            cwd=request.workspace_root, timeout=timeout, start_new_session=True,
        )
    except FileNotFoundError:
        message = (
            f"{command_name} is not available in interactive zsh. Check your shell setup."
            if use_shell_function
            else "codex CLI not found on PATH. Install Codex CLI and ensure it is on PATH."
        )
        return 127, "", message
    except sp.TimeoutExpired:
        return 124, "", f"codex headless timed out after {timeout} seconds."
    stdout, stderr = proc.stdout or "", proc.stderr or ""
    try:
        request.output_last_message_path.parent.mkdir(parents=True, exist_ok=True)
        request.output_last_message_path.write_text(stdout, encoding="utf-8")
    except OSError as exc:
        stderr = f"{stderr}\nWarning: Could not write output to {request.output_last_message_path}: {exc}".strip()
    return proc.returncode, stdout, stderr


def _alt_codex_authentication_hint(returncode: int, stdout: str, stderr: str) -> str:
    if returncode == 0 or ("not logged in" not in stdout.lower() and "/login" not in stdout.lower()):
        return stderr
    hint = (
        "Codex CLI appears to be unauthenticated.\nFix:\n"
        "  1) Run `codex` interactively and execute `/login`, then re-run evals.\n"
        "  2) Or run `codex setup-token` if you use token-based auth.\n"
        "Note: if you maintain multiple Codex setups/profiles, ensure the intended one is active.\n"
    )
    return (hint + "\n" + stderr).strip() + "\n"


def _run_alt_codex_exec(request: AltCodexExecRequest) -> Tuple[int, str, str]:
    cmd, use_shell_function, command_name = _alt_codex_command(request)
    returncode, stdout, stderr = _run_alt_codex_process(
        request, cmd, use_shell_function=use_shell_function, command_name=command_name,
    )
    return returncode, stdout, _alt_codex_authentication_hint(returncode, stdout, stderr)


def run_alt_codex_exec(
    request: AltCodexExecRequest | None = None,
    *,
    workspace_root: Path | None = None,
    prompt: str | None = None,
    output_last_message_path: Path | None = None,
    codex_bin: Path | None = None,
    output_format: str | None = None,
    settings_path: Path | None = None,
    cli_command: str | None = None,
    timeout_sec: float | None = None,
    timeout_profile: str | None = None,
    extra_codex_args: list[str] | None = None,
) -> Tuple[int, str, str]:
    """
    Run the alternate Codex transport from a typed request or legacy keywords.

    DEPRECATION: The legacy keyword argument interface is deprecated and will be removed
    in a future version. Use AltCodexExecRequest dataclass instead.
    """
    if request is not None and any([
        workspace_root, prompt, output_last_message_path, codex_bin, output_format,
        settings_path, cli_command, timeout_sec is not None, timeout_profile, extra_codex_args,
    ]):
        raise TypeError("pass either AltCodexExecRequest or legacy keyword arguments, not both")
    if request is None:
        if workspace_root is None or prompt is None or output_last_message_path is None or output_format is None or timeout_profile is None:
            raise TypeError("legacy keyword arguments require workspace_root, prompt, output_last_message_path, output_format, and timeout_profile")
        resolved = AltCodexExecRequest(
            workspace_root=workspace_root,
            prompt=prompt,
            output_last_message_path=output_last_message_path,
            codex_bin=codex_bin,
            output_format=output_format,
            settings_path=settings_path,
            cli_command=cli_command,
            timeout_sec=timeout_sec,
            timeout_profile=timeout_profile,
            extra_codex_args=extra_codex_args,
        )
    else:
        resolved = request
    return _run_alt_codex_exec(resolved)


def _run_openai_exec(request: OpenAiExecRequest) -> Tuple[int, str, str]:
    workspace_root = request.workspace_root
    prompt = request.prompt
    output_last_message_path = request.output_last_message_path
    openai_bin = request.openai_bin
    output_format = request.output_format
    timeout_sec = request.timeout_sec
    timeout_profile = request.timeout_profile
    extra_openai_args = request.extra_openai_args
    if openai_bin:
        cmd = [str(openai_bin)]
    else:
        cmd = ["openai"]

    cmd.extend(["--prompt", prompt, "--output-format", output_format])
    if extra_openai_args:
        cmd.extend(extra_openai_args)

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "openai CLI not found on PATH. Install OpenAI CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"openai headless timed out after {timeout} seconds."

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    try:
        output_last_message_path.parent.mkdir(parents=True, exist_ok=True)
        output_last_message_path.write_text(stdout, encoding="utf-8")
    except OSError as exc:
        stderr = f"{stderr}\nWarning: Could not write output to {output_last_message_path}: {exc}".strip()
    return proc.returncode, stdout, stderr


def run_openai_exec(
    request: OpenAiExecRequest | None = None,
    *,
    workspace_root: Path | None = None,
    prompt: str | None = None,
    output_last_message_path: Path | None = None,
    openai_bin: Path | None = None,
    output_format: str | None = None,
    timeout_sec: float | None = None,
    timeout_profile: str | None = None,
    extra_openai_args: list[str] | None = None,
) -> Tuple[int, str, str]:
    """
    Run the OpenAI transport from a typed request or legacy keywords.

    DEPRECATION: The legacy keyword argument interface is deprecated and will be removed
    in a future version. Use OpenAiExecRequest dataclass instead.
    """
    if request is not None and any([
        workspace_root, prompt, output_last_message_path, openai_bin, output_format,
        timeout_sec is not None, timeout_profile, extra_openai_args,
    ]):
        raise TypeError("pass either OpenAiExecRequest or legacy keyword arguments, not both")
    if request is None:
        if workspace_root is None or prompt is None or output_last_message_path is None or output_format is None or timeout_profile is None:
            raise TypeError("legacy keyword arguments require workspace_root, prompt, output_last_message_path, output_format, and timeout_profile")
        resolved = OpenAiExecRequest(
            workspace_root=workspace_root,
            prompt=prompt,
            output_last_message_path=output_last_message_path,
            openai_bin=openai_bin,
            output_format=output_format,
            timeout_sec=timeout_sec,
            timeout_profile=timeout_profile,
            extra_openai_args=extra_openai_args,
        )
    else:
        resolved = request
    return _run_openai_exec(resolved)


def _eval_timeout_seconds(
    *,
    timeout_sec: Optional[float],
    timeout_profile: str,
) -> float:
    if timeout_sec is not None:
        return float(timeout_sec)

    raw = os.environ.get("SKILL_EVAL_TIMEOUT_SEC")
    if raw is None:
        raw = os.environ.get("CODEX_EVAL_TIMEOUT_SEC")
    if raw is not None and str(raw).strip():
        return float(raw)

    if timeout_profile == "codex-heavy":
        return 180.0
    if timeout_profile == "discovery-heavy":
        return 300.0
    return 60.0


def _resolve_case_timeout(
    case: EvalCase,
    *,
    cli_timeout_sec: Optional[float],
    cli_timeout_profile: str,
) -> Tuple[Optional[float], str]:
    if cli_timeout_sec is not None:
        return float(cli_timeout_sec), cli_timeout_profile

    resolved_timeout_sec = case.timeout_sec if case.timeout_sec is not None else None
    resolved_timeout_profile = cli_timeout_profile

    if case.timeout_profile and cli_timeout_profile == "default":
        resolved_timeout_profile = case.timeout_profile

    return resolved_timeout_sec, resolved_timeout_profile


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def _rewrite_dash_prefixed_codex_args(argv: Sequence[str]) -> List[str]:
    """
    Allow ergonomic `--*-arg --flag` usage by rewriting it to
    `--*-arg=--flag` before argparse runs.

    We only rewrite when the next token is not a known script option.
    """
    out: List[str] = []
    i = 0
    n = len(argv)
    rewritable = {"--codex-arg", "--openai-arg"}
    while i < n:
        tok = argv[i]
        if tok in rewritable and i + 1 < n:
            nxt = argv[i + 1]
            if nxt.startswith("-") and nxt not in _SCRIPT_OPTIONS:
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out


def _parse_runners(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)

    if not expanded:
        raise ValueError("--runners provided but no runner names were parsed.")

    invalid = [x for x in expanded if x not in _RUNNER_CHOICES]
    if invalid:
        raise ValueError(
            f"Invalid runner(s): {', '.join(invalid)}. Allowed: {', '.join(_RUNNER_CHOICES)}."
        )
    return expanded


def _parse_csv_args(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)
    return expanded


def _build_next_reproduce_command(
    args: argparse.Namespace,
    *,
    selected_runners: Sequence[str],
    capture_jsonl: bool,
) -> str:
    parts = [
        "python3",
        "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py",
        args.path,
        "--eval-mode",
        args.eval_mode,
    ]
    if args.runners:
        for raw_runners in args.runners:
            parts.extend(["--runners", raw_runners])
    elif args.dual_run:
        parts.append("--dual-run")
    elif args.smoke:
        parts.append("--smoke")
    else:
        parts.extend(["--runner", ",".join(selected_runners)])
    for case_filter in args.case:
        parts.extend(["--case", case_filter])
    for category_filter in args.category:
        parts.extend(["--category", category_filter])
    if args.timeout_sec is not None:
        parts.extend(["--timeout-sec", str(args.timeout_sec)])
    if args.timeout_profile != "default":
        parts.extend(["--timeout-profile", args.timeout_profile])
    if capture_jsonl:
        parts.append("--capture-jsonl")
    if args.model:
        parts.extend(["--model", args.model])
    if args.profile:
        parts.extend(["--profile", args.profile])
    return " ".join(shlex.quote(part) for part in parts)

__all__ = [name for name in globals() if not name.startswith("__")]
