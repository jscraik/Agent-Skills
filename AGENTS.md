---
schema_version: 1
---

# agent-skills Agent Guide

Agent Skills Kit is the canonical control plane for authoring, validating,
discovering, and syncing Codex skills, operator docs, and agent workflows.

## Root Essentials

- On a fresh checkout, run `bash scripts/bootstrap-ask.sh --json` before
  requiring `./bin/ask`; if the wrapper is unavailable, verify the fallback with
  `python3 bin/ask repo status --json`.
- Use `./bin/ask` for repo operations; it forwards to
  `Infrastructure/bin/ask`.
- Before committing or pushing from a fresh or repaired worktree, run
  `bash scripts/install-prek-hooks.sh` or `make worktree-ready`. The installer
  forces generated `prek` git hooks to use repo-local `.cache/prek` so Codex
  sandboxed pushes do not fail on `~/.cache/prek/prek.log` write access.
- The repository root has no package manager install step. Use repo wrappers at
  the root, and use package commands only inside verified package roots.
- Before changing skills, sync policy, runtime projections, or agent-facing
  docs, read [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md).
- Edit canonical sources, not runtime projections. See
  [Path Ownership Boundaries](./Docs/agents/14-path-ownership-boundaries.md).
- Treat every Jamie steering or review feedback item as a high-signal candidate
  until classified otherwise, not as disposable chat context. Before repeating a
  corrected behavior or fixing a review comment line-locally, apply the
  [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
  protocol.
- After high-signal steering, do not resume ordinary task work until the uptake
  record states the operating failure, blocker, environment refinement,
  mechanism, proof, and repeat prevention, and the steering uptake validator
  passes.
- When the needed context may sit outside the current turn, scale OODA
  horizontally across adjacent organizational activity and vertically across
  stacked trajectories. Identify the compaction, harness, environment, repo,
  tracker, or review boundary; resume or query the smallest target context
  window that can reflect on it when available; then record what changed before
  acting.
- If Jamie says the agent is failing to operate effectively, repeating prior
  steering, or making him give the same feedback twice, treat that as a
  lane-changing stop signal. Halt the active implementation or review lane,
  close or cancel stale child agents when needed, make the smallest durable
  environment refinement, validate it, and report proof before resuming.
- When repo doctor, closeout, or another validator reports diagnostic findings,
  classify the dominant category, owner or decision boundary, and next action
  before calling the debt nonblocking.
- When feedback names one API, function, command, test, doc section, review
  line, error, or example but expresses a transferable principle, extract the
  generalized rule and classify similar cases in the nearest relevant surface
  before claiming uptake.
- Before applying principle-shaped feedback, ask what class of failure the
  feedback reveals. Use the loop: correction -> pattern -> sweep ->
  classification -> enforcement. Search sibling instances or equivalent cases in
  the chosen radius before editing only the named site, unless the sweep proves
  the issue is genuinely local.
- Do not fight repeated errors. If the same command, validator, tool call, or
  implementation attempt hits the same error twice, stop retrying, research 3-5
  plausible fixes using the web when available or repo-local docs when network
  is blocked, choose the most efficient safe fix, implement it, and record the
  evidence.
- Product posture: agents should set themselves up after being dropped into a
  workspace. Do not require the customer to integrate scattered docs, scripts,
  projections, and setup steps before the agent can report readiness. See
  [Zero-Setup Agent Workspace](./Docs/agents/21-zero-setup-agent-workspace.md).
- Systems-thinking posture: spot blockers, design mechanisms that let people
  and agents systematically overcome them, and explain how code carries that
  mechanism. See
  [Systems Thinking Product Rule](./Docs/agents/22-systems-thinking-product-rule.md).

- Treat every repeated user steering item or review correction from Jamie as a
  high-signal operating defect until classified. If the same command failure,
  tool-permission issue, approval blocker, or user correction appears twice in a
  lane, stop the active task, name the pattern, refine the repo/environment
  contract that allowed it, validate that refinement, and report the proof
  before resuming the original lane.
  Use [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
  and record uptake in `.harness/quality/steering-uptake.md`; validate with
  `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
- For live GitHub, CodeRabbit, CircleCI, Snyk, package registry, or other
  networked repo operations in Codex sandboxed runs, request explicit network
  permission before diagnosing an outage or credential problem. When a command
  may invoke `gh`, `mise`, or `uv`, keep tool caches and state inside
  approved temp paths before treating cache warnings as the blocker. Set
  `XDG_CACHE_HOME`, `XDG_STATE_HOME`, `MISE_CACHE_DIR`, and
  `UV_CACHE_DIR` as applicable for the command family.
- Prefer fixing the mechanism that caused repeated feedback over fixing only
  the immediate symptom. Durable mechanism fixes belong in the relevant skill,
  agent guide, solution doc, validation command, or wrapper script.

## Common Commands

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

## Further Guidance

- Repo command behavior and `--robot` mode:
  [Agent Operating Contract](./Docs/agents/16-agent-operating-contract.md)
- Tooling and package command policy:
  [Tooling and Command Policy](./Docs/agents/02-tooling-policy.md)
- Validation order and evidence rules:
  [Validation and Checks](./Docs/agents/04-validation.md)
- Workflow, git, refactoring, docs, and safety:
  [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md)
- Skill install, audit, fold, and line-budget rules:
  [Skill Management](./Docs/agents/17-skill-management.md)
- Browser and local preview fallback:
  [Browser and Local Preview](./Docs/agents/18-browser-and-local-preview.md)
- Turning steering and review comments into durable agent behavior:
  [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
- Instruction cleanup notes and stale guidance to remove:
  [Contradictions and Cleanup](./Docs/agents/05-contradictions-and-cleanup.md)

Start at [Docs/agents/README.md](./Docs/agents/README.md) when you need the
full instruction map.
