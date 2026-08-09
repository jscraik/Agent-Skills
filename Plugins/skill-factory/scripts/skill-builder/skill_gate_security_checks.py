from skill_gate_core import *  # noqa: F403

def _load_expected_pi_context(
    skill_dir: Path,
) -> Tuple[List[str], List[str], List[str], List[Finding]]:
    findings: List[Finding] = []
    cfg_path = skill_dir / "references" / "prompt-injection-expected-context.json"
    if not cfg_path.exists():
        return (
            list(_DEFAULT_PI_EXPECTED_PATH_PATTERNS),
            list(_DEFAULT_PI_CONTEXT_SIGNALS),
            list(_DEFAULT_PI_SKIP_BINARY_GLOBS),
            findings,
        )

    try:
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("expected object")
        raw_paths = raw.get("path_patterns", _DEFAULT_PI_EXPECTED_PATH_PATTERNS)
        raw_signals = raw.get("context_signals", _DEFAULT_PI_CONTEXT_SIGNALS)
        raw_binary = raw.get("skip_binary_globs", _DEFAULT_PI_SKIP_BINARY_GLOBS)

        if not isinstance(raw_paths, list) or not all(isinstance(x, str) and x.strip() for x in raw_paths):
            raise ValueError("path_patterns must be a non-empty string list")
        if not isinstance(raw_signals, list) or not all(isinstance(x, str) and x.strip() for x in raw_signals):
            raise ValueError("context_signals must be a non-empty string list")
        if not isinstance(raw_binary, list) or not all(isinstance(x, str) and x.strip() for x in raw_binary):
            raise ValueError("skip_binary_globs must be a non-empty string list")

        return list(raw_paths), list(raw_signals), list(raw_binary), findings
    except Exception as exc:
        findings.append(
            Finding(
                Level.WARN,
                "PI_EXPECTED_CONTEXT_CONFIG",
                f"Failed to load expected PI context config; using defaults ({exc}).",
                evidence=str(cfg_path.relative_to(skill_dir)),
            )
        )
        return (
            list(_DEFAULT_PI_EXPECTED_PATH_PATTERNS),
            list(_DEFAULT_PI_CONTEXT_SIGNALS),
            list(_DEFAULT_PI_SKIP_BINARY_GLOBS),
            findings,
        )


def _is_expected_pi_context(
    code: str,
    rel_path: str,
    text: str,
    path_patterns: Sequence[str],
    context_signals: Sequence[str],
) -> bool:
    rel = rel_path.replace("\\", "/")
    if any(fnmatch.fnmatch(rel, pat) for pat in path_patterns):
        return True

    # Content-signal bypass removed: generic terms like "pattern" or "regex"
    # are easily planted to suppress PI_* findings in arbitrary files.
    # Expected PI context is now path-scoped only.
    _ = (code, text, context_signals)
    return False


def check_codex_frontmatter(doc: SkillDoc, *, min_desc_len: int) -> List[Finding]:
    fm = doc.frontmatter
    out: List[Finding] = []

    name = fm.get("name")
    desc = fm.get("description")
    metadata = fm.get("metadata")

    if not isinstance(name, str) or not name.strip():
        out.append(Finding(Level.FAIL, "FM_NAME_MISSING", "Missing/invalid `name` (required)."))
    else:
        if "\n" in name or "\r" in name:
            out.append(Finding(Level.FAIL, "FM_NAME_MULTILINE", "`name` must be single-line."))
        if "<" in name or ">" in name:
            out.append(Finding(Level.FAIL, "FM_NAME_XML_TAGS", "`name` must not include `<` or `>` characters."))
        if len(name) > 100:
            out.append(Finding(Level.FAIL, "FM_NAME_TOO_LONG", f"`name` too long ({len(name)} > 100)."))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip()):
            out.append(Finding(Level.WARN, "FM_NAME_STYLE", "Consider kebab-case name (lowercase + hyphens)."))

    if metadata is not None:
        if not isinstance(metadata, dict):
            out.append(Finding(Level.WARN, "FM_METADATA_NOT_MAPPING", "`metadata` should be a YAML mapping when present."))
        elif not metadata.get("version"):
            out.append(Finding(Level.WARN, "FM_METADATA_VERSION_MISSING", "`metadata.version` is recommended for local Tessl review compatibility."))

    if not isinstance(desc, str) or not desc.strip():
        out.append(Finding(Level.FAIL, "FM_DESC_MISSING", "Missing/invalid `description` (required)."))
        return out

    if "\n" in desc or "\r" in desc:
        out.append(Finding(Level.FAIL, "FM_DESC_MULTILINE", "`description` must be single-line."))
    if "<" in desc or ">" in desc:
        out.append(Finding(Level.FAIL, "FM_DESC_XML_TAGS", "`description` must not include `<` or `>` characters."))
    if len(desc) > 500:
        out.append(Finding(Level.FAIL, "FM_DESC_TOO_LONG", f"`description` too long ({len(desc)} > 500)."))
    if len(desc.strip()) < min_desc_len:
        out.append(Finding(Level.WARN, "FM_DESC_SHORT", f"Description is brief (< {min_desc_len}); expand for better discovery."))

    has_when = _has_any(desc, ["when ", "if ", "whenever ", "use this skill", "use this when", "trigger"])
    has_what = _has_any(desc, [
        "draft", "generate", "analyze", "extract", "validate", "convert", "build",
        "create", "summarize", "review", "audit", "lint", "plan", "scaffold",
        # Common action verbs that are valid "what" signals for skills in this repo.
        "deploy", "debug", "diagnose", "troubleshoot", "automate", "control",
        "install", "download", "render",
    ])
    if not (has_when and has_what):
        out.append(Finding(
            Level.FAIL,
            "FM_DESC_WHAT_WHEN",
            "Description MUST include WHAT the skill does and WHEN to use it (trigger contexts).",
            evidence=f"description: {desc.strip()}",
        ))

    # Heuristic: avoid putting step-by-step workflow text in `description`.
    # The description is primarily for discovery/selection; workflows belong in the body/references.
    workflowy_terms = [
        "step", "steps", "first", "second", "third", "then", "next", "after", "before",
        "finally", "workflow", "procedure", "checklist",
    ]
    hits = [t for t in workflowy_terms if t in desc]
    if len(hits) >= 2 or re.search(r"\b(1\)|2\)|3\)|first|second|third|then|next|finally)\b", desc):
        out.append(Finding(
            Level.WARN,
            "FM_DESC_WORKFLOWY",
            "Description looks workflow-like. Prefer outcome + trigger keywords in `description`; keep procedures in the body/references.",
            evidence=f"description: {desc.strip()}",
        ))


    return out


def check_progressive_disclosure(doc: SkillDoc, *, max_lines: int, max_codeblock_lines: int) -> List[Finding]:
    out: List[Finding] = []

    total_lines = _count_lines(doc.raw)
    if total_lines > max_lines:
        out.append(Finding(
            Level.FAIL,
            "PD_SKILLMD_TOO_LONG",
            f"SKILL.md exceeds line budget ({total_lines} > {max_lines}). Move bulk content to references/ and scripts/.",
        ))

    blocks = _code_fence_blocks(doc.body)
    for i, b in enumerate(blocks, 1):
        blines = _count_lines(b)
        if blines > max_codeblock_lines:
            out.append(Finding(
                Level.WARN,
                "PD_LARGE_CODEBLOCK",
                f"Large code block detected ({blines} lines). Prefer scripts/ and reference them from SKILL.md.",
                evidence=f"codeblock #{i}: {blines} lines",
            ))

    return out


def check_required_sections(doc: SkillDoc, *, require_philosophy: bool) -> List[Finding]:
    out: List[Finding] = []
    h2s = _h2_titles(doc.body)

    required: Dict[str, List[str]] = {
        "when_to_use": ["when to use", "usage", "triggers", "invocation"],
        "inputs": ["inputs", "preconditions", "assumptions", "requirements"],
        "outputs": ["outputs", "output format", "deliverables", "result"],
        "workflow": ["workflow", "procedure", "steps", "process"],
        "failure_mode": [
            "failure mode",
            "failure modes",
            "failure handling",
            "failure behavior",
            "repair behavior",
            "repair loop",
            "stopping conditions",
            "rollback path",
            "handoff rules",
        ],
        "validation": ["validation", "checks", "verify", "acceptance", "gates"],
        "references": ["references", "progressive disclosure"],
    }

    def present(aliases: Sequence[str]) -> bool:
        return any(any(a.lower() in t for a in aliases) for t in h2s)

    for key, aliases in required.items():
        if not present(aliases):
            out.append(Finding(
                Level.WARN,
                f"SEC_{key.upper()}_MISSING",
                (
                    f"Missing canonical Skills SDK section: {key.replace('_', ' ')}. "
                    "Use the required KISS header set: When To Use, Inputs, Outputs, "
                    "Workflow, Failure Mode, Validation, References."
                ),
            ))

    critical_content: Dict[str, List[str]] = {
        "failure_mode": required["failure_mode"],
        "validation": required["validation"],
    }
    placeholder_pattern = re.compile(r"^(?:n/?a|none|tbd|todo|coming soon|placeholder)\.?\s*$", re.IGNORECASE)
    for key, aliases in critical_content.items():
        text = _find_section_text(doc.body, aliases).strip()
        if not text:
            # The missing-section finding above is already clearer when the heading is absent.
            if present(aliases):
                out.append(Finding(
                    Level.WARN,
                    f"SEC_{key.upper()}_EMPTY",
                    f"House-style section has no content: {key.replace('_', ' ')}.",
                ))
            continue
        if len(text) < 20 or placeholder_pattern.fullmatch(text):
            out.append(Finding(
                Level.WARN,
                f"SEC_{key.upper()}_THIN",
                f"Canonical section is too thin to be operational: {key.replace('_', ' ')}.",
            ))

    return out


def check_workflow_fail_fast(doc: SkillDoc, *, require_fail_fast: bool) -> List[Finding]:
    out: List[Finding] = []

    validation_text = _find_section_text(doc.body, ["validation", "checks", "verify", "gates", "acceptance"])
    if not validation_text:
        if require_fail_fast:
            out.append(Finding(
                Level.FAIL,
                "WF_FAIL_FAST_REQUIRED",
                "Validation section MUST specify fail-fast behavior (stop at first failed gate; do not proceed).",
            ))
        return out

    signals = ["fail fast", "do not proceed", "stop", "abort", "on failure", "if fails", "must stop", "exit early"]
    has = _has_any(validation_text, signals)

    if require_fail_fast and not has:
        out.append(Finding(
            Level.FAIL,
            "WF_FAIL_FAST_REQUIRED",
            "Validation section MUST specify fail-fast behavior (stop at first failed gate; do not proceed).",
        ))
    elif not has:
        out.append(Finding(
            Level.WARN,
            "WF_FAIL_FAST_MISSING",
            "Validation section should specify fail-fast behavior (stop at first failed gate).",
        ))

    return out


def check_redaction_language(doc: SkillDoc, *, require_redaction: bool) -> List[Finding]:
    out: List[Finding] = []

    constraints_text = _find_section_text(doc.body, ["constraints", "safety"])
    corpus = constraints_text if constraints_text else doc.body

    redaction_signals = [
        "redact", "redaction", "secrets", "tokens", "api key", "credentials",
        "pii", "personal data", "sensitive",
    ]
    has = _has_any(corpus, redaction_signals)

    if require_redaction and not has:
        out.append(Finding(
            Level.FAIL,
            "SAFE_REDACTION_REQUIRED",
            "Constraints/Safety MUST mention redaction of secrets/sensitive data by default.",
        ))
    elif not has:
        out.append(Finding(
            Level.WARN,
            "SAFE_REDACTION_MISSING",
            "Consider adding redaction guidance (secrets/tokens/PII) in Constraints/Safety.",
        ))

    return out


def check_schema_version_signal(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []

    body = doc.body.lower()
    schema_signals = [
        "output schema", "schema.json", "json schema", "zod", "schema_version", "strict json",
        "machine-checkable", "validator", "contract",
    ]
    if _has_any(body, schema_signals):
        if "schema_version" not in body:
            out.append(Finding(
                Level.WARN,
                "OUT_SCHEMA_VERSION_MISSING",
                "Schema-bound outputs detected; consider including `schema_version` in the output contract.",
            ))
    return out


def check_path_safety(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []

    body = doc.body

    if re.search(r"(?m)^[A-Za-z]:\\", body):
        out.append(Finding(Level.WARN, "PATH_WINDOWS", "Windows-style paths detected; prefer POSIX-style relative paths."))

    local_absolute_refs = sorted(
        set(re.findall(r"(?<![\w:])/(?:Users|home|Volumes|private|tmp|var|etc|opt)/[^\s)`>]+", body))
    )
    if re.search(r"(?m)^\s*/", body) or local_absolute_refs:
        evidence = ", ".join(local_absolute_refs[:3])
        out.append(
            Finding(
                Level.WARN,
                "PATH_ABSOLUTE",
                "Absolute paths detected; prefer public-safe repo-relative paths.",
                evidence=evidence,
            )
        )

    repo_root: Optional[Path] = None
    for base in [doc.path.parent, *doc.path.parent.parents]:
        if (base / ".git").exists():
            repo_root = base.resolve()
            break

    if repo_root is None:
        for base in [doc.path.resolve().parent, *doc.path.resolve().parent.parents]:
            if (base / ".git").exists():
                repo_root = base.resolve()
                break

    repo_link_pattern = re.compile(r"\]\(repo:([^)]+)\)")
    bad_repo_links: List[str] = []
    missing_repo_links: List[str] = []
    for raw_target in sorted(set(repo_link_pattern.findall(body))):
        target = raw_target.strip()
        if target.startswith("/") or target.startswith("../") or "/../" in target:
            bad_repo_links.append(f"repo:{target}")
            continue
        if repo_root is None:
            continue
        resolved = (repo_root / target).resolve()
        if not resolved.is_relative_to(repo_root):
            bad_repo_links.append(f"repo:{target}")
        elif not resolved.exists():
            missing_repo_links.append(f"repo:{target}")

    if bad_repo_links:
        sample = ", ".join(bad_repo_links[:3])
        out.append(
            Finding(
                Level.WARN,
                "PATH_REPO_LINK_TRAVERSAL",
                "`repo:` link(s) must stay inside the repository root.",
                evidence=sample,
            )
        )
    if missing_repo_links:
        sample = ", ".join(missing_repo_links[:3])
        out.append(
            Finding(
                Level.WARN,
                "PATH_REPO_LINK_MISSING",
                "`repo:` link target(s) were not found.",
                evidence=sample,
            )
        )

    traversal_refs = sorted(set(re.findall(r"\.\./[A-Za-z0-9._/\-]+", body)))
    unresolved_or_external: List[str] = []
    for rel in traversal_refs:
        candidates = [
            (doc.path.parent / rel).resolve(),
            (doc.path.resolve().parent / rel).resolve(),
        ]
        if repo_root and any(candidate.is_relative_to(repo_root) for candidate in candidates):
            continue
        unresolved_or_external.append(rel)

    if unresolved_or_external:
        sample = ", ".join(unresolved_or_external[:3])
        out.append(
            Finding(
                Level.WARN,
                "PATH_TRAVERSAL",
                "Parent traversal path(s) unresolved or outside repo root; prefer repo-relative in-repo paths.",
                evidence=sample,
            )
        )

    return out



def check_script_security(skill_dir: Path, doc: SkillDoc) -> List[Finding]:
    """
    Heuristic safety checks for script-backed skills.

    Goals:
    - catch accidental secret/env echo
    - discourage implicit network dependency
    - encourage explicit confirmation for destructive operations
    """
    out: List[Finding] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists() or not scripts_dir.is_dir():
        return out

    script_files: List[Path] = []
    for ext in ("*.py", "*.sh", "*.bash", "*.zsh", "*.js", "*.ts"):
        script_files.extend(sorted(scripts_dir.glob(ext)))

    if not script_files:
        return out

    body_l = doc.body.lower()
    mentions_network = _has_any(body_l, ["network", "internet", "offline", "allow-network", "no network"])
    mentions_network_allowlist = _has_any(
        body_l,
        [
            "allowlist",
            "allowed domains",
            "allowed hosts",
            "domain allowlist",
            "host allowlist",
            "network allowlist",
        ],
    )
    mentions_confirm = _has_any(body_l, ["--confirm", "--force", "dry-run", "destructive"])

    # Patterns: keep tight to avoid false positives.
    env_echo_patterns = [
        re.compile(r"print\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"pprint\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"logging\.\w+\s*\(\s*os\.environ", re.IGNORECASE),
        re.compile(r"console\.log\s*\(\s*process\.env", re.IGNORECASE),
    ]
    secret_echo_patterns = [
        re.compile(
            r"(print|logging\.\w+|console\.log)\s*\([^)]*(os\.environ|getenv\(|process\.env)[^)]*(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(print|logging\.\w+|console\.log)\s*\([^)]*(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[^)]*(os\.environ|getenv\(|process\.env)",
            re.IGNORECASE,
        ),
    ]
    network_patterns = [
        re.compile(r"^\s*import\s+requests\b", re.MULTILINE),
        re.compile(r"^\s*from\s+requests\b", re.MULTILINE),
        re.compile(r"^\s*import\s+httpx\b", re.MULTILINE),
        re.compile(r"^\s*import\s+aiohttp\b", re.MULTILINE),
        re.compile(r"urllib\.request\.urlopen", re.IGNORECASE),
        re.compile(r"\bcurl\b", re.IGNORECASE),
        re.compile(r"\bwget\b", re.IGNORECASE),
    ]
    network_url_patterns = [
        re.compile(r"https?://[A-Za-z0-9.\-_/:%?=&#+]+", re.IGNORECASE),
    ]
    destructive_patterns = [
        re.compile(r"shutil\.rmtree", re.IGNORECASE),
        re.compile(r"\.unlink\s*\(", re.IGNORECASE),
        re.compile(r"os\.remove\s*\(", re.IGNORECASE),
        re.compile(r"os\.rmdir\s*\(", re.IGNORECASE),
        re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
        re.compile(r"\bgit\s+push\b", re.IGNORECASE),
        re.compile(r"\bnpm\s+publish\b", re.IGNORECASE),
    ]
    untrusted_input_patterns = [
        re.compile(r"\bsys\.argv\b", re.IGNORECASE),
        re.compile(r"\bargparse\.ArgumentParser\b", re.IGNORECASE),
        re.compile(r"\binput\s*\(", re.IGNORECASE),
        re.compile(r"\bstdin\b", re.IGNORECASE),
        re.compile(r"\bprocess\.argv\b", re.IGNORECASE),
        re.compile(r"\breadline\s*\(", re.IGNORECASE),
    ]
    shell_sink_patterns = [
        re.compile(r"\bos\.system\s*\(", re.IGNORECASE),
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\([^\)]*shell\s*=\s*True", re.IGNORECASE | re.DOTALL),
        re.compile(r"\bchild_process\.(exec|execSync)\s*\(", re.IGNORECASE),
        re.compile(r"\bexecSync\s*\(", re.IGNORECASE),
    ]
    command_sink_patterns = [
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\(", re.IGNORECASE),
        re.compile(r"\bchild_process\.(spawn|spawnSync|exec|execSync)\s*\(", re.IGNORECASE),
        re.compile(r"\bspawn(Sync)?\s*\(", re.IGNORECASE),
    ]
    sanitizer_patterns = [
        re.compile(r"\bshlex\.quote\s*\(", re.IGNORECASE),
        re.compile(r"\bshell\s*=\s*False\b", re.IGNORECASE),
        re.compile(r"\bsubprocess\.(run|Popen|call|check_output)\s*\(\s*\[", re.IGNORECASE),
    ]

    for f in script_files:
        txt = _read_text(f)

        if any(p.search(txt) for p in env_echo_patterns):
            out.append(Finding(
                Level.FAIL,
                "SAFE_ENV_ECHO",
                "Script appears to print environment variables. Never echo env vars or secrets.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        if any(p.search(txt) for p in secret_echo_patterns):
            out.append(Finding(
                Level.FAIL,
                "SAFE_SECRET_ECHO",
                "Script appears to log/print secret-like values (API_KEY/TOKEN/SECRET/PASSWORD). Redact or remove.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        uses_network = any(p.search(txt) for p in network_patterns)
        if uses_network and not mentions_network:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_UNDECLARED",
                "Network usage detected in scripts but SKILL.md does not explicitly describe network requirements/constraints. Default to offline; gate behind --allow-network if needed.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        if uses_network and not mentions_network_allowlist:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_ALLOWLIST",
                "Network usage detected in scripts without an explicit domain/host allowlist policy in SKILL.md.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        if uses_network and any(p.search(txt) for p in network_url_patterns) and not mentions_network_allowlist:
            out.append(Finding(
                Level.WARN,
                "SAFE_NETWORK_URL_ALLOWLIST",
                "Hard-coded URL(s) detected in scripts; document explicit allowed domains/hosts in SKILL.md.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        is_destructive = any(p.search(txt) for p in destructive_patterns)
        if is_destructive and not mentions_confirm and not _has_any(txt.lower(), ["--dry-run", "--confirm", "--force", "dry_run", "confirm", "force"]):
            out.append(Finding(
                Level.WARN,
                "SAFE_DESTRUCTIVE_GUARD",
                "Potentially destructive operations detected in scripts without an obvious dry-run/confirm guard. Prefer --dry-run default and require --confirm/--force.",
                evidence=str(f.relative_to(skill_dir)),
            ))

        has_untrusted_input = any(p.search(txt) for p in untrusted_input_patterns)
        has_shell_sink = any(p.search(txt) for p in shell_sink_patterns)
        has_command_sink = any(p.search(txt) for p in command_sink_patterns)
        has_sanitizer = any(p.search(txt) for p in sanitizer_patterns)

        if has_untrusted_input and has_shell_sink:
            out.append(Finding(
                Level.FAIL,
                "SAFE_UNTRUSTED_TO_SHELL",
                "Untrusted input source combined with shell-style command execution detected. Avoid shell mode/os.system/exec* on user-controlled input.",
                evidence=str(f.relative_to(skill_dir)),
            ))
        elif has_untrusted_input and has_command_sink and not has_sanitizer:
            out.append(Finding(
                Level.WARN,
                "SAFE_UNTRUSTED_TO_COMMAND",
                "Untrusted input appears to flow into command execution without clear sanitization/argument-list hardening.",
                evidence=str(f.relative_to(skill_dir)),
            ))

    return out


def check_prompt_injection_signals(skill_dir: Path, doc: SkillDoc, *, pi_high_fail: bool) -> List[Finding]:
    out: List[Finding] = []

    patterns, config_findings = _load_prompt_patterns(skill_dir)
    out.extend(config_findings)
    allowlist, blocklist, local_findings = _load_allow_block_patterns()
    out.extend(local_findings)
    expected_paths, context_signals, skip_binary_globs, expected_findings = _load_expected_pi_context(skill_dir)
    out.extend(expected_findings)

    def _scan(text: str, evidence: str) -> None:
        for pattern, message, severity in blocklist:
            if pattern.search(text):
                out.append(Finding(_severity_to_level(severity, fail_on_high=pi_high_fail), "PI_BLOCKLIST", f"[{severity}] {message}", evidence=evidence))

        for code, pattern, message, severity in patterns:
            if any(allow.search(evidence) for allow in allowlist):
                continue
            if _is_expected_pi_context(code, evidence, text, expected_paths, context_signals):
                continue
            if pattern.search(text):
                out.append(Finding(_severity_to_level(severity, fail_on_high=pi_high_fail), code, f"[{severity}] {message}", evidence=evidence))

    _scan(doc.raw, "SKILL.md")

    for path, is_text in _iter_scan_targets(skill_dir):
        rel_path = str(path.relative_to(skill_dir))
        # Pattern definition files contain attack strings intentionally.
        if path.name == "prompt-injection-patterns.json":
            continue
        if not is_text:
            if any(fnmatch.fnmatch(rel_path, pat) for pat in skip_binary_globs):
                continue
            out.append(Finding(
                Level.WARN,
                "PI_BINARY_ATTACHMENT",
                "Binary attachment detected; manual review required (prompt scan skipped).",
                evidence=rel_path,
            ))
            continue
        if path.name == "SKILL.md":
            continue
        _scan(_read_text(path), rel_path)

    return out


def check_security_eval_coverage(skill_dir: Path, *, require_security_evals: bool) -> List[Finding]:
    """
    Ensure eval suites include adversarial security coverage.

    Focus:
    - at least one negative (non-trigger) case
    - at least one pressure/adversarial PI case
    - at least one deterministic safety guard for high-risk commands
    """
    out: List[Finding] = []
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        if require_security_evals:
            out.append(
                Finding(
                    Level.FAIL,
                    "SEC_EVALS_MISSING",
                    "references/evals.yaml not found; required when --require-security-evals is set.",
                )
            )
        return out

    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        out.append(Finding(Level.WARN, "SEC_EVALS_PARSE", f"Could not parse evals.yaml for security coverage checks: {exc}"))
        return out

    if not isinstance(obj, dict) or not isinstance(obj.get("cases"), list):
        return out

    cases = [c for c in obj.get("cases", []) if isinstance(c, dict)]
    if not cases:
        return out

    pi_terms = (
        "prompt injection",
        "jailbreak",
        "ignore previous",
        "ignore system",
        "override system",
        "bypass safety",
        "exfiltrate",
        "hidden instruction",
    )
    risky_commands = ("rm -rf", "curl", "wget", "netcat", "nc", "powershell", "invoke-webrequest")

    def _contains_risky_command(text: str) -> bool:
        for command in risky_commands:
            if command == "nc":
                if re.search(r"(^|[\s;&|])nc($|[\s;&|])", text):
                    return True
                continue
            if command in text:
                return True
        return False

    has_negative = False
    has_pressure = False
    has_pi_prompt_case = False
    has_risky_command_guard = False

    for c in cases:
        category = str(c.get("category", "")).strip().lower()
        should_trigger = c.get("should_trigger")
        prompt = str(c.get("prompt", "")).lower()
        acceptance = c.get("acceptance", [])
        deterministic_checks = c.get("deterministic_checks", {})

        if category == "negative" or should_trigger is False:
            has_negative = True
        if category == "pressure":
            has_pressure = True
        if any(term in prompt for term in pi_terms):
            has_pi_prompt_case = True

        # Check deterministic forbidden commands and textual acceptance guards.
        forbidden_cmds: List[str] = []
        if isinstance(deterministic_checks, dict):
            raw_forbidden = deterministic_checks.get("forbidden_commands", [])
            if isinstance(raw_forbidden, list):
                forbidden_cmds = [str(x).lower() for x in raw_forbidden]
            elif isinstance(raw_forbidden, str):
                forbidden_cmds = [raw_forbidden.lower()]
        if any(_contains_risky_command(cmd) for cmd in forbidden_cmds):
            has_risky_command_guard = True

        if isinstance(acceptance, list):
            for a in acceptance:
                text = str(a).lower()
                if _contains_risky_command(text):
                    has_risky_command_guard = True
                    break

    missing: List[Tuple[str, str]] = []
    if not has_negative:
        missing.append(("SEC_EVALS_NEGATIVE_MISSING", "No negative/non-trigger security case detected in evals.yaml. Add `category: negative` or `should_trigger: false` coverage."))
    if not has_pressure:
        missing.append(("SEC_EVALS_PRESSURE_MISSING", "No pressure/adversarial case detected in evals.yaml. Add at least one `category: pressure` case."))
    if not has_pi_prompt_case:
        missing.append(("SEC_EVALS_PI_CASE_MISSING", "No prompt-injection/jailbreak-style prompt detected in evals.yaml. Add one adversarial PI prompt case."))
    if not has_risky_command_guard:
        missing.append(("SEC_EVALS_COMMAND_GUARD_MISSING", "No deterministic risky-command guard detected. Add forbidden command checks (e.g., curl/wget/rm -rf/netcat)."))

    level = Level.FAIL if require_security_evals else Level.WARN
    for code, message in missing:
        out.append(Finding(level, code, message, evidence="references/evals.yaml"))

    return out
__all__ = [name for name in globals() if not name.startswith("__")]
