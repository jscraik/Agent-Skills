#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_COMMANDS = (
    "bash scripts/bootstrap-ask.sh --json",
    "python3 bin/ask repo status --json",
)

NORMATIVE_DOCS = (
    "README.md",
    "AGENTS.md",
    "Docs/agents/5-minute-success-path.md",
    "Docs/agents/README.md",
    "Docs/agents/16-agent-operating-contract.md",
    "Docs/agents/04-validation.md",
)


def validate_doc(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: missing normative first-contact doc"]
    text = path.read_text(encoding="utf-8")
    missing = [
        f"{path}: missing `{command}`"
        for command in REQUIRED_COMMANDS
        if command not in text
    ]
    return missing


def validate_docs(repo_root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in NORMATIVE_DOCS:
        failures.extend(validate_doc(repo_root / relative_path))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    failures = validate_docs(Path(args.repo_root).resolve())
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("ask bootstrap docs validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
