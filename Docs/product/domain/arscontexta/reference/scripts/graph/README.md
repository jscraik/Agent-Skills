# Graph Script Reference (Ars Contexta)

Reference implementations for advanced graph analysis scripts that generated vaults can place under `Infrastructure/ops/Infrastructure/scripts/graph/`.

## Table of Contents
- [Scripts](#scripts)
- [Usage](#usage)
- [Feedback loop](#feedback-loop)
- [User feedback capture (AskQuestion)](#user-feedback-capture-askquestion)
- [Output contracts](#output-contracts)
- [Validation](#validation)
- [Notes](#notes)

## Scripts

- `find-communities-leiden.sh`
  - Preferred community detection entrypoint.
  - Uses true Leiden when `python3` has `igraph` + `leidenalg`.
  - Falls back to deterministic label propagation with modularity scoring when optional deps are missing.
- `pagerank.sh`
  - Directed PageRank over wiki links.
  - Reports convergence metadata and ranked notes.
- `betweenness.sh`
  - Undirected Brandes betweenness centrality.
  - Highlights structural brokers/bridge notes.
- `smoke-test.sh`
  - End-to-end local validation with a synthetic vault graph.
- `feedback-loop.sh`
  - Runs all graph analyzers, stores timestamped snapshots, compares drift vs previous run, and writes actionable recommendations.
- `record-feedback.sh`
  - Appends user-judged recommendation outcomes (good/neutral/bad) to a durable JSONL log.
- `feedback-scoreboard.sh`
  - Summarizes decision/outcome performance by recommendation action key.

## Usage

From a vault root containing `notes/`:

```bash
./Infrastructure/ops/Infrastructure/scripts/graph/find-communities-leiden.sh notes
./Infrastructure/ops/Infrastructure/scripts/graph/pagerank.sh notes 20
./Infrastructure/ops/Infrastructure/scripts/graph/betweenness.sh notes 20
./Infrastructure/ops/Infrastructure/scripts/graph/feedback-loop.sh . notes 20 Infrastructure/ops/metrics/graph
./Infrastructure/ops/Infrastructure/scripts/graph/record-feedback.sh . rec-001 accepted good high "Improved retrieval quality"
./Infrastructure/ops/Infrastructure/scripts/graph/feedback-scoreboard.sh . Infrastructure/ops/metrics/graph
```

From this repository (reference scripts):

```bash
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/find-communities-leiden.sh /path/to/vault/notes
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/pagerank.sh /path/to/vault/notes 20
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/betweenness.sh /path/to/vault/notes 20
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/feedback-loop.sh /path/to/vault notes 20 Infrastructure/ops/metrics/graph
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/record-feedback.sh /path/to/vault rec-001 accepted good high "Improved retrieval quality"
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/feedback-scoreboard.sh /path/to/vault Infrastructure/ops/metrics/graph
```

## Feedback loop

`feedback-loop.sh` turns one-off graph analysis into an improvement cycle:

1. Run `pagerank.sh`, `betweenness.sh`, and `find-communities-leiden.sh`.
2. Write timestamped raw outputs and normalized snapshot JSON.
3. Compare against the previous snapshot for drift signals.
4. Generate:
   - `Infrastructure/ops/metrics/graph/snapshots/<timestamp>.json`
   - `Infrastructure/ops/metrics/graph/Infrastructure/reports/<timestamp>.md`
   - `Infrastructure/ops/metrics/graph/recommendations/<timestamp>.json`
   - `latest.*` copies for automation consumers

Typical weekly command from vault root:

```bash
./Infrastructure/ops/Infrastructure/scripts/graph/feedback-loop.sh . notes 20 Infrastructure/ops/metrics/graph
```

## User feedback capture (AskQuestion)

After recommendations are shown, collect user judgment with non-blocking `request_user_input` feedback capture:

1. Did you apply recommendation `rec-XXX`? (`accepted` | `partial` | `rejected` | `deferred`)
2. Outcome quality? (`good` | `neutral` | `bad` | `unknown`)
3. Confidence in judgment? (`high` | `medium` | `low`)

Record it:

```bash
./Infrastructure/ops/Infrastructure/scripts/graph/record-feedback.sh . rec-001 accepted good high "Reduced orphan notes"
```

Review score trends:

```bash
./Infrastructure/ops/Infrastructure/scripts/graph/feedback-scoreboard.sh . Infrastructure/ops/metrics/graph
```

## Output contracts

All scripts emit:
- metadata header (`mode`, `notes`, `edges`, etc.)
- tabular body section for ranked entities or communities
- deterministic sort order for stable automation consumption

## Validation

Run smoke test:

```bash
./product/domain/ars-contexta-codex/reference/Infrastructure/scripts/graph/smoke-test.sh
```

## Notes

- Wiki link parsing supports `[[Title]]`, `[[Title|Alias]]`, and `[[Title#Heading]]`.
- Duplicate note titles are de-duplicated by first-seen file stem.
- These scripts are dependency-light by design; optional Leiden dependencies are best-effort.
