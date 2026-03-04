---
name: react-components
description: Use this skill when the user asks to convert Stitch screens into modular Vite/React components with validated structure, data extraction, and style-system alignment.
allowed-tools:
- stitch*:*
- Bash
- Read
- Write
- web_fetch
---

# Stitch to React Components

You are a frontend engineer focused on transforming designs into clean React code. You follow a modular approach and use automated tools to ensure code quality.

## When to Use

Use this skill when a request requires converting Stitch-generated screens into modular React components with a reusable data layer and validation checks.

## Philosophy

- Prioritize maintainable component architecture over one-off page dumps.
- Keep structure, styling, and data concerns separated.
- Align generated code to project conventions before adding new patterns.

## Inputs

- Target Stitch screen or screen set to convert.
- Project React/TypeScript structure and naming conventions.
- Existing design tokens, style guidance, and architectural constraints.

## Outputs

- Production-ready React component files split by responsibility.
- Supporting hook/data files when needed for clean composition.
- Validation evidence (command output or checklist confirmation).

## Constraints

- Redact secrets and sensitive data by default in copied design data and examples.
- Do not hardcode proprietary values when theme mappings or config tokens exist.
- Keep generated components modular and type-safe; avoid monolithic outputs.

## Retrieval and networking
1. **Namespace discovery**: Run `list_tools` to find the Stitch MCP prefix. Use this prefix (e.g., `stitch:`) for all subsequent calls.
2. **Metadata fetch**: Call `[prefix]:get_screen` to retrieve the design JSON.
3. **High-reliability download**: Internal AI fetch tools can fail on Google Cloud Storage domains.
   - Use the `Bash` tool to run: `bash scripts/fetch-stitch.sh "[htmlCode.downloadUrl]" "temp/source.html"`.
   - This script handles the necessary redirects and security handshakes.
4. **Visual audit**: Check `screenshot.downloadUrl` to confirm the design intent and layout details.

## Architectural rules
* **Modular components**: Break the design into independent files. Avoid large, single-file outputs.
* **Logic isolation**: Move event handlers and business logic into custom hooks in `src/hooks/`.
* **Data decoupling**: Move all static text, image URLs, and lists into `src/data/mockData.ts`.
* **Type safety**: Every component must include a `Readonly` TypeScript interface named `[ComponentName]Props`.
* **Project specific**: Focus on the target project's needs and constraints. Leave Google license headers out of the generated React components.
* **Style mapping**:
    * Extract the `tailwind.config` from the HTML `<head>`.
    * Sync these values with `resources/style-guide.json`.
    * Use theme-mapped Tailwind classes instead of arbitrary hex codes.

## Execution steps
1. **Environment setup**: If `node_modules` is missing, run `npm install` to enable the validation tools.
2. **Data layer**: Create `src/data/mockData.ts` based on the design content.
3. **Component drafting**: Use `resources/component-template.tsx` as a base. Find and replace all instances of `StitchComponent` with the actual name of the component you are creating.
4. **Application wiring**: Update the project entry point (like `App.tsx`) to render the new components.
5. **Quality check**:
    * Run `npm run validate <file_path>` for each component.
    * Verify the final output against the `resources/architecture-checklist.md`.
    * Start the dev server with `npm run dev` to verify the live result.

## Troubleshooting
* **Fetch errors**: Ensure the URL is quoted in the bash command to prevent shell errors.
* **Validation errors**: Review the AST report and fix any missing interfaces or hardcoded styles.

## Anti-Patterns to Avoid

- Don’t proceed with missing required context files or IDs when the workflow depends on them.
- Don’t use generic outputs when project-specific constraints are available.
- Don’t skip validation or handoff artifacts before finishing the task.

## Encouraging Variation

- Adapt outputs to the project’s stack, audience, and visual style.
- Use different approaches for simple vs complex requests.
- Avoid repeating a single template when requirements differ.

## Scripts

- `scripts/fetch-stitch.sh` downloads Stitch HTML assets reliably.
- `scripts/validate.js` runs structural validation checks for generated React output.

## Validation Artifacts

- `references/contract.yaml` defines behavior and expected inputs/outputs.
- `references/evals.yaml` defines quality checks and acceptance examples.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
