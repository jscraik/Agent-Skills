# Skill Factory Router Discovery Interview

Use this only when a Skill Factory request cannot be routed safely from the
current input. Ask one round at a time and stop as soon as the lane, target, and
authority are clear enough to route.

## Request user input mini-templates

Use one of these shapes when the route is ambiguous:

- Inputs: I can route this, but I need one missing piece first.
- Why this matters: the selected lane controls which source files, evidence, and validation gates are safe to use.
- Round 1 question: What should this skill help you do?

When the request already names Skill Factory but not the lane, prefer:

- Inputs: I see a Skill Factory request, but not the target lifecycle lane.
- Why this matters: creating, capturing, hardening, analyzing, and installing skills have different write and proof boundaries.
- Round 1 question: What should this skill-factory work help you do first?

## Copy paste payload examples

Example:

    Inputs: I can route this Skill Factory request, but I need the first routing target.
    Why this matters: the selected lane controls whether I should create, capture, harden, analyze, or install before touching files.
    Round 1 question: What should this skill help you do?

Example:

    Inputs: I can see the target skill, but not whether this pass is read-only, source editing, validation, or external upload.
    Why this matters: routing can stay read-only, but source edits and Tessl uploads need explicit authority.
    Round 1 question: Should this pass be read-only routing, source editing, validation, or an approval handoff?

## Round 1: Routing Target

Question: What should this skill-factory work help you do first: create a new
skill, capture a repeatable workflow, harden an existing skill, analyze skill
health, or install/prove runtime visibility?

Why this matters: the router must choose exactly one lane before loading deeper
instructions or changing files, and the wrong lane can create broad edits or
unsafe side effects.

## Round 2: Target Artifact

Question: Which skill path, plugin path, workflow note, evidence report, or
install source should this route use?

Why this matters: Skill Factory lanes operate on canonical source or bounded
evidence, not vague handles or generated projections.

## Round 3: Authority Boundary

Question: Should this pass be read-only routing, source editing, validation, or
an approval handoff?

Why this matters: routing can recommend a lane without write authority, but
source edits, installs, projection refreshes, and external uploads require a
clear boundary.

## Round 4: Validation Requirement

Question: Which proof should decide success: strict audit, local eval, Tessl
scenario preparation, external review, runtime visibility, or a blocker report?

Why this matters: different lanes stop on different gates, so the router should
hand off the smallest proof that answers the current request.

## Round 5: Missing Evidence

Question: Is there a current report, failed trace, review comment, or user
correction that should anchor the route?

Why this matters: Skill Factory should route from current evidence when possible
instead of turning stale fixtures or broad impressions into source changes.

## Round 6: Confirmation

Question: Does this capture the routing target, artifact, authority boundary,
and validation proof well enough for me to select one lane?

Why this matters: confirmation prevents the router from silently expanding scope
or loading the wrong downstream skill.
