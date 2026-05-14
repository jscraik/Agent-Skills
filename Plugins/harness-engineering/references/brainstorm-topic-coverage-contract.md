# Brainstorm Topic Coverage Contract

Read when: `he-brainstorm` or folded `he-ideate` explores a fuzzy improvement,
options, or direction-setting request before a spec.

## Purpose

Good ideation should cover the real option space without becoming a backlog
dump. Use topic axes to ensure strong candidates are not missed, then surface
only warranted survivors.

## Topic Axes

Before selecting survivors, derive three to five evidence-backed axes from the
subject. Examples:

- architecture impact
- routing or execution determinism
- agent discoverability
- validation or eval quality
- governance simplicity
- user workflow quality
- moat or cognition quality

Skip axis generation only when the request is atomic and the reason is obvious.

## Coverage Recovery

If a relevant axis has no viable candidate, run one bounded recovery pass:

- generate at most two additional candidates for the missing axis;
- reject them if evidence remains weak;
- do not preserve weak ideas just to fill the grid.

## Survivor Selection

Every surfaced survivor must include:

- covered axis or axes;
- evidence basis: `direct`, `repo`, `external`, or `reasoned`;
- rejection reason for nearby weaker alternatives;
- downstream route: `he-brainstorm`, `he-spec`, `he-plan`, `he-reframe`,
  `he-linear-plan`, `he-code-review`, `he-eval-report`, or `Do Not Create`.

If two or more survivors remain and the choice would shape a downstream spec,
plan, Linear object, or implementation slice, apply
`interactive-steering-contract.md`. In headless mode, record the conservative
assumption instead of asking.

## Output Fields

```yaml
topic_axes:
  - "<axis>"
axis_coverage:
  "<axis>": covered|missing|recovered|not_applicable
coverage_recovery_status: not_needed|performed|skipped|blocked
survivor_selection_status: selected|needs_user_choice|autonomous_assumption|none
survivor_selection_reason: "<why this survivor is safe to route next>"
```

## Anti-Patterns

- Producing many ideas without explaining what space they cover.
- Choosing a survivor silently when multiple options would change downstream
  scope or validation gates.
- Treating novelty as leverage without repo, Linear, session, or external
  evidence.
