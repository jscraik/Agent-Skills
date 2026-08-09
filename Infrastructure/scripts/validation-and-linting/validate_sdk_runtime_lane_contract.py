#!/usr/bin/env python3
"""Validate the Skills SDK runtime lane contract stays explicit."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "Docs/agents/25-sdk-runtime-lane-contract.md"
README_PATH = ROOT / "Docs/agents/README.md"
VALIDATION_PATH = ROOT / "Docs/agents/04-validation.md"
EVALS_PATH = ROOT / "Infrastructure/scripts/lib/ask/commands/evals.py"

REQUIRED_LANES = {
    "SDK mechanical validation": [
        "./bin/ask skills package verify <skill-path> --json --robot",
        "./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot",
        "./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot",
        "./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot",
        "./bin/ask skills audit <skill-path>/SKILL.md --level strict --json --robot",
    ],
    "oss-local flow": [
        "codex exec --profile oss-local",
        "codex_profile=oss-local",
        "oss-local.config.toml",
    ],
    "oss-cloud flow": [
        "codex exec --profile oss-cloud",
        "codex_profile=oss-cloud",
        "oss-cloud.config.toml",
        "run-auth-backed.sh --env-file ~/.codex/.env --require-env",
        "run-codex-exec.sh --profile oss-cloud",
        "--strict-config",
        "-c 'approval_policy=\"on-request\"'",
        "--sandbox read-only",
        "--ephemeral",
        "execution_argv",
    ],
    "Tessl local flow": [
        "./bin/ask evals run <skill-path> --mode smoke or release --json --robot",
        "./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot",
        "requires `--execute` for a temporary Tessl install",
        "/tmp/ask-tessl-*",
    ],
    "Tessl external flow": [
        "./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --execute --json --robot",
        "./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot",
        "./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot",
        "tessl eval view --json",
        "Foundry package id",
        "private Tessl package id",
        "candidate-bound project-link receipt",
    ],
}

REQUIRED_NON_SUBSTITUTION_PHRASES = [
    "Do not skip SDK mechanical validation before runtime proof",
    "Do not use generic `./bin/ask evals run --runner codex --model <model>` as",
    "Do not treat a ChatGPT-account model error as an oss-local blocker",
    "Do not treat an oss-local pass as oss-cloud proof",
    "codex exec --profile fast",
    "cannot substitute for oss-local or oss-cloud promotion evidence",
    "Do not treat local Tessl package staging as external Tessl scoring proof",
    "Do not treat external Tessl command completion as readiness",
    "Do not treat a one-off Tessl upload as external proof",
]

REQUIRED_PIPELINE_PHRASES = [
    "## Promotion Pipeline",
    "1. SDK mechanical validation",
    "Skills SDK Gold Standard Rubric",
    "/Docs/reference/skills-sdk-gold-standard-rubric.md",
    "2. oss-local flow",
    "3. oss-cloud flow",
    "4. Tessl local flow",
    "5. Tessl external flow",
    "durable private Tessl registry/workspace package",
    "iterate until the sandboxed local OSS lane is valid",
    "iterate until the sandboxed cloud OSS lane is valid",
    "iterate until the rubric and scenario package are good enough",
    "## Tessl External Identity Contract",
    "`jscraik` is the single intended Tessl workspace",
    "Tessl workspace and Tessl project are different identifiers",
    "each standalone skill or plugin-owned package is generated, linked,",
    "`jscraik/technical-writer`",
    "`jscraik/skill-factory`",
    "Every staged Tessl plugin manifest must start with `private: true`",
    "Public visibility requires a separate explicit publish lane",
    "foundry_package_id",
    "tessl_private_package_id",
    "staged package digest",
    "## First-Time Tessl Workspace Setup",
    "tessl install tessl-labs/tile-creator sharaf/migrate-to-tessl --agent codex --agent agents",
    "Do not use `pnpx tessl i ...` for SDK runtime lanes",
    "candidate-bound project-link receipt",
    "The live evaluator never repairs, relinks, updates, or creates a project.",
    "Do not run `tessl plugin publish`",
    "registry upload commands in runtime-lane proof",
    "staged-package lint",
    "scored `tessl eval view --json` artifacts",
    "workspace selection: `jscraik` for every Skills SDK Tessl project",
    "manifest visibility: staged plugin manifests start `private: true`",
    "publish readiness: not claimed from runtime-lane proof",
    "## Format Projection Rules",
    "The Skills SDK must not publish an OpenAI/Codex plugin directory directly as a Tessl package",
    "`agents/**`: preserve as OpenAI metadata",
    "copy required OpenAI/Codex skill metadata such as `agents/openai.yaml`",
    "`skills/<skill-name>/agents/**`",
    "`.codex-plugin/plugin.json`: translate selected identity",
    "There is no separate required OpenAI plugin marketplace JSON inside each plugin package",
    "`.tessl-plugin/plugin.json`: required Tessl registry manifest",
    "optional `rules`, and optional `mcpServers` entries",
    "`rules` must not be used as a replacement for skill references",
    "into a Tessl `.tessl-plugin/plugin.json`",
    "include `.tessl-plugin/plugin.json`, `README.md` for registry presentation",
    "`README.md`: include for private and public registry promotion",
    "Tessl docs treat it as Registry UI presentation and not as agent context",
    "GitHub Badge section",
    "tessl skill review --optimize",
    "tessl review run",
    "`skills/<skill-name>/SKILL.md`",
    "`skills/<skill-name>/references/**`",
    "Do not translate skill references into Tessl `rules/`",
    "Tessl's own skill packages use",
    "`skills/<skill-name>/scripts/**`",
    "`.mcp.json`: include only when the plugin bundles MCP servers",
    "This plugin-bundled file is distinct from",
    "`evals/<case-id>/task.md` and `evals/<case-id>/criteria.json`",
    "`.tesslignore`: include at the staged plugin root",
    "`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.harness/`, `.agents/`, `.codex/`",
    "must not ignore manifest entrypoints",
    "Tessl projection-shape validator",
    "`hooks/**`: omit or block unless the Tessl projection explicitly models",
    "`mcp/**` and `apps/**`: omit or block unless the Tessl projection explicitly models",
    "`tessl.json`: use as the workspace/project dependency manifest",
    "Its `name` must be the exact",
    "`<workspace>/<project-slug>`",
    "`AGENTS.md`: treat as consuming-workspace or repository instruction context",
    "not skill reference material or a Tessl runtime rule",
]


@dataclass
class Finding:
    code: str
    message: str
    path: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _phrase_present(text: str, compact_text: str, phrase: str) -> bool:
    return phrase in text or phrase in compact_text


def _contract_finding(code: str, message: str) -> Finding:
    return Finding(code, message, _relative(CONTRACT_PATH))


def _missing_phrase_findings(
    text: str,
    compact_text: str,
    *,
    phrases: list[str],
    code: str,
    message_prefix: str,
) -> list[Finding]:
    return [
        _contract_finding(code, f"{message_prefix}: {phrase}")
        for phrase in phrases
        if not _phrase_present(text, compact_text, phrase)
    ]


def _validate_lane(text: str, compact_text: str, lane: str, phrases: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    if lane not in text:
        findings.append(_contract_finding("missing_lane", f"Runtime lane contract must describe {lane}."))
    findings.extend(
        _missing_phrase_findings(
            text,
            compact_text,
            phrases=phrases,
            code="missing_lane_command",
            message_prefix="Runtime lane contract is missing required phrase",
        )
    )
    return findings


def _validate_contract() -> list[Finding]:
    text = _read(CONTRACT_PATH)
    if not text:
        return [_contract_finding("missing_contract", "Skills SDK runtime lane contract document is missing or unreadable.")]
    compact_text = " ".join(text.split())
    findings = [
        finding
        for lane, phrases in REQUIRED_LANES.items()
        for finding in _validate_lane(text, compact_text, lane, phrases)
    ]
    findings.extend(
        _missing_phrase_findings(
            text,
            compact_text,
            phrases=REQUIRED_NON_SUBSTITUTION_PHRASES,
            code="missing_non_substitution_rule",
            message_prefix="Runtime lane contract is missing non-substitution rule",
        )
    )
    findings.extend(
        _missing_phrase_findings(
            text,
            compact_text,
            phrases=REQUIRED_PIPELINE_PHRASES,
            code="missing_promotion_pipeline",
            message_prefix="Runtime lane contract is missing promotion-pipeline phrase",
        )
    )
    return findings


def _validate_index_links() -> list[Finding]:
    findings: list[Finding] = []
    readme = _read(README_PATH)
    validation = _read(VALIDATION_PATH)
    if "25-sdk-runtime-lane-contract" not in readme:
        findings.append(
            Finding(
                "missing_readme_link",
                "Agent instruction map must link the Skills SDK runtime lane contract.",
                _relative(README_PATH),
            )
        )
    required_validation_phrases = [
        "Skills SDK runtime lane contract",
        "Skills SDK Gold Standard Rubric",
        "/Docs/reference/skills-sdk-gold-standard-rubric.md",
        "validate_sdk_runtime_lane_contract.py --json",
        "SDK mechanical validation",
        "codex exec --profile oss-local",
        "codex exec --profile oss-cloud",
        "--tessl-live-private",
    ]
    for phrase in required_validation_phrases:
        if phrase not in validation:
            findings.append(
                Finding(
                    "missing_validation_reference",
                    f"Validation guidance is missing runtime-lane phrase: {phrase}",
                    _relative(VALIDATION_PATH),
                )
            )
    return findings


def _validate_external_effect_routes() -> list[Finding]:
    findings: list[Finding] = []
    source = _read(EVALS_PATH)
    start = source.find("def _run_tessl_live_private_eval(")
    if start < 0:
        live_body = ""
    else:
        end = source.find("\ndef ", start + 1)
        live_body = source[start:] if end < 0 else source[start:end]
    if not live_body:
        findings.append(Finding("missing_live_tessl_route", "Live Tessl evaluator source is missing or unreadable.", _relative(EVALS_PATH)))
    elif "_ensure_tessl_project_link(" in live_body:
        findings.append(Finding("live_eval_mutates_project", "Live Tessl evaluator must consume a receipt, not repair, relink, update, or create a Tessl project.", _relative(EVALS_PATH)))
    elif "_validate_tessl_project_link_receipt(" not in live_body:
        findings.append(Finding("missing_project_link_receipt_gate", "Live Tessl evaluator must require a candidate-bound project-link receipt.", _relative(EVALS_PATH)))
    if "PYTEST_CURRENT_TEST" not in live_body or "unittest.mock" not in live_body or "ASK_ALLOW_TEST_TESSL_LIVE" in live_body:
        findings.append(Finding("missing_hermetic_test_firewall", "Live Tessl evaluator must block pytest provider effects unless subprocess is an in-process mock, without a test-only opt-in escape hatch.", _relative(EVALS_PATH)))
    return findings


def validate() -> list[Finding]:
    return [*_validate_contract(), *_validate_index_links(), *_validate_external_effect_routes()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = validate()
    payload = {
        "status": "pass" if not findings else "fail",
        "finding_count": len(findings),
        "findings": [finding.__dict__ for finding in findings],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])
        for finding in findings:
            print(f"{finding.code}: {finding.path}: {finding.message}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
