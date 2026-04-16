---
source: https://docs.coderabbit.ai/guide/chat
---

Integrate CodeRabbit into a GitHub repository that you own

Observe CodeRabbit perform a code review of a pull request that you initiate

>>> Converse with CodeRabbit about the code review

Prompt CodeRabbit to generate its own improvements to the pull request

## Engage in interactive dialogue

One of CodeRabbit’s most powerful features is its ability to engage in natural, context-aware conversations about your code. Rather than just receiving static feedback, you can ask follow-up questions, request clarifications, challenge recommendations, or explore alternative approaches.
This interactivity transforms code review into a collaborative dialogue, helping you understand not just *what* to change, but *why* changes are recommended.

## Ask CodeRabbit for clarification

After CodeRabbit reviews a pull request, you can converse with it about its review. You can question its recommendations, ask for explanations, or request it to adjust its review approach for your project’s specific needs.

1. Post the following as a new GitHub comment attached to the pull request:

   ```
   @coderabbitai Why do all of these functions need docstrings? Isn't it obvious enough what they do?
   ```

   After a few moments, CodeRabbit posts its reply, explaining its motivations for its recommendation. The reply might resemble the following:
   > You’re right that these functions are quite self-explanatory from their names alone. Docstrings aren’t strictly necessary for every function, especially in smaller projects with clear function names.
   > While docstrings do provide benefits (IDE tooltips, documentation generation, help for future developers), they can sometimes feel redundant for very straightforward functions. It’s ultimately a matter of coding style and project requirements.
   > If you prefer to skip docstrings for obvious utility functions in this project, that’s perfectly reasonable. Would you like me to adjust my review approach regarding documentation for this repository?

   In this case, CodeRabbit is offering to adjust its future behavior when reviewing changes to this repository. Instead, follow the next step to ask CodeRabbit to implement part of its suggestions.

## What you can discuss with CodeRabbit

CodeRabbit can engage in various types of conversations about your code:

* **Question recommendations** - Ask why certain changes were suggested
* **Explore alternatives** - Discuss different approaches to solving the same problem
* **Request context** - Get explanations about best practices or design patterns
* **Clarify implementation details** - Understand how to apply suggestions in your specific context
* **Discuss trade-offs** - Explore the pros and cons of different solutions

You can mention CodeRabbit using `@coderabbitai` in any pull request comment
to start a conversation. It understands the context of your entire pull
request and can reference specific files, functions, or previous comments in
its responses.
