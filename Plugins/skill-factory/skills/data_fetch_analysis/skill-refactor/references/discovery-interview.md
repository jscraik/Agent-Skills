# Skill Refactor Discovery Interview

Use this only when a skill lifecycle analysis cannot be grounded in bounded
evidence yet. Ask one round at a time and stop as soon as the scope, evidence,
decision criteria, and approval boundary are clear enough to analyze.

## Request user input mini-templates

Use one of these shapes when the analysis target is ambiguous:

- Inputs: I can analyze this skill lifecycle question, but I need one missing piece first.
- Why this matters: lifecycle recommendations should be based on bounded current evidence, not broad impressions.
- Round 1 question: What should this skill help you do?

When the request names skill-refactor but omits evidence, prefer:

- Inputs: I see a skill health request, but not the evidence surface to trust first.
- Why this matters: keep, improve, merge, split, retire, and observe decisions need different proof strength.
- Round 1 question: Which current evidence path or report should anchor this analysis?

## Copy paste payload examples

Example:

    Inputs: I can analyze this skill health request, but I need the first evidence anchor.
    Why this matters: lifecycle recommendations should cite current bounded evidence before naming repairs or retirements.
    Round 1 question: Which current report, validation output, or session evidence path should anchor this analysis?

Example:

    Inputs: I can see the evidence path, but not the approval boundary for lifecycle changes.
    Why this matters: merge, fold, retire, install, publish, and projection refresh decisions require explicit approval handoffs.
    Round 1 question: Should this pass only recommend a lane, or may it prepare an approval handoff for merge, fold, or retire?

## Round 1: Evidence Anchor

Question: Which current report, validation output, review artifact, or session
evidence path should anchor this analysis?

Why this matters: skill-refactor should classify current evidence strength before
recommending keep, observe, improve, merge, split, or retire.

## Round 2: Scope

Question: Is the scope one skill, one plugin family, one category, or a bounded
inventory?

Why this matters: broad inventory analysis uses weaker confidence unless the
request provides enough current evidence to compare across skills.

## Round 3: Decision Criteria

Question: Which criterion should decide the lifecycle lane: severity,
confidence, implementation cost, user impact, release risk, or validation gap?

Why this matters: the same evidence can justify observe, improve, or approval
handoff depending on the decision criterion.

## Round 4: Approval Boundary

Question: Should this pass stay read-only, recommend skill-builder repairs, or
prepare an approval handoff for merge, fold, retire, install, publish, or
projection refresh?

Why this matters: skill-refactor analyzes and routes by default; lifecycle
mutations and external writes are separate approval events.

## Round 5: Missing Evidence

Question: Is there a recent user correction, failed eval, Tessl result, Plugin
Eval report, or review finding that should outweigh older artifacts?

Why this matters: stale evidence is weak, while repeated user-corrected failures
can justify a stronger lifecycle decision when validation matches.

## Round 6: Confirmation

Question: Does this capture the evidence anchor, scope, decision criterion, and
approval boundary well enough for me to analyze one lifecycle lane?

Why this matters: confirmation prevents the analysis from silently widening into
portfolio cleanup or unapproved source edits.
