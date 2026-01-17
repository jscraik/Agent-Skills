# Standards Baseline (Jan 2026)

## Core Protocols and Schemas
- HTTP Semantics: RFC 9110 (https://www.rfc-editor.org/rfc/rfc9110)
- JSON: RFC 8259 (https://www.rfc-editor.org/rfc/rfc8259)
- JSON Schema: Draft 2020-12 (https://json-schema.org/draft/2020-12/json-schema-core.html)
- YAML: 1.2.1 (https://yaml.org/spec/1.2.1/)
- OpenAPI: latest published spec (3.2.0 with 3.1.2 patch; check `oas/latest`) (https://spec.openapis.org/oas/latest.html) (https://www.openapis.org/blog/2025/10/01/openapi-initiative-newsletter-september-2025)
- GraphQL: latest edition (Sep 2025) (https://spec.graphql.org/)

## Security Baselines
- OWASP Top 10 (2025) (https://owasp.org/www-project-top-ten/)
- OWASP API Security Top 10 (2023) (https://owasp.org/API-Security/)

## Compliance (if in scope)
- SOC 2: Trust Services Criteria (https://www.aicpa.org/resources/landing/trust-services-criteria)
- ISO/IEC 27001:2022 (ISMS requirements) + Amd 1:2024 (https://www.iec.ch/website-27001-2022)
- PCI DSS v4.0.1 (limited revision to v4.0; no new requirements) (https://www.pcisecuritystandards.org/)
- GDPR (Regulation (EU) 2016/679) (https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- CCPA/CPRA (California DOJ + CPPA regulations) (https://oag.ca.gov/privacy/ccpa) (https://cppa.ca.gov/regulations/)

## Notes
- If compliance scope is "all", include a superset checklist and flag legal review.

## What changed since 2024/2025 (summary)
- OpenAPI 3.2.0 released, with 3.1.2 patch; use `oas/latest` to avoid pinning to older patches. (https://www.openapis.org/blog/2025/10/01/openapi-initiative-newsletter-september-2025) (https://spec.openapis.org/oas/latest.html)
- OAuth 2.1 is the consolidated best-practice profile for OAuth (PKCE required; implicit flow discouraged) and is published as the IETF draft. (https://oauth.net/2.1/)
- PCI DSS moved from 4.0 to 4.0.1 with targeted clarifications, not new requirements. (https://www.pcisecuritystandards.org/)
- GraphQL spec updates (Sep 2025) clarify and consolidate normative guidance. (https://spec.graphql.org/)
- OWASP Top 10 2025 released, superseding the 2021 edition. (https://owasp.org/www-project-top-ten/)

## Tooling compatibility note (OpenAPI 3.2.0 vs 3.1.x)
- Some client generators and validators still lag on full 3.2.0 support; default to 3.1.2 for codegen if a toolchain is not 3.2.0-ready, and keep a 3.2.0 source-of-truth spec.
