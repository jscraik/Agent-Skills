"""Static command metadata for the public ask wrapper."""

from __future__ import annotations

from typing import Dict, List, Tuple

VALID_TOPICS = ["repo", "skills", "reviewers", "runtime", "plugins", "evals", "graph", "mcp", "memory", "wiki", "workouts"]
VALID_ACTIONS = {
    "repo": ["status", "validate", "check-stability", "doctor", "closeout", "doctor-catalog", "provider-audit", "surface"],
    "skills": [
        "list",
        "budget",
        "capabilities",
        "codex-preview",
        "load-preview",
        "render-preview",
        "config",
        "inject-preview",
        "implicit-preview",
        "handles",
        "resolve",
        "parse",
        "proof",
        "prove",
        "explain",
        "doctor",
        "package",
        "conformance",
        "profiles",
        "events",
        "memory",
        "route",
        "goal",
        "improve",
        "starter",
        "sync",
        "audit",
        "external-review",
        "validate-skill-gate",
        "validate-openai-format",
        "validate-boundaries",
        "install",
        "fold",
        "init",
    ],
    "reviewers": ["resolve"],
    "runtime": ["surface", "budget"],
    "plugins": ["list", "status", "doctor", "sync-local-runtime", "init", "create", "install", "import", "harden", "uninstall"],
    "evals": ["run", "benchmark", "dashboard", "macro-report", "prepare-tessl-scenarios"],
    "graph": ["related", "find", "info", "chain", "list", "topics"],
    "mcp": ["sync"],
    "memory": ["list", "read", "search"],
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
        "ask skills doctor he-heartbeat --json --robot",
        "ask skills package he-heartbeat --json --robot",
        "ask skills package verify he-heartbeat --json --robot",
        "ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance --json --robot",
        "ask skills codex-preview --json --robot",
        "ask skills render-preview --context-window 200000 --json --robot",
        "ask skills config explain --json --robot",
        "ask skills profiles --json --robot",
        "ask skills profiles eval --json --robot",
        "ask skills events --json --robot",
        "ask skills memory search projection --json --robot",
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
        "ask evals dashboard",
        "ask evals macro-report --json --robot",
        "ask evals prepare-tessl-scenarios Skills/agent-ops/goal-governor --tessl-workspace skills-sdk --dry-run --json --robot",
    ],
    "graph": [
        "ask graph find security",
        "ask graph related skill-builder --depth 2",
        "ask graph info cli-spec",
    ],
    "mcp": [
        "ask mcp sync",
    ],
    "memory": [
        "ask memory list --json --robot",
        "ask memory search timeout --json --robot",
        "ask memory read .harness/memory/LEARNINGS.md --json --robot",
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
    ("skills", "capabilities"): [
        "ask skills capabilities --runtime-target codex --json --robot",
    ],
    ("skills", "codex-preview"): [
        "ask skills codex-preview --json --robot",
        "ask skills codex-preview",
    ],
    ("skills", "load-preview"): [
        "ask skills load-preview --json --robot",
    ],
    ("skills", "render-preview"): [
        "ask skills render-preview --json --robot",
        "ask skills render-preview --context-window 200000 --json --robot",
    ],
    ("skills", "config"): [
        "ask skills config explain --json --robot",
    ],
    ("skills", "inject-preview"): [
        "ask skills inject-preview '$browser' --json --robot",
    ],
    ("skills", "implicit-preview"): [
        "ask skills implicit-preview --command 'cat SKILL.md' --json --robot",
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
    ("skills", "doctor"): [
        "ask skills doctor he-heartbeat --json",
        "ask skills doctor Skills/agent-ops/autofix --strict --json",
    ],
    ("skills", "profiles"): [
        "ask skills profiles --json",
        "ask skills profiles authoring --json",
        "ask skills profiles eval --json",
    ],
    ("skills", "events"): [
        "ask skills events --json",
        "ask skills events eval_blocked --json",
    ],
    ("skills", "package"): [
        "ask skills package he-heartbeat --json",
        "ask skills package he-heartbeat --checkout-test --json",
        "ask skills package Plugins/harness-engineering/skills/he-heartbeat --strict --json",
        "ask skills package verify he-heartbeat --json",
        "ask skills package verify ./package.zip --expected-sha256 <sha256> --json",
    ],
    ("skills", "conformance"): [
        "ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance --json",
    ],
    ("skills", "memory"): [
        "ask skills memory list --json",
        "ask skills memory search projection --json",
        "ask skills memory read .harness/memory/LEARNINGS --json",
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
    ("memory", "list"): [
        "ask memory list --json",
        "ask memory list --source harness-memory --json",
    ],
    ("memory", "read"): [
        "ask memory read .harness/memory/LEARNINGS.md --json",
    ],
    ("memory", "search"): [
        "ask memory search timeout --json",
    ],
    ("skills", "audit"): [
        "ask skills audit Skills/backend-platform/cli-spec --level compat",
    ],
    ("skills", "external-review"): [
        "ask skills external-review Skills/backend-platform/cli-spec --json",
        "ask skills external-review Plugins/skill-factory/skills/code_quality_review/skill-builder --report-path artifacts/skill-reviews/skill-builder.json --json",
        "ask skills external-review Plugins/skill-factory/skills/code_quality_review/skill-builder --dashboard --json",
        "ask skills external-review Skills/backend-platform/cli-spec --include-snyk --dashboard --json",
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
    "memory": "memory",
    "mem": "memory",
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
    "capability": "capabilities",
    "capabilities": "capabilities",
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
