---
schema_version: 1
title: Agent Skills Codex Cloud Eval Strategy
status: draft-for-review
date: 2026-05-17
selected_mode: architecture_review
repo: agent-skills
primary_reader: Jamie and future Codex agents implementing eval runners
decision_status: proposed
---

# Agent Skills Codex Cloud Eval Strategy

## Command Summary

BLUF: This artifact gives Jamie and future Codex agents the decision boundary for adding Codex Cloud to the agent-skills eval system. Codex Cloud should become an asynchronous behavior-eval lane for skill quality, not a replacement for local deterministic gates or CI-grade codex exec JSON/schema runs. The distinction matters because release confidence needs machine-readable local proof for hard gates while Cloud is better suited to parallel, best-of-N behavior evidence. The first execution slice should add a first-class ./bin/ask evals cloud command that submits and tracks read-only Cloud eval tasks, persists task metadata immediately, classifies Cloud-specific blockers, and marks the lane advisory until task lifecycle parsing is stable enough for release gating.

Decision Needed: Accept the three-tier eval model: local static gates for deterministic structure, local codex exec for machine-readable CI behavior checks, and Codex Cloud for parallel best-of-N behavior evaluation.

Top Risks: codex cloud is experimental and currently only list exposes JSON locally; Cloud task success can be mistaken for eval success; Cloud diffs or summaries can become private external state without durable local artifacts; adding Cloud too early as a hard gate could turn release confidence into lifecycle noise.

Next Action: Implement the smallest Cloud runner skeleton around task submission, codex cloud list --json polling, artifact persistence, timeout/blocker classification, and mocked unit tests before running live Cloud tasks as release evidence.

## Sources

- Official Codex non-interactive docs: https://developers.openai.com/codex/noninteractive
- Official Codex Cloud docs: https://developers.openai.com/codex/cloud
- Official Codex Cloud environments docs: https://developers.openai.com/codex/cloud/environments
- Official Codex CLI reference: https://developers.openai.com/codex/cli/reference#codex-cloud
- Official Codex GitHub Action docs: https://developers.openai.com/codex/github-action
- Local command evidence: codex --version, codex cloud --help, codex cloud exec --help, codex cloud list --help, codex cloud status --help, codex cloud diff --help, codex cloud apply --help, codex cloud list --json --limit 5
- Repo evidence: Infrastructure/scripts/lib/ask/commands/evals.py, Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py, Infrastructure/tests/test_ask_evals_command.py, Skills/agent-ops/evals-router/SKILL.md
- Eval observability contract: Infrastructure/references/eval-observability-otel-contract.md

## Inspection Method

- Used $he-strategy in architecture_review mode because the question is a runner architecture and release-confidence decision, not an implementation request.
- Checked official OpenAI documentation for current codex exec, Codex Cloud, CLI, environment, and GitHub Action behavior.
- Checked local CLI help and a structured Cloud list call to distinguish official capability from this installed alpha's current scriptability.
- Inspected the local eval command and skill-builder eval runner to identify the lowest-risk integration surface.

## Reference Status

- OpenAI docs: live-doc-verified during the investigation immediately preceding this artifact.
- Local CLI: repo/local-verified on codex-cli 0.131.0-alpha.22.
- Repo integration surface: repo-verified from current files.
- Cloud environment suitability: unknown until Jamie selects or provisions the Codex Cloud environment id for this repo.
- OTel-inspired eval observability suitability: advisory and local-package
  scoped. The Braintrust OTel guide was supplied as inspiration only; actual
  Braintrust packages, projects, credentials, endpoints, and export flows are
  out of scope unless Jamie explicitly starts a separate integration lane.

## Facts

- codex exec is documented as the official non-interactive mode for scripts and CI, supports JSONL events with --json, final output files with -o, and schema-constrained final responses with --output-schema.
- codex exec defaults to a read-only sandbox in current docs; the docs recommend explicit sandbox selection such as --sandbox workspace-write, and mark --full-auto as deprecated.
- Codex Cloud tasks run in background cloud environments, check out a selected branch or commit SHA, run setup, apply internet-access settings, and produce an answer and diff.
- Codex Cloud environment configuration owns setup scripts, package versions, environment variables, secrets, cache behavior, and internet access. Secrets are available during setup and then removed before the agent phase.
- The official CLI reference marks codex cloud experimental and documents codex cloud exec --env ENV_ID --attempts 1-4.
- The installed local CLI exposes codex cloud exec, status, list, apply, and diff.
- The installed local CLI exposes --json for codex cloud list, but not for exec, status, diff, or apply.
- A live codex cloud list --json --limit 5 call succeeded from this repo with network enabled, proving the local account can reach Codex Cloud task metadata.
- Infrastructure/scripts/lib/ask/commands/evals.py currently offers ./bin/ask evals run with codex and discovery-smoke runner choices at the command surface.
- Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py already has runner choices including codex, codex-kimi, codex-zai, openai, and discovery-smoke, plus release-mode JSONL capture for codex.
- run_skill_evals.py already supports --output-schema for cases and writes per-case artifacts such as stdout.txt, stderr.txt, final.txt, result.json, and codex_events.jsonl.
- The current blocker taxonomy in Infrastructure/scripts/lib/ask/commands/evals.py is local-runner shaped and does not distinguish Cloud auth, environment, timeout, unstructured lifecycle output, task failure, or diff-unavailable states.
- Existing eval artifacts already carry local trace evidence such as
  codex_events.jsonl, stdout/stderr captures, result JSON, summaries, and
  scorecards; an OTel export failure has appeared historically in eval stderr,
  so telemetry export failure is a real blocker class to separate from skill
  correctness.

## Interpretations

- Claim: Cloud agents are valuable for skill behavior evals because they test real agent routing, evidence gathering, and multi-attempt convergence in isolated background environments.
  Confidence: high.
  Authority limit: This does not prove Cloud is ready as a hard CI gate.
- Claim: Local deterministic gates should remain the first line of confidence because they are fast, explainable, and owned by the repo.
  Confidence: high.
  Authority limit: Static gates cannot prove realistic skill invocation quality.
- Claim: codex exec with JSON/schema should remain the CI-grade live-agent gate until codex cloud exposes more stable structured lifecycle output.
  Confidence: high.
  Authority limit: This could change if a future CLI adds JSON output for Cloud exec, status, and diff.
- Claim: evals cloud should be first-class rather than hidden behind evals run --runner codex-cloud because Cloud has different lifecycle semantics: task submission, task ids, polling, attempts, delayed completion, external URLs, and diff collection.
  Confidence: medium-high.
  Authority limit: A future unified runner abstraction may justify merging command surfaces after the lifecycle contract stabilizes.

## Assumptions

- Jamie wants Cloud evals for behavior and release confidence, not as a publishing or registry path.
- Cloud eval tasks should be read-only by default unless a specific eval case is testing implementation behavior.
- Applying Cloud diffs is out of scope for scoring and should require an explicit separate action.
- The repo will eventually have a canonical Codex Cloud environment id or environment label for agent-skills.

## Affected Systems

- ./bin/ask evals command surface.
- Infrastructure/scripts/lib/ask/commands/evals.py lifecycle and blocker taxonomy.
- Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py if the runner model is later unified.
- Skill eval artifacts under Infrastructure/artifacts/skills.
- Release confidence reporting for evals-router, skill-builder, architecture/review skills, and PR closeout skills.
- CI and GitHub Action guidance for machine-readable eval gates.

## Recommended Architecture

Use three distinct tiers:

    Tier 0: static local gates
    - YAML/frontmatter parsing
    - strict skill audit
    - discovery-smoke contract checks
    - OpenClaw/static security
    - Plugin Eval, Tessl, and Snyk lane policy

    Tier 1: local machine-readable agent runs
    - codex exec --json
    - --output-schema
    - JSONL trace capture
    - deterministic trace checks
    - CI-grade pass/fail

    Tier 2: Codex Cloud behavior evals
    - codex cloud exec --env ... --attempts 1-4
    - async task tracking
    - list-json polling
    - best-of-N behavior comparison
    - advisory release signal at first

    Optional observability lane: repo-owned OTel-style traces
    - record redacted eval spans for debugging and dataset creation
    - correlate local trace summaries with local artifact paths
    - advisory unless a named eval program explicitly requires it
    - exporter failure does not fail the underlying skill eval

Do not collapse these tiers into one pass/fail score. Their evidence types are different.

## Proposed Command Contract

First-class command:

    ./bin/ask evals cloud <skill> --suite release --env <ENV_ID> --attempts 3 --json --robot

Acceptable future unification:

    ./bin/ask evals run <skill> --mode release --runner codex-cloud --env <ENV_ID> --attempts 3 --json --robot

The first command is preferable for the initial implementation because it can expose Cloud lifecycle state without distorting the current local subprocess runner.

## Cloud Runner Contract

1. Resolve the canonical skill path before submitting any Cloud task.
2. Resolve branch or commit SHA explicitly.
3. Generate a deterministic eval prompt from selected eval cases.
4. Submit the task with codex cloud exec --env CODEX_CLOUD_ENV_ID --branch BRANCH_OR_SHA --attempts 3 PROMPT.
5. Persist task metadata immediately before polling, including schema_version skill-cloud-eval-task.v1, runner, skill, task_id, environment_id, branch, attempts, and submitted_at.
6. Poll with codex cloud list --json --env ENV_ID first because it is the structured local command.
7. Use codex cloud status TASK_ID only as human-readable fallback evidence.
8. On completion, collect task id, task URL, status, attempt count, summary, and codex cloud diff TASK_ID --attempt N for each attempted run.
9. Score from durable artifacts and required final output, not from the mere existence of a Cloud task.
10. Never call codex cloud apply during eval scoring.

## Artifact Contract

Write Cloud eval artifacts under:

    Infrastructure/artifacts/skills/<skill>/<run_id>/cloud/
      task.json
      status.json
      status.txt
      diff-attempt-1.patch
      diff-attempt-2.patch
      diff-attempt-3.patch
      result.json

result.json should classify status, runner, task_id, task_url, environment_id, branch_or_sha, attempts_requested, attempts_observed, blocker_class, evidence_paths, score_basis, and release_gate_status.

When local OTel-style export is configured, result.json should also include an
observability object with status, exporter, redaction_status, exported_trace
identifier when safe to store, and local artifact paths used to reconstruct the
trace. When export is not configured, report not_configured rather than
blocked. Do not require Braintrust configuration for this lane.

## Blocker Taxonomy Additions

Add Cloud-specific classes rather than forcing them into local runtime buckets:

- blocked_cloud_auth: Cloud account, login, or access unavailable.
- blocked_cloud_environment: environment id missing, invalid, inaccessible, or unsuitable.
- blocked_cloud_timeout: task did not complete within the configured polling window.
- blocked_cloud_unstructured_output: required task id, status, or attempt data could not be parsed from available CLI output.
- blocked_cloud_task_failed: Cloud task completed in a failed state.
- blocked_cloud_diff_unavailable: task completed but expected attempt diff/artifact could not be retrieved.
- blocked_eval_observability: local OTel collector/exporter was requested but
  unavailable or failed.
- blocked_external_observability: a non-local export target was explicitly
  requested but network, endpoint, package, or policy approval was missing.

## Prompt Contract

Default Cloud eval prompts should be read-only:

    You are running a behavior eval for <skill> in this repository.

    Task:
    Evaluate whether <skill> correctly handles this scenario.

    Rules:
    - Do not edit files.
    - Inspect the canonical skill source and referenced eval/reference files.
    - Select at most 1-3 relevant lenses when lens references apply.
    - Cite repo evidence before applying a lens.
    - Do not cite source books, Cookbook examples, or docs as proof of repo behavior.
    - Return JSON only matching the schema.

Expected final schema fields: overall_pass, selected_lenses, evidence, findings, blocked_reason, and verdict.

## Smallest Feedback Slice

Implement only the Cloud lifecycle shell first:

1. Add evals cloud argument parsing and help text.
2. Add a helper that shells to codex cloud list --json, parses task metadata, and classifies parse failures.
3. Add a submit wrapper that records raw stdout/stderr and writes task.json before polling.
4. Add polling timeout and Cloud blocker classification.
5. Add an observability summary field that defaults to not_configured and does
   not require OTel, Braintrust, network, or credentials.
6. Add mocked tests in Infrastructure/tests/test_ask_evals_command.py.
7. Do one manual live smoke only with codex cloud list --json or a tiny read-only task after tests pass.

Do not implement live Braintrust export in this lane. The Braintrust guide is a
pattern source for the local eval package, not a target service.

Do not wire the lane into release-required dashboards until the artifact contract and blocker taxonomy are stable.

## Drift And Moat Impact

- Positive drift reduction: separates static, local live-agent, and Cloud behavior evidence instead of blending incompatible confidence signals.
- Positive operator leverage: lets Codex run behavior evals asynchronously and in parallel while Jamie keeps local gates deterministic.
- Moat impact: improves the Agent Skills Kit as a professional skill SDK by adding a credible behavior-eval plane without sacrificing evidence discipline.
- Main drift risk: Cloud summaries become another external truth surface unless task metadata and result artifacts are persisted locally every time.

## Direct Strategic Critique

Strongest leverage: Use Cloud for what local evals cannot cheaply prove: realistic multi-attempt skill behavior, routing, and evidence discipline under isolated background execution.

Biggest drag: The current Cloud CLI lifecycle is not structured enough to be a hard gate without wrapper discipline.

Highest-risk contradiction: Treating Cloud as more reliable because it is remote, while ignoring that local codex exec currently has the stronger machine-readable contract.

Hard recommendation: Build evals cloud as advisory first, and require codex exec with JSON/schema or the Codex GitHub Action for hard CI-grade gating until Cloud lifecycle output is structured end to end.

## Future Agent Guidance

- Do not replace local evals with Cloud evals.
- Do not mark Cloud task submission as eval success.
- Do not apply Cloud diffs during scoring.
- Always persist Cloud task metadata, status, raw output, and attempt diffs before summarizing.
- Prefer codex cloud list --json for polling until other Cloud commands expose JSON locally.
- Classify Cloud blockers with Cloud-specific blocker classes.
- Treat Braintrust/OTel material as inspiration for opt-in local observability.
  Record redacted spans and artifact pointers only; never require Braintrust
  credentials for ordinary local evals.
- Keep Snyk, Tessl, Plugin Eval, strict audit, discovery-smoke, and static checks in their own lanes.
- Use codex exec with JSON/schema for CI-grade final JSON and trace checks.

## Stop/Pivot Condition

Pivot the strategy if a future Codex CLI release exposes structured JSON for codex cloud exec, status, diff, and task final outputs, or if local codex exec with JSON/schema stops being the documented CI automation path.

## Clarification Status

No clarification requested. The unknown that blocks implementation confidence is the selected Codex Cloud environment id for agent-skills, not the architecture direction.

## Evidence & Traceability Matrix

| Claim | Evidence | Type | Confidence | Action |
| --- | --- | --- | --- | --- |
| codex exec is the CI-grade structured runner | Official non-interactive docs for --json, -o, and --output-schema | fact | high | Keep Tier 1 as hard gate |
| Codex Cloud is suitable for async background tasks | Official Cloud and environment docs | fact | high | Add Tier 2 behavior lane |
| Cloud CLI is partly unstructured locally | codex cloud list --help has --json; status, diff, apply, and exec help do not | fact | high | Advisory first |
| Local account can read Cloud task metadata | codex cloud list --json --limit 5 succeeded with network enabled | fact | high | Live smoke possible |
| Current ask evals surface has only local runners | Infrastructure/scripts/lib/ask/commands/evals.py and Infrastructure/bin/ask help text | fact | high | Add first-class command |
| Existing skill eval runner already captures JSONL/schema for codex | run_skill_evals.py release-mode JSONL and --output-schema paths | fact | high | Reuse Tier 1 rather than replace it |
| Cloud needs new blocker classes | Current EVAL_BLOCKER_TAXONOMY lacks Cloud-specific classes | fact/interpreted | high | Add taxonomy in first slice |
| OTel-style local observability should be optional | User-supplied Braintrust OTel guide as inspiration plus local OTel export error evidence | inferred | medium-high | Add local observability lane, not Braintrust integration |

## Validation

- pass: rg -n "Codex Cloud" .harness Plugins Skills Docs Infrastructure
- pass: python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/strategy/2026-05-17-agent-skills-codex-cloud-eval-strategy.md --json

## Post Artifact Review Status

not_requested
