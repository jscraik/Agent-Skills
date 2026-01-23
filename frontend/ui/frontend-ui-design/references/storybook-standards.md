# Storybook Standards (Dec 2025)

Last verified: 2026-01-01

Use when adding or updating React components.

## Required stories
- Default
- Loading
- Empty
- Error
- Disabled
- Edge case (long text or overflow)

## Tests
- Include a11y tests for each story.
- Add interaction tests for key states.
- Visual regression for UI changes.
- Use Storybook Test Runner for interaction + a11y in CI.
- Prefer `play` functions + Testing Library queries for interactions.
- Configure addon-a11y to fail on violations in CI via `parameters.a11y.test = "error"`.
- Storybook 9: a11y tests run out of the box with addon-a11y + test-runner.
- Storybook 8: use `@storybook/test-runner` + `axe-playwright` if needed.

## Docs
- Include usage notes and token references.
- Document accessibility behaviors and keyboard interactions.

## References
- Accessibility testing: https://storybook.js.org/docs/writing-tests/accessibility-testing
- Interaction testing: https://storybook.js.org/docs/writing-tests/interaction-testing
- Test runner: https://storybook.js.org/docs/writing-tests/test-runner
 - Test runner addon page: https://storybook.js.org/addons/%40storybook/test-runner
