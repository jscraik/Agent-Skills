---
source: https://docs.coderabbit.ai/guides/repository-settings
---

## About repository settings

CodeRabbit provides three ways to manage its code-review behavior with each of your organization’s repositories:

## Configuration file

Add a `.coderabbit.yaml` file to your repository for version-controlled
settings

## Central configuration

Apply organization-wide settings that inherit to all repositories
automatically

## Web interface

View or modify your per-repository settings using the CodeRabbit dashboard

### Configuration precedence

CodeRabbit applies settings in the following order:

Repository YAML file (highest priority)

If your repository contains a `.coderabbit.yaml` file at the top level of
its default branch, CodeRabbit applies all settings from this file

Repository web interface settings

If your repository doesn’t have a `.coderabbit.yaml` file, CodeRabbit
applies the configuration from the repository’s web interface settings

Central configuration (organization-wide)

Settings from your organization’s central configuration are applied to
repositories that don’t have repository-specific settings

Default values (lowest priority)

CodeRabbit applies its own default values to any configuration settings not
defined elsewhere

## Configure your repository with `.coderabbit.yaml`

## Learn more about YAML configuration

Complete guide to adding and customizing configuration files

## Browse and modify your settings using the web interface

To view or modify your repository settings using the CodeRabbit web interface:

Select repository

Click the gear-shaped **Settings** icon of the repository whose settings you
want to view or modify

Configure inheritance

If the **Use Organization Settings** toggle is on, click it to turn it off
to customize this repository’s settings

Modify settings

Browse and modify your settings. The settings page opens in **Concise** mode
by default, which shows the most commonly used settings. Click **Apply
Changes** when you are finished.

### Settings view modes

The web interface provides three ways to view and edit your repository settings. All three modes read from the same underlying configuration, so changes persist when you switch between them.

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
