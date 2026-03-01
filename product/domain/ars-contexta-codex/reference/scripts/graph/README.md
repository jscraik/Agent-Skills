# Graph Script Reference (Ars Contexta)

Reference implementations for advanced graph analysis scripts that generated vaults can place under `ops/scripts/graph/`.

## Table of Contents
- [Scripts](#scripts)
- [Usage](#usage)
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

## Usage

From a vault root containing `notes/`:

```bash
./ops/scripts/graph/find-communities-leiden.sh notes
./ops/scripts/graph/pagerank.sh notes 20
./ops/scripts/graph/betweenness.sh notes 20
```

From this repository (reference scripts):

```bash
./product/domain/ars-contexta-codex/reference/scripts/graph/find-communities-leiden.sh /path/to/vault/notes
./product/domain/ars-contexta-codex/reference/scripts/graph/pagerank.sh /path/to/vault/notes 20
./product/domain/ars-contexta-codex/reference/scripts/graph/betweenness.sh /path/to/vault/notes 20
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
