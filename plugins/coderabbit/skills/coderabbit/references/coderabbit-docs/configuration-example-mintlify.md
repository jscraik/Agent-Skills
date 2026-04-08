---
source: https://docs.coderabbit.ai/configuration/example/other/mintlify-documentation
---

# Sample Configuration for Mintlify-based Documentation

````yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: "en-US"
review_status: "chill"
review_status_post: true
request_changes_workflow: false
high_level_summary: true
poem: false
finishing_touches:
  docstrings:
    enabled: false
path_filters:
  - "!**/node_modules/**"
  - "!**/.github/**"
  - "!**/.vscode/**"
  - "!**/pnpm-lock.yaml"
  - "!**/package-lock.json"
  - "!**/images/**"
  - "!**/*.svg"
  - "!**/*.png"
  - "!openapi.json"
path_instructions:
  - path: "**/*.mdx"
    instructions: |
      - When reviewing MDX files, check for duplicated content across documentation pages. If rate limits, feature descriptions, or other factual information is updated in one file, verify if similar or duplicated content exists in other MDX files that may also need updating. Raise a warning if potentially related content is found in other files but not updated.
      - CodeRabbit can be configured via web interface or via `.coderabbit.yaml` configuration file. In the documentation, both ways should be explained using the Mintlify Tabs component. Good Example:
        ```
        <Tabs>
          <Tab title="Using configuration file">
            ```yaml
            chat:
              integrations:
                jira:
                  usage: enabled
            ```
          </Tab>
          <Tab title="Using the Web Interface">
            ![Jira configuration](images/assets/images/jira-integration-setup.png)
          </Tab>
        </Tabs>
        ```
      - Recommend using tabs for other cases when the content is a good fit. For example, when showing mutually exclusive instructions (windows/linux, jira/linear, etc.)
      - Every time a page (.mdx file) is created, renamed, or deleted, the `/docs.json` file should be checked for needed adjustments. Example:
        ```
        File `management/seats-licenses-billing-faq.mdx` was renamed to `management/seat-assignment.mdx`. In this case, it should be also adjusted in `docs.json`. If the file existed for some time already with the old name, a redirect should be added accordingly.
        ```
      - For Pro plan feature warnings, check if inline Info, Warning or Tip blocks mentioning "Pro plan" and "pricing page" are used. If found, recommend replacing them with the ProPlanInfo snippet: `import ProPlanInfo from "/snippets/ProPlanInfo.mdx"` and `<ProPlanInfo />` instead of inline Info blocks.
  - path: "docs.json"
    instructions: |
      Check that all referenced files exist. Flag any broken file references.
  - path: "changelog.mdx"
    instructions: |
      Verify changelog entries follow consistent formatting: date, clear title, and include relevant links. Check that new entries are added chronologically.
````
