# Plugin Eval Confidence Contract

HE confidence claims must separate static packaged-plugin cost from rooted
runtime handle cost.

## Required Evidence

- Run `Infrastructure/bin/plugin-eval analyze Plugins/harness-engineering --format markdown`.
- Run `Infrastructure/bin/plugin-eval explain-budget Plugins/harness-engineering --format markdown` when the grade is below `B`.
- Run `./bin/ask skills handles --check-command-handles --json` after projection changes.
- Run `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --json` before claiming release confidence for lifecycle changes.
- Run `./bin/ask skills sync --scope workspace --projection rooted --json` and classify any cache refresh blocker by plugin.

## Current Budget Interpretation

`plugin-eval` analyzes the packaged plugin source. For HE that includes the
plugin manifest, all first-level lifecycle `SKILL.md` entrypoints, and the
deferred references/scripts/tests shipped with the plugin. A static grade such
as `D / 63` is therefore a real packaged-source budget risk. It is not proof
that rooted runtime command handles load the same text during ordinary use.

Do not call this budget failure resolved unless one of these is true:

- the full plugin-eval static grade no longer fails invoke or deferred budget
  checks,
- plugin-eval has an explicit rooted-runtime profile and that profile passes,
  with the static packaged-source failure still documented,
- observed usage benchmarks show representative HE routed runs stay within the
  accepted runtime budget and the static packaged-source failure is explicitly
  excluded from the runtime confidence claim.

## Confidence Boundary

Near-complete HE confidence requires all of:

- static plugin-eval result recorded, including failures,
- rooted handle check passing,
- workspace rooted sync passing or non-HE cache blockers explicitly excluded
  with the cache sync status recorded,
- lifecycle release eval lane passing for changed lifecycle skills and adjacent
  route skills,
- any remaining plugin-eval budget failure recorded as either blocking,
  excluded from the claim, or assigned to a specific follow-up.

If the static plugin-eval result is still `D / 63`, the only acceptable HE
claim is:

> Runtime routed lifecycle confidence is supported by rooted handles and release
> evals. Static packaged-plugin budget confidence is not complete.

Do not compress or delete HE reference material only to improve a static score
when that material is required for correct routed execution. Move context only
when the resulting route remains discoverable, eval-covered, and projection-safe.
