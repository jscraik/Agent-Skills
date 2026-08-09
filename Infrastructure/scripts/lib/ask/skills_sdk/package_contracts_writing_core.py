from .package_contracts_core import *  # noqa: F403
from .package_contracts_rubric import *  # noqa: F403
from .package_contracts_support import *  # noqa: F403
from .package_contracts_optimization import *  # noqa: F403

def _quality_check(
    name: str,
    status: str,
    *,
    dimension: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable writing-quality check record."""
    return {
        "name": name,
        "dimension": dimension,
        "status": status,
        "evidence": evidence or {},
    }


def _quality_blocker(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    severity: str = "blocked",
) -> dict[str, Any]:
    """Return a stable writing-quality blocker record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": severity,
        "path": path,
        "message": message,
    }


def _quality_advisory(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable non-blocking writing-quality advisory record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "advisory",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _frontmatter_bool(frontmatter: dict[str, Any], field: str) -> bool:
    """Return a frontmatter boolean from bools or common string spellings."""
    value = frontmatter.get(field)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def markdown_heading_titles(text: str) -> list[str]:
    """Return normalized markdown heading titles in document order."""
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        title = stripped.lstrip("#").strip()
        if title:
            titles.append(title)
    return titles


def markdown_heading_titles_for_level(text: str, level: int) -> list[str]:
    """Return normalized markdown heading titles at one heading level."""
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        marker = stripped.split(maxsplit=1)[0]
        if len(marker) != level or set(marker) != {"#"}:
            continue
        title = stripped[len(marker):].strip()
        if title:
            titles.append(title)
    return titles


def _has_any_heading(text: str, headings: tuple[str, ...]) -> bool:
    return any(markdown_heading_declared(text, heading) for heading in headings)


def _body_contains_any(body: str, needles: tuple[str, ...]) -> bool:
    lowered = body.lower()
    return any(needle.lower() in lowered for needle in needles)


def _token_set(text: str) -> set[str]:
    """Return normalized natural-language tokens without broad regex parsing."""
    punctuation = ".,:;!?()[]{}\"'<>"
    return {
        token.strip(punctuation).lower()
        for token in text.replace("/", " ").replace("-", " ").split()
        if token.strip(punctuation)
    }


def _skill_body_without_frontmatter(text: str) -> str:
    """Return markdown body text with leading YAML frontmatter removed."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def _construction_step_body(text: str) -> str:
    """Return the combined procedural body used for construction checks."""
    sections: list[str] = []
    for heading in ("Workflow", "Procedure", "Steps"):
        if markdown_heading_declared(text, heading):
            sections.append(markdown_section_body(text, heading))
    return "\n".join(section for section in sections if section.strip())


def _construction_line_items(text: str) -> list[str]:
    """Return non-heading text lines that are likely to carry instructions."""
    items: list[str] = []
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("\u0060\u0060\u0060"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line or line.startswith("#"):
            continue
        while line.startswith(("-", "*")):
            line = line[1:].strip()
        if len(line) >= 3 and line[0].isdigit() and line[1] == ".":
            line = line[2:].strip()
        if line:
            items.append(line)
    return items


def _long_paragraphs_without_behavior(text: str) -> list[dict[str, Any]]:
    """Return long prose paragraphs that lack routing, gate, output, or action terms."""
    body = _skill_body_without_frontmatter(text)
    paragraphs: list[str] = []
    current: list[str] = []
    in_code_block = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("\u0060\u0060\u0060"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not line or line.startswith("#") or line.startswith(("-", "*")):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))

    findings: list[dict[str, Any]] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        tokens = _token_set(paragraph)
        word_count = len([word for word in paragraph.split() if word.strip()])
        carries_behavior = bool(
            tokens & CONSTRUCTION_OBLIGATION_TERMS
            or tokens & CONSTRUCTION_PHASE_TERMS
            or "references/" in paragraph
            or "Command:" in paragraph
            or "Output Contract" in paragraph
        )
        if word_count >= CONSTRUCTION_SEDIMENT_WORD_LIMIT and not carries_behavior:
            findings.append(
                {
                    "paragraph": index,
                    "word_count": word_count,
                    "preview": paragraph[:120],
                }
            )
    return findings


def _duplicate_instruction_lines(text: str) -> list[dict[str, Any]]:
    """Return repeated instruction-shaped lines that should be deduplicated."""
    seen: dict[str, dict[str, Any]] = {}
    for line_number, item in enumerate(_construction_line_items(text), start=1):
        tokens = _token_set(item)
        if len(tokens) < CONSTRUCTION_DUPLICATE_LINE_WORD_LIMIT:
            continue
        if not (tokens & CONSTRUCTION_OBLIGATION_TERMS or "references/" in item):
            continue
        normalized = " ".join(sorted(tokens))
        if normalized not in seen:
            seen[normalized] = {
                "line_numbers": [],
                "text": item[:120],
            }
        seen[normalized]["line_numbers"].append(line_number)
    duplicates: list[dict[str, Any]] = []
    for record in seen.values():
        if len(record["line_numbers"]) > 1:
            duplicates.append(record)
    return duplicates


def _package_support_files(skill_md: Path | None) -> list[Path]:
    """Return package-local support files that should have a routing pointer."""
    if not skill_md:
        return []
    package_root = skill_md.parent
    support_roots = [
        package_root / "references",
        package_root / "scripts",
        package_root / "assets",
        package_root / "agents",
        package_root / "workflows",
    ]
    files: list[Path] = []
    for root in support_roots:
        if not root.is_dir():
            continue
        for candidate in sorted(path for path in root.rglob("*") if path.is_file()):
            if candidate.name.startswith(".") or candidate.name in PACKAGE_IGNORED_FILE_NAMES:
                continue
            files.append(candidate)
    return files


def _package_text_surfaces(skill_md: Path | None, text: str) -> str:
    """Return the bounded package text used to detect routed support files."""
    if not skill_md:
        return text
    surfaces = [text]
    for relative_path in (
        "agents/openai.yaml",
        "references/contract.yaml",
        "references/evals.yaml",
        "references/knowledge-capsule-routing.md",
        "references/source-provenance.md",
        "references/source-context.yaml",
        "workflows/skillflow.json",
    ):
        candidate = skill_md.parent / relative_path
        if not candidate.is_file():
            continue
        try:
            surfaces.append(candidate.read_text(encoding="utf-8"))
        except OSError:
            continue
    return "\n".join(surfaces)


def _orphaned_support_files(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> list[str]:
    """Return support files not mentioned by package entrypoints or contracts."""
    if not skill_md:
        return []
    package_text = _package_text_surfaces(skill_md, text)
    package_root = skill_md.parent
    orphaned: list[str] = []
    implicitly_routed = {
        "agents/openai.yaml",
        "references/contract.yaml",
        "references/evals.yaml",
        "references/knowledge-capsule.manifest.yaml",
        "references/knowledge-demand.yaml",
        "references/task-profile.json",
    }
    for candidate in _package_support_files(skill_md):
        relative = candidate.relative_to(package_root).as_posix()
        if relative in implicitly_routed:
            continue
        if relative.startswith("references/evals/") and (
            package_root / "references" / "evals.yaml"
        ).is_file():
            continue
        if relative.startswith("references/scorer-calibration/") and (
            package_root / "references" / "scorer-calibration" / "manifest.json"
        ).is_file():
            continue
        if relative in package_text or candidate.name in package_text:
            continue
        orphaned.append(repo_relative_path(repo_root, candidate) if repo_root else relative)
    return [path for path in orphaned if path]


def _package_relative_path(skill_md: Path | None, path: str) -> str:
    """Return a package-relative path when a repo-relative path points into a skill."""
    if not skill_md:
        return path
    package_root = skill_md.parent
    marker = f"{package_root.as_posix()}/"
    if path.startswith(marker):
        return path.removeprefix(marker)
    parts = path.split("/")
    for index, part in enumerate(parts):
        if part == "references":
            return "/".join(parts[index:])
    return path


def _manifest_orphaned_bundle_files(
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
) -> list[str]:
    """Return bundle support files that must be routed when a capsule manifest exists."""
    if not skill_md:
        return []
    manifest_path = skill_md.parent / "references" / "knowledge-capsule.manifest.yaml"
    if not manifest_path.is_file():
        return []
    orphaned = _orphaned_support_files(repo_root, skill_md, text)
    bundle_paths: list[str] = []
    for path in orphaned:
        package_path = _package_relative_path(skill_md, path)
        if package_path.startswith("references/knowledge-capsules/") or package_path in {
            "references/source-context.yaml",
            "references/source-provenance.md",
        }:
            bundle_paths.append(path)
    return sorted(bundle_paths)


def _review_lens_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill appears to be a review/audit lens."""
    name = str(frontmatter.get("name") or "")
    description = str(frontmatter.get("description") or "")
    haystack = f"{name} {description} {text}".lower()
    return (
        name.startswith("review-")
        or "review-lens" in name
        or "review lens" in haystack
        or "reviewer lens" in haystack
    )


def _external_input_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill inspects external or untrusted artifacts."""
    haystack = (
        f"{frontmatter.get('name') or ''} "
        f"{frontmatter.get('description') or ''} {text}"
    ).lower()
    return any(
        needle in haystack
        for needle in (
            "third-party",
            "external skill",
            "untrusted",
            "review a diff",
            "reviewer plugin",
            "intake",
            "fetched",
            "user-provided",
        )
    )


def _improvement_skill(frontmatter: dict[str, Any], text: str) -> bool:
    """Return whether the skill claims to improve or optimize an artifact."""
    tokens = _token_set(
        f"{frontmatter.get('name') or ''} {frontmatter.get('description') or ''} {text}"
    )
    return bool(tokens & {"improve", "improving", "optimize", "optimization", "repair"})


def _writing_quality_advisories(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    text: str,
    *,
    user_invoked: bool,
    description: str,
    procedural: bool,
    source_path: str | None,
) -> list[dict[str, Any]]:
    """Return Tessl-derived advisory rubric findings for skill writing quality."""
    advisories: list[dict[str, Any]] = []
    description_tokens = _token_set(description)
    action_terms = sorted(description_tokens & DESCRIPTION_ACTION_TERMS)
    if not user_invoked and description:
        if len(description_tokens) < 8 or not action_terms:
            advisories.append(
                _quality_advisory(
                    "description_specificity_weak",
                    "Description should name concrete capabilities rather than vague skill identity.",
                    dimension="invocation",
                    path=source_path,
                    evidence={
                        "token_count": len(description_tokens),
                        "action_terms": action_terms,
                    },
                )
            )
        trigger_markers = {"when", "asks", "mentions", "needs", "wants", "use"}
        if len(description_tokens & trigger_markers) < 2:
            advisories.append(
                _quality_advisory(
                    "description_trigger_terms_missing",
                    "Description should include natural trigger terms a user would actually say.",
                    dimension="invocation",
                    path=source_path,
                    evidence={"trigger_markers": sorted(description_tokens & trigger_markers)},
                )
            )
        conflict_terms = {"help", "helps", "stuff", "things", "tasks", "anything", "everything"}
        if description_tokens & conflict_terms:
            advisories.append(
                _quality_advisory(
                    "description_conflict_risk",
                    "Description includes generic terms that can overlap with other skills.",
                    dimension="invocation",
                    path=source_path,
                    evidence={"generic_terms": sorted(description_tokens & conflict_terms)},
                )
            )

    commands = skill_command_candidates(text)
    workflow_text = "\n".join(
        markdown_section_body(text, heading)
        for heading in ("Workflow", "Procedure", "Steps")
        if markdown_heading_declared(text, heading)
    )
    action_output_terms = {"return", "report", "write", "create", "run", "validate", "emit", "record"}
    if procedural and not commands and not (_token_set(workflow_text) & action_output_terms):
        advisories.append(
            _quality_advisory(
                "content_actionability_weak",
                "Procedural skills should provide concrete commands, artifacts, outputs, or action verbs.",
                dimension="actionability",
                path=source_path,
                evidence={"command_count": len(commands)},
            )
        )

    search_terms = {"search", "inspect", "review", "audit", "compare", "scan"}
    bounded_terms = {"bounded", "budget", "limit", "stop", "first", "few", "narrowest"}
    text_tokens = _token_set(text)
    if text_tokens & search_terms and not (text_tokens & bounded_terms):
        advisories.append(
            _quality_advisory(
                "unbounded_search_instruction",
                "Search, review, or audit skills should declare a stop condition or bounded search budget.",
                dimension="actionability",
                path=source_path,
                evidence={"search_terms": sorted(text_tokens & search_terms)},
            )
        )

    if _review_lens_skill(frontmatter, text):
        missing_review_sections = [
            heading
            for heading in ("Stance", "What to look for", "How to report")
            if not markdown_heading_declared(text, heading)
        ]
        if missing_review_sections:
            advisories.append(
                _quality_advisory(
                    "review_lens_output_contract_missing",
                    "Review-lens skills should declare Stance, What to look for, and How to report sections.",
                    dimension="review_lens",
                    path=source_path,
                    evidence={"missing_sections": missing_review_sections},
                )
            )

    if _external_input_skill(frontmatter, text) and not _body_contains_any(
        text,
        ("treat", "untrusted", "as data", "not instructions", "trust boundary"),
    ):
        advisories.append(
            _quality_advisory(
                "missing_untrusted_input_boundary",
                "Skills that inspect external artifacts should state the untrusted-input boundary.",
                dimension="safety_boundary",
                path=source_path,
            )
        )

    if _improvement_skill(frontmatter, text) and not _body_contains_any(
        text,
        ("baseline", "before", "after", "rerun", "regression"),
    ):
        advisories.append(
            _quality_advisory(
                "improvement_claim_without_before_after_evidence",
                "Improvement skills should require baseline, change, rerun, and regression evidence.",
                dimension="self_improving",
                path=source_path,
            )
        )

    orphaned = _orphaned_support_files(repo_root, skill_md, text)
    if orphaned:
        advisories.append(
            _quality_advisory(
                "orphaned_bundle_reference",
                "Package support files should be routed by SKILL.md or package contracts.",
                dimension="progressive_disclosure",
                path=source_path,
                evidence={"orphaned_paths": orphaned},
            )
        )

    return advisories


def _skill_evals_yaml_path(skill_md: Path | None) -> Path | None:
    if not skill_md:
        return None
    candidate = skill_md.parent / "references" / "evals.yaml"
    return candidate if candidate.is_file() else None


def _case_id(case: Any, index: int) -> str:
    if isinstance(case, dict) and case.get("id"):
        return str(case["id"])
    return f"case[{index}]"


def _scenario_cases_from_reference(
    evals_path: Path,
    loaded: dict[str, Any],
) -> list[Any]:
    """Return eval cases, using a small fallback for nested cases YAML."""
    cases = loaded.get("cases")
    if isinstance(cases, list) and cases and all(isinstance(case, dict) for case in cases):
        return cases
    try:
        text = evals_path.read_text(encoding="utf-8")
    except OSError:
        return cases if isinstance(cases, list) else []
    parsed_cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_list_key: str | None = None
    in_cases = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not in_cases:
            if indent == 0 and stripped == "cases:":
                in_cases = True
            continue
        if indent == 0 and not stripped.startswith("- "):
            break
        if indent in {0, 2} and stripped.startswith("- id:"):
            if current is not None:
                parsed_cases.append(current)
            current = {}
            current_list_key = None
            remainder = stripped[2:].strip()
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_frontmatter_scalar(value.strip())
            continue
        if current is None:
            continue
        if current_list_key and indent >= 2 and stripped.startswith("- "):
            values = current.setdefault(current_list_key, [])
            if isinstance(values, list):
                values.append(parse_frontmatter_scalar(stripped[2:].strip()))
            continue
        if indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current[key] = parse_frontmatter_scalar(value)
                current_list_key = None
            else:
                current[key] = []
                current_list_key = key
    if current is not None:
        parsed_cases.append(current)
    return parsed_cases or (cases if isinstance(cases, list) else [])


def _scenario_alignment_checks(
    repo_root: Path | None,
    skill_md: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic gold-scenario shape checks for references/evals.yaml."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    evals_path = _skill_evals_yaml_path(skill_md)
    rel_path = repo_relative_path(repo_root, evals_path) if repo_root and evals_path else None
    if evals_path is None:
        checks.append(
            _quality_check(
                "scenario_alignment_declared",
                "not_applicable",
                dimension="scenario_alignment",
                evidence={"path": None, "reason": "references/evals.yaml not declared"},
            )
        )
        return checks, blockers

    loaded, error = read_structured_reference(evals_path)
    if error is not None or not isinstance(loaded, dict):
        checks.append(
            _quality_check(
                "scenario_alignment_parse",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "error": error or "evals.yaml must be a mapping"},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_unparseable",
                "references/evals.yaml must be parseable before scenario quality can be trusted.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    cases = _scenario_cases_from_reference(evals_path, loaded)
    if not isinstance(cases, list) or not cases:
        checks.append(
            _quality_check(
                "scenario_alignment_cases_declared",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "case_count": 0},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_cases_missing",
                "references/evals.yaml must declare at least one case before scenario-quality can run.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    missing_by_case: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            missing_by_case.append({"case": _case_id(case, index), "missing": ["mapping"]})
            continue
        missing: list[str] = []
        for field in ("id", "category"):
            if not str(case.get(field) or "").strip():
                missing.append(field)
        if not str(case.get("prompt") or case.get("user_task") or "").strip():
            missing.append("prompt_or_user_task")
        if not str(case.get("given") or case.get("why_realistic") or "").strip():
            missing.append("given_or_why_realistic")
        if not str(
            case.get("should")
            or case.get("expected_behavior")
            or case.get("expected_evidence")
            or ""
        ).strip():
            missing.append("should_or_expected_behavior")
        acceptance = case.get("acceptance")
        expected_evidence = case.get("expected_evidence")
        if not (
            isinstance(acceptance, list)
            and acceptance
            or isinstance(expected_evidence, list)
            and expected_evidence
        ):
            missing.append("acceptance_or_expected_evidence")
        if missing:
            missing_by_case.append({"case": _case_id(case, index), "missing": missing})

    status = "blocked_validation" if missing_by_case else "pass"
    checks.append(
        _quality_check(
            "scenario_alignment_gold_shape",
            status,
            dimension="scenario_alignment",
            evidence={
                "path": rel_path,
                "case_count": len(cases),
                "missing_by_case": missing_by_case,
            },
        )
    )
    if missing_by_case:
        blockers.append(
            _quality_blocker(
                "scenario_alignment_gold_shape_incomplete",
                "references/evals.yaml cases must include gold-standard fields: id, category, task, given, should, and acceptance evidence.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
    return checks, blockers
__all__ = [name for name in globals() if not name.startswith("__")]
