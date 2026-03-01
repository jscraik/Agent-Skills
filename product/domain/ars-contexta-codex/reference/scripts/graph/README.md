# Graph Script Reference (Ars Contexta)

Reference implementations for advanced graph analysis scripts that generated vaults can place under `ops/scripts/graph/`.

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
./ops/scripts/graph/find-communities-leiden.sh notes
./ops/scripts/graph/pagerank.sh notes 20
./ops/scripts/graph/betweenness.sh notes 20
./ops/scripts/graph/feedback-loop.sh . notes 20 ops/metrics/graph
./ops/scripts/graph/record-feedback.sh . rec-001 accepted good high "Improved retrieval quality"
./ops/scripts/graph/feedback-scoreboard.sh . ops/metrics/graph
```

From this repository (reference scripts):

```bash
./product/domain/ars-contexta-codex/reference/scripts/graph/find-communities-leiden.sh /path/to/vault/notes
./product/domain/ars-contexta-codex/reference/scripts/graph/pagerank.sh /path/to/vault/notes 20
./product/domain/ars-contexta-codex/reference/scripts/graph/betweenness.sh /path/to/vault/notes 20
./product/domain/ars-contexta-codex/reference/scripts/graph/feedback-loop.sh /path/to/vault notes 20 ops/metrics/graph
./product/domain/ars-contexta-codex/reference/scripts/graph/record-feedback.sh /path/to/vault rec-001 accepted good high "Improved retrieval quality"
./product/domain/ars-contexta-codex/reference/scripts/graph/feedback-scoreboard.sh /path/to/vault ops/metrics/graph
```

## Feedback loop

`feedback-loop.sh` turns one-off graph analysis into an improvement cycle:

1. Run `pagerank.sh`, `betweenness.sh`, and `find-communities-leiden.sh`.
2. Write timestamped raw outputs and normalized snapshot JSON.
3. Compare against the previous snapshot for drift signals.
4. Generate:
   - `ops/metrics/graph/snapshots/<timestamp>.json`
   - `ops/metrics/graph/reports/<timestamp>.md`
   - `ops/metrics/graph/recommendations/<timestamp>.json`
   - `latest.*` copies for automation consumers

Typical weekly command from vault root:

```bash
./ops/scripts/graph/feedback-loop.sh . notes 20 ops/metrics/graph
```

## User feedback capture (AskQuestion)

After reviewing recommendations, collect user judgment with AskQuestion / `request_user_input`:

1. Did you apply recommendation `rec-XXX`? (`accepted` | `partial` | `rejected` | `deferred`)
2. Outcome quality? (`good` | `neutral` | `bad` | `unknown`)
3. Confidence in judgment? (`high` | `medium` | `low`)

Record it:

```bash
./ops/scripts/graph/record-feedback.sh . rec-001 accepted good high "Reduced orphan notes"
```

Review score trends:

```bash
./ops/scripts/graph/feedback-scoreboard.sh . ops/metrics/graph
```

## Output contracts

All scripts emit:
- metadata header (`mode`, `notes`, `edges`, etc.)
- tabular body section for ranked entities or communities
- deterministic sort order for stable automation consumption

## Validation

Run smoke test:

```bash
./product/domain/ars-contexta-codex/reference/scripts/graph/smoke-test.sh
```

## Notes

- Wiki link parsing supports `[[Title]]`, `[[Title|Alias]]`, and `[[Title#Heading]]`.
- Duplicate note titles are de-duplicated by first-seen file stem.
- These scripts are dependency-light by design; optional Leiden dependencies are best-effort.
