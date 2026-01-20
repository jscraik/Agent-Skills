# Claudeception (Codex skill)

Claudeception is a **meta-skill** for **OpenAI Codex**.

It helps you do a quick post-task retrospective and turn non-obvious fixes / workflows into **new Codex skills** (a `SKILL.md` plus optional scripts/assets) so the next time you hit the same class of problem, Codex can retrieve the solution fast.

## Install (user-scoped)

Codex loads user skills from `~/.codex/skills/`.

1) Ensure the user skills folder exists:

```bash
mkdir -p ~/.codex/skills
```

2) Copy this folder to `~/.codex/skills/claudeception`:

```bash
# from the directory that contains the ./claudeception folder
rm -rf ~/.codex/skills/claudeception
cp -R ./claudeception ~/.codex/skills/claudeception
```

Restart Codex after installing so it re-scans skills.

## Make it habitual

### Global AGENTS.md reminder

Add this to `~/.codex/AGENTS.md`:

```md
## Continuous learning (Claudeception)
After finishing a task, do a 15–30s retrospective.
If the solution involved non-obvious debugging, workarounds, or a repeatable workflow:
- invoke $claudeception
- extract a new skill into ~/.codex/skills/<skill-name>/SKILL.md
```

### Optional notify hook

This repo includes:

- `scripts/claudeception-notify.py`

Example `~/.codex/config.toml`:

```toml
notify = ["python3", "~/.codex/skills/claudeception/scripts/claudeception-notify.py"]
```

If `terminal-notifier` (macOS) or `notify-send` (Linux) is available, the script will use it; otherwise it prints a short reminder.

## Usage

- Run `/skills` and pick `claudeception`, or
- Type `$claudeception` in your prompt.

## Example skills

Sample skills are stored in `references/examples/` as plain `.md` files so they are **not auto-loaded** as separate skills.

To install one as a real skill:

1) Create a folder: `~/.codex/skills/<skill-name>/`
2) Save the content as: `~/.codex/skills/<skill-name>/SKILL.md`

## License

MIT
