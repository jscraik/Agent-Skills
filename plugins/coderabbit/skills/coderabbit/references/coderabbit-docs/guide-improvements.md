---
source: https://docs.coderabbit.ai/guide/improvements
---

Integrate CodeRabbit into a GitHub repository that you own

Observe CodeRabbit perform a code review of a pull request that you initiate

Converse with CodeRabbit about the code review

>>> Prompt CodeRabbit to generate its own improvements to the pull request

## Request code improvements

One of CodeRabbit’s powerful features is its ability to not just identify issues, but also generate the code changes needed to fix them. Instead of manually implementing the suggestions from the review, you can ask CodeRabbit to do it for you.
In this step, you’ll use a CodeRabbit command to automatically generate documentation improvements for your Python code.

### Generate docstrings

Post the following as a new comment on your pull request:

```
@coderabbitai generate docstrings
```

This command instructs CodeRabbit to analyze your code and create documentation strings for all functions.

### What CodeRabbit does next

After a few moments, CodeRabbit automatically performs the following actions:

1. **Creates a new branch** - CodeRabbit generates a new branch based on your `add-utils` branch
2. **Commits the changes** - CodeRabbit adds properly formatted docstrings to your `simple_utils.py` file
3. **Opens a pull request** - CodeRabbit creates a new pull request from the new branch back into `add-utils`

You can review the generated docstrings in the new pull request, and if you’re satisfied with them, merge them into your original branch.

## Review the generated changes

Once CodeRabbit creates the new pull request with the docstrings:

1. Navigate to the new pull request
2. Review the generated documentation
3. Check that the docstrings accurately describe each function
4. Merge the changes if they meet your standards

This demonstrates how CodeRabbit can handle not just code review, but also automated code generation based on best practices.

### Other available commands

CodeRabbit supports many other commands to help you improve your code. For example:

* `@coderabbitai generate tests` - Create unit tests for your code
* `@coderabbitai fix` - Apply suggested fixes from the review
* `@coderabbitai help` - See all available commands

You can use CodeRabbit commands on any pull request comment to request
specific actions. This makes it easy to iterate on code improvements without
leaving GitHub.
