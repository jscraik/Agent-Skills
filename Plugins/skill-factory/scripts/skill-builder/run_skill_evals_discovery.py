from run_skill_evals_cli import *  # noqa: F403

def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def _extract_first_question(text: str, patterns: Sequence[str], fallback: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())
    return fallback


def run_discovery_smoke(
    *,
    skill_md_path: Path,
    skill_dir: Path,
    case: EvalCase,
    output_last_message_path: Path,
    include_skill_context: bool = True,
) -> Tuple[int, str, str, List[str]]:
    """
    Fast, deterministic smoke check for discovery-first-turn behavior.

    This bypasses external model execution and verifies that the skill contract
    encodes the expected interview UX. It emits a contract-derived first-turn
    response so normal acceptance assertions can run against it.
    """

    warnings: List[str] = []

    if not include_skill_context:
        response = "\n".join(
            [
                "## Inputs",
                "- Skill context was intentionally withheld for this no-skill baseline run.",
                "- The response can only use the task prompt and generic repository expectations.",
                "",
                "## Outputs",
                "- Baseline response recorded for comparison against the skill-enabled runner.",
                "- No skill-specific routing, discovery contract, or reference-file evidence is available.",
                "",
                "## Next step",
                "- Compare this control output with the normal skill-enabled output before claiming skill lift.",
                "",
                "## Failure mode",
                "- Passing this baseline means the case may not prove the skill added value.",
            ]
        )
        output_last_message_path.write_text(response, encoding="utf-8")
        return 0, response, "", warnings

    skill_text = _read_text(skill_md_path)
    discovery_ref = skill_dir / "references" / "discovery-interview.md"
    discovery_text = _read_text(discovery_ref) if discovery_ref.exists() else ""

    missing: List[str] = []
    if not _contains_any(skill_text, ["## Discovery interview"]):
        missing.append("SKILL.md missing discovery interview section")
    if not _contains_any(
        skill_text,
        [
            "ask one round at a time",
            "one round at a time",
        ],
    ):
        missing.append("SKILL.md missing one-round-at-a-time guidance")
    if not _contains_any(
        skill_text,
        [
            "plain-language question",
            "plain language question",
        ],
    ):
        missing.append("SKILL.md missing plain-language question guidance")
    if not _contains_any(
        skill_text,
        [
            "why the round matters",
            "explain why the round matters",
            "why this matters",
        ],
    ):
        missing.append("SKILL.md missing why-this-matters guidance")
    if not _contains_any(
        skill_text,
        [
            "avoid dumping the whole interview plan at once",
            "avoid dumping the full interview plan at once",
        ],
    ):
        missing.append("SKILL.md missing no-full-plan-dump guidance")
    if not discovery_text:
        missing.append("discovery-interview.md not found")
    else:
        if "## Request user input mini-templates" not in discovery_text:
            missing.append("discovery-interview.md missing mini-templates section")
        if not _contains_any(
            discovery_text,
            [
                "## Copy-paste payload examples",
                "## Copy paste payload examples",
                "## Payload examples",
            ],
        ):
            missing.append("discovery-interview.md missing payload examples section")
        if not _contains_any(
            discovery_text,
            [
                "what should this skill help you do?",
                "what kind of help should this skill provide?",
                "which documentation surface should we improve first?",
                "which documentation surface should this update target first?",
                "what should this docs work help you do?",
            ],
        ):
            missing.append("discovery-interview.md missing intuitive round-1 question")

    smoke_mode = case.smoke_mode or "discovery-round-one"
    round_one_question = _extract_first_question(
        discovery_text,
        patterns=[
            r"which documentation surface should(?: we improve first| this update target first)?\?",
            r"what should this docs work help you do\?",
            r"what should this skill help you do\?",
            r"what kind of help should this skill provide\?",
        ],
        fallback="What should this work help you do?",
    )

    if smoke_mode == "discovery-round-one":
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: the exact target surface, primary reader, and job-to-be-done for this documentation work.",
                "- Why this matters: keeping the goal clear prevents scope creep and makes the later validation and ownership decisions more reliable.",
                "",
                "## Outputs",
                "- After discovery confirms the goal, return a tight docs plan or patch scoped to the right surface.",
                "",
                "## Next step",
                f"- Round 1 question: {round_one_question}",
                "",
                "## Failure mode",
                "- Do not draft or rewrite the docs yet when the workflow is still underspecified; finish round 1 first.",
            ]
        )
    elif smoke_mode == "discovery-round-six":
        if "## Round 6: Confirmation" not in discovery_text:
            missing.append("discovery-interview.md missing round-6 confirmation section")
        if not _contains_any(
            discovery_text,
            [
                "does this capture it",
                "does this capture the docs work well enough for me to implement",
                "anything to add or change before i implement it",
                "anything to add or change before i build it",
            ],
        ):
            missing.append("discovery-interview.md missing explicit confirmation question guidance")
        primary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"does this capture[^?]*\?",
                r"ready to implement\?",
            ],
            fallback="Does this capture the work well enough for me to implement?",
        )
        secondary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"anything to add or change before i (?:implement|build) it\?",
            ],
            fallback="Anything to add or change before I implement it?",
        )
        response = "\n".join(
            [
                "## Inputs",
                "- No major discovery gaps remain; this turn is for confirmation before implementation starts.",
                "",
                "## Outputs",
                "- Provide a compact docs work summary and wait for confirmation before making edits.",
                "",
                "## Next step",
                "- Ask for confirmation before implementation begins.",
                "",
                "## Failure mode",
                "- Do not assume approval from silence; ask for confirmation before implementing.",
                "",
                "## Skill Summary: docs-expert",
                "",
                "**Goal:** Help audit or rewrite documentation with a clear target surface, reader, and verification path.",
                "**Trigger:** natural requests about improving README, docs, runbooks, or in-code documentation.",
                "**Arguments:** target doc path or surface, audience, source of truth, and validation expectations",
                "",
                "**Process:**",
                "1. Confirm the target documentation surface and audience.",
                "2. Confirm the governing source of truth and constraints.",
                "3. Confirm the validation and handoff expectations.",
                "4. Return a concise docs summary and wait for approval to implement.",
                "",
                "**Inputs:** target doc surface, audience, source material, and constraints",
                "**Outputs:** compact docs summary plus the agreed implementation path",
                "**Dependencies:** none required for the smoke example",
                "**Guardrails:** avoid inventing commands or policy and do not implement before confirmation",
                "",
                "Assumptions: this is a docs workflow summary and not the final documentation patch.",
                "",
                primary_confirmation,
                secondary_confirmation,
            ]
        )
    else:
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: a supported smoke mode.",
                "",
                "## Outputs",
                "- None until the smoke mode is corrected.",
                "",
                "## Next step",
                "- Correct the smoke mode and rerun the eval.",
                "",
                "## Failure mode",
                "- Unsupported discovery smoke mode.",
            ]
        )
    output_last_message_path.write_text(response, encoding="utf-8")

    stderr = ""
    if missing:
        stderr = "discovery-smoke contract gaps: " + "; ".join(missing)
        warnings.append(stderr)
        return 2, response, stderr, warnings

    if case.smoke_mode and case.smoke_mode not in {"discovery-round-one", "discovery-round-six"}:
        msg = f"Unsupported smoke_mode for discovery-smoke runner: {case.smoke_mode}"
        warnings.append(msg)
        return 2, response, msg, warnings

    return 0, response, stderr, warnings

__all__ = [name for name in globals() if not name.startswith("__")]
