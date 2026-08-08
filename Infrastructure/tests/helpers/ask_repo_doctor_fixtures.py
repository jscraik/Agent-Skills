import json
from pathlib import Path


_RUNTIME_CARD = {
    "schema_version": 1,
    "card_id": "runtime-card-context7-codex",
    "created_at": "2026-05-25T09:00:00Z",
    "skill_handle": "context7",
    "command_handle": "$context7",
    "runtime_target": "codex",
    "runtime_status": "blocked_runtime",
    "runtime_session": {
        "session_id": "runtime-proof-context7-codex",
        "runtime_target": "codex",
        "runtime_status": "blocked_runtime",
        "created_at": "2026-05-25T09:00:00Z",
        "actor_type": "agent",
        "visibility_status": "user_observable",
    },
    "thread_runs": [],
    "turn_events": [],
    "artifacts": [],
    "evidence_receipts": [],
    "verifier_results": [],
    "permission_profile": {},
    "actor_type": "agent",
    "mutation_scope": "evidence_write",
    "visibility_status": "user_observable",
    "limitations": [],
    "recovery_plan": {
        "recovery_status": "blocked_runtime",
        "reason": "Codex runtime unavailable.",
        "next_commands": [],
        "preconditions": [],
        "permission_profile": {},
        "expected_outcome": "Runtime proof can be rerun.",
    },
}


def write_runtime_card(repo_root: Path, relative_path: str) -> None:
    card_path = repo_root / relative_path
    card_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_root = str(repo_root.resolve())
    payload = {
        **_RUNTIME_CARD,
        "workspace_root": workspace_root,
        "runtime_session": {
            **_RUNTIME_CARD["runtime_session"],
            "workspace_root": workspace_root,
        },
    }
    card_path.write_text(json.dumps(payload), encoding="utf-8")
