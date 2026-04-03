---
source: https://docs.coderabbit.ai/guide/code-review
---

# Code Review

Experience CodeRabbit's automated code review by creating your first pull request.

## Create a pull request

Now that CodeRabbit is integrated with your repository, it's time to see it in action. You'll create a pull request with intentionally imperfect code to demonstrate how CodeRabbit identifies issues and provides actionable feedback.

The following steps guide you through creating a pull request that adds a small Python library with a few common code quality issues.

Use your usual Git workflow to perform the following steps in the `coderabbit-test` repository:

1. Create a branch
   Create a branch named `add-utils`.

2. Create a new file
   In that new `add-utils` branch, create a new file called `simple_utils.py`, with the following content:

   ```python
   # simple_utils.py - A tiny utility library
   def reverse_string(text):
       """Reverses the characters in a string."""
       return text[::-1]

   def count_words(sentence):
       return len(sentence.split())

   def celsius_to_fahrenheit(celsius):
       return (celsius * 9/5) + 32
   ```

3. Commit the file
   Commit the added file to the `add-utils` branch. Use any text you want for the commit message.

4. Create a pull request
   Create a pull request that proposes to merge the `add-utils` branch into the `main` branch. Use any text you want for the pull request message.

After a few moments, CodeRabbit responds to the pull request using the `@coderabbitai` GitHub account. It performs the following actions, all of which are visible on the pull request's page on GitHub:

- If you didn't write a pull request summary, then CodeRabbit adds a new summary to the pull request.
- CodeRabbit posts a comment titled **Walkthrough** containing analysis and commentary about the content of the pull request.
- CodeRabbit attaches a detailed code review to the pull request as another comment.

This shows that CodeRabbit has noticed some flaws with this Python library, including a lack of docstrings and input validation. The review comment identifies these flaws, and suggests how you might improve them.
