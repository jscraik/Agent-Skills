#!/usr/bin/env python3
"""
init_skill.py

Create a new Agent Skill folder with a high-signal SKILL.md scaffold plus optional
resources (references/, scripts/, assets/, workflows/) and agents/openai.yaml.

Design goals:
- Progressive disclosure: keep SKILL.md short; push depth into references/ and scripts/.
- Discovery: description should read like routing logic (use when / don't use when / outputs / success).
- Safety: no secrets in repo; script-backed skills should be offline by default.

Usage:
    init_skill.py <skill-name> --category <category> [options]
    init_skill.py <skill-name> --path <path> [options]

Examples:
    init_skill.py my-new-skill --category utilities
    init_skill.py my-new-skill --category backend --resources scripts,references,assets
    init_skill.py my-router-skill --category product --structure router
    init_skill.py my-script-skill --category utilities --run-type python
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional

TARGET_NAME_LIMITS = {"portable": 64, "codex": 100, "claude": 64}
TARGET_DESCRIPTION_LIMITS = {"portable": 1024, "codex": 500, "claude": 1024}
DEFAULT_TARGET = "codex"

CATEGORIES = {"github", "frontend", "apple", "backend", "product", "utilities"}

ALLOWED_RESOURCES = {"scripts", "references", "assets", "workflows"}
STRUCTURES = {"simple", "router"}
VALID_LIFECYCLE_STATES = ("incubating", "active", "maintenance", "deprecated")
VALID_MATURITY_LEVELS = ("experimental", "validated", "canonical")


SKILL_TEMPLATE_SIMPLE = """---
name: {skill_name}
description: "{description}"
metadata:
  lifecycle_state: {lifecycle_state}
  maturity: {maturity}
  owner: {owner}
  review_cadence: {review_cadence}
  last_reviewed: {last_reviewed}
  metadata_source: frontmatter
---

# {skill_title}

This scaffold starts in `{lifecycle_state}` state with `{maturity}` maturity. Replace the starter guidance below before treating it as active or broadly reusable.

## Working agreement
- Follow the repo's `AGENTS.md` (map, not a megadoc).
- For long runs, also follow `~/.codex/instructions/shell-skills-compaction.md` if present.
- Artifact boundary:
  - Local CLI: write deliverables to `./artifacts/`
  - Hosted shell: write deliverables to `/mnt/data/`

## When to use
- Primary triggers:
  - Replace with the real user ask this skill should own.
- Non-triggers (route elsewhere):
  - Replace with the neighboring asks this skill should reject or reroute.

## Inputs
- Assumptions:
  - Replace with the minimum safe assumptions for this skill.
- Replace with the concrete files, repos, APIs, schemas, or constraints the finished skill will need.
- Ask clarifying questions only for genuine gaps.

## Outputs
- Replace with the concrete outputs, paths, and formats the skill should produce.
- Always write artifacts to `./artifacts/` (local) or `/mnt/data/` (hosted).

## Constraints and safety
- Redact secrets/PII by default.
- If networking is required: specify a minimal domain allowlist and gate it behind explicit opt-in.
- Destructive actions require explicit confirmation; prefer dry-run first.

## Principles
- Replace with 2–6 bullets capturing the mental model for this skill.
- Adapt execution and output shape to context; avoid rigid one-size-fits-all responses.

## Workflow
1) Replace with the smallest reliable workflow for this skill.
2) Prefer progressive disclosure:
   - Put deep docs in `references/` and link to them.
   - Put reusable automation in `scripts/` and reference it here.
   - Put templates/boilerplate in `assets/`.
3) End by writing artifacts + listing changed files/commands.

## Validation
- Replace with the commands, tests, or checks that prove this skill is safe to use.
- Fail fast: if a gate fails, stop and report the failure before continuing.
- For non-trivial skills, add `references/evals.yaml` with at least:
  - happy-path
  - edge-case
  - failure-mode

## Gotchas
- Replace with the recurring mistake, misconception, or failure pattern this skill should call out early.

## See Also
| Skill | When to use |
|---|---|
| `adjacent-skill-name-1` | Replace with a real nearby skill this one is commonly confused with. |
| `adjacent-skill-name-2` | Replace with another real related skill in the local graph. |

**Topic map:** `[[topic-name]]`

## Anti-patterns
- ❌ Replace with the common pitfalls and what not to do.

## Examples
- Triggering prompt: "Replace with a realistic triggering prompt."
- Non-triggering prompt: "Replace with a realistic non-triggering prompt."
"""


SKILL_TEMPLATE_ROUTER = """---
name: {skill_name}
description: "{description}"
metadata:
  lifecycle_state: {lifecycle_state}
  maturity: {maturity}
  owner: {owner}
  review_cadence: {review_cadence}
  last_reviewed: {last_reviewed}
  metadata_source: frontmatter
---

# {skill_title}

This router scaffold starts in `{lifecycle_state}` state with `{maturity}` maturity. Replace the starter routes before treating it as active or reusable.

## Working agreement
- Follow the repo's `AGENTS.md` (map, not a megadoc).
- For long runs, also follow `~/.codex/instructions/shell-skills-compaction.md` if present.
- Artifact boundary:
  - Local CLI: write deliverables to `./artifacts/`
  - Hosted shell: write deliverables to `/mnt/data/`

## When to use
- This is a **router skill**: it asks one intake question and routes to a workflow in `workflows/`.
- Primary triggers:
  - Replace with the routing asks this skill should own.
- Non-triggers (route elsewhere):
  - Replace with the nearby asks this router should reject or hand off.

## Inputs
- Replace with the minimum user signal you need before routing.
- Ask follow-up questions only when the route cannot be selected safely.

## Outputs
- Replace with the routed output contract, including paths and formats.
- Always write artifacts to `./artifacts/` (local) or `/mnt/data/` (hosted).

## Constraints and safety
- Redact secrets/PII by default.
- Prefer read-only checks before mutating actions.
- Destructive actions require explicit confirmation.

## Principles
- Route with the smallest sufficient question.
- Prefer deterministic route criteria over intuition.
- Keep route explanations concise and evidence-based.

## Intake
Replace this line with the one concise routing question the user should answer.

## Routes
| Response | Workflow |
|----------|----------|
| 1 | `workflows/option-1.md` |
| 2 | `workflows/option-2.md` |
| 3 | `workflows/option-3.md` |

## Workflow
1) Ask one intake question and capture the response.
2) Match the response to the route table and select one workflow.
3) Read the chosen workflow fully, then execute it exactly.
4) End with created/modified files, commands run, and route rationale.

## Validation
- Validate route selection before execution.
- Fail fast: if route criteria are ambiguous or checks fail, stop and ask for clarification.
- Verify outputs match the chosen workflow contract.

## Gotchas
- Replace with the routing misconception or common failure pattern this router should surface early.

## See Also
| Skill | When to use |
|---|---|
| `adjacent-router-or-skill-1` | Replace with a real nearby route or skill this router should defer to when appropriate. |
| `adjacent-router-or-skill-2` | Replace with another real related route or skill in the local graph. |

**Topic map:** `[[topic-name]]`

## References map
Prefer pointers over pasted docs.
- `references/` for deep docs, contracts, and evals.

## Anti-patterns
- ❌ Asking multiple intake questions before attempting routing.
- ❌ Executing multiple routes in parallel without explicit user approval.
- ❌ Proceeding when route criteria are ambiguous.

## Examples
- Triggering prompt: "Replace with a realistic routing request."
- Non-triggering prompt: "Replace with a realistic non-routing request."
"""


PYTHON_RUNNER_TEMPLATE = '''#!/usr/bin/env python3
"""
scripts/run.py — script entrypoint scaffold for %(skill_name)s

Security / safety baseline:
- Offline by default. If networking is required, gate behind --allow-network and document allowed domains.
- Never echo secrets (do not print os.environ / token values).
- Destructive actions require explicit confirmation. Prefer --dry-run by default.

Replace the TODOs with your actual implementation.
"""

from __future__ import annotations

import argparse


def require_confirm(*, confirm: bool, dry_run: bool, message: str) -> None:
    if dry_run:
        print(f"[DRY RUN] {message}")
        return
    if not confirm:
        raise SystemExit("Refusing to perform a destructive action without --confirm. Re-run with --dry-run to preview.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill helper entrypoint for %(skill_name)s")
    parser.add_argument("--dry-run", action="store_true", help="Preview intended actions without making changes")
    parser.add_argument("--confirm", action="store_true", help="Required to run destructive actions (delete/overwrite/remote writes)")
    parser.add_argument("--allow-network", action="store_true", help="Opt-in to network operations (default: offline)")
    args = parser.parse_args()

    # TODO: implement the real behavior for this skill.
    if not args.allow_network:
        # Keep network code paths disabled unless explicitly enabled.
        pass

    # Example destructive action:
    # require_confirm(confirm=args.confirm, dry_run=args.dry_run, message="Would delete ./build and recreate it")
    # if not args.dry_run:
    #     ...

    print("TODO: implement skill script")


if __name__ == "__main__":
    main()
'''
DOCKERFILE_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app
COPY . /app

# If you add dependencies, include a requirements.txt and uncomment:
# RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scripts/run.py", "--help"]
"""


AGENTS_OPENAI_YAML_TEMPLATE = """# OpenAI Agents SDK Configuration
# This file configures how the skill appears in Codex and any MCP dependencies.
#
# interface:
#   display_name: "Optional user-facing name"
#   short_description: "Optional user-facing description"
#   icon_small: "./assets/small-logo.svg"    # 16x16px SVG with currentColor fill
#   icon_large: "./assets/large-logo.png"    # 100x100px PNG/JPG
#   brand_color: "#3B82F6"
#   default_prompt: "Optional surrounding prompt"
#
# policy:
#   allow_implicit_invocation: true
#
# dependencies:
#   tools:
#     - type: "mcp"
#       value: "serverName"
#       description: "MCP server description"
#       transport: "streamable_http"
#       url: "https://example.com/mcp"
"""


WORKFLOW_PLACEHOLDER = """# Workflow: {title}

## Goal
TODO

## Steps
1) TODO

## Validation
- TODO

## Outputs
- TODO (write to ./artifacts/ or /mnt/data/)

## Notes / anti-patterns
- TODO
"""


def normalize_skill_name(raw: str) -> str:
    normalized = raw.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_csv_list(raw: str, allowed: set[str]) -> List[str]:
    if not raw:
        return []
    items = [i.strip() for i in raw.split(",") if i.strip()]
    invalid = sorted({i for i in items if i not in allowed})
    if invalid:
        allowed_str = ", ".join(sorted(allowed))
        raise SystemExit(f"[ERROR] Unknown value(s): {', '.join(invalid)}. Allowed: {allowed_str}")
    out: List[str] = []
    seen: set[str] = set()
    for i in items:
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out


def find_repo_root(start: Path) -> Path:
    """Find the repo root by walking upward until a `.git` entry is found."""
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback for unusual layouts: keep historical behavior for this repo.
    try:
        return Path(__file__).resolve().parents[3]
    except Exception:
        return start.resolve().parent if start.is_file() else start.resolve()


def create_resource_dirs(*, skill_dir: Path, skill_title: str, resources: List[str], include_examples: bool) -> None:
    repo_root = find_repo_root(Path(__file__).resolve().parent)
    template_contract = repo_root / "templates" / "contract.yaml"
    template_evals = repo_root / "templates" / "evals.yaml"

    for r in resources:
        (skill_dir / r).mkdir(exist_ok=True)

    if "references" in resources:
        plan_md = skill_dir / "references" / "plan.md"
        if not plan_md.exists():
            plan_md.write_text(
                f"# Plan for {skill_title}\n\n"
                "TODO: Paste the output from `$create-plan` (if available) or write the plan used to build this skill.\n",
                encoding="utf-8",
            )

        if template_contract.exists():
            target_contract = skill_dir / "references" / "contract.yaml"
            if not target_contract.exists():
                target_contract.write_text(template_contract.read_text(encoding="utf-8"), encoding="utf-8")

        if template_evals.exists():
            target_evals = skill_dir / "references" / "evals.yaml"
            if not target_evals.exists():
                target_evals.write_text(template_evals.read_text(encoding="utf-8"), encoding="utf-8")

    if "workflows" in resources and include_examples:
        for idx in range(1, 4):
            wf = skill_dir / "workflows" / f"option-{idx}.md"
            if not wf.exists():
                wf.write_text(WORKFLOW_PLACEHOLDER.format(title=f"Option {idx}"), encoding="utf-8")


def init_skill(
    *,
    skill_name: str,
    out_dir: Path,
    structure: str,
    resources: List[str],
    include_examples: bool,
    run_type: str,
    target: str,
    dry_run: bool,
    description: str,
    owner: str,
    review_cadence: str,
    last_reviewed: str,
    lifecycle_state: str,
    maturity: str,
) -> Optional[Path]:
    skill_dir = out_dir.resolve() / skill_name
    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}", file=sys.stderr)
        return None

    if dry_run:
        print("[DRY RUN] Would create:")
        print(f"  {skill_dir}/")
        print("  SKILL.md")
        for r in resources:
            print(f"  {r}/")
        print("  agents/openai.yaml")
        if run_type in ("python", "container"):
            print("  scripts/run.py")
        if run_type == "container":
            print("  Dockerfile")
        return skill_dir

    skill_dir.mkdir(parents=True, exist_ok=False)
    print(f"[OK] Created skill directory: {skill_dir}")

    skill_title = title_case_skill_name(skill_name)

    template = SKILL_TEMPLATE_ROUTER if structure == "router" else SKILL_TEMPLATE_SIMPLE
    content = template.format(
        skill_name=skill_name,
        skill_title=skill_title,
        description=description,
        owner=owner,
        review_cadence=review_cadence,
        last_reviewed=last_reviewed,
        lifecycle_state=lifecycle_state,
        maturity=maturity,
    )

    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    print("[OK] Created SKILL.md")

    if resources:
        create_resource_dirs(skill_dir=skill_dir, skill_title=skill_title, resources=resources, include_examples=include_examples)
        for r in resources:
            print(f"[OK] Created {r}/")

    agents_dir = skill_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / "openai.yaml").write_text(AGENTS_OPENAI_YAML_TEMPLATE, encoding="utf-8")
    print("[OK] Created agents/openai.yaml")

    if run_type in ("python", "container"):
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        run_py = scripts_dir / "run.py"
        if not run_py.exists():
            run_py.write_text(PYTHON_RUNNER_TEMPLATE % {"skill_name": skill_name}, encoding="utf-8")
            try:
                run_py.chmod(run_py.stat().st_mode | 0o111)
            except Exception:
                pass
            print("[OK] Created scripts/run.py")

    if run_type == "container":
        dockerfile = skill_dir / "Dockerfile"
        if not dockerfile.exists():
            dockerfile.write_text(DOCKERFILE_TEMPLATE, encoding="utf-8")
            print("[OK] Created Dockerfile")

    # Hint users about description limits for the chosen target.
    print("\nNotes:")
    print(f"- Target '{target}' description max: {TARGET_DESCRIPTION_LIMITS[target]} chars (single line).")

    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    next_steps = [
        "Replace the starter trigger, workflow, validation, and example text in SKILL.md with the real skill contract.",
        "Keep SKILL.md as a map; put depth in references/ and scripts/.",
    ]
    if run_type != "instruction":
        next_steps.append("Implement scripts/run.py and document usage in SKILL.md.")
    next_steps.extend(
        [
            "Configure agents/openai.yaml for UI metadata and MCP dependencies.",
            "Run validation when ready (quick_validate.py, skill_gate.py, evals).",
        ]
    )
    for i, step in enumerate(next_steps, 1):
        print(f"{i}. {step}")

    return skill_dir


def get_auto_resources(*, run_type: str, structure: str, minimal: bool, explicit: Optional[List[str]]) -> List[str]:
    if minimal:
        return []
    if explicit is not None:
        return explicit

    resources = {"references", "assets"}
    if structure == "router":
        resources.add("workflows")
    if run_type in ("python", "container"):
        resources.add("scripts")
    return sorted(resources)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Create a new skill directory with a SKILL.md template.")
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--target", choices=sorted(TARGET_NAME_LIMITS.keys()), default=DEFAULT_TARGET, help="Target environment (controls name/description limits)")
    parser.add_argument("--category", choices=sorted(CATEGORIES), help="Category folder under the repo")
    parser.add_argument("--path", help="Output directory for the skill (alternative to --category)")
    parser.add_argument("--description", required=True, help="Concrete discovery description for the skill frontmatter")
    parser.add_argument("--owner", required=True, help="Primary maintainer or owner string for lifecycle governance")
    parser.add_argument("--review-cadence", required=True, help="Concrete review cadence such as monthly or quarterly")
    parser.add_argument(
        "--last-reviewed",
        default=date.today().isoformat(),
        help="ISO date for the most recent lifecycle review (defaults to today)",
    )
    parser.add_argument("--lifecycle-state", choices=VALID_LIFECYCLE_STATES, default="incubating", help="Initial lifecycle state for the new skill")
    parser.add_argument("--maturity", choices=VALID_MATURITY_LEVELS, default="experimental", help="Initial maturity level for the new skill")
    parser.add_argument("--structure", choices=sorted(STRUCTURES), default="simple", help="Skill structure: simple (default) or router")
    parser.add_argument("--run-type", choices=["instruction", "python", "container"], default="instruction", help="Scaffold type: instruction-only, python script-backed, or container-backed")
    parser.add_argument("--resources", default="", help="Explicit comma-separated list: scripts,references,assets,workflows")
    parser.add_argument("--minimal", action="store_true", help="Minimal structure: only SKILL.md and agents/openai.yaml")
    parser.add_argument("--examples", action="store_true", help="Create example files in references/ and workflows/ where applicable")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without writing files")
    args = parser.parse_args(list(argv) if argv is not None else None)

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.", file=sys.stderr)
        return 1

    max_name_len = TARGET_NAME_LIMITS[args.target]
    if len(skill_name) > max_name_len:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). Maximum for target '{args.target}' is {max_name_len}.",
            file=sys.stderr,
        )
        return 1

    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    explicit_resources = parse_csv_list(args.resources, ALLOWED_RESOURCES) if args.resources else None
    resources = get_auto_resources(run_type=args.run_type, structure=args.structure, minimal=args.minimal, explicit=explicit_resources)

    if args.examples and not resources:
        print("[ERROR] --examples requires resources (don't use --minimal without --resources).", file=sys.stderr)
        return 1

    if bool(args.path) == bool(args.category):
        print("[ERROR] Use exactly one of --category or --path.", file=sys.stderr)
        return 1

    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)

    if args.category:
        out_dir = repo_root / args.category
    else:
        out_dir = Path(args.path).expanduser().resolve()

    # Reject flat symlink view if present (repo-specific guardrail).
    skills_symlink = (repo_root / "skills").resolve()
    resolved_out = out_dir.resolve()
    if resolved_out == skills_symlink or str(resolved_out).startswith(str(skills_symlink) + "/"):
        print("[ERROR] Do not create skills under the flat skills/ symlink view.", file=sys.stderr)
        print("       Use a canonical category folder path instead.", file=sys.stderr)
        return 1

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {out_dir}")
    print(f"   Target: {args.target}")
    print(f"   Structure: {args.structure}")
    print(f"   Run type: {args.run_type}")
    if args.resources:
        print(f"   Resources: {', '.join(resources)} (explicit)")
    elif args.minimal:
        print("   Resources: minimal (none)")
    else:
        print(f"   Resources: {', '.join(resources)} (auto-selected)")
    if args.examples:
        print("   Examples: enabled")
    if args.dry_run:
        print("   Dry run: enabled")
    print()

    result = init_skill(
        skill_name=skill_name,
        out_dir=out_dir,
        structure=args.structure,
        resources=resources,
        include_examples=args.examples,
        run_type=args.run_type,
        target=args.target,
        dry_run=args.dry_run,
        description=args.description,
        owner=args.owner,
        review_cadence=args.review_cadence,
        last_reviewed=args.last_reviewed,
        lifecycle_state=args.lifecycle_state,
        maturity=args.maturity,
    )

    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
