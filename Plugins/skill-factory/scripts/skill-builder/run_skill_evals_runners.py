from run_skill_evals_assertions import *  # noqa: F403

def run_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    output_schema_path: Optional[Path],
    sandbox: str,
    ask_for_approval: Optional[str],
    model: Optional[str],
    profile: Optional[str],
    codex_home: Optional[Path],
    jsonl_path: Optional[Path],
    codex_bin: Optional[Path],
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
    fallback_profile: Optional[str] = None,
) -> Tuple[int, str, str, List[str]]:
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
    warnings: List[str] = []
    env = os.environ.copy()
    if codex_home:
        env["CODEX_HOME"] = str(codex_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    def _invoke(effective_profile: Optional[str]) -> Tuple[int, str, str]:
        if effective_profile == "oss-cloud":
            try:
                if sandbox != "read-only":
                    raise ValueError("oss-cloud execution requires the read-only sandbox")
                if ask_for_approval not in (None, "on-request"):
                    raise ValueError("oss-cloud execution requires on-request approval")
                if model and model != OSS_CLOUD_MODEL:
                    raise ValueError(f"oss-cloud execution requires model {OSS_CLOUD_MODEL}")
                if output_schema_path is not None:
                    raise ValueError("oss-cloud execution does not support an output schema")
                if extra_codex_args:
                    raise ValueError("oss-cloud execution does not accept ad hoc Codex arguments")
                env_file = actual_opaque_env_path()
                if env_file is None:
                    raise ValueError("oss-cloud execution requires an operator-approved opaque environment stream")
                relative_output = output_last_message_path.resolve().relative_to(workspace_root.resolve())
                logical_command = [
                    "codex",
                    "exec",
                    "--profile",
                    "oss-cloud",
                    "-c",
                    'approval_policy="on-request"',
                    "--cd",
                    ".",
                    "--sandbox",
                    "read-only",
                    "--output-last-message",
                    relative_output.as_posix(),
                    "--json",
                    "-",
                ]
                with configs_auth_backed_invocation(env_file) as invocation:
                    cmd = invocation.runtime_argv(configs_oss_cloud_exec_command(logical_command))
            except (OSError, ValueError) as exc:
                return 2, "", str(exc)
        else:
            cmd = _codex_exec_prefix(codex_bin)
        # Eval cases pass prompt/context explicitly. When a named runtime lane
        # profile is requested, keep profile config available while still using
        # the isolated CODEX_HOME copied below.
        if effective_profile != "oss-cloud":
            ignore_user_config_support = _codex_supports_exec_flag(codex_bin, "--ignore-user-config")
            if effective_profile:
                if ignore_user_config_support is not False:
                    cmd.append("--ignore-user-config")
                    warnings.append(
                        "Ignored base Codex user config while preserving the explicit --profile for noninteractive eval subprocesses."
                    )
                else:
                    warnings.append(
                        "Codex CLI does not support --ignore-user-config; profile eval subprocess may inherit base user config."
                    )
                disable_support = _codex_supports_exec_flag(codex_bin, "--disable")
                if disable_support is not False:
                    cmd.extend(["--disable", "apps"])
                    warnings.append("Disabled Codex apps for noninteractive profile eval subprocesses.")
                else:
                    warnings.append("Codex CLI does not support --disable; eval runner could not disable apps.")
            elif ignore_user_config_support is not False:
                cmd.append("--ignore-user-config")
            else:
                warnings.append("Codex CLI does not support --ignore-user-config; eval runner continued without it.")
            cmd.extend(["--sandbox", sandbox])

            if ask_for_approval:
                supports = _codex_supports_exec_flag(codex_bin, "--ask-for-approval")
                if supports is not False:
                    cmd.extend(["--ask-for-approval", ask_for_approval])

            cmd.extend([
                "--output-last-message",
                str(output_last_message_path),
            ])

            if extra_codex_args:
                cmd.extend(extra_codex_args)

            if effective_profile:
                cmd.extend(["--profile", effective_profile])
            if model:
                cmd.extend(["--model", model])
            if output_schema_path:
                cmd.extend(["--output-schema", str(output_schema_path)])

            if jsonl_path:
                cmd.append("--json")

            cmd.append("-")

        try:
            proc = sp.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                env=env,
                cwd=workspace_root,
                timeout=timeout,
                start_new_session=True,
            )
        except FileNotFoundError:
            return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
        except sp.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            if jsonl_path and stdout:
                jsonl_path.parent.mkdir(parents=True, exist_ok=True)
                jsonl_path.write_text(stdout, encoding="utf-8")
            timeout_message = f"codex exec timed out after {timeout} seconds."
            stderr = f"{stderr.rstrip()}\n{timeout_message}".strip()
            return 124, stdout, stderr

        if jsonl_path:
            jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            jsonl_path.write_text(proc.stdout, encoding="utf-8")

        return proc.returncode, proc.stdout, proc.stderr

    rc, stdout, stderr = _invoke(profile)

    has_last_message_artifact = output_last_message_path.exists() and output_last_message_path.read_text(encoding="utf-8").strip()
    if rc == 124 and not stdout.strip() and not has_last_message_artifact and stderr.startswith("codex exec timed out after "):
        warnings.append("Codex timed out without output; retrying once with a fresh exec process.")
        # Only delete output_last_message_path if no usable artifact exists
        if output_last_message_path.exists():
            try:
                content = output_last_message_path.read_text(encoding="utf-8").strip()
                if not content:
                    output_last_message_path.unlink()
            except OSError as exc:
                warnings.append(f"Could not read {output_last_message_path} before retry: {exc}")
                output_last_message_path.unlink(missing_ok=True)
        if jsonl_path and jsonl_path.exists():
            jsonl_path.unlink()
        rc, stdout, stderr = _invoke(profile)

    if (
        rc != 0
        and fallback_profile
        and fallback_profile != profile
        and _is_codex_reasoning_summary_unsupported(f"{stderr}\n{stdout}")
    ):
        if profile == "oss-cloud":
            warnings.append(
                "Codex rejected reasoning.summary for oss-cloud; skipped cross-profile fallback "
                "to preserve the authenticated Configs transport and requested provider identity."
            )
        else:
            warnings.append(
                "Codex rejected reasoning.summary for the active profile/model; "
                f"retrying with fallback profile `{fallback_profile}`."
            )
            rc, stdout, stderr = _invoke(fallback_profile)

    return rc, stdout, stderr, warnings


def run_alt_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    codex_bin: Optional[Path],
    output_format: str,
    settings_path: Optional[Path],
    cli_command: Optional[str],
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    command_name = (cli_command or "").strip() or "codex"
    use_shell_function = command_name != "codex"

    base_args: List[str] = [command_name, "-p"]
    if settings_path:
        base_args.extend(["--settings", str(settings_path)])
    base_args.extend(["--output-format", output_format])
    if extra_codex_args:
        base_args.extend(extra_codex_args)

    if use_shell_function:
        command_str = " ".join(shlex.quote(x) for x in base_args)
        cmd = ["zsh", "-ic", command_str]
    else:
        if codex_bin:
            cmd = [str(codex_bin), *base_args[1:]]
        else:
            cmd = base_args

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
            start_new_session=True,
        )
    except FileNotFoundError:
        if use_shell_function:
            return 127, "", f"{command_name} is not available in interactive zsh. Check your shell setup."
        return 127, "", "codex CLI not found on PATH. Install Codex CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"codex headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr = proc.stderr or ""
    stdout = proc.stdout or ""

    if proc.returncode != 0 and ("not logged in" in stdout.lower() or "/login" in stdout.lower()):
        hint = (
            "Codex CLI appears to be unauthenticated.\n"
            "Fix:\n"
            "  1) Run `codex` interactively and execute `/login`, then re-run evals.\n"
            "  2) Or run `codex setup-token` if you use token-based auth.\n"
            "Note: if you maintain multiple Codex setups/profiles, ensure the intended one is active.\n"
        )
        stderr = (hint + "\n" + stderr).strip() + "\n"

    return proc.returncode, stdout, stderr


def run_openai_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    openai_bin: Optional[Path],
    output_format: str,
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_openai_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
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

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


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
