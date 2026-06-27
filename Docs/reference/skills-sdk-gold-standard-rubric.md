# Skills SDK Gold Standard Rubric

## Purpose

Use this rubric to decide whether a skill package is ready for live Tessl evals
and later private or public registry release. The package includes SKILL.md and
its associated references, scripts, assets, evals, README, metadata, Tessl
projection files, and validation receipts.

This rubric is not a replacement for command evidence. A package must still
pass the Skills SDK, Plugin Eval, Tessl, and runtime-lane gates named in the
validation docs. The rubric prevents a false positive where high scores or
structural checks hide that the skill lacks an observable contract for the work
it is supposed to perform.

## Domain Analysis

- Domain: AI skill package design, technical documentation, eval design,
  package governance, and release engineering.
- Artifact type: SKILL.md plus package-owned references, scripts, assets,
  agents metadata, README, contract, evals, Tessl projection files, and
  receipts.
- Intended audience: skill authors, SDK maintainers, human reviewers, LLM
  judges, PR reviewers, Tessl reviewers, registry release owners, and future
  agents loading the skill.
- Primary objective: prove that the package can reliably cause the intended
  agent behavior with bounded context, explicit safety boundaries, observable
  evidence, and replayable validation.
- Classification step: before scoring, classify the package's primary domain
  and artifact type. If the package spans multiple domains, score the shared
  package criteria once and add domain-specific criteria for each major
  component.

## Success Definition

A gold-standard skill package:

1. States the user outcome and trigger boundary clearly enough that the correct
   skill is selected and nearby skills are not over-triggered.
2. Keeps SKILL.md compact and routes deeper knowledge through package-local
   references, scripts, assets, and evals.
3. Defines observable success criteria in references/contract.yaml.
4. Provides scenarios and rubrics that test real behavior without leaking the
   scoring answer into the task.
5. Separates SDK validation, OSS profile proof, Tessl local proof, Tessl
   external scoring, registry readiness, and local runtime truth.
6. Preserves evidence so another reviewer can replay or audit the readiness
   claim.

## Best Practice Summary

The rubric applies these practices rather than merely naming them:

- Specification by Example: expected behavior is expressed through concrete
  scenarios, acceptance checks, and failure examples.
- Analytic rubric design: each criterion measures one observable dimension.
- Behaviorally Anchored Rating Scales: each score level describes visible
  package behavior, not taste.
- Technical writing practice: headings, procedures, examples, and recovery
  paths are reader-task oriented.
- Reliable eval design: evals are behavioral, evidence anchored, calibrated
  against failure modes, and resistant to rubric copying.
- Secure package design: permission boundaries, untrusted inputs, secrets,
  external writes, and destructive actions are explicit.
- Release engineering: readiness is based on lane-specific receipts and
  current command evidence, not summaries or score vibes.

## Analytic Rubric

Score each criterion from 1 to 5. Use the evidence listed under each criterion.
Do not award a score above 3 when required evidence is absent.

### 1. Domain And Artifact Classification

#### Purpose

Measures whether reviewers can identify what the skill package is, what domain
it serves, and which associated files are part of the release surface.

#### Evidence

SKILL.md frontmatter, description, references/contract.yaml, package tree,
README, eval metadata, plugin metadata when present, and release notes.

#### Scoring

5: The package names its domain, artifact type, audience, primary objective,
and release surface; associated files are clearly owned or excluded.

4: The package is classifiable with minor ambiguity in optional support files.

3: The main skill is classifiable, but associated files or audience are partly
implicit.

2: Reviewers must infer the domain or release surface from scattered files.

1: The package's purpose or artifact type cannot be determined reliably.

### 2. User Outcome And Trigger Boundary

#### Purpose

Measures whether the skill selects for the right work and avoids adjacent
skills, broad requests, or unsafe tasks.

#### Evidence

Description, When To Use, Avoid, Inputs, Preconditions, non-goals, routing
contracts, and sibling skill boundaries.

#### Scoring

5: Trigger, non-trigger, user outcome, inputs, and routing handoffs are explicit
and distinguish the skill from nearby skills.

4: Trigger and handoff behavior are clear, with minor edge-case ambiguity.

3: The trigger works for common cases but may over-trigger or under-route
adjacent work.

2: The skill relies on broad keywords or lacks clear non-goals.

1: The skill cannot be selected predictably from its description and headings.

### 3. Basic Requirement Rubric

#### Purpose

Measures whether the package defines what "does the skill's basic job" means
before external scoring starts.

#### Evidence

references/contract.yaml purpose, inputs, outputs, quality_criteria,
evidence_requirements, capability selectors, and package verify receipt.

#### Scoring

5: The contract defines observable quality criteria, evidence requirements,
automatic blockers, and selector criteria for every major mode.

4: Criteria and evidence requirements are present, with minor gaps in edge
cases or automatic blockers.

3: Basic criteria exist but are too broad to produce consistent reviewer
scores without interpretation.

2: Criteria are present only as prose or examples and are not tied to evidence.

1: No explicit basic requirement rubric exists.

### 4. Information Architecture And Progressive Disclosure

#### Purpose

Measures whether the package gives agents enough context without overloading
the always-loaded entrypoint.

#### Evidence

SKILL.md line count, headings, Progressive Disclosure section, reference paths,
scripts, assets, examples, and missing-reference checks.

#### Scoring

5: SKILL.md is compact, task-first, and routes all heavy, conditional, or
domain-specific material to existing package-local files.

4: Entry point is compact and routed, with minor organization issues.

3: Entry point is usable but includes some heavy detail or weak routing.

2: Important context is buried, duplicated, or loaded unconditionally.

1: Agents cannot find required context or the entrypoint is too broad to use.

### 5. Operational Accuracy And Grounding

#### Purpose

Measures whether commands, paths, versions, runtime claims, and process claims
match live repository evidence.

#### Evidence

Command outputs, file existence checks, wrapper contracts, docs references,
line citations, generated receipts, and blocker notes.

#### Scoring

5: Operational claims cite current files, commands, receipts, or explicit
blockers; proof lanes are separated.

4: Claims are mostly grounded, with minor stale wording or non-critical gaps.

3: Common claims are grounded, but some commands, paths, or readiness language
need manual verification.

2: Several operational claims are unsupported or stale.

1: The package fabricates, guesses, or misrepresents operational behavior.

### 6. Safety, Permission, And Trust Boundaries

#### Purpose

Measures whether the skill prevents unsafe actions, secret exposure, destructive
commands, external writes, and untrusted-input misuse.

#### Evidence

Safety Boundaries, permission profile, approval gates, untrusted input rules,
script behavior, command allow and deny lists, and registry/upload constraints.

#### Scoring

5: Safety, permissions, approvals, secrets, external writes, and destructive
actions are explicit and enforced by validation or command shape where possible.

4: Boundaries are clear, with minor gaps in rare operational paths.

3: Basic safety guidance exists but depends on reviewer interpretation.

2: Boundaries are incomplete or conflict with examples/scripts.

1: The package enables unsafe actions or hides dangerous side effects.

### 7. Scenario And Eval Quality

#### Purpose

Measures whether evals prove skill-specific behavior rather than structure,
keywords, or rubric copying.

#### Evidence

references/evals.yaml, references/evals/\*.md, scenario-source receipts,
scenario-quality receipts, calibration probes, scorer-quality receipts, and
Tessl staged task and criteria files.

#### Scoring

5: Scenarios cover normal, edge, pressure, and negative cases; criteria are
behavioral, file-observable, non-leaky, calibrated, and at least 20
gold-standard cases exist for behavioral live Tessl readiness.

4: Scenario set is behavioral and mostly complete, with minor coverage gaps.

3: Scenarios exercise common behavior but under-cover edge cases or evidence
boundaries.

2: Scenarios are keyword, structure, or happy-path dominated.

1: Evals are missing, impossible, leaky, duplicated, or unrelated to the skill.

### 8. Evidence And Readiness Lanes

#### Purpose

Measures whether readiness claims are tied to the correct lane and do not
substitute one kind of proof for another.

#### Evidence

SDK package verify, strict audit, scenario-quality, scorer-quality,
scorer-calibration, oss-local receipt, oss-cloud receipt, Tessl local proof,
Tessl dry-run, handoff-readiness, Tessl score receipt, and runtime proof.

#### Scoring

5: Each lane has current pass, fail, or blocked evidence; adjacent lanes remain
unclaimed unless separately proven.

4: Major lanes are separated, with minor reporting gaps.

3: Local and external evidence are mostly separate but summaries require
manual interpretation.

2: Scores, command completion, and release claims are blended.

1: The package claims readiness from the wrong proof lane.

### 9. Package Projection And Registry Readiness

#### Purpose

Measures whether the package can be projected into Tessl/private registry shape
without leaking repo-local state or treating eval staging as publication.

#### Evidence

README, plugin metadata, staged /tmp/ask-tessl-\* package, projection receipts,
included/omitted file lists, digest, workspace identity, and project-link
evidence.

#### Scoring

5: Registry-facing files, package identity, workspace, staged digest,
included/omitted surfaces, and project link are explicit and reproducible.

4: Projection is reproducible, with minor registry presentation gaps.

3: Projection shape is mostly clear but requires manual review before release.

2: Projection includes ambiguous local paths, stale staged files, or unclear
workspace identity.

1: The package cannot be safely projected or confuses staging with publishing.

### 10. Runtime Usability And Recovery

#### Purpose

Measures whether a future agent can use, validate, diagnose, and recover from
blocked skill execution.

#### Evidence

Procedure, Validation, Failure Mode, Handoff Rules, recovery examples, scripts,
error handling, runtime-link proof, and rollback procedure.

#### Scoring

5: Common success and failure paths include exact commands, statuses, blockers,
handoffs, and rollback or recovery actions.

4: Recovery is clear for common failures, with minor gaps in rare blockers.

3: The skill is usable, but recovery depends on general repo knowledge.

2: Blockers are named without actionable diagnostics or handoffs.

1: Agents cannot recover safely when the skill fails.

### 11. Maintainability And Self-Improvement

#### Purpose

Measures whether the package can absorb new eval results, steering, review
findings, and runtime failures without losing its contract.

#### Evidence

Scenario drift review, versioning, review cadence, change notes, steering
uptake, reference ownership, generated artifact policy, and update procedure.

#### Scoring

5: The package names how changes update scenarios, contracts, references,
versions, and proof receipts before rerun.

4: Maintenance path is clear, with minor gaps in version or drift details.

3: Updates are possible but depend on maintainer judgment.

2: Changes can easily leave stale evals, references, or package projections.

1: The package has no durable update or drift-handling path.

### 12. Domain-Specific Quality

#### Purpose

Measures whether the package applies the accepted standards for its own domain,
such as software engineering, technical writing, security, accessibility,
DevRel, eval design, or UX.

#### Evidence

Domain references, style guides, security standards, accessibility criteria,
code standards, examples, and domain-specific eval cases.

#### Scoring

5: Domain standards are translated into observable package behavior, examples,
and tests.

4: Domain standards are applied, with minor missing edge cases.

3: Domain fit is adequate but generic in places.

2: Domain guidance is named but not operationalized.

1: Domain guidance is absent or contradicted by package behavior.

## Automatic Failure Conditions

Any item below blocks Tessl live readiness and registry release claims until
resolved or explicitly accepted as a blocker by the operator:

- Fabricated command output, file path, citation, score, or Tessl run ID.
- Missing SKILL.md, invalid frontmatter, or unparseable required metadata.
- Missing or unparseable references/contract.yaml when the package declares a
  contract.
- Missing quality_criteria or evidence_requirements in references/contract.yaml.
- Multi-capability package without a selector contract, selector output, or
  top-level routing path.
- Direct SKILL.md references to private capsule bodies that bypass the
  top-level routing manifest.
- Broken examples, commands, scripts, or support-file paths needed for the
  advertised behavior.
- Unsafe destructive command, secret exposure, unapproved external write, or
  registry publish/upload path in a non-publish lane.
- Tessl staging points at live repo source instead of a controlled staged copy.
- Behavioral live Tessl readiness claimed with fewer than 20 gold-standard
  structured scenarios.
- Tessl score below readiness threshold, below baseline, missing final view
  artifact, or non-discriminative baseline not classified.
- Plugin Eval below B+, Plugin Eval failures, Tessl review below 95, or strict
  audit/package verify failure when those gates are in scope.
- Readiness claim blends SDK validation, OSS proof, Tessl local proof, Tessl
  external score, registry publication, and runtime truth into one status.

## Weighting

Weighting is appropriate because some criteria are release blockers while
others refine maintainability. The weighted score helps compare packages, but
automatic failures and lane-specific command gates override the numeric score.

| Criterion                                           | Weight |
| --------------------------------------------------- | -----: |
| Domain and artifact classification                  |      5 |
| User outcome and trigger boundary                   |      8 |
| Basic requirement rubric                            |     12 |
| Information architecture and progressive disclosure |      8 |
| Operational accuracy and grounding                  |     10 |
| Safety, permission, and trust boundaries            |     10 |
| Scenario and eval quality                           |     12 |
| Evidence and readiness lanes                        |     12 |
| Package projection and registry readiness           |      8 |
| Runtime usability and recovery                      |      6 |
| Maintainability and self-improvement                |      5 |
| Domain-specific quality                             |      4 |

Readiness floors:

- Tessl live eval candidate: no automatic failures, weighted score at least
  4.0, and no criterion below 4 for basic requirement, safety, scenario/eval
  quality, evidence lanes, or package projection.
- Private registry release candidate: no automatic failures, weighted score at
  least 4.5, no criterion below 4, and all required lane receipts current.
- Public registry release candidate: private release candidate plus explicit
  publish approval, registry identity, README presentation, rollback path, and
  local runtime truth after install.

## Validation Review

- Criteria overlap check: each criterion measures one dimension. Evidence lanes
  measure proof separation; scenario quality measures test content; package
  projection measures registry shape.
- Reviewer consistency check: each score describes observable package behavior,
  files, receipts, commands, or blockers.
- Subjectivity check: labels such as good and professional are avoided in
  scoring anchors; reviewers score visible evidence.
- Missing coverage check: the rubric covers source shape, contract quality,
  safety, evals, proof lanes, registry projection, runtime recovery, and
  maintainability.
- Discrimination check: score 1 captures unusable or unsafe packages, score 3
  captures usable but incomplete packages, and score 5 captures release-ready
  packages with replayable evidence.

## Recommended Use

- Human review: use the rubric before approving a skill hardening or release
  PR.
- AI evaluation: give the rubric to an LLM judge only with package files and
  command receipts; do not ask the judge to infer missing evidence.
- Pair review: have one reviewer score package/source behavior and another
  score evidence lanes and registry projection.
- CI/CD: enforce automatic failure conditions with deterministic validators;
  use weighted scoring as advisory unless encoded in a receipt.
- LLM evals: translate each criterion into binary or small-scale checks for the
  target skill's scenarios; prevent rubric text from leaking into task.md.
- Pull request review: require exact command evidence for any claim that a
  package is ready for Tessl live evals, private registry release, or public
  registry release.

## Required Command Evidence

For a release-readiness claim, attach current outcomes for the applicable
commands:

- ./bin/ask skills package verify <skill-path> --json --robot
- ./bin/ask skills audit <skill-path> --level strict --json --robot
- ./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot
- ./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot
- ./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot
- ./bin/plugin-eval analyze <skill-path> --format json
- ./bin/ask skills external-review <skill-path> --json --robot
- ./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --execute --json --robot
- ./bin/ask sdk eval handoff-readiness --skill <skill-path> --preview --json --robot
- ./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot

OSS profile proof must use codex exec --profile oss-local and codex exec
--profile oss-cloud, or SDK receipts that prove those profiles were invoked.
Plugin Eval and Tessl review evidence must remain separate from live Tessl
scoring and registry publication evidence.
