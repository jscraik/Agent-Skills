from validate_skill_authoring_family_benchmarks_core import *  # noqa: F403

def _validate_evals(skill_rel: str, skill_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        findings.append(Finding("FAIL", "EVALS_MISSING", skill_rel, "missing references/evals.yaml"))
        return findings

    try:
        evals = _load_yaml(evals_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "EVALS_PARSE", skill_rel, f"could not parse evals.yaml: {exc}"))
        return findings

    schema_version = str(evals.get("schema_version", "")).strip()
    if schema_version != "2.0":
        findings.append(
            Finding("FAIL", "EVALS_SCHEMA_VERSION", skill_rel, f"evals schema_version must be 2.0 (found: {schema_version or 'missing'})")
        )

    expected_skill_name = _normalize_skill_name(skill_dir)
    skill_name = str(evals.get("skill_name", "")).strip()
    if skill_name != expected_skill_name:
        findings.append(
            Finding("FAIL", "EVALS_SKILL_NAME", skill_rel, f"evals skill_name mismatch: expected {expected_skill_name}, found {skill_name or 'missing'}")
        )

    cases = evals.get("cases")
    if not isinstance(cases, list) or not cases:
        findings.append(Finding("FAIL", "EVALS_CASES", skill_rel, "evals.yaml must include a non-empty cases list"))
        return findings

    if len(cases) < 5:
        findings.append(Finding("FAIL", "EVALS_CASE_COUNT", skill_rel, f"evals must include at least 5 cases (found {len(cases)})"))
    elif len(cases) < 8:
        findings.append(
            Finding(
                "WARN",
                "EVALS_CASE_COUNT_BELOW_TARGET",
                skill_rel,
                f"evals include {len(cases)} cases; the value-efficient behavioral release target is 8 distinct scenarios",
            )
        )

    seen_ids: Set[str] = set()
    categories: Set[str] = set()
    has_pi_case = False
    has_negative_should_trigger_false = False
    has_pressure_command_guard = False
    cases_with_det_checks = 0
    happy_missing_smoke: List[str] = []

    for idx, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            findings.append(Finding("FAIL", "EVALS_CASE_SHAPE", skill_rel, f"case #{idx} is not an object"))
            continue

        case_id = str(case.get("id", "")).strip()
        if not case_id:
            findings.append(Finding("FAIL", "EVALS_CASE_ID", skill_rel, f"case #{idx} missing id"))
        elif case_id in seen_ids:
            findings.append(Finding("FAIL", "EVALS_CASE_ID_DUP", skill_rel, f"duplicate case id: {case_id}"))
        else:
            seen_ids.add(case_id)

        category = str(case.get("category", "")).strip().lower()
        if category:
            categories.add(category)

        should_trigger = case.get("should_trigger")
        if category == "negative" and should_trigger is False:
            has_negative_should_trigger_false = True

        eval_modes = case.get("eval_modes")
        if not isinstance(eval_modes, list) or not eval_modes:
            findings.append(Finding("FAIL", "EVALS_EVAL_MODES", skill_rel, f"case {case_id or idx} missing non-empty eval_modes"))
        else:
            normalized_modes = {str(mode).strip().lower() for mode in eval_modes}
            invalid_modes = sorted(normalized_modes - {"smoke", "release"})
            if invalid_modes:
                findings.append(
                    Finding(
                        "FAIL",
                        "EVALS_EVAL_MODES_INVALID",
                        skill_rel,
                        f"case {case_id or idx} has invalid eval_modes: {', '.join(invalid_modes)}",
                    )
                )
            # P1.3: happy-path cases without smoke can't catch regressions in quick runs
            if category == "happy" and "smoke" not in normalized_modes:
                happy_missing_smoke.append(case_id or f"#{idx}")

        if _case_has_pi_language(case):
            has_pi_case = True

        if category == "pressure":
            commands = _case_forbidden_commands(case)
            if commands and commands.intersection(RISKY_COMMAND_TOKENS):
                has_pressure_command_guard = True

        # P1.1: track deterministic_checks coverage
        det = case.get("deterministic_checks")
        if isinstance(det, dict) and det:
            cases_with_det_checks += 1

    missing_categories = sorted(REQUIRED_CASE_CATEGORIES - categories)
    if missing_categories:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_CATEGORY_COVERAGE",
                skill_rel,
                f"missing eval categories: {', '.join(missing_categories)}",
            )
        )

    if not has_negative_should_trigger_false:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_NEGATIVE_SHOULD_TRIGGER",
                skill_rel,
                "missing negative case with should_trigger: false",
            )
        )

    if not has_pi_case:
        findings.append(Finding("FAIL", "EVALS_PI_CASE", skill_rel, "missing explicit prompt injection/jailbreak pressure coverage"))

    if not has_pressure_command_guard:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_PRESSURE_COMMAND_GUARD",
                skill_rel,
                "missing pressure case with deterministic forbidden command guard (curl/wget/rm -rf/netcat)",
            )
        )

    # P1.1: deterministic_checks coverage ratio
    total_valid = len([c for c in cases if isinstance(c, dict)])
    if total_valid > 0:
        coverage = cases_with_det_checks / total_valid
        if coverage < _DET_CHECK_COVERAGE_WARN_THRESHOLD:
            findings.append(
                Finding(
                    "WARN",
                    "EVALS_DET_CHECK_COVERAGE",
                    skill_rel,
                    f"only {cases_with_det_checks}/{total_valid} cases ({coverage:.0%}) have deterministic_checks; "
                    f"aim for ≥{_DET_CHECK_COVERAGE_WARN_THRESHOLD:.0%} to reduce reliance on LLM-graded outputs alone",
                )
            )

    # P1.3: happy-path cases without smoke mode
    if happy_missing_smoke:
        findings.append(
            Finding(
                "WARN",
                "EVALS_HAPPY_NO_SMOKE",
                skill_rel,
                f"{len(happy_missing_smoke)} happy-path case(s) lack smoke eval_mode and won't catch regressions "
                f"in quick runs: {', '.join(happy_missing_smoke)}",
            )
        )

    # Item 3: JSON Schema structural validation
    findings.extend(_validate_with_schema(skill_rel, evals, _EVALS_SCHEMA_PATH, "EVALS_SCHEMA", "evals.yaml"))

    return findings


def _validate_task_profile(skill_rel: str, skill_dir: Path, *, expected_scope_skill: str) -> List[Finding]:
    findings: List[Finding] = []
    profile_path = skill_dir / "references" / "task-profile.json"
    if not profile_path.exists():
        findings.append(Finding("FAIL", "TASK_PROFILE_MISSING", skill_rel, "missing Infrastructure/references/task-profile.json"))
        return findings

    try:
        profile = _load_json(profile_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "TASK_PROFILE_PARSE", skill_rel, f"could not parse task-profile.json: {exc}"))
        return findings

    missing = sorted(REQUIRED_TASK_PROFILE_KEYS - set(profile.keys()))
    if missing:
        findings.append(
            Finding(
                "FAIL",
                "TASK_PROFILE_KEYS",
                skill_rel,
                f"task-profile.json missing required keys: {', '.join(missing)}",
            )
        )

    scope_skill = str(profile.get("scope_skill", "")).strip()
    if scope_skill != expected_scope_skill:
        findings.append(
            Finding(
                "FAIL",
                "TASK_PROFILE_SCOPE",
                skill_rel,
                f"scope_skill must equal {expected_scope_skill} (found: {scope_skill or 'missing'})",
            )
        )

    # P2.6: rubric_version must be a valid ISO date and not stale
    rubric_version = str(profile.get("rubric_version", "")).strip()
    if rubric_version:
        try:
            rubric_date = datetime.strptime(rubric_version, "%Y-%m-%d").date()
            today = date.today()
            age_days = (today - rubric_date).days
            if age_days > _RUBRIC_VERSION_STALE_DAYS:
                findings.append(
                    Finding(
                        "WARN",
                        "TASK_PROFILE_RUBRIC_STALE",
                        skill_rel,
                        f"rubric_version {rubric_version} is {age_days} days old "
                        f"(threshold: {_RUBRIC_VERSION_STALE_DAYS} days); review and update rubric",
                    )
                )
        except ValueError:
            findings.append(
                Finding(
                    "WARN",
                    "TASK_PROFILE_RUBRIC_FORMAT",
                    skill_rel,
                    f"rubric_version '{rubric_version}' is not a valid ISO date (expected YYYY-MM-DD)",
                )
            )

    return findings


def _validate_reference_pi(skill_rel: str, skill_dir: Path) -> List[Finding]:
    """
    Scan SKILL.md and non-eval files under references/ for indirect prompt-injection patterns and emit warnings for matches.

    This function ignores `references/evals.yaml` (indirect PI language there is treated as test coverage).

    Returns:
        findings (List[Finding]): A list of WARN findings describing each detected indirect prompt-injection occurrence.
    """
    findings: List[Finding] = []

    # SKILL.md body (everything after closing frontmatter ---)
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        raw = skill_md.read_text(encoding="utf-8", errors="replace")
        body = _skill_markdown_body(raw)
        if _INDIRECT_PI_TOKENS.search(body):
            findings.append(
                Finding(
                    "WARN",
                    "SKILL_MD_INDIRECT_PI",
                    skill_rel,
                    "SKILL.md body contains language matching indirect prompt injection patterns; "
                    "verify this is intentional (e.g., documenting attack patterns)",
                )
            )

    # References directory — scan .md and .yaml but skip evals.yaml
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.iterdir()):
            if ref_file.name == "evals.yaml":
                continue  # PI language in evals is deliberate test coverage
            if ref_file.suffix not in {".md", ".yaml", ".yml"}:
                continue
            try:
                text = ref_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if _INDIRECT_PI_TOKENS.search(text):
                findings.append(
                    Finding(
                        "WARN",
                        "REFERENCE_INDIRECT_PI",
                        skill_rel,
                        f"reference file {ref_file.name} contains indirect prompt injection patterns; "
                        "review for unintended instructions that could influence skill behaviour",
                    )
                )

    return findings
__all__ = [name for name in globals() if not name.startswith("__")]
