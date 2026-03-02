# CI Integration Patterns

Patterns for integrating diagram-cli into CI/CD pipelines.

## GitHub Actions

### Basic Architecture Tests

```yaml
name: Architecture
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: diagram test . --format junit --output results.xml

      - uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: Architecture Tests
          path: results.xml
          reporter: java-junit
```

### PR Impact Analysis

```yaml
name: Architecture Impact
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for diff

      - uses: actions/setup-node@v4
      - run: npm ci

      - name: Analyze PR impact
        run: |
          diagram workflow pr . \
            --base ${{ github.event.pull_request.base.sha }} \
            --head ${{ github.event.pull_request.head.sha }} \
            --verbose

      - uses: actions/upload-artifact@v4
        with:
          name: pr-impact
          path: .diagram/pr-impact/

  risk-gate:
    needs: analyze
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci

      - name: Risk gate
        run: |
          diagram workflow pr . \
            --base ${{ github.event.pull_request.base.sha }} \
            --head ${{ github.event.pull_request.head.sha }} \
            --risk-threshold high \
            --fail-on-risk
```

### Artifact Generation

```yaml
name: Diagram Artifacts
on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci

      - name: Generate diagrams
        run: diagram all . --output-dir .diagram

      - name: Generate manifest
        run: diagram manifest . --output .diagram/manifest-summary.json

      - uses: actions/upload-artifact@v4
        with:
          name: diagram-artifacts
          path: .diagram/
```

## GitLab CI

```yaml
architecture:
  stage: test
  image: node:18
  script:
    - npm ci
    - diagram test . --format junit --output architecture-results.xml
  artifacts:
    when: always
    reports:
      junit: architecture-results.xml
    paths:
      - architecture-results.xml
```

## CircleCI

```yaml
version: 2.1

jobs:
  architecture:
    docker:
      - image: cimg/node:18
    steps:
      - checkout
      - run: npm ci
      - run:
          name: Architecture tests
          command: diagram test . --format junit --output results.xml
      - store_test_results:
          path: results.xml
      - store_artifacts:
          path: .diagram/

workflows:
  version: 2
  test:
    jobs:
      - architecture
```

## Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running architecture tests..."
diagram test .
if [ $? -ne 0 ]; then
  echo "Architecture tests failed. Commit blocked."
  exit 1
fi
```

Or with husky:

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "diagram test ."
    }
  }
}
```

## Conditional Execution

### Only on changed files

```yaml
- name: Check for relevant changes
  id: changes
  uses: dorny/paths-filter@v3
  with:
    filters: |
      code:
        - 'src/**'
        - 'lib/**'

- name: Architecture tests
  if: steps.changes.outputs.code == 'true'
  run: diagram test .
```

### Skip on draft PRs

```yaml
- name: Architecture tests
  if: github.event.pull_request.draft == false
  run: diagram test .
```

## Best Practices

1. **Fetch full history** for PR impact analysis (`fetch-depth: 0`)
2. **Upload artifacts** on both success and failure
3. **Use JUnit format** for test reporter integration
4. **Gate on risk threshold** for critical paths
5. **Run on all PRs** but allow draft bypass
6. **Comment results** on PRs for visibility
