# Local bridge patch: skill-creator template extraction

## Reason

`scripts/init_skill_templates.py` is a local, behavior-preserving extraction
from `scripts/init_skill.py`. It keeps the governed `skill-creator` bridge
within the repository's module budget without changing the template payloads,
the initializer CLI, or the bridge's runtime location.

## Upstream source

The bridge remains governed by
`Infrastructure/GOVERNANCE/skills-system-upstream.lock.json`, pinned to
`openai/skills` at `e940b8a86138adf03972802b990a1dfc57fcbf09`. The extracted
templates originated in this repository's tracked bridge file
`skills-system/skill-creator/scripts/init_skill.py`; they are not a fork of an
upstream `SKILL.md` body.

## Expected refresh path

When the upstream lock is refreshed, first refresh the bridge through its
normal lock/projection workflow. Then reapply this extraction only if the
updated initializer still exceeds the module budget, preserving the template
bytes and rerunning the initializer and upstream-lock checks. Do not overwrite
or independently edit the extracted template module from a runtime projection.

## Validation record

The extraction is covered by the skill-creator lifecycle/scaffold tests and
the upstream-lock validator. The modularity-debt retirement change additionally
checks that the extracted module remains within the repository module budget.
