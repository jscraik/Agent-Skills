# Examples

## Example 1: Choose tier for a new internal utility repo

User request:
- "I’m building a tiny internal CLI for myself. Should I keep this lightweight or set up the full governance wrappers?"

Input signals:
- single runtime surface
- one maintainer
- low compliance pressure
- infrequent releases

Expected result:
- choose `lite`
- avoid introducing strict governance layers
- keep one command contract and one validation path

## Example 2: Audit drift in a mature multi-repo workspace

User request:
- "Please audit why our repo process keeps breaking. Local docs and CI no longer agree."

Observed symptoms:
- `.codex/environments/environment.toml` exists but `Infrastructure/scripts/check-environment.sh` disagrees
- CI required checks differ from local wrappers
- duplicated policy text across docs and scripts

Expected result:
- likely `growth` or `strict` depending on compliance pressure
- prioritize canonical-source realignment and check-name parity

## Example 3: Mixed npm and uv stacks in one repo

User request:
- "I need one remediation plan for our mixed Node + Python repo without forcing the wrong package manager."

Observed symptoms:
- Node package scripts documented for npm while automation uses pnpm
- Python instructions use manual venv activation despite uv lockfile

Expected result:
- explicit lane split with policy ownership by directory/surface
- normalize npm lane with lockfile discipline
- normalize Python lane with `uv run --python 3.12`

## Example 4: Over-scaffold detection

User request:
- "We added strict governance templates, but nobody follows them and PRs are slower. Should we back this down?"

Observed symptoms:
- strict controls present but bypassed
- operators cannot maintain policy artifacts
- frequent "fix the process" churn with no reliability gain

Expected result:
- de-escalate toward `growth`
- remove non-operational controls
- keep only enforceable validation gates

## Example 5: Personal style alignment from `~/dev`

User request:
- "Tailor this recommendation to how I usually scaffold repos."
- user has many git repos with AGENTS and preflight wrappers, but mixed npm/pnpm lockfiles

Expected result:
- run `bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev`
- include style-profile summary in recommendation output
- align to wrapper-first governance without forcing a single package manager across all repos
