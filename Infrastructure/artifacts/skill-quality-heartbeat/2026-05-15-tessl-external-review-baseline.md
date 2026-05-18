# Tessl External Review Baseline - Skill Factory, Plugin Factory, Harness Engineering

Date: 2026-05-15
Branch: codex/he-productization-pr
Scope:
- Plugins/skill-factory/skills/*
- Plugins/plugin-factory/skills/*
- Plugins/harness-engineering/skills/*

## Policy

This run used local/internal-only review commands. Tessl was used through the installed local CLI path only.

Hard boundaries:
- no npx
- no Tessl publish
- no registry upload
- no Tessl login requirement
- no archived fixture skills in scope

Primary command shape:

```bash
python3 Infrastructure/bin/ask skills external-review <skill-path> --audit-level compat --json
```

The command runs repo-native ask audit, plugin-eval, Tessl local lint, and Tessl local skill review. Tessl lint validates a temporary tile package; Tessl review evaluates a temporary copied SKILL.md folder.

## Evidence Status

This artifact preserves the interpreted baseline from the sweep. The original raw command outputs remain in the Codex session transcript for this run. Future repeats should write raw JSON reports with `--report-path` so the full Tessl/plugin-eval payloads are retained in repo artifacts as machine-readable evidence.

Recommended future report path pattern:

```bash
python3 Infrastructure/bin/ask skills external-review <skill-path> \
  --audit-level compat \
  --report-path Infrastructure/artifacts/skill-quality-heartbeat/<date>/<skill-name>.json \
  --json
```

## Main Calibration Finding

Tessl found quality gaps that local plugin-eval often missed.

The repeated gap:
- plugin-eval frequently reports A or 100/100
- Tessl still reports weak activation wording, low content quality, abstract workflows, missing output examples, and poor progressive disclosure

Implication:
- plugin-eval is useful for local structure, cost, and repo-specific signals
- Tessl is useful as an external best-practice calibration model
- our internal review/eval/optimization rules need to absorb recurring Tessl findings

## Skill Factory Baseline

| Skill | plugin-eval | Tessl Description | Tessl Content | Current Gap |
| --- | ---: | ---: | ---: | --- |
| skill-builder | 53/F | 85% | 35% | Verbose body, missing concrete examples, references not tile-contained |
| skill-refactor | 95/A | 50% | 35% | Vague description, unclear evidence wording, missing output examples |
| skillify | 100/A | 75% | 20% | Strong local score but poor external content quality, abstract workflow |
| skill-factory-router | 100/A | 75% | 70% | Mostly sound, needs concrete routing examples and self-contained references |

First hardening order:
1. skillify
2. skill-builder
3. skill-refactor
4. skill-factory-router

## Plugin Factory Baseline

| Skill | plugin-eval | Tessl Description | Tessl Content | Current Gap |
| --- | ---: | ---: | ---: | --- |
| plugin-builder | 100/A | 75% | 22% | Missing inline workflow, output examples, and concrete validation steps |
| plugin-installer | 100/A | 67% | 22% | Jargon-heavy, missing staged install example and output schema |
| plugin-factory-router | 100/A | 57% | 50% | Abstract routing language, missing decision table |
| plugin-creator | 100/A | 60% | 38% | Missing scaffold example and concrete manifest/output template |
| plugin-router | 100/A | 52% | 50% | Needs natural trigger terms and complete handoff output example |

First hardening order:
1. plugin-builder
2. plugin-installer
3. plugin-creator
4. plugin-factory-router
5. plugin-router

## Harness Engineering Baseline

| Skill | plugin-eval | Tessl Description | Tessl Content | Priority Note |
| --- | ---: | ---: | ---: | --- |
| he-brainstorm | 95/A | 57% | 50% | Replace HE jargon with concrete exploration/decision language |
| he-code-review | 81/C | 100% | 42% | Description strong; body needs an output example and jargon cleanup |
| he-compound | 100/A | 60% | 70% | Remove duplicated context-disposition text; clarify lifecycle terms |
| he-eval-report | 77/C | 75% | 35% | Needs concrete eval report example and clearer closure triggers |
| he-fix-bugs | 100/A | 75% | 50% | Add reproduction/root-cause/test/patch trigger terms and commands |
| he-heartbeat | 100/A | 85% | 42% | Add heartbeat output example and plain trigger terms |
| he-improve | 95/A | 75% | 35% | Add worked improvement cycle and concrete validation commands |
| he-linear-plan | 81/C | 75% | 20% | Critical: weak content; needs concrete Linear plan example |
| he-phase-heartbeat | 91/B | 60% | 20% | Critical: weak content and lint failure; clarify phase/checkpoint flow |
| he-phase-work | 91/B | 85% | 20% | Critical: weak content and lint failure; add concrete heartbeat/phase examples |
| he-plan | 81/C | 75% | 35% | Add complete plan output example and natural planning triggers |
| he-reconcile | 95/A | 52% | 35% | Clarify safe resume routing in plain language |
| he-reframe | 86/B | 25% | 35% | Critical: weakest description; clarify domain, inputs, and outputs |
| he-reinforce | 95/A | 75% | 35% | Add learning artifact example and natural trigger terms |
| he-router | 95/A | 90% | 50% | Add concrete route-preview example and define inspected surfaces |
| he-spec | 86/B | 85% | 35% | Add spec output example and natural requirements/spec triggers |
| he-strategy | 86/B | 40% | 42% | Critical: weak description; define HE/ADR and concrete synthesis outputs |
| he-work | 91/B | 75% | 42% | Add exact structured output template and concrete implementation verbs |

First hardening order:
1. he-linear-plan
2. he-phase-heartbeat
3. he-phase-work
4. he-reframe
5. he-strategy
6. he-eval-report
7. he-plan
8. he-spec
9. he-reconcile
10. he-improve

## Recurring Tessl Finding Classes

These should become internal plugin-eval checks or Skill Factory hardening rules.

1. Natural trigger coverage
   - Add trigger terms users actually say.
   - Examples: "fix skill tests", "create Linear issue", "continue later", "implementation plan", "write a spec".

2. Concrete capability wording
   - Descriptions should say what the skill does, not only the internal lane name.
   - Replace or supplement jargon like HE cognition, survivor routes, lifecycle recovery, evidence-bound learning artifacts.

3. Worked example requirement
   - Every operational skill should include or reference one compact example showing input -> expected output.
   - Output templates must include real field names and sample values, not only prose lists.

4. Compact inline workflow
   - Progressive disclosure is good, but the main SKILL.md still needs a small actionable spine.
   - Do not defer the entire workflow to references/workflow.md.

5. Self-contained package references
   - Tessl lint exposes links or referenced files that do not exist inside the temporary tile package.
   - For external-style portability, either include local references under the skill package or classify cross-repo references as intentional repo-local dependencies.

6. Verbosity and duplicated policy sections
   - Merge repeated Safety, Constraints, Anti-Patterns, Gotchas, Preconditions, and Failure Mode content.
   - Keep SKILL.md as the compact execution map.

## Target State

A skill should not be called improved until it has this evidence:

- ask audit passes
- plugin-eval does not hide Tessl-visible activation/content issues
- Tessl lint either passes or every package-boundary warning is classified
- Tessl review has acceptable Description and Content scores
- the skill includes natural trigger terms
- the skill includes a compact inline workflow
- the skill includes at least one concrete output example or template
- bulky details are moved to references without removing the actionable spine

Proposed threshold for this family during hardening:
- Tessl Description >= 80%
- Tessl Content >= 70%
- plugin-eval >= 90/100
- zero unclassified Tessl lint failures

## How This Becomes a Pathway

1. Baseline
   - This artifact records the before-state for the three plugin families.

2. Patch loop
   - Pick one priority skill.
   - Patch only one or two recurring finding classes.
   - Rerun `ask skills external-review <skill> --audit-level compat --json`.

3. Evidence update
   - Store the raw JSON report with `--report-path`.
   - Update this baseline or create a dated follow-up artifact with before/after movement.

4. Eval improvement
   - Any recurring Tessl issue not caught by plugin-eval becomes a new internal check, metric, or rubric item.

5. Release confidence
   - A skill is ready only when internal and Tessl-backed external signals agree, or any disagreement is explicitly classified.
