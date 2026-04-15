---
type: moc
name: security-ops
description: "Skills for security reviews, threat modeling, vulnerability analysis, and ownership mapping across codebases and infrastructure."
covers:
  - threat-modeling
  - security-review
  - ownership-analysis
  - secure-auth
---

# Security Ops

> Skills for security reviews, threat modeling, vulnerability analysis, and secure-by-default implementation guidance.

## Table of Contents
- [Threat Modeling & Reviews](#threat-modeling--reviews)
- [Auth & Secrets](#auth--secrets)
- [Ownership & Risk Analysis](#ownership--risk-analysis)

---

## Threat Modeling & Reviews

- [[security-threat-model]] — Repository-grounded threat modeling: trust boundaries, assets, attacker capabilities, abuse paths, mitigations, and Markdown threat model output.
- [[security-best-practices]] — Language and framework-specific security best-practice reviews for Python, JavaScript/TypeScript, and Go.
- [[recon-workbench]] — Authorized, evidence-backed Recon Workbench (rwb) workflows for macOS/iOS, web/React, or OSS targets under explicit scope.

## Auth & Secrets

- [[create-auth]] — Build Better Auth integrations for TS/JS apps with secure defaults: implementation or migration.
- [[best-practices]] — Review Better Auth setups and highlight secure integration best practices.
- [[1password]] — 1Password CLI setup for secret injection and auth: `op run/read/inject`, env vars, `.env` files.

## Ownership & Risk Analysis

- [[security-ownership-map]] — Analyze git repositories to map security ownership (people-to-file), compute bus-factor and sensitive-code risk; export CSV/JSON/graph artifacts.

---

## Pipelines

- Complete security review: [[security-threat-model]] → [[security-best-practices]] → [[security-ownership-map]].
- Auth implementation: [[create-auth]] → [[best-practices]] → [[1password]].
- Ad-hoc recon: [[recon-workbench]] → [[security-threat-model]].

## Cross-links

- Topic maps: [[backend-platform]] | [[agent-ops]] | [[product-strategy]]
