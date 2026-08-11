from validate_skill_authoring_family_benchmarks_core import *  # noqa: F403

def _validate_context_relocation(skill_rel: str, canonical_rel: str, skill_dir: Path) -> List[Finding]:
    """
    Validate that a skill enforces progressive-disclosure context disposition and return findings for any missing signals.

    This check applies only to skills listed in the relocation-guard set; for other skills it returns an empty list. When applicable, it inspects SKILL.md and the references/ directory and emits FAIL findings for each missing requirement: an explicit context-disposition policy, a "Read when:" signpost, a Markdown link into references/, and at least one document-like file in references/.

    Parameters:
        skill_rel (str): Repository-relative skill path used as the `skill` field on findings.
        canonical_rel (str): Canonicalized repository-relative path used to decide whether the relocation guard applies.
        skill_dir (Path): Filesystem path to the skill directory to inspect.

    Returns:
        List[Finding]: A list of findings describing each missing progressive-disclosure relocation requirement; empty if none are missing or the guard does not apply.
    """
    if canonical_rel.lower() not in _RELOCATION_GUARD_SKILLS:
        return []

    findings: List[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return findings

    body = _skill_markdown_body(skill_md.read_text(encoding="utf-8", errors="replace"))

    if not any(pattern.search(body) for pattern in _CONTEXT_POLICY_PATTERNS):
        findings.append(
            Finding(
                "FAIL",
                "CONTEXT_RELOCATION_POLICY_MISSING",
                skill_rel,
                "missing explicit context-disposition policy in SKILL.md; "
                "important still-valid context must be relocated to references, "
                "while stale, duplicated, unsafe, inappropriate, superseded, or "
                "low-signal text may be intentionally discarded",
            )
        )

    if re.search(r"read when\s*:", body, re.IGNORECASE) is None:
        findings.append(
            Finding(
                "FAIL",
                "CONTEXT_RELOCATION_READ_WHEN_MISSING",
                skill_rel,
                "missing `Read when:` progressive-disclosure signpost in SKILL.md",
            )
        )

    refs_dir = skill_dir / "references"

    # Accept both local and repo-level references links.
    ref_link_pattern = re.compile(r"\]\(([^)]*references/[^)]*)\)", re.IGNORECASE)
    ref_matches = ref_link_pattern.findall(body)

    if not ref_matches:
        findings.append(
            Finding(
                "FAIL",
                "CONTEXT_RELOCATION_REFERENCE_LINK_MISSING",
                skill_rel,
                "missing SKILL.md link into references/ for relocated context",
            )
        )
    else:
        # Verify local references targets exist; repo-level links are allowed as signposts.
        allowed_suffixes = {".md", ".yaml", ".yml", ".json"}
        for ref_path in ref_matches:
            normalized_ref = ref_path.strip()
            if normalized_ref.startswith("./"):
                normalized_ref = normalized_ref[2:]

            if normalized_ref.lower().startswith("references/"):
                resolved_path = skill_dir / normalized_ref
                if not resolved_path.exists():
                    findings.append(
                        Finding(
                            "FAIL",
                            "CONTEXT_RELOCATION_REFERENCE_MISSING",
                            skill_rel,
                            f"referenced file '{ref_path}' does not exist",
                        )
                    )
                elif resolved_path.suffix.lower() not in allowed_suffixes:
                    findings.append(
                        Finding(
                            "FAIL",
                            "CONTEXT_RELOCATION_REFERENCE_MISSING",
                            skill_rel,
                            f"referenced file '{ref_path}' has disallowed suffix (expected: {', '.join(sorted(allowed_suffixes))})",
                        )
                    )

    has_ref_docs = refs_dir.is_dir() and any(path.suffix in {".md", ".yaml", ".yml", ".json"} for path in refs_dir.iterdir())
    if not has_ref_docs:
        findings.append(
            Finding(
                "FAIL",
                "CONTEXT_RELOCATION_REFERENCES_EMPTY",
                skill_rel,
                "references/ must contain relocation targets for progressive disclosure",
            )
        )

    return findings
__all__ = [name for name in globals() if not name.startswith("__")]
