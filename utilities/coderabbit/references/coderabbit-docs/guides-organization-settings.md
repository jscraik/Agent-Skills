---
source: https://docs.coderabbit.ai/guides/organization-settings
---

Configure CodeRabbit settings for your entire organization to establish consistent code review standards across all repositories. For a general overview of configuring CodeRabbit, see [Configure CodeRabbit](/guides/configuration-overview).

## About organization settings

You can use the CodeRabbit web interface to set the CodeRabbit configuration for all Git repositories associated with your organization. By default, all repositories apply your organization’s CodeRabbit configuration.

You can override organization settings for individual repositories if needed.
For more information, see [Repository
settings](/guides/repository-settings).

## Browse and modify your organization settings

Access the CodeRabbit web interface

Navigate to organization settings

In the sidebar, click **Organization Settings**.

Modify settings

Browse and modify your settings. The settings page opens in **Concise** mode
by default, which shows the most commonly used settings. When you’re finished
making changes, click **Apply Changes** to save your configuration.

### Settings view modes

The web interface provides three ways to view and edit your organization settings. All three modes read from the same underlying configuration, so changes persist when you switch between them.

* **Concise (default)**: A curated subset of the most commonly changed settings, organized into categories like General, Reviews, Pre-merge checks, and Finishing touches.
* **All Settings**: The complete list of every available setting. Switch to this mode if you need to access less common settings such as individual tool configurations, chat settings, knowledge base, code generation, and issue enrichment.
* **YAML Editor**: Direct YAML editing with syntax highlighting, real-time schema validation, and clipboard support. Only non-default values are shown. The YAML format matches `.coderabbit.yaml` for easy transfer between the web interface and repository files.

To switch modes, use the **Change mode** dropdown at the bottom of the sidebar.

Use **Cmd+K** (Mac) or **Ctrl+K** (Windows/Linux) to open the command
palette and search for any setting across all modes.

In YAML Editor mode, validation errors must be resolved before saving
changes.

### Preview

In Concise and All Settings modes, a live Preview panel appears on the right side of the settings page. This panel shows a mock PR review comment that visualizes how your settings affect the information CodeRabbit displays in pull request reviews.

* Toggle the preview using the **Preview** button in the top-right corner. Preview is enabled by default.
* Settings that affect the PR review output are tagged with **Preview**, so you can identify which settings have a visible impact.
* When you change a setting with preview support, the preview panel automatically scrolls to the affected section and highlights the change.

The preview includes sections such as the PR summary, CodeRabbit-generated summary, walkthrough with changes table, sequence diagrams, pre-merge check results, and finishing touches.
