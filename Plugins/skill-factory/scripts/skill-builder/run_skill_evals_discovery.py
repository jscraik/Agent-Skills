import re
from pathlib import Path
from typing import List, Sequence, Tuple

from run_skill_evals_cli import *  # noqa: F403
from run_skill_evals_cli import EvalCase, _read_text

def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def _extract_first_question(text: str, patterns: Sequence[str], fallback: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())
    return fallback


def _baseline_discovery_response() -> str:
    return "\n".join(
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


def _discovery_reference_text(skill_dir: Path) -> str:
    reference = skill_dir / "references" / "discovery-interview.md"
    try:
        if reference.resolve().is_relative_to(skill_dir.resolve()) and reference.is_file():
            return _read_text(reference)
    except (OSError, RuntimeError):
        pass
    return ""


def _discovery_contract_gaps(skill_text: str, discovery_text: str) -> List[str]:
    linked = bool(re.search(
        r"(?<![\w/.-])(?:\./)?references/discovery-interview\.md(?![\w/.-])", skill_text
    ))
    contract = skill_text + "\n" + discovery_text if linked else skill_text
    missing = []
    if not _contains_any(skill_text, ["## Discovery interview"]) and not linked:
        missing.append("SKILL.md missing discovery interview section or explicit reference link")
    requirements = (
        (("ask one round at a time", "one round at a time"), "one-round-at-a-time"),
        (("plain-language question", "plain language question"), "plain-language question"),
        (("why the round matters", "explain why the round matters", "why this matters"), "why-this-matters"),
        (("avoid dumping the whole interview plan at once", "avoid dumping the full interview plan at once", "do not dump the full plan"), "no-full-plan-dump"),
    )
    for patterns, label in requirements:
        if not _contains_any(contract, patterns):
            missing.append(f"Discovery contract missing {label} guidance")
    return missing + _discovery_reference_gaps(discovery_text)


def _discovery_reference_gaps(text: str) -> List[str]:
    if not text:
        return ["discovery-interview.md not found"]
    missing = []
    if "## Request user input mini-templates" not in text:
        missing.append("discovery-interview.md missing mini-templates section")
    requirements = (
        (("## Copy-paste payload examples", "## Copy paste payload examples", "## Payload examples"), "payload examples section"),
        (("what should this skill help you do?", "what kind of help should this skill provide?", "which documentation surface should we improve first?", "which documentation surface should this update target first?", "what should this docs work help you do?"), "intuitive round-1 question"),
    )
    for patterns, label in requirements:
        if not _contains_any(text, patterns):
            missing.append(f"discovery-interview.md missing {label}")
    return missing


def _discovery_round_one_question(discovery_text: str) -> str:
    return _extract_first_question(
        discovery_text,
        patterns=[
            r"which documentation surface should(?: we improve first| this update target first)?\?",
            r"what should this docs work help you do\?",
            r"what should this skill help you do\?",
            r"what kind of help should this skill provide\?",
        ],
        fallback="What should this work help you do?",
    )


def _discovery_round_one_response(discovery_text: str) -> str:
    round_one_question = _discovery_round_one_question(discovery_text)
    return "\n".join(
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


def _discovery_confirmation_gaps(text: str) -> List[str]:
    missing = []
    if "## Round 6: Confirmation" not in text:
        missing.append("discovery-interview.md missing round-6 confirmation section")
    if not _contains_any(text, (
        "does this capture it", "does this capture the docs work well enough for me to implement",
        "anything to add or change before i implement it", "anything to add or change before i build it",
    )):
        missing.append("discovery-interview.md missing explicit confirmation question guidance")
    return missing


def _discovery_confirmation_questions(discovery_text: str) -> Tuple[str, str]:
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
    return primary_confirmation, secondary_confirmation


def _discovery_confirmation_summary(primary_confirmation: str, secondary_confirmation: str) -> List[str]:
    return [
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


def _discovery_round_six_response(discovery_text: str) -> str:
    primary, secondary = _discovery_confirmation_questions(discovery_text)
    return "\n".join([
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
        *_discovery_confirmation_summary(primary, secondary),
    ])


def _unsupported_discovery_response() -> str:
    return "\n".join(
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


def run_discovery_smoke(
    *,
    skill_md_path: Path,
    skill_dir: Path,
    case: EvalCase,
    output_last_message_path: Path,
    include_skill_context: bool = True,
) -> Tuple[int, str, str, List[str]]:
    """Emit contract-derived smoke output; this is not live model behavior."""
    if not include_skill_context:
        response = _baseline_discovery_response()
        output_last_message_path.write_text(response, encoding="utf-8")
        return 0, response, "", []
    skill_text = _read_text(skill_md_path)
    discovery_text = _discovery_reference_text(skill_dir)
    missing = _discovery_contract_gaps(skill_text, discovery_text)
    mode = case.smoke_mode or "discovery-round-one"
    if mode == "discovery-round-one":
        response = _discovery_round_one_response(discovery_text)
    elif mode == "discovery-round-six":
        missing.extend(_discovery_confirmation_gaps(discovery_text))
        response = _discovery_round_six_response(discovery_text)
    else:
        response = _unsupported_discovery_response()
    output_last_message_path.write_text(response, encoding="utf-8")
    if missing:
        stderr = "discovery-smoke contract gaps: " + "; ".join(missing)
        return 2, response, stderr, [stderr]
    if case.smoke_mode and mode not in {"discovery-round-one", "discovery-round-six"}:
        stderr = f"Unsupported smoke_mode for discovery-smoke runner: {case.smoke_mode}"
        return 2, response, stderr, [stderr]
    return 0, response, "", []

__all__ = [name for name in globals() if not name.startswith("__")]
