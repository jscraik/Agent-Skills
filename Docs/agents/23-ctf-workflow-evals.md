# CTF Workflow Evals

High-level workflow skills must close the loop by proving they can complete
realistic tasks, not only by sounding plausible. Use capture-the-flag style
evals for workflows such as logging in, uploading attachments and starting a
chat, or granting a group access to a Workplace Agent.

The flag is the win condition. Capturing it proves that the skill navigated the
real workflow, observed the right state, and completed the intended outcome.

## Scope

This is eval-driven harness engineering for agentic coding. It is not coding
reinforcement learning. The system improves skills by repeated attempts,
self-reflection, automation scheduling, and commits that refine the skill
against observed failures.

## Eval Loop

1. Plant a flag in the UI or target workflow state.
2. Run the skill through the app or automation under realistic conditions.
3. Require the agent to capture the flag as the win condition.
4. Record wall-clock time, reliability, blockers, and codebase drift observed.
5. Ask the agent to reflect on the failed or slow step with evidence.
6. Commit the smallest skill or harness refinement that improves the next run.
7. Repeat until the skill is reliable against the current product surface.

## Workflow Skill Requirements

A high-level workflow skill should declare:

- target workflow and user-facing goal;
- required workspace, app, credentials, permissions, and fixtures;
- flag location and capture condition;
- allowed setup and mutation scope;
- blocker taxonomy for auth, permissions, UI drift, missing fixtures, sandbox
  limits, and external service failures;
- success evidence, failure evidence, and reflection artifact format;
- reliability and wall-clock targets.

## Optimization Targets

Optimize in this order:

1. Correct flag capture.
2. Reliable blocker classification.
3. Resistance to changing codebase and UI details.
4. Wall-clock time.
5. Minimal skill surface and low setup burden.

Do not optimize speed before the skill can reliably distinguish product
failure, auth failure, setup failure, UI drift, and its own instruction gap.

## Closeout Rule

Do not call a workflow skill production-ready until it has recent CTF-style
eval evidence or an explicit reason that such an eval is not applicable. A
passing static review is not enough for workflows whose truth lives in the UI
or app state.
