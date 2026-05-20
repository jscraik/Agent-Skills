# Eval Artifact Proof

Read when: the task involves eval runners, smoke fixtures, scorer contracts,
baseline comparison, judge outputs, or .harness/evals artifacts.

## Doctrine

Artifacts decide. Telemetry explains. LLM judges advise until calibrated.
Repo-local suites own domain truth. External frameworks are adapters.

## Local Executable Spine

A trustworthy eval lane should provide one local, replayable loop:

1. read one fixture with provenance and privacy metadata;
2. run without network unless explicitly designed otherwise;
3. write a machine-readable and human-readable artifact bundle;
4. compute deterministic scorer verdicts;
5. record baseline state explicitly;
6. validate schemas and artifact hashes;
7. leave closure evidence under the repo-owned artifact path.

## Artifact Bundle

Prefer a bundle shaped like:

- result.json
- report.md
- command-log.json
- manifest.json
- scorer-results.json
- baseline-result.json
- latest.json

latest.json should point to first-order evidence so agents do not guess the
newest run directory.

## Ownership Split

Shared eval infrastructure owns:

- runner mechanics;
- canonical schema shape;
- artifact bundle contract;
- deterministic scorer interface;
- baseline result contract;
- closure artifact expectations.

Consuming repos own:

- suite intent;
- real fixtures;
- domain rubrics;
- acceptance thresholds;
- baseline promotion decisions;
- privacy approval for real evidence.

## Judge Policy

LLM judges may provide advisory scores, qualitative review, and rubric feedback.
They must not pass, fail, block, promote, or close required gates until
calibration artifacts prove they improve reliability.

Every judge output should record judge mode, model, prompt or prompt hash,
rubric version, evaluator version, calibration status, run ID, and artifact
references.

## Required Failure Discipline

- A missing baseline is explicit state, not success.
- A metric with denominator 0 is insufficient evidence, not pass.
- A missing artifact or stale artifact on disk fails artifact verification.
- A prettier rubric is not calibration.
