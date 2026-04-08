# CodeRabbit Discovery Interview

Read when: the request is ambiguous and you need one short clarification round before giving CodeRabbit guidance.

## Round template
Ask one plain-language question, then include a short `Why this matters:` line.

Example:
- Question: "Which platform are you using for CodeRabbit right now (GitHub, GitLab, Bitbucket, or Azure DevOps)?"
- Why this matters: "Platform differences affect command syntax, integration steps, and safe rollout advice."

## Round 1
- Question: "What should this skill help you do?"
- Why this matters: "This prevents over-scoping and keeps recommendations focused."

## Round 2
- Question: "Which platform should the guidance target?"
- Why this matters: "CodeRabbit setup details vary by platform and integration path."

## Round 3
- Question: "Do you want minimal guidance or a production rollout checklist?"
- Why this matters: "This sets the right level of detail and risk controls."

## Stop rule
- Stop after one round when enough detail is available to answer safely.
- Do not provide a full multi-round plan unless the user explicitly asks for it.

## Request user input mini-templates
- Use one short question per round with 2-3 option labels.
- Keep options mutually exclusive and concrete.
- Add one sentence for tradeoff impact per option.

## Copy paste payload examples
Template:
- Question: "What should this skill help you do?"
- Why this matters: "Keeping the goal clear prevents scope creep and makes the later validation and ownership decisions more reliable."

Payload example:
- question: "What should this skill help you do?"
- options:
  - "Create or adjust `.coderabbit.yaml`."
  - "Summarize PR commands and operator workflow."
  - "Compare features and rollout caveats."
