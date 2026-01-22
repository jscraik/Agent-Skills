#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --category <category> [--resources scripts,references,assets] [--examples]
    init_skill.py <skill-name> --path <path> [--resources scripts,references,assets] [--examples]

Examples:
    init_skill.py my-new-skill --category utilities
    init_skill.py my-new-skill --category backend --resources scripts,references
    init_skill.py my-api-helper --category product --resources scripts --examples
    init_skill.py custom-skill --path /custom/location
"""

import argparse
import re
import sys
from pathlib import Path

TARGET_NAME_LIMITS = {"portable": 64, "codex": 100, "claude": 64}
DEFAULT_TARGET = "portable"
ALLOWED_RESOURCES = {"scripts", "references", "assets"}
CATEGORIES = {"github", "frontend", "apple", "backend", "product", "utilities"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: One-line description of WHAT this skill does and WHEN to use it (trigger contexts + keywords)."
---

# {skill_title}

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## When to Use
- TODO: List triggers/symptoms that should activate this skill.
- Reminder: In Codex, only `name` + `description` are loaded for discovery; keep trigger keywords in the description too.

## Inputs
- TODO: Required information, files, repos, constraints, and assumptions.
- Ask clarifying questions only for genuine gaps.

## Outputs
- TODO: Concrete deliverables (files changed, scripts run, reports, commands, PR text, etc.).

## Principles
- TODO: 2-6 bullets capturing the core mental model / philosophy (why this approach works).
- Keep this lightweight; move deep context to references/.

## Procedure
1) TODO: Provide the smallest reliable workflow.
2) Prefer progressive disclosure:
   - Put heavy reference material in `references/` and link to it.
   - Put reusable automation in `scripts/` and reference it from here.
3) Include at least one realistic example (short, high-signal).

## Validation
- TODO: Define how to verify correctness (tests, commands, file checks).
- Add `references/evals.yaml` with at least 3 cases (happy-path / edge-case / failure-mode).

## Anti-patterns
- TODO: Common pitfalls + explicit "do not do X" guidance.

## Constraints
- Redact secrets/PII by default.
- Keep `name` and `description` single-line YAML scalars (quote if needed).
- Do not add new dependencies without explicit user approval.

## Resources (optional)
- `references/`: deep docs loaded only when needed
- `scripts/`: executable helpers (more reliable + token-efficient than inline code)
- `assets/`: templates/static files copied into outputs
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images
"""

def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output Codex produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""

PYTHON_RUNNER_TEMPLATE = '''#!/usr/bin/env python3
"""
Skill script entrypoint for {skill_name}.

Keep scripts deterministic and safe:
- Do not print secrets or env vars
- Prefer --dry-run modes for destructive operations
- Avoid network assumptions unless explicitly enabled
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill helper entrypoint for {skill_name}")
    parser.add_argument("--dry-run", action="store_true", help="Print intended actions without making changes")
    args = parser.parse_args()

    # TODO: implement the real behavior for this skill.
    if args.dry_run:
        print("[DRY RUN] TODO: describe intended actions")
        return

    print("TODO: implement {skill_name} script")


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



def normalize_skill_name(skill_name):
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples):
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=True)
        if resource == "scripts":
            if include_examples:
                example_script = resource_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
                example_script.chmod(0o755)
                print("[OK] Created scripts/example.py")
            else:
                print("[OK] Created scripts/")
        elif resource == "references":
            if include_examples:
                example_reference = resource_dir / "api_reference.md"
                example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
                print("[OK] Created references/api_reference.md")
            else:
                print("[OK] Created references/")
        elif resource == "assets":
            if include_examples:
                example_asset = resource_dir / "example_asset.txt"
                example_asset.write_text(EXAMPLE_ASSET)
                print("[OK] Created assets/example_asset.txt")
            else:
                print("[OK] Created assets/")


def init_skill(skill_name, path, resources, include_examples, run_type="instruction"):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories
        run_type: 'instruction', 'python', or 'container' (scaffolds script/container stubs)

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"[ERROR] Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / "SKILL.md"
    try:
        if "Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md" not in skill_content:
            print("[ERROR] SKILL.md template missing GOLD compliance instruction.")
            return None
        skill_md_path.write_text(skill_content)
        print("[OK] Created SKILL.md")
    except Exception as e:
        print(f"[ERROR] Error creating SKILL.md: {e}")
        return None

    # Create resource directories if requested
    if resources:
        try:
            create_resource_dirs(skill_dir, skill_name, skill_title, resources, include_examples)
        except Exception as e:
            print(f"[ERROR] Error creating resource directories: {e}")
            return None

    # Scaffold run-type helpers (optional)
    if run_type != "instruction":
        try:
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)

            run_py = scripts_dir / "run.py"
            if not run_py.exists():
                run_py.write_text(PYTHON_RUNNER_TEMPLATE.format(skill_name=skill_name))
                try:
                    # Best-effort: make executable on POSIX systems.
                    run_py.chmod(run_py.stat().st_mode | 0o111)
                except Exception:
                    pass
                print("[OK] Created scripts/run.py")

            if run_type == "container":
                dockerfile = skill_dir / "Dockerfile"
                if not dockerfile.exists():
                    dockerfile.write_text(DOCKERFILE_TEMPLATE)
                    print("[OK] Created Dockerfile")
        except Exception as e:
            print(f"[ERROR] Error scaffolding run-type '{run_type}': {e}")
            return None


    # Print next steps
    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    if resources:
        if include_examples:
            print("2. Customize or delete the example files in scripts/, references/, and assets/")
        else:
            print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")
    print("3. Run the validator when ready to check the skill structure")

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument(
        "--target",
        choices=sorted(TARGET_NAME_LIMITS.keys()),
        default=DEFAULT_TARGET,
        help="Target environment (controls name/description limits): portable (Agent Skills spec subset), codex (OpenAI Codex), claude (Claude Code).",
    )
    parser.add_argument("--path", help="Output directory for the skill")
    parser.add_argument(
        "--category",
        choices=sorted(CATEGORIES),
        help="Category folder under the repo (github, frontend, apple, backend, product, utilities)",
    )
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--run-type",
        choices=["instruction", "python", "container"],
        default="instruction",
        help="Scaffold type: instruction-only (default), python script-backed (scripts/run.py), or container-backed (Dockerfile + scripts/run.py).",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    max_name_len = TARGET_NAME_LIMITS[args.target]
    if len(skill_name) > max_name_len:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum for target '{args.target}' is {max_name_len} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    if args.run_type != "instruction":
        if "scripts" not in resources:
            resources.append("scripts")
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)

    if args.path and args.category:
        print("[ERROR] Use either --path or --category, not both.")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parents[3]
    if args.category:
        path = repo_root / args.category
    elif args.path:
        path = Path(args.path)
    else:
        print("[ERROR] Missing required option: --category or --path.")
        sys.exit(1)

    # Reject the flat symlink view to keep skills in canonical category folders.
    skills_symlink = (repo_root / "skills").resolve()
    resolved_path = path.resolve()
    if resolved_path == skills_symlink or str(resolved_path).startswith(str(skills_symlink) + "/"):
        print("[ERROR] Do not create skills under the flat skills/ symlink view.")
        print("       Use --category or a category folder path instead.")
        sys.exit(1)

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
        if args.examples:
            print("   Examples: enabled")
    else:
        print("   Resources: none (create as needed)")
    print()

    result = init_skill(skill_name, path, resources, args.examples, run_type=args.run_type)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
