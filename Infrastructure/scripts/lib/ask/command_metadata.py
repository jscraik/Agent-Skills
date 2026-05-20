"""Static command metadata for the public ask wrapper."""

from __future__ import annotations

from typing import Dict, List, Tuple

VALID_TOPICS = ["repo", "skills", "reviewers", "runtime", "plugins", "evals", "graph", "mcp", "wiki", "workouts"]
VALID_ACTIONS = {
    "repo": ["status", "validate", "check-stability", "doctor", "closeout", "doctor-catalog", "provider-audit", "surface"],
    "skills": [
        "list",
        "budget",
        "handles",
        "resolve",
        "parse",
        "proof",
        "prove",
        "explain",
        "route",
        "goal",
        "improve",
        "starter",
        "sync",
        "audit",
        "external-review",
        "install",
        "fold",
        "init",
    ],
    "reviewers": ["resolve"],
    "runtime": ["surface", "budget"],
    "plugins": ["list", "status", "doctor", "sync-local-runtime", "init", "create", "install", "import", "harden", "uninstall"],
    "evals": ["run", "benchmark", "dashboard"],
    "graph": ["related", "find", "info", "chain", "list", "topics"],
    "mcp": ["sync"],
    "wiki": ["lint", "ingest", "add", "query", "add-asset"],
    "workouts": ["list", "run", "score", "promote"],
}

TOPIC_EXAMPLES: Dict[str, List[str]] = {
    "repo": [
        "ask repo doctor --json --robot",
        "ask repo closeout --changed --json --robot",
        "ask repo validate --ephemeral",
        "ask repo status",
        "ask repo surface --json",
        "ask repo doctor-catalog --strict",
    ],
    "skills": [
        "ask skills improve \"fix PR review comments faster\" --json --robot",
        "ask skills explain he-heartbeat --json --robot",
        "ask skills prove he-heartbeat --json --robot",
        "ask skills list",
        "ask skills budget --json",
        "ask skills handles --check --json",
        "ask skills resolve he-heartbeat --json",
        (
            "ask skills parse "
            "\"use $skill-builder to validate $he-heartbeat with @skillinspector\" --json"
        ),
        "ask skills proof he-heartbeat --json",
        "ask skills route \"find the right security skill\"",
        "ask skills audit Skills/backend-platform/cli-spec --level strict",
        "ask skills external-review Skills/backend-platform/cli-spec --json",
    ],
    "reviewers": [
        "ask reviewers resolve skillinspector --json",
    ],
    "runtime": [
        "ask runtime surface --json",
        "ask runtime budget --json",
    ],
    "plugins": [
        "ask plugins list",
        "ask plugins status plugin-factory",
        "ask plugins harden Plugins/plugin-factory",
    ],
    "evals": [
        "ask evals run Skills/backend-platform/cli-spec --mode smoke",
        "ask evals run Skills/backend-platform/cli-spec --mode release",
        "ask evals dashboard",
    ],
    "graph": [
        "ask graph find security",
        "ask graph related skill-builder --depth 2",
        "ask graph info cli-spec",
    ],
    "mcp": [
        "ask mcp sync",
    ],
    "wiki": [
        "ask wiki lint",
        "ask wiki query \"1password signing\"",
    ],
    "workouts": ["ask workouts list --json"],
}

COMMAND_EXAMPLES: Dict[Tuple[str, str], List[str]] = {
    ("repo", "doctor"): [
        "ask repo doctor --json",
        "ask repo doctor --robot --json",
    ],
    ("repo", "closeout"): [
        "ask repo closeout --changed --json",
        "ask repo closeout --changed --robot --json",
    ],
    ("repo", "doctor-catalog"): [
        "ask repo doctor-catalog",
    ],
    ("repo", "provider-audit"): [
        "ask repo provider-audit",
    ],
    ("repo", "surface"): [
        "ask repo surface --json",
        "ask repo surface --strict --json",
    ],
    ("skills", "budget"): [
        "ask skills budget",
    ],
    ("skills", "handles"): [
        "ask skills handles --json",
    ],
    ("skills", "resolve"): [
        "ask skills resolve he-heartbeat --json",
    ],
    ("skills", "parse"): [
        (
            "ask skills parse "
            "\"use $skill-builder to validate $he-heartbeat with @skillinspector\" --json"
        ),
    ],
    ("skills", "proof"): [
        "ask skills proof he-heartbeat --json",
        "ask skills sync --scope workspace --projection rooted --json",
        "ask skills sync --scope user --projection rooted --json",
    ],
    ("skills", "prove"): [
        "ask skills prove he-heartbeat --json",
    ],
    ("skills", "explain"): [
        "ask skills explain autofix --json",
    ],
    ("reviewers", "resolve"): [
        "ask reviewers resolve skillinspector --json",
    ],
    ("runtime", "surface"): [
        "ask runtime surface --json",
    ],
    ("runtime", "budget"): [
        "ask runtime budget",
    ],
    ("skills", "audit"): [
        "ask skills audit Skills/backend-platform/cli-spec --level compat",
    ],
    ("skills", "external-review"): [
        "ask skills external-review Skills/backend-platform/cli-spec --json",
        "ask skills external-review Plugins/harness-engineering/skills/goal-governor --json",
        "ask skills external-review Skills/backend-platform/cli-spec --skip-tessl-review --json",
    ],
    ("skills", "goal"): [
        "ask skills goal \"implement auth safely\"",
    ],
    ("skills", "improve"): [
        "ask skills improve \"make agents better at fixing PR review comments\" --json",
    ],
    ("skills", "route"): [
        "ask skills route \"debug flaky tests\"",
    ],
    ("skills", "install"): [
        "ask skills install https://github.com/<owner>/<repo>/tree/main/.codex/skills/<skill> --remediate",
    ],
    ("wiki", "add-asset"): [
        "ask wiki add-asset ./tmp/screenshot.png --title \"Checkout\" --summary \"Reference layout\"",
        "ask wiki add-asset --interactive",
    ],
}

ACTION_TO_TOPICS: Dict[str, List[str]] = {
    action: []
    for actions in VALID_ACTIONS.values()
    for action in actions
}
for _topic, _actions in VALID_ACTIONS.items():
    for _action in _actions:
        ACTION_TO_TOPICS[_action].append(_topic)

FUZZY_MATCHES = {
    "skill": "skills",
    "skil": "skills",
    "skils": "skills",
    "repo": "repo",
    "rep": "repo",
    "plugin": "plugins",
    "plug": "plugins",
    "eval": "evals",
    "evaluation": "evals",
    "mcp": "mcp",
    "mc": "mcp",
    "wiki": "wiki",
    "wik": "wiki",
    "wili": "wiki",
    "aud": "audit",
    "audt": "audit",
    "sync": "sync",
    "syn": "sync",
    "install": "install",
    "instal": "install",
    "list": "list",
    "ls": "list",
    "resolve": "resolve",
    "prove": "prove",
    "explain": "explain",
    "handles": "handles",
    "init": "init",
    "create": "init",
    "harden": "harden",
    "fold": "fold",
    "merge": "fold",
    "search": "find",
    "query": "find",
    "related": "related",
    "rel": "related",
    "neighbors": "related",
    "info": "info",
    "show": "info",
    "details": "info",
    "chain": "chain",
    "path": "chain",
    "route": "chain",
    "goal": "goal",
    "improve": "improve",
    "closeout": "closeout",
    "finish": "closeout",
    "doctor": "doctor",
    "catalog": "doctor-catalog",
    "provider": "provider-audit",
    "provider-audit": "provider-audit",
    "surface": "surface",
    "budget": "budget",
    "topics": "topics",
    "tags": "topics",
    "categories": "topics",
    "ingest": "ingest",
    "import": "ingest",
    "add": "add",
    "triage": "add",
    "lookup": "query",
    "asset": "add-asset",
    "add-asset": "add-asset",
    "lint": "lint",
    "check": "lint",
}
