# Evals Router Discovery Interview

Use this only when the eval request is underspecified and interaction is available.
Ask one round at a time; do not dump the full plan.

## Request user input mini-templates

Round 1 target question:

What should this skill help you do?

What exact eval, trace folder, judge prompt, scorecard, dashboard, skill, or workflow should this skill inspect?

Why this matters: eval work must stay tied to the real evidence source before changing prompts, validators, dashboards, or success thresholds.

## Copy paste payload examples

Ambiguous target:

What exact eval, trace folder, judge prompt, scorecard, dashboard, skill, or workflow should this skill inspect?

Ambiguous proof:

Which result should prove the eval is trustworthy: deterministic validator output, human labels, judge agreement, scorecard signals, or a local dashboard artifact?

## Round 1: Target

What exact eval, trace folder, judge prompt, scorecard, dashboard, skill, or workflow should this skill inspect?

Why this matters: the route changes depending on whether the problem is coverage, trace errors, judge wording, evaluator calibration, RAG quality, synthetic inputs, or review tooling.

## Round 2: Evidence

What evidence is available right now: failed traces, labeled examples, command output, scorecards, dashboard HTML, or repo files?

Why this matters: objective evidence should use deterministic checks; subjective quality claims need labeled examples before a judge score is trusted.

## Round 3: Done

What outcome should count as done: route recommendation, prompt rewrite, validation plan, eval contract repair, dashboard fix, or rerun evidence?

Why this matters: completion claims need pass, fail, blocked, or advisory evidence rather than a generic quality score.

## Round 4: Boundaries

Are external evaluators, network calls, or third-party uploads allowed, or is this local-only?

Why this matters: private skill and eval evidence should stay local unless the user explicitly approves a specific external tool.

## Round 5: Confirmation

Does this capture the eval target, available evidence, proof standard, and local-only boundary well enough for me to proceed?

Anything to add or change before implementation?
