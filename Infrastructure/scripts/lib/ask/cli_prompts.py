from typing import List, Optional


def safe_input(prompt: str) -> Optional[str]:
    """Prompt with defensive handling of EOFError and KeyboardInterrupt."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n\nInteractive input cancelled by user.")
        raise SystemExit(130)


def prompt_choice(prompt: str, options: List[str]) -> str:
    """Prompt the operator for one option using 1-based indexing."""
    if not options:
        raise ValueError("prompt_choice requires at least one option")
    print(prompt)
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")
    while True:
        raw = (safe_input("> ") or "").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        if raw in options:
            return raw
        print(f"Please choose 1-{len(options)} or type an exact option value.")


def prompt_nonempty(prompt: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = (safe_input(prompt) or "").strip()
        if value:
            return value
        print("This value cannot be empty.")


def prompt_optional(prompt: str) -> str:
    """Prompt for an optional value (can be empty)."""
    return (safe_input(prompt) or "").strip()
