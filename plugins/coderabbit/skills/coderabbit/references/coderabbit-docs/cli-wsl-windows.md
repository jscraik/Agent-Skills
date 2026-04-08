---
source: https://docs.coderabbit.ai/cli/wsl-windows
---

# WSL on Windows

The CodeRabbit CLI runs on Windows Subsystem for Linux (WSL), allowing you to access AI code reviews in your development environment. WSL provides a full Linux environment on Windows, making it ideal for running command-line tools like CodeRabbit.

## Video of install steps

For a visual walkthrough, use the official guide page where the install flow is maintained: [WSL on Windows](https://docs.coderabbit.ai/cli/wsl-windows).

## Why use CodeRabbit CLI on WSL

WSL gives you Linux-native shell tooling on Windows, which is usually the cleanest path for reproducible CLI workflows.

- Keep Windows IDE ergonomics while running CLI automation in Linux.
- Avoid many Windows-specific PATH and shell-compatibility issues.
- Match CI-like environments more closely for local review/debug loops.

## Prerequisites

- Windows with WSL 2 enabled and at least one Linux distribution installed.
- Basic CLI dependencies in WSL: `curl`, `unzip`, and `git`.
- A repository checked out inside WSL (recommended for performance).

Quick checks:

```bash
wsl -l -v
which curl unzip git
```

## Installation

Install the CLI from WSL and confirm it is available:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
coderabbit --version
```

Expected result: the version command prints a semantic version and exits with status `0`.

## Authentication

Start browser-based login from WSL:

```bash
coderabbit auth login
coderabbit auth status
```

If your organization uses token-based auth, follow your internal credential policy before running review commands.

## Usage workflow

End-to-end first run:

```bash
cd ~/projects/my-repo
git status
coderabbit --type uncommitted --plain
```

Typical flow:
1. Make or pull changes.
2. Run `coderabbit` in WSL.
3. Iterate on feedback until the diff is clean.
4. Commit and push from the same WSL workspace.

### Running code reviews

### Review options

Control what CodeRabbit analyzes:

```bash
# Review only uncommitted changes
coderabbit --type uncommitted

# Review only committed changes
coderabbit --type committed

# Review all changes (default)
coderabbit --type all

# Specify a different base branch
coderabbit --base develop

# Get AI-optimized output (useful for AI coding assistants)
coderabbit --prompt-only
```

### Using Windows-based IDEs

You can edit files in Windows IDEs (VS Code, Visual Studio, etc.) while running CodeRabbit reviews in WSL:

1. **Open your project in Windows**: Use your preferred Windows IDE
2. **Run reviews in WSL**: Keep a WSL terminal open for running CodeRabbit
3. **Seamless file sync**: Changes in Windows immediately reflect in WSL

### Git configuration

If you use git in both Windows and WSL, you may need to configure line endings:

```bash
# In WSL
git config --global core.autocrlf input
```

This prevents line-ending conflicts between Windows and Linux.

## Troubleshooting

### CodeRabbit command not found

If `coderabbit` isn't recognized after installation:

1. **Verify installation**: Check if the binary exists:

   ```bash
   ls -la ~/.coderabbit/bin/coderabbit
   ```
2. **Reload shell configuration**:

   ```bash
   source ~/.bashrc
   # or
   source ~/.zshrc
   ```
3. **Manually add to PATH** (if needed):

   ```bash
   echo 'export PATH="$HOME/.coderabbit/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Authentication URL not clickable

If the authentication URL isn't clickable in your terminal:

1. **Copy manually**: Select and copy the URL, then paste into your Windows browser
2. **Upgrade terminal**: Consider using Windows Terminal for better WSL integration
3. **Alternative authentication**: The authentication process is browser-based, so any modern browser works

### Slow performance on Windows files

If CodeRabbit runs slowly when working with files in `/mnt/c/`:

1. **Move repository to Linux filesystem**: Copy your project to `~/projects/` for better performance
2. **Use WSL 2**: Ensure you're running WSL 2 (check with `wsl -l -v` in PowerShell)
3. **Consider git clone in WSL**: Clone repositories directly in WSL's filesystem

### CodeRabbit not finding issues

If CodeRabbit isn't detecting expected issues:

1. **Check authentication status**: Run `coderabbit auth status` (authentication improves review quality but isn't required)
2. **Verify git status**: CodeRabbit analyzes tracked changes - check `git status`
3. **Consider review type**: Use the `--type` flag to specify what to review:
   - `coderabbit --type uncommitted` - only uncommitted changes
   - `coderabbit --type committed` - only committed changes
   - `coderabbit --type all` - both committed and uncommitted (default)
4. **Specify base branch**: If your main branch isn't `main`, use `--base`:
   - `coderabbit --base develop`
   - `coderabbit --base master`
5. **Review file types**: CodeRabbit focuses on code files, not docs or configuration

## Advanced: WSL integration tips

### Access WSL from Windows Explorer

You can access your WSL files from Windows Explorer:

- Type `\\wsl$\` in the Explorer address bar
- Navigate to your distribution (e.g., `\\wsl$\Ubuntu\home\username\`)

### Run CodeRabbit from Windows PowerShell

You can invoke WSL commands from Windows PowerShell:

```bash
wsl coderabbit --version
wsl -e bash -c "cd ~/projects/my-repo && coderabbit"
```

### Set up VS Code Remote - WSL

For the best development experience:

1. Install the "Remote - WSL" extension in VS Code
2. Open a WSL terminal and navigate to your project
3. Run `code .` to open VS Code in WSL mode
4. Use the integrated terminal to run CodeRabbit commands
