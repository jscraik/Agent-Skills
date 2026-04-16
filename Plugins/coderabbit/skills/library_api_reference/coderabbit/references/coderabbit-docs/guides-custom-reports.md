---
source: https://docs.coderabbit.ai/guides/custom-reports
---

```
Generate a report of all pull requests in the following format:

- As the first paragraph, start with "🟣" if merged, "⚫" if draft, "🟢" if open, "🔴" if closed
  - On the same line, add the PR title in bold (and only the title; don't put anything else in bold after that)
  - On the same line, add the PR browser link (do not use an api link)
  - On the same line, add the last activity date in the format "Day Month Year, Hour:Minute AM/PM (Timezone)" in italic (don't put anything else in italic after that and make sure it's not bold)
- Make a new bullet-point list of high-level changes in the PR
  - Start each change with a gitmoji followed by a very terse one-liner to mention at a high level what the change does and to what part of the application it applies to
  - Do not start with verbose non-speak such as "The pull request enhances" or "This PR introduces". Keep it terse and straight to the point. Start change descriptions with a verb
  - Do not end with justifications or reasons for the changes such as "... enhancing type safety". Stick to the facts, do not make up the outcome of a change
  - Limit to the 4 most relevant changes
  - Examples: "✨ Add a rotating tagline on the home page", "🔧 Add func-style to ESLint", "📝 Add download badge to `README.md`", "✅ Add unit tests for comment trees", "👷 Create a pipeline to publish to npmjs.org", "🐛 Fix comment submission in posts", "📄 License under AGPL-3.0-or-later", "📱 Change post view for mobile", "💄 Make sidebar links blue", "🩹 Fix unfollow button", "🔒️ Limit login cookies to a specific subdomain", "🥅 Handle errors when commenting in a post", "🙈 Stop ignoring `.env` and start ignoring `.env.local` and `.env.*.local`", "⬆️ Update lemmy-js-client to v0.19.4", "🏷️ Define interfaces for pull request events", "🔐 Add environment variables for Bitbucket Server", "🚚 Rename exported client instances in test files", "🏷️ Add type alias `EventKey` and its type guard `isEventKey`", "🏗️ Aggregate exports for pull request events in an index file"
- Start the next paragraph with "Blockers:" in bold
  - Summarize any issues preventing the PR from progressing
    - Some examples: "Waiting for merge", "Waiting for review", "Failing CI/CD", "Needs more tests", "Needs rebase", "@username is waiting for a response", etc.
  - If the PR is stale, note it here
- Do not add a "Report" heading
- Make sure there is one empty line between each paragraph

These are the available emojis and the type of change they represent. Do not using any other emoji. Make sure the change corresponds to the gitmoji.

<gitmojis>
🎨: Improve structure / format of the code.
⚡️: Improve performance.
🔥: Remove code or files.
🐛: Fix a bug.
🚑️: Critical hotfix.
✨: Introduce new features.
📝: Add or update documentation.
🚀: Deploy stuff.
💄: Add or update the UI and style files.
🎉: Begin a project.
✅: Add, update, or pass tests.
🔒️: Fix security or privacy issues.
🔐: Add or update secrets.
🔖: Release / Version tags.
🚨: Fix compiler / linter warnings.
🚧: Work in progress.
💚: Fix CI Build.
⬇️: Downgrade dependencies.
⬆️: Upgrade dependencies.
📌: Pin dependencies to specific versions.
👷: Add or update CI build system.
📈: Add or update analytics or track code.
♻️: Refactor code.
➕: Add a dependency.
➖: Remove a dependency.
🔧: Add or update configuration files.
🔨: Add or update development scripts.
🌐: Internationalization and localization.
✏️: Fix typos.
💩: Write bad code that needs to be improved.
⏪️: Revert changes.
🔀: Merge branches.
📦️: Add or update compiled files or packages.
👽️: Update code due to external API changes.
🚚: Move or rename resources (e.g.: files, paths, routes).
📄: Add or update license.
💥: Introduce breaking changes.
🍱: Add or update assets.
♿️: Improve accessibility.
💡: Add or update comments in source code.
🍻: Write code drunkenly.
💬: Add or update text and literals.
🗃️: Perform database related changes.
🔊: Add or update logs.
🔇: Remove logs.
👥: Add or update contributor(s).
🚸: Improve user experience / usability.
🏗️: Make architectural changes.
📱: Work on responsive design.
🤡: Mock things.
🥚: Add or update an easter egg.
🙈: Add or update a .gitignore file.
📸: Add or update snapshots.
⚗️: Perform experiments.
🔍️: Improve SEO.
🏷️: Add or update types.
🌱: Add or update seed files.
🚩: Add, update, or remove feature flags.
🥅: Catch errors.
💫: Add or update animations and transitions.
🗑️: Deprecate code that needs to be cleaned up.
🛂: Work on code related to authorization, roles and permissions.
🩹: Simple fix for a non-critical issue.
🧐: Data exploration/inspection.
⚰️: Remove dead code.
🧪: Add a failing test.
👔: Add or update business logic.
🩺: Add or update healthcheck.
🧱: Infrastructure related changes.
🧑‍💻: Improve developer experience.
💸: Add sponsorships or money related infrastructure.
🧵: Add or update code related to multithreading or concurrency.
🦺: Add or update code related to validation.
</gitmojis>
```
