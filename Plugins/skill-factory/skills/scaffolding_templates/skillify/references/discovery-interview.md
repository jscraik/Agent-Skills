# Skillify Discovery Interview

Use this only when a workflow-to-skill request cannot be turned into a safe
package yet. Ask one round at a time and stop as soon as source evidence,
destination, owner, repeatability, and validation are clear enough to decide
whether to build.

## Request user input mini-templates

Use one of these shapes when the package boundary is ambiguous:

- Inputs: I can help skillify this, but I need one missing piece first.
- Why this matters: a skill package needs repeatable evidence, a canonical destination, and a local proof before files are created.
- Round 1 question: What should this skill help you do?

When the request names a workflow but omits evidence, prefer:

- Inputs: I see the workflow idea, but not the bounded source evidence.
- Why this matters: skillify captures proven repeatable behavior, not transcript noise or unvalidated intention.
- Round 1 question: Which workflow note, report, or completed session should be the source evidence?

## Copy paste payload examples

Example:

    Inputs: I can build a skill package from this workflow, but I need the source evidence first.
    Why this matters: skillify should preserve repeatable behavior from bounded evidence before creating SKILL.md or eval files.
    Round 1 question: Which workflow note, report, or completed session should be the source evidence?

Example:

    Inputs: I can see the source evidence, but not the destination or validation proof.
    Why this matters: the destination controls the active AGENTS.md boundary, and the validation command proves the package is more than ceremonial.
    Round 1 question: What canonical skill path and local validation command should this package use?

## Round 1: Source Evidence

Question: Which workflow note, report, completed session, or bounded evidence
artifact should be the source for this skill?

Why this matters: skillify should capture proven repeatable behavior, not raw
transcript noise, private details, or an untested idea.

## Round 2: Destination

Question: Which canonical skill path should receive this package?

Why this matters: the path determines ownership, active AGENTS.md guidance,
runtime visibility expectations, and validation commands.

## Round 3: Owner And Repeatability

Question: Who owns this workflow, and what repeated trigger proves it should be
a skill rather than a doc, script, rule, or direct answer?

Why this matters: a skill needs a durable cognitive workflow with clear triggers,
not a one-off transcript or broad brainstorm.

## Round 4: Validation

Question: Which exact local proof command should decide whether the new package
is valid?

Why this matters: skillify should fail fast on the smallest deterministic gate
before claiming readiness or adding broader artifacts.

## Round 5: Side Effects

Question: Does this workflow require repo writes, external writes, installs,
runtime projection refreshes, generated media persistence, or approval-gated
actions?

Why this matters: side effects change the safety boundary and may require a
handoff before files are created.

## Round 6: Confirmation

Question: Does this capture the evidence, destination, owner, repeatable trigger,
validation proof, and side-effect boundary well enough for me to decide whether
to build a skill?

Why this matters: confirmation prevents creating a ceremonial skill from
incomplete or unsafe source material.
