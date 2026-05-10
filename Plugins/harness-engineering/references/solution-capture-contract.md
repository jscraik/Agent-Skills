# Solution Capture Contract

Use this when `he-compound` captures a verified solved problem or refreshes a
high-overlap existing solution.

## Canonical Root

New Harness Engineering solution captures belong under:

```text
.harness/solutions/*.md
```

Legacy `docs/solutions/**` entries remain valid source evidence. When a target
repo already has a governed `docs/solutions/**` library, read it for overlap,
freshness, and admission rules, then write or refresh the `.harness/solutions/**`
artifact unless the user explicitly asks to maintain the legacy path.

## Admission Minimum

A solution capture is valid only when it includes:

- a linked governed asset or asset family;
- at least one concrete source artifact such as a spec, plan, review,
  validation result, task artifact, diff, PR, Linear issue, or governed path;
- a concise problem statement;
- a concise resolution statement;
- evidence that the problem is solved or the previous solution was refreshed;
- maintenance ownership context;
- a freshness marker suitable for later review.

Do not capture unresolved bugs, one-off execution notes, raw investigation logs,
or chat-only summaries as solution docs.

## Duplicate And Refresh Rule

Before writing a new solution:

1. Search `.harness/solutions/**` and legacy `docs/solutions/**` for high-overlap
   entries.
2. Refresh the existing `.harness/solutions/**` entry when the same problem and
   resolution already exist.
3. If only a legacy `docs/solutions/**` entry matches, use it as source evidence
   and create or refresh the `.harness/solutions/**` counterpart.
4. Create a new `.harness/solutions/**` entry only when no high-overlap solution
   exists.

## Discoverability Check

Before marking a solution capture complete, verify whether future agents can
find the solution root from the repo's active instruction surfaces:

- Search applicable `AGENTS.md`, README/front-door docs, instruction maps, and
  `.harness/knowledge/**` guidance when Project Brain exists.
- Confirm `.harness/solutions/**` is named as the canonical solved-problem
  surface or that the handoff explicitly records a `discoverability_blocked`
  status with the missing doc path.
- Confirm legacy `docs/solutions/**` is described as source evidence or
  compatibility only when both roots exist.
- Do not create broad governance docs only to mention solutions. Patch the
  smallest active instruction surface that future agents already read.

## Project Brain Sync

When the repo has `.harness/knowledge/**` or an explicit Project Brain contract,
solution capture must report one of:

```yaml
project_brain_status: updated|blocked|not_applicable|explicitly_deferred
project_brain_evidence:
  source: ".harness/solutions/<file>.md"
  target: ".harness/knowledge/<domain>/knowledge.md"
  reason: "<why synced, deferred, blocked, or not applicable>"
```

For repos that use Project Brain, append or refresh the matching
`.harness/knowledge/<domain>/knowledge.md` entry from the solution doc unless the
user explicitly asks for solution-only capture. If Project Brain write/sync is
blocked, preserve the ready-to-write payload in the handoff instead of silently
dropping it.

UI plans use `ui-plan-routing-contract.md`: they feed Project Brain as
plan/decision context first, then become `.harness/solutions/**` knowledge only
after implementation or review proves a reusable solved pattern.

Apply the redaction gate before Project Brain or Local Memory sync: remove
credentials, tokens, secrets, personal data, and internal-only URLs.

## Output Status

Use this shape when structured output helps downstream agents:

```yaml
schema_version: 1
solution_status: created|refreshed|blocked|not_applicable
solution_artifact: ".harness/solutions/<file>.md"
legacy_sources:
  - "docs/solutions/<file>.md"
project_brain_status: updated|blocked|not_applicable|explicitly_deferred
discoverability_status: visible|blocked|not_applicable|explicitly_deferred
next_action: "<one next HE stage or none>"
```
