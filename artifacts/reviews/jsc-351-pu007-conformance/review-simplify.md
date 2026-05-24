# PU-007 Simplify Review

## Status

PASS: one cleanup applied, no remaining blocker findings.

## Findings

### Medium: Stale archive wrapper remained after SDK module extraction

- Evidence before remediation: Infrastructure/scripts/lib/ask/commands/skills_impl.py contained _verify_package_archive_candidate, but rg showed only the definition.
- Why it mattered: leaving unused package-verifier wrappers in the CLI layer would make future maintainers inspect two archive-verification paths and increase the chance of divergent safety behavior.
- Remediation: removed the unused wrapper; archive verification is now only delegated through _verify_archive_package.
- Validation: focused py_compile and focused pytest both passed after removal.

## Skipped

- Did not split the remaining skills_package_verify command orchestration out of skills_impl.py; that would be larger than PU-007 and overlaps the existing JSC-351 service-boundary sequence.

WROTE: artifacts/reviews/jsc-351-pu007-conformance/review-simplify.md
