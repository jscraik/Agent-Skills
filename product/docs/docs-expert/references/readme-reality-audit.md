# README reality audit

## Table of Contents
- [When to use](#when-to-use)
- [Audit sources](#audit-sources)
- [Required outputs](#required-outputs)
- [Writing rules](#writing-rules)

## When to use

Use this mode when the README is likely behind the current product or repository reality.

Typical triggers:
- code and tests show stronger capabilities than the README claims;
- examples, scripts, or commands have evolved;
- changelog or recent history introduced important value that the README still hides;
- the current README sounds generic, overstated, or stale.

## Audit sources

Check these sources in priority order:
1. executable product behavior in code and tests;
2. examples, demo scripts, and automation entry points;
3. changelog, release notes, and recent commit history;
4. existing README and linked docs.

Rules:
- separate verified capabilities from inferred ones;
- if history suggests a capability but current code does not support it clearly, mark that as uncertain;
- prefer concrete repo evidence over marketing language.

## Required outputs

Include:
- understated or omitted capabilities discovered during the audit;
- the README sections that need revision;
- concrete value framing tied to current behavior;
- practical usage guidance for the main user paths;
- concise confidence notes for anything that still needs confirmation.

## Writing rules

- lead with real user value, not generic setup boilerplate;
- use trustworthy wording: do not overclaim, hedge where evidence is partial;
- keep examples practical and current;
- tie major claims to a surface the repo actually exposes today.
