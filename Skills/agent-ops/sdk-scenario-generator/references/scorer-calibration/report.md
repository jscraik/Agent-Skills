# Scorer Calibration Report

This bundle is a held-out calibration set for the SDK scenario generator release scorer.

## Expected Matrix

- True positives: 3
- True negatives: 3
- False positives: 0
- False negatives: 0
- Threshold: 0.9

## Proof Boundary

This bundle proves the local scorer-calibration receipt can measure whether the
declared scorer catches known pass and known fail examples. It does not prove
future model behavior, external Tessl execution, hosted CI, human review, or PR
merge readiness.
