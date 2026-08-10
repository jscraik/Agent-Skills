from validate_skill_authoring_family_benchmarks_core import *  # noqa: F403
from validate_skill_authoring_family_benchmarks_eval_checks import *  # noqa: F403
from validate_skill_authoring_family_benchmarks_context_checks import *  # noqa: F403

def _validate_skill(skill_rel: str) -> List[Finding]:
    """
    Validate a single skill directory and collect findings for contract, evals, task-profile, reference PI, and context-relocation checks.

    Parameters:
        skill_rel (str): Repository-relative path to the skill to validate.

    Returns:
        List[Finding]: Accumulated findings (FAIL/WARN) detected for the given skill. If the skill directory is missing, returns a single `FAIL` finding with code `SKILL_DIR_MISSING`. Findings reference the provided `skill_rel`.
    """
    skill_dir = (REPO_ROOT / skill_rel).resolve()
    canonical_rel = _canonical_skill_rel(skill_rel)
    findings: List[Finding] = []

    skill_dir = (REPO_ROOT / skill_rel).resolve()
    canonical_rel = _canonical_skill_rel(skill_rel)
    findings: List[Finding] = []

    if not skill_dir.exists():
        return [Finding("FAIL", "SKILL_DIR_MISSING", skill_rel, "skill directory not found")]

    try:
        expected_scope_skill = _resolve_scope_skill_for_path(canonical_rel)
    except RuntimeError as exc:
        findings.append(Finding("FAIL", "TASK_PROFILE_SCOPE_RESOLVER", skill_rel, str(exc)))
        expected_scope_skill = canonical_rel

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        findings.append(Finding("FAIL", "SKILL_MD_MISSING", skill_rel, "missing SKILL.md"))

    findings.extend(_validate_contract(skill_rel, skill_dir))
    findings.extend(_validate_evals(skill_rel, skill_dir))
    findings.extend(_validate_task_profile(skill_rel, skill_dir, expected_scope_skill=expected_scope_skill))
    findings.extend(_validate_reference_pi(skill_rel, skill_dir))
    findings.extend(_validate_context_relocation(skill_rel, canonical_rel, skill_dir))
    return findings


def _print_text(findings: Sequence[Finding], checked: Sequence[str]) -> None:
    print("[family-benchmark] checked skills:")
    for skill in checked:
        print(f"  - {skill}")

    fails = [f for f in findings if f.level == "FAIL"]
    warns = [f for f in findings if f.level == "WARN"]

    if not fails:
        print("[family-benchmark] pass: all family benchmark checks satisfied")
    else:
        print("[family-benchmark] failures:")
        for finding in fails:
            print(f"  - {finding.level} {finding.code} [{finding.skill}] {finding.message}")

    if warns:
        print("[family-benchmark] warnings:")
        for finding in warns:
            print(f"  - {finding.level} {finding.code} [{finding.skill}] {finding.message}")


def _print_json(findings: Sequence[Finding], checked: Sequence[str]) -> None:
    fails = [f for f in findings if f.level == "FAIL"]
    payload = {
        "checked": list(checked),
        "findings": [
            {
                "level": finding.level,
                "code": finding.code,
                "skill": finding.skill,
                "message": finding.message,
            }
            for finding in findings
        ],
        "pass": not fails,
    }
    print(json.dumps(payload, indent=2))


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate equivalent family benchmark requirements.")
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Skill path relative to repo root (repeatable). Defaults to all family members.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    _default_baseline = REPO_ROOT / "artifacts" / "validation" / "baselines" / "family-gate-baseline.json"
    parser.add_argument(
        "--write-baseline",
        metavar="PATH",
        nargs="?",
        const=str(_default_baseline),
        help="Write current findings as the regression baseline (default path if no arg given)",
    )
    parser.add_argument(
        "--check-baseline",
        metavar="PATH",
        nargs="?",
        const=str(_default_baseline),
        help="Compare current findings against a saved baseline and fail on regressions",
    )
    args = parser.parse_args(list(argv))

    skills = _dedupe_requested_skills(tuple(args.skill) if args.skill else DEFAULT_FAMILY_SKILLS)
    findings: List[Finding] = []
    for skill in skills:
        findings.extend(_validate_skill(skill))

    # P2.6: family-level rubric_version divergence check
    rubric_dates: List[tuple[str, date]] = []
    for skill in skills:
        skill_dir = (REPO_ROOT / skill).resolve()
        profile_path = skill_dir / "references" / "task-profile.json"
        if profile_path.exists():
            try:
                profile = _load_json(profile_path)
                rv = str(profile.get("rubric_version", "")).strip()
                rubric_dates.append((skill, datetime.strptime(rv, "%Y-%m-%d").date()))
            except (OSError, TypeError, ValueError) as exc:
                findings.append(
                    Finding(
                        "WARN",
                        "TASK_PROFILE_RUBRIC_UNREADABLE",
                        skill,
                        f"could not read rubric_version from {profile_path.name}: {exc}; "
                        "this skill is excluded from the family divergence check",
                    )
                )
    if len(rubric_dates) >= 2:
        dates_only = [d for _, d in rubric_dates]
        spread_days = (max(dates_only) - min(dates_only)).days
        if spread_days > _RUBRIC_VERSION_DIVERGENCE_DAYS:
            oldest = min(rubric_dates, key=lambda x: x[1])
            newest = max(rubric_dates, key=lambda x: x[1])
            findings.append(
                Finding(
                    "WARN",
                    "TASK_PROFILE_RUBRIC_DIVERGENCE",
                    "family",
                    f"rubric_version spread across family is {spread_days} days "
                    f"(oldest: {oldest[0]} at {oldest[1]}, newest: {newest[0]} at {newest[1]}); "
                    f"align family rubric versions within {_RUBRIC_VERSION_DIVERGENCE_DAYS} days",
                )
            )

    # Item 5: Baseline write/check
    if args.write_baseline:
        baseline_path = Path(args.write_baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_data = {
            "schema_version": 1,
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "skills": list(skills),
            "findings": [{"level": f.level, "code": f.code, "skill": f.skill} for f in findings],
            "summary": {
                "fail_count": sum(1 for f in findings if f.level == "FAIL"),
                "warn_count": sum(1 for f in findings if f.level == "WARN"),
            },
        }
        baseline_path.write_text(json.dumps(baseline_data, indent=2) + "\n", encoding="utf-8")
        print(f"[family-benchmark] baseline written: {baseline_path}")

    regression_findings: List[Finding] = []
    if args.check_baseline:
        baseline_path = Path(args.check_baseline)
        if not baseline_path.exists():
            print(f"[family-benchmark] ERROR: baseline not found at {baseline_path}; regression check required", file=sys.stderr)
            return 1
        else:
            try:
                baseline_data = _load_json(baseline_path)
                # Group baseline findings by (code, skill) -> max severity rank
                baseline_by_code: Dict[tuple, int] = {}
                for f in baseline_data.get("findings", []):
                    if isinstance(f, dict):
                        key = (f["code"], f["skill"])
                        rank = SEVERITY_RANK.get(f["level"], 0)
                        baseline_by_code[key] = max(baseline_by_code.get(key, 0), rank)

                # Group current findings by (code, skill) -> max severity rank
                current_by_code: Dict[tuple, int] = {}
                for f in findings:
                    key = (f.code, f.skill)
                    rank = SEVERITY_RANK.get(f.level, 0)
                    current_by_code[key] = max(current_by_code.get(key, 0), rank)

                # Find regressions: new findings or worsened severity
                regressions = []
                for key, current_rank in current_by_code.items():
                    code, skill = key
                    baseline_rank = baseline_by_code.get(key, -1)
                    if current_rank > baseline_rank:
                        # Severity increased or completely new finding
                        level_name = {v: k for k, v in SEVERITY_RANK.items()}.get(current_rank, "UNKNOWN")
                        regressions.append((level_name, code, skill))

                if regressions:
                    for level, code, skill in sorted(regressions):
                        regression_findings.append(
                            Finding("FAIL", "BASELINE_REGRESSION", skill, f"new or worsened finding vs baseline: {level} {code}")
                        )
                else:
                    print("[family-benchmark] baseline check: no regressions detected")
            except (OSError, TypeError, ValueError) as exc:
                print(f"[family-benchmark] ERROR: could not load/parse baseline: {exc}", file=sys.stderr)
                return 1

    all_findings = list(findings) + regression_findings

    if args.format == "json":
        _print_json(all_findings, skills)
    else:
        _print_text(all_findings, skills)

    fails = [f for f in all_findings if f.level == "FAIL"]
    return 2 if fails else 0
__all__ = [name for name in globals() if not name.startswith("__")]
