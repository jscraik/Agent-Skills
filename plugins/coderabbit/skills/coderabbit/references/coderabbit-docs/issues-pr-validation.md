---
source: https://docs.coderabbit.ai/issues/pr-validation
---

# PR Validation using Linked Issues

CodeRabbit provides intelligent assessment of linked issues to validate whether pull requests properly address their requirements. This guide explains how to effectively use linked issues and write clear issue descriptions for optimal results.

To use linked issues with Jira or Linear, you must first enable the corresponding integration. Note that these integrations are enabled for private repositories by default, but disabled for public repositories. See Issue trackers for setup instructions.

## Understanding linked issues

A linked issue is one that is explicitly referenced in your pull request description using platform-specific syntax:

**GitHub:**
```
fixes #123
closes #123
resolves #123
```

When CodeRabbit detects linked issues, it analyzes them against your pull request changes to determine if the requirements are met.

If a requirement from the linked issue isn't addressed, CodeRabbit flags it during review.

## Best practices for issue writing

### Issue titles

Create descriptive, technical titles that clearly state the goal:

**Good examples:**
- "Add PrismaLint integration to configuration flow"
- "Fix race condition in user authentication"
- "Implement caching for GraphQL queries"

**Poor examples:**
- "Fix bug"
- "Update code"
- "Improve performance"

### Issue descriptions

Write comprehensive descriptions that provide clear technical context:

1. **Problem statement** - Clearly describe what needs to be changed, include technical details about affected components, reference specific files or functions if known
2. **Expected solution** - Outline the desired implementation approach, include code examples or pseudo-code when relevant, list specific acceptance criteria

**Example description:**
```
Problem:
The configuration system doesn't validate Prisma schema files before deployment,
leading to potential runtime errors.

Solution:
Integrate PrismaLint into the configuration flow to:
- Validate schema files during PR checks
- Enforce consistent naming conventions
- Prevent common Prisma anti-patterns

Affected Components:
- Configuration validation pipeline
- CI/CD workflow
- Schema validation logic

Acceptance Criteria:
- [ ] PrismaLint runs on all PR checks
- [ ] Failed validations block merging
- [ ] Clear error messages for schema issues
```

### Consistent terminology

Use consistent terminology between issues and pull requests:

**Good practices:**
- Use the same technical terms consistently
- Reference components with their exact names
- Maintain consistent naming patterns

**Poor practices:**
- Mixing different terms for the same component
- Using vague or non-technical language
- Inconsistent capitalization or formatting

## Linking issues effectively

### In pull requests

**Direct references:**
```
Fixes #123
Resolves organization/repo#456
Closes https://github.com/org/repo/issues/789
```

**Multiple issues:**
```
This PR addresses:
- Fixes #123
- Closes #456
- Resolves https://jira.company.com/browse/PROJ-789
```

### Cross-references

For better traceability:

1. Add PR references in issue comments - Link back to the pull request from the issue discussion
2. Use complete URLs for external systems - Include full URLs when referencing Jira, Linear, or other platforms
3. Maintain bidirectional links - Ensure related issues reference each other for complete context

## How CodeRabbit assesses linked issues

CodeRabbit evaluates linked issues through this process:

1. **Analyze issue content** - Reviews issue titles and descriptions for requirements and context
2. **Compare PR changes** - Examines the code changes in the pull request
3. **Validate requirements** - Determines if the changes meet the stated objectives
4. **Provide assessment** - Returns one of three possible outcomes:
   - **Addressed**: Objective completed (no explanation needed)
   - **Not addressed**: Objective not met (explanation provided)
   - **Unclear**: Uncertain if objective is met (explanation provided)

Only the issue title and description are considered in the assessment. Comments and discussion threads are not currently analyzed.

## Tips for better assessments

### Be specific
- Include clear, measurable objectives
- List specific technical requirements
- Reference affected code components

### Provide context
- Explain why changes are needed
- Document current behavior
- Describe expected outcomes

### Use technical details
- Include file paths when known
- Reference specific functions or classes
- Mention relevant technologies

### Keep it focused
- One main objective per issue
- Clear scope boundaries
- Specific acceptance criteria

## Related resources

- **Review instructions** - Learn how to add custom instructions to your reviews
- **Issue creation** - Automatically create issues from PR reviews
- **Issue trackers** - Set up Jira or Linear integrations for linked issues
