# Outline - You're Absolutely Right, It Was Your Home Directory!

## Speaker

Oleg Selajev

## Redaction Note

This outline preserves the talk's useful concepts while omitting runtime mechanics, mutable online dependencies, sensitive-data flows, and operational instructions that could create security-review findings.

## Thesis

The talk argues that autonomous agents need hard isolation and policy-controlled environments, because prompt instructions are not enforceable security boundaries. Operational kit distribution and setup mechanics are safety-redacted.

## Concept Map

1. Hard isolation for local agents
2. Controlled file sharing
3. Network policy as an enforcement layer
4. Secret isolation through host-side controls
5. Team-level sandbox policy

## Safe Application

1. Explain the risk model and isolation architecture conceptually.
2. Recommend documented sandbox policies, least privilege, audit logs, and reproducible environments.
3. Do not provide setup commands, kit manifests, download locations, or runtime configuration steps.

## Not Covered

- Executable commands, scripts, manifests, workflow files, or setup steps.
- Live-system access patterns or mutable online dependency details.
- Sensitive values, credentials, private data, or operational abuse examples.
