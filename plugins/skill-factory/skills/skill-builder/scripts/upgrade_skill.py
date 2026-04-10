#!/usr/bin/env python3
"""
upgrade_skill.py

Heuristically review a Codex agent skill and print suggestions to improve its
SKILL.md instructions and frontmatter.

Usage:
    python upgrade_skill.py <path/to/skill-dir-or-SKILL.md>

Examples:
    python upgrade_skill.py github/my-skill
    python upgrade_skill.py github/my-skill/SKILL.md

Exit codes:
    0  success (no HIGH-priority suggestions)
    1  parsing/IO error
    2  at least one HIGH-priority suggestion was emitted (useful for CI)

Notes:
- Skill selection relies heavily on `name` and `description` because only those
  are loaded at startup. The body is only loaded when the skill is invoked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

# ---------------------------------------------------------------------------
# Shared frontmatter parser (sibling module)
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from yaml_frontmatter import (  # noqa: E402  # type: ignore[import]
    parse_frontmatter as _parse_frontmatter_shared,
    read_text as _read_text,
    resolve_skill_md_path as _resolve_skill_md_path,
)


# -----------------------------
# Data model
# -----------------------------

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class Suggestion:
    rule: str
    category: str
    priority: Priority
    message: str
    rationale: str = ""
    example: str = ""


@dataclass(frozen=True)
class SkillDoc:
    skill_md_path: Path
    raw_text: str
    frontmatter: Dict[str, Any]
    body: str
    fm_start_line: int  # 1-indexed
    fm_end_line: int    # 1-indexed (line containing closing ---)


# -----------------------------
# Frontmatter parsing — delegates to shared yaml_frontmatter module
# -----------------------------


def load_skill(path_like: str) -> SkillDoc:
    skill_md_path = _resolve_skill_md_path(path_like)

    if not skill_md_path.exists():
        raise FileNotFoundError(f"SKILL.md not found at: {skill_md_path}")

    raw_text = _read_text(skill_md_path)
    fm, body, fm_start, fm_end = _parse_frontmatter_shared(raw_text)
    return SkillDoc(
        skill_md_path=skill_md_path,
        raw_text=raw_text,
        frontmatter=fm,
        body=body,
        fm_start_line=fm_start,
        fm_end_line=fm_end,
    )


# -----------------------------
# Heuristics
# -----------------------------

_H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _has_any(text: str, needles: Sequence[str]) -> bool:
    t = text.lower()
    return any(n.lower() in t for n in needles)


def _extract_h2_headings(body: str) -> List[str]:
    return [_norm(m.group(1)) for m in _H2_RE.finditer(body)]


def _iter_files(skill_dir: Path, rel_dir: str) -> List[Path]:
    p = skill_dir / rel_dir
    if not p.exists() or not p.is_dir():
        return []
    return sorted([c for c in p.rglob("*") if c.is_file()])


def _extract_h2_blocks(body: str) -> List[Tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", body))
    blocks: List[Tuple[str, str]] = []
    for i, match in enumerate(matches):
        title = _norm(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        blocks.append((title, body[start:end].strip()))
    return blocks


def _find_section_text(body: str, aliases: Sequence[str]) -> str:
    for title, text in _extract_h2_blocks(body):
        if any(alias.lower() in title for alias in aliases):
            return text
    return ""


def _research_surface_count(text: str) -> int:
    patterns = [
        r"\bskills?\b",
        r"\bagents?\b",
        r"\bhooks?\b",
        r"\bprompts?\b",
        r"\bplugins?\b",
        r"\bapps?\b",
        r"\bmcp(?:s| servers?)?\b",
    ]
    return sum(1 for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE))


def _focus_language_count(text: str) -> int:
    phrases = [
        "smallest package",
        "smallest viable",
        "smallest boundary",
        "focused",
        "narrow",
        "2-3",
        "2–3",
        "2 to 3",
        "first pass",
        "start with",
        "limit scope",
        "avoid sprawling",
        "package boundary",
        "keep scope tight",
    ]
    return sum(1 for phrase in phrases if phrase in text.lower())


def _load_eval_cases(skill_dir: Path) -> List[Dict[str, Any]]:
    evals_path = skill_dir / "references" / "evals.yaml"
    if yaml is None or not evals_path.exists():
        return []
    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(obj, dict):
        return []
    cases = obj.get("cases", [])
    if not isinstance(cases, list):
        return []
    return [case for case in cases if isinstance(case, dict)]


def generate_suggestions(doc: SkillDoc, *, min_description_len: int = 120) -> List[Suggestion]:
    fm = doc.frontmatter
    body = doc.body
    headings = _extract_h2_headings(body)

    skill_dir = doc.skill_md_path.parent

    suggestions: List[Suggestion] = []

    def add(
        *,
        rule: str,
        category: str,
        priority: Priority,
        message: str,
        rationale: str = "",
        example: str = "",
    ) -> None:
        suggestions.append(
            Suggestion(
                rule=rule,
                category=category,
                priority=priority,
                message=message,
                rationale=rationale.strip(),
                example=textwrap.dedent(example).strip(),
            )
        )

    # --- Frontmatter: required fields + spec constraints ---
    name = fm.get("name")
    description = fm.get("description")

    if not isinstance(name, str) or not name.strip():
        add(
            rule="frontmatter.name.missing_or_invalid",
            category="Frontmatter",
            priority=Priority.HIGH,
            message="Add a non-empty `name` field in YAML frontmatter.",
            rationale="`name` is required for Codex to load the skill.",
            example="""\
            ---
            name: my-skill-name
            description: Use this skill when ...
            ---
            """,
        )
    else:
        if "\n" in name or "\r" in name:
            add(
                rule="frontmatter.name.single_line",
                category="Frontmatter",
                priority=Priority.HIGH,
                message="Make `name` a single line (no newlines).",
                rationale="The skills format expects a single-line name.",
            )
        if len(name) > 100:
            add(
                rule="frontmatter.name.max_len",
                category="Frontmatter",
                priority=Priority.HIGH,
                message=f"Shorten `name` (current length {len(name)}; max 100).",
                rationale="Codex validates max length on startup.",
            )
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.strip()):
            add(
                rule="frontmatter.name.kebab_case",
                category="Frontmatter",
                priority=Priority.MEDIUM,
                message="Consider using kebab-case for `name` (e.g., `draft-commit-message`).",
                rationale="Consistent naming improves discoverability and avoids quoting/escaping.",
            )

    if not isinstance(description, str) or not description.strip():
        add(
            rule="frontmatter.description.missing_or_invalid",
            category="Frontmatter",
            priority=Priority.HIGH,
            message="Add a non-empty `description` field in YAML frontmatter.",
            rationale=(
                "Only `name` and `description` are loaded at startup; "
                "description strongly affects skill selection and implicit invocation."
            ),
            example="""\
            description: Draft a conventional commit message when the user asks for help writing a commit message.
            """,
        )
    else:
        if "\n" in description or "\r" in description:
            add(
                rule="frontmatter.description.single_line",
                category="Frontmatter",
                priority=Priority.HIGH,
                message="Make `description` a single line (no newlines).",
                rationale="The skills format expects a single-line description.",
            )
        if len(description) > 500:
            add(
                rule="frontmatter.description.max_len",
                category="Frontmatter",
                priority=Priority.HIGH,
                message=f"Shorten `description` (current length {len(description)}; max 500).",
                rationale="Codex validates max length on startup.",
            )
        # Keep your original "expand description" behavior as HIGH priority
        # (while still allowing the threshold to be configured via flag).
        if len(description.strip()) < min_description_len:
            add(
                rule="frontmatter.description.too_short",
                category="Description",
                priority=Priority.HIGH,
                message=(
                    f"Expand the `description` field (current length {len(description.strip())}; "
                    f"aim for ~{min_description_len}–200 chars with clear trigger + outcome)."
                ),
                rationale=(
                    "Short/ambiguous descriptions reduce correct implicit invocation. "
                    "Include a clear 'when' clause and the expected output."
                ),
                example=f"""\
                Current: {description.strip()}

                Suggested pattern:
                description: Use this skill when <trigger>. It will <produce outcome> using <inputs>.
                """,
            )
        if not _has_any(description, ["when ", "if ", "whenever ", "use this skill"]):
            add(
                rule="frontmatter.description.trigger_language",
                category="Description",
                priority=Priority.MEDIUM,
                message="Add explicit trigger language to `description` (e.g., 'when the user asks ...').",
                rationale="Codex relies on the description to decide when to invoke a skill implicitly.",
            )

    # Optional agents/openai.yaml short_description
    metadata = fm.get("metadata")
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    has_openai_short_description = False
    if openai_yaml.exists():
        try:
            openai_obj = yaml.safe_load(openai_yaml.read_text(encoding="utf-8")) or {}
            interface = openai_obj.get("interface") if isinstance(openai_obj, dict) else {}
            short_description = interface.get("short_description") if isinstance(interface, dict) else None
            has_openai_short_description = isinstance(short_description, str) and bool(short_description.strip())
        except Exception:
            has_openai_short_description = False

    if metadata is not None:
        add(
            rule="frontmatter.metadata.discouraged",
            category="Frontmatter",
            priority=Priority.LOW,
            message="Prefer minimal SKILL.md frontmatter (name + description). Move UI metadata to `agents/openai.yaml` and remove `metadata`.",
            example="""\
            # agents/openai.yaml
            interface:
              display_name: "Human-friendly name"
              short_description: "One-line summary shown in skill pickers."
            """,
        )
    elif not has_openai_short_description:
        add(
            rule="agents.openai_yaml.short_description",
            category="Frontmatter",
            priority=Priority.LOW,
            message="Consider adding `agents/openai.yaml` with `interface.short_description` for user-facing UI (optional).",
            example="""\
            interface:
              display_name: "Human-friendly name"
              short_description: "One-line summary shown in skill pickers."
            """,
        )


    # NOTE:
    # We intentionally do not emit "prohibited heading" suggestions for
    # "when to use", "inputs", "outputs", or "failure mode". Earlier guidance
    # conflicted with the active skill-gate expectations and existing templates.

    # --- Body: structure + progressive disclosure ---
    if not body.strip():
        add(
            rule="body.missing",
            category="Body",
            priority=Priority.HIGH,
            message="Add an instruction body (or at least a minimal workflow) to SKILL.md.",
            rationale=(
                "While the body is optional, most skills need step-by-step instructions to be reliable. "
                "If the skill is script-backed, document how/when to run scripts and expected inputs/outputs."
            ),
            example="""\
            ## What this skill does
            - ...

            ## Workflow
            1. ...
            2. ...

            ## Deliverables
            - ...
            """,
        )
    else:
        # Philosophy check (your original intent; keep HIGH)
        if not _has_any(body, ["philosophy", "principle", "principles", "mental model"]):
            add(
                rule="body.philosophy.missing",
                category="Philosophy",
                priority=Priority.HIGH,
                message="Add a philosophy or principles section.",
                example="""\
                ## Core Philosophy

                Before diving into procedures, understand the fundamental approach:
                - What is the underlying philosophy guiding this domain?
                - What questions should be asked before taking action?
                - What mental model helps make better decisions?
                """,
            )

        # Anti-patterns check with the original heuristic:
        # - If no anti-pattern wording exists anywhere
        # - AND 'avoid' isn't present in the first 500 chars
        body_lc = body.lower()
        antipattern_signals = ["anti-pattern", "anti pattern", "anti patterns", "pitfalls", "what to avoid"]
        has_antipattern_anywhere = _has_any(body, antipattern_signals)
        avoid_in_first_500 = "avoid" in body_lc[:500]

        if (not has_antipattern_anywhere) and (not avoid_in_first_500):
            add(
                rule="body.antipatterns.missing",
                category="Anti-Patterns",
                priority=Priority.HIGH,
                message='Add anti-patterns or a "what to avoid" section.',
                example="""\
                ## Anti-Patterns to Avoid

                Common mistakes when [doing this task]:
                - ❌ **Template trap**: Using rigid templates that constrain creativity
                - ❌ **Context blindness**: Applying same approach regardless of situation
                - ❌ **Over-specification**: Adding unnecessary constraints
                """,
            )

        # Variation encouragement (keep MEDIUM like your original)
        if not _has_any(body, ["vary", "variation", "different", "context-dependent", "no two outputs"]):
            add(
                rule="body.variation.missing",
                category="Variation",
                priority=Priority.MEDIUM,
                message="Add explicit variation encouragement.",
                example="""\
                ## Encouraging Variation

                **IMPORTANT**: Outputs should vary based on context. Avoid converging on "favorite" patterns:
                - Adapt to the specific use case
                - Consider different approaches for different scenarios
                - No two outputs should be identical unless requirements are identical
                """,
            )

        # Empowerment (missing previously; keep LOW like your original)
        if not _has_any(body, ["extraordinary", "capable"]):
            add(
                rule="body.empowerment.missing",
                category="Empowerment",
                priority=Priority.LOW,
                message="Add a short empowering conclusion.",
                example="""\
                ## Remember

                The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
                Use judgment, adapt to context, and push boundaries when appropriate.
                """,
            )

        # Organization check (keep MEDIUM like your original)
        if len(headings) < 3:
            add(
                rule="body.organization.headers",
                category="Organization",
                priority=Priority.MEDIUM,
                message="Add more section headers for better organization.",
                example="""\
                Organize the skill into clear sections:
                ## Philosophy/Principles
                ## Core Guidelines
                ## Anti-Patterns
                ## Examples (optional)
                ## Advanced Topics (optional)
                """,
            )

        # Conciseness check (align with ~200–300 lines, hard cap ~400)
        line_count = len(doc.raw_text.splitlines())
        if line_count > 400:
            add(
                rule="body.too_long",
                category="Conciseness",
                priority=Priority.HIGH,
                message=f"SKILL.md is too long ({line_count} lines). Reduce to ~200–300; hard cap ~400.",
                rationale="Shorter skills improve focus and reduce model drift.",
            )
        elif line_count > 300:
            add(
                rule="body.long",
                category="Conciseness",
                priority=Priority.MEDIUM,
                message=f"SKILL.md is a bit long ({line_count} lines). Aim for ~200–300 lines.",
                rationale="Concise skills are easier to execute reliably.",
            )

        if not _has_any(body, ["example prompt", "example prompts", "examples"]):
            add(
                rule="body.examples.missing",
                category="Body",
                priority=Priority.LOW,
                message="Consider adding 2–3 example prompts that should trigger this skill.",
            )
        else:
            examples_text = _find_section_text(body, ["examples", "example prompts"])
            examples = re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+.+$", examples_text)
            quoted_examples = re.findall(r'`[^`]{10,}`|"[^"\n]{10,}"', examples_text)
            if len(examples) + len(quoted_examples) < 2:
                add(
                    rule="body.examples.too_thin",
                    category="Examples",
                    priority=Priority.MEDIUM,
                    message="Expand the examples section to include 2–3 realistic user-style prompts or worked examples.",
                    rationale="Research-backed skill routing is stronger when examples look like real user requests instead of abstract placeholders.",
                )

            realism_signals = ("when the user asks", "user says", "github", "convert", "validate", "inspect", "migrate")
            realism_hits = sum(1 for signal in realism_signals if signal in examples_text.lower())
            if realism_hits == 0:
                add(
                    rule="body.examples.synthetic",
                    category="Examples",
                    priority=Priority.MEDIUM,
                    message="Rewrite examples to sound like realistic user requests rather than template labels.",
                    rationale="Concrete, natural-language examples improve routing and reduce overfitting to synthetic phrasing.",
                )

        if not _has_any(body, ["constraints", "do not", "never", "refuse", "safety"]):
            add(
                rule="body.constraints.missing",
                category="Body",
                priority=Priority.LOW,
                message="Consider adding a 'Constraints / Safety' section (especially for destructive actions).",
            )

    # --- Repo integration checks (scripts/references/assets) ---
    scripts = _iter_files(skill_dir, "scripts")
    references = _iter_files(skill_dir, "references")
    assets = _iter_files(skill_dir, "assets")

    if scripts:
        script_names = [p.name for p in scripts]
        if not _has_any(body, ["scripts/"] + script_names):
            add(
                rule="repo.scripts.unreferenced",
                category="Repo Integration",
                priority=Priority.MEDIUM,
                message="You have `scripts/` files but SKILL.md doesn't mention how to use them.",
                rationale="Script-backed skills should document commands, inputs, outputs, and failure modes.",
            )

    for rel_dir, files in [("references", references), ("assets", assets)]:
        if files and not _has_any(body, [f"{rel_dir}/"] + [p.name for p in files]):
            add(
                rule=f"repo.{rel_dir}.unreferenced",
                category="Repo Integration",
                priority=Priority.LOW,
                message=f"You have `{rel_dir}/` files but SKILL.md doesn't reference them.",
                rationale="Linking on-disk resources keeps SKILL.md shorter and more maintainable.",
            )

    corpus = f"{description or ''}\n{body}"
    surfaces = _research_surface_count(corpus)
    focus_signals = _focus_language_count(corpus)
    if surfaces >= 4 and focus_signals <= 1:
        add(
            rule="repo.focus.overbundled",
            category="Scope",
            priority=Priority.MEDIUM,
            message="Narrow the first-pass package boundary or state explicit scope limits such as 'start with 2-3 focused surfaces'.",
            rationale="Research on skill usefulness favors smaller, targeted bundles over sprawling multi-surface packages.",
        )

    cases = _load_eval_cases(skill_dir)
    skill_name = name.strip().lower() if isinstance(name, str) else ""
    trigger_cases = [
        case for case in cases
        if case.get("should_trigger") is not False and str(case.get("category", "")).strip().lower() != "negative"
    ]
    if trigger_cases and skill_name:
        leaky = 0
        realistic = 0
        for case in trigger_cases:
            prompt = str(case.get("prompt", "")).strip().lower()
            if skill_name in prompt:
                leaky += 1
            if any(token in prompt for token in ("please", "can you", "help me", "github", "convert", "validate", "build", "inspect")):
                realistic += 1

        if leaky / len(trigger_cases) > 0.5:
            add(
                rule="evals.prompts.leaky",
                category="Evals",
                priority=Priority.MEDIUM,
                message="Rewrite positive eval prompts so most do not mention the skill name directly.",
                rationale="Leaky prompts can make evals look good without proving real-world routing quality.",
            )
        if realistic / len(trigger_cases) < 0.34:
            add(
                rule="evals.prompts.unrealistic",
                category="Evals",
                priority=Priority.MEDIUM,
                message="Make more eval prompts read like realistic user requests instead of benchmark labels.",
                rationale="Natural prompts are a better proxy for real skill invocation behavior.",
            )

    # Deterministic ordering: priority desc then category then rule
    suggestions.sort(key=lambda s: (-int(s.priority), s.category.lower(), s.rule))
    return suggestions


# -----------------------------
# Output formatting
# -----------------------------

def _priority_label(p: Priority) -> str:
    return {Priority.HIGH: "HIGH", Priority.MEDIUM: "MEDIUM", Priority.LOW: "LOW"}[p]


def _priority_icon(p: Priority, *, emoji: bool) -> str:
    if not emoji:
        return ""
    return {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}[p]


def print_text_report(doc: SkillDoc, suggestions: Sequence[Suggestion], *, emoji: bool = True) -> None:
    title = doc.frontmatter.get("name") if isinstance(doc.frontmatter.get("name"), str) else "unknown"
    print(f"\nSkill: {title}")
    print(f"Path:  {doc.skill_md_path}\n")
    print("=" * 78)

    if not suggestions:
        print("✅ No suggestions. SKILL.md looks solid.\n" if emoji else "No suggestions. SKILL.md looks solid.\n")
        return

    grouped: Dict[Priority, List[Suggestion]] = {Priority.HIGH: [], Priority.MEDIUM: [], Priority.LOW: []}
    for s in suggestions:
        grouped[s.priority].append(s)

    for prio in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
        if not grouped[prio]:
            continue
        icon = _priority_icon(prio, emoji=emoji)
        print(f"\n{icon} {_priority_label(prio)} PRIORITY ({len(grouped[prio])})")
        print("-" * 78)
        for idx, s in enumerate(grouped[prio], 1):
            print(f"\n{idx}. [{s.category}] {s.message}")
            if s.rationale:
                print(f"   Why: {s.rationale}")
            if s.example:
                print("\n   Example:\n")
                print(textwrap.indent(s.example, "   "))
    print("\n" + "=" * 78)

    print(
        textwrap.dedent(
            """\
            NEXT STEPS
            1) Review the suggestions above.
            2) Edit your SKILL.md to incorporate relevant improvements.
            3) Run analyze_skill.py to see how the score improves (if you have it).
            4) Test the skill with real use cases.
            5) Iterate based on performance.
            """
        ).strip()
    )
    print("")


def print_machine_report(suggestions: Sequence[Suggestion], *, fmt: str) -> None:
    payload = [
        {
            "rule": s.rule,
            "category": s.category,
            "priority": _priority_label(s.priority),
            "message": s.message,
            "rationale": s.rationale,
            "example": s.example,
        }
        for s in suggestions
    ]

    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif fmt == "yaml":
        print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
    else:
        raise ValueError(f"Unsupported format: {fmt}")


# -----------------------------
# CLI
# -----------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="upgrade_skill.py",
        description="Generate suggestions for improving an existing Codex skill (SKILL.md).",
    )
    p.add_argument("path", help="Path to a skill directory or to a SKILL.md file.")
    p.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--min-description-len",
        type=int,
        default=120,
        help="Minimum recommended description length before suggesting expansion (default: 120).",
    )
    p.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emoji in text output (useful for CI logs).",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if yaml is None:
        print(
            "ERROR: PyYAML is required to run upgrade_skill.py.\n\n"
            "Fix:\n"
            "  ~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/upgrade_skill.py <path/to/skill-dir-or-SKILL.md>\n",
            file=sys.stderr,
        )
        return 1

    try:
        doc = load_skill(args.path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    suggestions = generate_suggestions(doc, min_description_len=args.min_description_len)

    if args.format == "text":
        print_text_report(doc, suggestions, emoji=not args.no_emoji)
    else:
        print_machine_report(suggestions, fmt=args.format)

    # Exit code 2 if HIGH priority suggestions exist (useful for CI gating).
    if any(s.priority == Priority.HIGH for s in suggestions):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
