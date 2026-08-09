"""Small shared token helpers for package-contract checks."""
from __future__ import annotations


def _token_set(text: str) -> set[str]:
    """Return normalized natural-language tokens without broad regex parsing."""
    punctuation = ".,:;!?()[]{}\"'<>"
    return {
        token.strip(punctuation).lower()
        for token in text.replace("/", " ").replace("-", " ").split()
        if token.strip(punctuation)
    }


__all__ = ["_token_set"]
