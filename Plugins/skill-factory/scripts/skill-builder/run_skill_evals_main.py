"""Public entrypoint for the modular skill evaluation workflow."""

from run_skill_evals_workflow import *  # noqa: F403


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run selected skill evaluation cases and return the workflow exit code."""
    return execute_eval_workflow(argv)


__all__ = [name for name in globals() if not name.startswith("__")]
