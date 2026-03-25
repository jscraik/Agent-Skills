# Official docs baseline

Use this reference when updating `docs-expert` or auditing repository docs against current platform guidance.

## Table of Contents
- [GitHub trust and community surfaces](#github-trust-and-community-surfaces)
- [GitHub discoverability surfaces](#github-discoverability-surfaces)
- [Documentation architecture baseline](#documentation-architecture-baseline)
- [Implications for docs-expert](#implications-for-docs-expert)
- [Sources](#sources)

## GitHub trust and community surfaces

- GitHub community profile remains the operator-facing checklist for public-repository health.
- Organization-level default community health files in a public `.github` repository can satisfy many trust surfaces when a repo does not define its own file.
- `SECURITY.md` should give a real vulnerability-reporting path and should not rely on vague public-issue guidance.
- `SUPPORT.md`, contribution guidance, issue templates, and PR templates still matter as first-line contributor trust signals.

## GitHub discoverability surfaces

- Repository description, homepage, topics, and social preview image remain the main GitHub-native discoverability fields.
- `CITATION.cff` is still the canonical GitHub citation surface when citation is relevant.
- `.github/FUNDING.yml` is still the canonical sponsor-button configuration surface when funding is relevant.
- `CODEOWNERS` remains the clearest ownership signal when a repo has multiple maintainers.

## Documentation architecture baseline

- Diataxis remains the best light-weight official structure model for separating tutorials, how-to guides, reference, and explanation.
- Keep one dominant document type per page.
- Link across document types instead of collapsing all user needs into one page.

## Implications for docs-expert

- Default to a neutral repo QA baseline, not a branded fallback.
- Treat fallback brand assets as opt-in, not automatic.
- When local checkout cannot prove GitHub UI state, use a manual GitHub UI checklist instead of guessing.
- Make discovery explicit for underspecified docs work, because audience and page type drive almost every good docs decision.

## Sources

- GitHub community profile: `https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/accessing-a-projects-community-profile`
- Default community health files: `https://docs.github.com/en/github/building-a-strong-community/creating-a-default-community-health-file`
- Security policy: `https://docs.github.com/github/managing-security-vulnerabilities/adding-a-security-policy-to-your-repository`
- Repository topics: `https://docs.github.com/en/enterprise-cloud%40latest/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics`
- Social preview: `https://docs.github.com/en/github/administering-a-repository/customizing-your-repositorys-social-media-preview`
- CITATION files: `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files`
- FUNDING sponsor button: `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository`
- CODEOWNERS: `https://docs.github.com/enterprise-server%403.17/articles/about-code-owners`
- Diataxis: `https://diataxis.fr/`, `https://diataxis.fr/start-here/`, `https://diataxis.fr/map/`
