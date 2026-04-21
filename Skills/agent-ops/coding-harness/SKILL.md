---
name: coding-harness
description: Use when a repository needs `@brainwav/coding-harness` installed, bootstrapped, updated, audited, or explained. Covers `harness init`, harness-managed CI migration, governance checks, and Codex environment action-sync guidance. Do not use for unrelated coding, general deployment, or broad cloud work.
metadata:
  skill-type: team_automation
  lifecycle_state: active
  maturity: validated
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-04-04
  metadata_source: frontmatter
---

# Coding Harness
Operate `@brainwav/coding-harness` with command-accurate setup flows, conservative mutation rules, and explicit governance boundaries.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [References](#references)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [Examples](#examples)
- [See Also](#see-also)

## When to use
Use this skill when the request is to:
- install `@brainwav/coding-harness` in a repository and verify the scaffold safely;
- bootstrap or repair `harness init`, including preview, update, migrate, and rollback paths;
- explain what coding-harness can and cannot do, including required tokens, remote-check boundaries, and environment setup;
- audit whether `.codex/environments/environment.toml` action blocks are aligned with current project scripts;
- guide or execute GitHub Actions to CircleCI cutover using `harness ci-migrate` instead of manual workflow deletion.

Do not use this skill for:
- unrelated application feature work;
- generic cloud deployment work that is not about harness governance;
- broad security reviews that are not tied to coding-harness install, policy, or verification surfaces.
- ordinary questions or creative tasks that do not involve coding-harness. In those cases, answer normally or route to a more relevant skill.

## Required inputs
- target repository path and package-manager context;
- current harness state: `not installed`, `installed`, `needs update`, or `broken`;
- execution posture: `no-execution` guidance or command-running execution mode;
- auth posture for remote checks, such as PAT or GitHub App JWT, when `verify-coderabbit` or similar remote checks are requested;
- desired verification depth: lightweight setup confirmation or deep runtime/artifact validation.

If details are missing, make the safest reasonable assumption:
- default to no-execution mode for explanation-only asks;
- default to preview-first commands before mutative operations;
- default to skipping remote checks until the user provides auth material.

## Deliverables
Produce only what the request needs, usually:
- a setup or remediation summary with exact commands run;
- a file-level change summary when harness scaffolds or updates repository files;
- a validation ladder summary that distinguishes baseline gates, deep gates, and conditional harness-specific checks;
- a capability boundary summary covering `can do`, `cannot do`, and `requires user-provided auth`;
- explicit pass/fail evidence plus the next safe action when anything remains unresolved;
- machine-readable reports that preserve `schema_version` whenever the output is schema-bound.

## Philosophy
- Prefer deterministic, evidence-backed setup over assumptions.
- Keep installation and update guidance reversible, preview-first, and command-accurate.
- Treat capability boundaries as part of the contract, especially around auth, destructive changes, and enforced scaffold files.
- Separate `skill bundle is accurate` from `target repo is fully green` because those are different claims.
- When refusing unsafe or unsupported requests, say `cannot` plainly and explain the missing evidence or prerequisite.
- Start with the smallest viable harness boundary, keep scope tight, and expand only when the user clearly asks for more than bootstrap, CI migration, environment action-sync, or auth-bound verification.

## Workflow
1. Confirm execution mode.
- Do stay in no-execution mode when the user wants explanation or planning because that keeps guidance reversible.
- Do switch to execution mode only when command evidence is required because completion claims must be grounded in the live repo state.
- Do not inspect the current workspace when the request is explanation-only and no target repo path was provided because the answer should come from the documented harness contract first.

2. Preflight the repository.
- Do confirm repo root, toolchain availability, and current harness state because path-sensitive or multi-step work is fragile without preflight.
- Do run `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required` when available because harness-enabled repos often encode extra local policy there.

3. Install or upgrade harness conservatively.
- Do prefer `mise install -g npm:@brainwav/coding-harness` for consumer repos because it matches the current recommended global install posture.
- Do prefer `pnpm exec tsx src/cli.ts --help` as command truth when working inside `~/dev/coding-harness`, because a globally installed `harness` binary may lag behind source.
- Do bootstrap with `harness init --dry-run` followed by `harness init` because the current CLI-safe path is preview-first.
- Do treat existing harness-managed repos differently from fresh bootstrap: run `harness init --check-updates`, then `harness upgrade --dry-run`, then `harness upgrade` because that is the routine update lane now.
- Do reserve `harness init --update` for re-scaffolding missing tracked baseline files because it is not the default upgrade path for mature installs.
- Do know that `harness init --check-updates`, `harness init --update`, and `harness upgrade` can auto-repair legacy `.harness/restore-manifest.json` files missing `ciProvider` when the active provider can be inferred safely.
- Do not pass `--ci circleci` to `harness init` because the current CLI treats the extra positional token as a target directory in this flow.
- Do use `harness ci-migrate prepare --provider circleci --dry-run`, then `--apply`, `verify --snapshot <snapshot-id>`, `commit --snapshot <snapshot-id>`, and `abort --snapshot <snapshot-id>` because cutover must stay reversible and snapshot-bound.
- Do use project-local source execution only when you are actively developing the coding-harness repository because consumer repos should follow the packaged CLI contract.

4. Validate setup and policy state.
- Do run the baseline repository gate first because `pnpm check` catches the broad integration surface expected by the tool.
- Do escalate to `pnpm test:deep` when runtime behavior or artifact formats changed because baseline checks are not enough for behavior-affecting work.
- Do use targeted harness checks such as `harness check-environment`, `verify-coderabbit`, `check-authz`, `docs-gate`, and `tooling-audit` when the user asks for specific governance evidence.
- Do rely on structured `--json` output for gates and `health --auto-fix --dry-run` because machine-readable findings are safer to automate than table scraping.
- Do answer directly that a repo is not verified yet when checks were skipped because unsupported certainty is worse than an incomplete status.

5. Report capability boundaries explicitly.
- Do say which checks were actually run because remote verification and auth-dependent gates are optional until credentials exist.
- Do call out user-managed surfaces such as secrets, tokens, branch protection ownership, and non-autogenerated environment files because harness does not replace human authority there.

6. Record repo-specific learnings when applicable.
- Do read `~/.codex/instructions/Learnings.md` first and `.harness/memory/LEARNINGS.md` second because the skill uses both global and repo-scoped memory.
- Do append only repo-specific lessons to `.harness/memory/LEARNINGS.md` when `.harness/` exists because harness repos treat that file as an append-only local knowledge base.

## Validation
Run the smallest relevant checks first, then broaden before claiming completion:

```bash
harness --help
harness init --dry-run
harness init --check-updates
harness upgrade --dry-run
harness upgrade
pnpm check
pnpm test:deep
```

Use targeted governance or lifecycle commands as needed:

```bash
harness init --check-updates
harness upgrade --dry-run
harness upgrade
harness init --update
harness init --migrate
harness init --rollback
harness ci-migrate prepare --provider circleci --dry-run
harness ci-migrate prepare --provider circleci --apply
harness ci-migrate verify --snapshot <snapshot-id>
harness ci-migrate commit --snapshot <snapshot-id>
harness ci-migrate abort --snapshot <snapshot-id>
harness verify-coderabbit
harness verify-coderabbit --token <token-or-jwt> --owner <owner> --repo <repo>
harness check-authz --contract <path> --repo <owner/repo> --branch <branch>
harness check-environment --contract <path> --attestation <path>
harness docs-gate --mode advisory --json
harness tooling-audit --path <dir> --format table
harness evidence-verify --files <paths>
harness health --auto-fix --dry-run --json
```

Canonical skill maintenance gates after edits:

```bash
bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict
bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn
python3 Infrastructure/scripts/lifecycle-and-sync/gotcha_pipeline.py validate
python3 Infrastructure/scripts/validation-and-linting/check-see-also.py . --changed-files Skills/coding-harness/SKILL.md
python3 Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py --repo-root . --expected-count 0
bash Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh
bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh
python3 Skills/skill-builder/Infrastructure/scripts/skill_gate.py Skills/coding-harness --require-fail-fast --require-security-evals
python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/coding-harness --eval-mode release --runner codex --capture-jsonl --timeout-profile codex-heavy --profile d --codex-fallback-profile ''
```

Fail fast on the first blocking gate, fix the specific issue, rerun that gate, and only then continue to broader validation.

## References
- `Infrastructure/references/agent-install-guide.md`
  Read when: you need the human-readable install, update, and CI migration sequence with rollback.
- `Infrastructure/references/agent-install.json`
  Read when: you need machine-readable phases, commands, or scaffolded file lists.
- `Infrastructure/references/setup-and-commands.md`
  Read when: you need the wider command map, lifecycle commands, or CI secret wiring details.
- `Infrastructure/references/structured-json-output.md`
  Read when: you need the `GateResult` schema, `jq` extraction patterns, or `health --auto-fix` usage.
- `Infrastructure/references/contract.yaml`
  Read when: you need the machine-checkable input/output contract for this skill.
- `Infrastructure/references/evals.yaml`
  Read when: you need trigger coverage, adversarial cases, or release-eval inputs.
- `Infrastructure/references/plan.md`
  Read when: you need preserved implementation context from the packaged-skill work rather than the operator-facing wrapper alone.
- `agents/openai.yaml`
  Read when: you need the display metadata used by external skill packaging surfaces.

## Constraints and safety
- Redact secrets, tokens, and sensitive repository data in logs, artifacts, and summaries.
- Require explicit user confirmation before destructive or high-impact mutations.
- Treat `harness --help` as command truth when older docs disagree.
- Do not claim full setup success without command evidence from the current repository state.
- Treat remote checks as optional until the user provides the required auth material.
- Do not hand-edit enforced harness outputs such as `Infrastructure/harness.contract.json`, `.circleci/config.yml`, or `Infrastructure/scripts/check-environment.sh` because `harness init --update` will overwrite them.
- Only auto-update `.codex/environments/environment.toml` when the file is harness-generated because user-owned environment config needs an approval checkpoint.

## Anti-patterns
- claiming harness is configured without running verification commands;
- deleting `.github/workflows/` files manually instead of using `harness ci-migrate`;
- treating `pnpm check` and `pnpm test:deep` as interchangeable when runtime behavior changed;
- reporting remote verification as passed when auth was never supplied;
- treating `harness init --update` as the routine existing-repo upgrade lane;
- applying `harness init --update` without previewing first when repo state is unclear;
- editing enforced scaffold files by hand and assuming the changes will persist.

## Failure mode
- If the target repo path cannot be verified, stop before mutating anything and ask for the exact root.
- If auth-dependent checks are requested without credentials, explain the missing prerequisite and continue only with local/non-remote validation.
- If command help output conflicts with packaged docs, follow the command output, call out the drift, and repair the canonical copy before claiming completion.
- If the repo is already red on unrelated gates, separate `skill bundle is correct` from `repo aggregate is green` instead of overstating success.
- If the request is unrelated to coding-harness, do not force this workflow onto it; either answer normally or route to the correct skill.

## Gotchas
- Symptom: `harness init --ci circleci` fails with a path-resolution error. Cause: the current CLI interprets `circleci` like a target directory in that flow. Do instead: run `harness init --dry-run` and then `harness init`. Check: rerun `harness init --dry-run` and confirm the scaffold plan renders normally.
- Symptom: an agent treats `harness init --update` as the normal way to update an existing harness repo. Cause: older summaries collapsed the upgrade lane into the re-scaffold lane. Do instead: run `harness init --check-updates`, then `harness upgrade --dry-run`, then `harness upgrade`; use `harness init --update` only when tracked baseline files are missing and need re-scaffolding. Check: the final plan should distinguish routine upgrade from re-scaffold explicitly.
- Symptom: a legacy repo reports that `.harness/restore-manifest.json` is missing `ciProvider`. Cause: the repo was scaffolded before that metadata became mandatory for the update lane. Do instead: rerun `harness init --check-updates`, `harness upgrade --dry-run`, or `harness init --update` and let current harness repair the manifest automatically when the active provider can be inferred. Check: verify the manifest now includes `ciProvider` and the upgrade lane proceeds.
- Symptom: CI migration guidance looks right but rollback is missing. Cause: older summaries often stop after `commit`. Do instead: preserve the full snapshot-based sequence including `abort --snapshot <snapshot-id>`. Check: confirm preview, apply, verify, commit, and abort all appear in both `SKILL.md` and `Infrastructure/references/agent-install-guide.md`.
- Symptom: an agent claims repo setup is complete after only local checks. Cause: remote gates such as CodeRabbit verification were skipped because auth was missing. Do instead: report the local pass separately from auth-blocked remote checks. Check: the final summary should say exactly which checks were skipped and why.
- Symptom: `.harness/memory/LEARNINGS.md` guidance is applied to a repo without `.harness/`. Cause: the memory layer is repo-specific, not universal. Do instead: skip creation when `.harness/` is absent. Check: only read or append the repo memory file when the harness directory exists.
- Symptom: `run_skill_evals.py` fails early with `Unsupported parameter: 'reasoning.summary'` under a Spark-oriented Codex profile. Cause: the active profile/model does not support the runner's default reasoning setting. Do instead: pin the eval run to `--profile d --codex-fallback-profile ''`. Check: the release run should emit normal case artifacts and a populated `scorecard.json`.

## Examples
- When the user asks: "Can you help me add the Brainwav harness to this repo and tell me which steps still need my credentials?"
- When the user asks: "Please map the safe bootstrap flow for this repo, including preview, validation, update, and rollback commands."
- When the user asks: "Help me inspect whether our Codex environment actions are still aligned with the current scripts."
- When the user asks: "Can you explain whether we should use a GitHub App JWT or a PAT for the harness verification checks?"
- Do not trigger for: "Build a new dashboard for our admin panel."

## See Also
| Skill | When to use |
|---|---|
| [[bootstrap]] | Clone and bootstrap a repository before coding-harness setup begins |
| [[circleci:circleci-cli]] | Work on CircleCI-specific pipeline design or migration details beyond the harness wrapper |
| [[verification-before-completion]] | Add a stronger final verification pass before claiming a repo change is complete |
| [[he-fix-bugs]] | Root-cause failing harness commands or broken repo state before applying fixes |

**Topic map:** [[agent-ops]]
