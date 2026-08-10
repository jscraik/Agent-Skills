from skill_gate_core import *  # noqa: F403
from skill_gate_security_checks import *  # noqa: F403
from skill_gate_research_checks import *  # noqa: F403

def _lvl_name(level: Level) -> str:
    return {Level.INFO: "INFO", Level.WARN: "WARN", Level.FAIL: "FAIL"}[level]


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_json_payload(doc: SkillDoc, findings: Sequence[Finding], *, failed: bool) -> Dict[str, Any]:
    exit_code = 2 if failed else 0
    skill_uri = _sarif_artifact_uri(doc.path)
    return {
        "schema_version": "1.1",
        "tool": "skill_gate",
        "generated_at": _utc_now_iso(),
        "skill": skill_uri,
        "skill_path": skill_uri,
        "name": doc.frontmatter.get("name"),
        "decision": "fail" if failed else "pass",
        "exit_code": exit_code,
        "failed": failed,
        "findings": [
            {"level": _lvl_name(f.level), "code": f.code, "message": f.message, "evidence": f.evidence}
            for f in findings
        ],
    }


def _find_repo_root(path: Path) -> Optional[Path]:
    resolved = path.expanduser().resolve()
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _sarif_artifact_uri(path: Path) -> str:
    resolved = path.expanduser().resolve()
    repo_root = _find_repo_root(resolved)
    if repo_root is not None:
        try:
            return resolved.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return resolved.name


def _build_sarif_payload(doc: SkillDoc, findings: Sequence[Finding], *, failed: bool) -> Dict[str, Any]:
    rules = []
    seen_codes = set()
    for finding in findings:
        if finding.code in seen_codes:
            continue
        seen_codes.add(finding.code)
        level = _lvl_name(finding.level).lower()
        rules.append(
            {
                "id": finding.code,
                "name": finding.code,
                "shortDescription": {"text": finding.message},
                "properties": {"defaultSeverity": level},
            }
        )
    results = []
    uri = _sarif_artifact_uri(doc.path)
    seen_results = set()
    for finding in findings:
        result_key = (finding.code, finding.message, finding.evidence)
        if result_key in seen_results:
            continue
        seen_results.add(result_key)
        level = _lvl_name(finding.level).lower()
        results.append(
            {
                "ruleId": finding.code,
                "level": {"info": "note", "warn": "warning", "fail": "error"}[level],
                "message": {"text": finding.message + (f" | {finding.evidence}" if finding.evidence else "")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": uri},
                        }
                    }
                ],
            }
        )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "skill_gate",
                        "informationUri": "https://github.com/openai/skills",
                        "rules": rules,
                    }
                },
                "invocations": [{"executionSuccessful": not failed}],
                "results": results,
            }
        ],
    }


def run_gate(
    doc: SkillDoc,
    *,
    max_lines: int,
    max_codeblock_lines: int,
    min_desc_len: int,
    require_contract: bool,
    require_evals: bool,
    require_philosophy: bool,
    require_redaction: bool,
    require_fail_fast: bool,
    require_security_evals: bool,
    pi_high_fail: bool,
) -> List[Finding]:
    findings: List[Finding] = []

    findings.extend(check_codex_frontmatter(doc, min_desc_len=min_desc_len))
    findings.extend(check_progressive_disclosure(doc, max_lines=max_lines, max_codeblock_lines=max_codeblock_lines))
    findings.extend(check_required_sections(doc, require_philosophy=require_philosophy))
    findings.extend(check_canonical_header_order(doc))
    findings.extend(check_workflow_fail_fast(doc, require_fail_fast=require_fail_fast))
    findings.extend(check_redaction_language(doc, require_redaction=require_redaction))
    findings.extend(check_schema_version_signal(doc))
    findings.extend(check_path_safety(doc))

    skill_dir = doc.path.parent
    findings.extend(check_script_security(skill_dir, doc))
    findings.extend(check_prompt_injection_signals(skill_dir, doc, pi_high_fail=pi_high_fail))
    findings.extend(check_security_eval_coverage(skill_dir, require_security_evals=require_security_evals))
    findings.extend(check_research_scope_focus(doc))
    findings.extend(check_research_example_quality(doc))
    findings.extend(check_research_eval_prompt_realism(doc))
    findings.extend(check_contract_and_evals(skill_dir, require_contract=require_contract, require_evals=require_evals))
    findings.extend(check_repo_references(doc))

    findings.sort(key=lambda f: (-int(f.level), f.code))
    return findings


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skill_gate.py", description="Gold-standard gate for Codex SKILL.md quality.")
    p.add_argument("path", help="Path to a skill directory or SKILL.md file.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--output", default=None, help="Optional path to write the rendered report.")
    p.add_argument("--sarif-out", default=None, help="Optional path to write SARIF 2.1.0 findings for CI/code scanning.")

    p.add_argument("--max-lines", type=int, default=360, help="Max allowed lines in SKILL.md (default: 360).")
    p.add_argument("--max-codeblock-lines", type=int, default=120, help="Warn if a code block exceeds this (default: 120).")
    p.add_argument("--min-description-len", type=int, default=120, help="Warn if description shorter than this (default: 120).")

    p.add_argument(
        "--strict-frontmatter-line1",
        action="store_true",
        help="Require frontmatter to start on line 1 with `---`.",
    )

    p.add_argument("--no-require-contract", action="store_true", help="Do not require references/contract.yaml.")
    p.add_argument("--no-require-evals", action="store_true", help="Do not require references/evals.yaml.")
    p.add_argument("--no-require-philosophy", action="store_true", help="Do not require a Philosophy/Principles section.")
    p.add_argument("--no-require-redaction", action="store_true", help="Do not require redaction language in Constraints/Safety.")
    p.add_argument("--require-fail-fast", action="store_true", help="Require fail-fast language in Validation section (FAIL if absent).")
    p.add_argument(
        "--require-security-evals",
        action="store_true",
        help="Fail when adversarial security eval coverage is missing (negative/pressure/PI/command-guard checks).",
    )
    p.add_argument(
        "--pi-high-fail",
        action="store_true",
        help="Treat high-severity prompt-injection pattern matches as FAIL instead of WARN.",
    )

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    try:
        doc = load_skill(args.path, strict_line1=args.strict_frontmatter_line1)
    except Exception as e:
        print(
            f"skill_gate: ERROR loading {args.path}: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        return 1

    findings = run_gate(
        doc,
        max_lines=args.max_lines,
        max_codeblock_lines=args.max_codeblock_lines,
        min_desc_len=args.min_description_len,
        require_contract=not args.no_require_contract,
        require_evals=not args.no_require_evals,
        require_philosophy=not args.no_require_philosophy,
        require_redaction=not args.no_require_redaction,
        require_fail_fast=bool(args.require_fail_fast),
        require_security_evals=bool(args.require_security_evals),
        pi_high_fail=bool(args.pi_high_fail),
    )

    failed = any(f.level == Level.FAIL for f in findings)

    rendered = ""
    if args.format == "json":
        payload = _build_json_payload(doc, findings, failed=failed)
        rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        lines = [f"Skill: {doc.frontmatter.get('name', 'unknown')}", f"Path:  {doc.path}", ""]
        for f in findings:
            ev = f" | {f.evidence}" if f.evidence else ""
            lines.append(f"{_lvl_name(f.level)} {f.code}: {f.message}{ev}")
        lines.extend(["", f"RESULT: {'FAIL' if failed else 'PASS'}"])
        rendered = "\n".join(lines)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")

    if args.sarif_out:
        sarif_path = Path(args.sarif_out).expanduser().resolve()
        sarif_path.parent.mkdir(parents=True, exist_ok=True)
        sarif_payload = _build_sarif_payload(doc, findings, failed=failed)
        sarif_path.write_text(json.dumps(sarif_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(rendered)

    return 2 if failed else 0
__all__ = [name for name in globals() if not name.startswith("__")]
