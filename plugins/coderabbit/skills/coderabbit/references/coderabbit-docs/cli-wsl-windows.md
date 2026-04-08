---
source: https://docs.coderabbit.ai/cli/wsl-windows
---

# WSL on Windows

The CodeRabbit CLI runs on Windows Subsystem for Linux (WSL), allowing you to access AI code reviews in your development environment. WSL provides a full Linux environment on Windows, making it ideal for running command-line tools like CodeRabbit.

## Video of install steps

## Why use CodeRabbit CLI on WSL

## Prerequisites

## Installation

## Authentication

## Usage workflow

### Running code reviews

### Review options

Control what CodeRabbit analyzes:

```
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

```
# In WSL
git config --global core.autocrlf input
```

This prevents line-ending conflicts between Windows and Linux.

## Troubleshooting

### CodeRabbit command not found

If `coderabbit` isn't recognized after installation:

1. **Verify installation**: Check if the binary exists:

   ```
   ls -la ~/.coderabbit/bin/coderabbit
   ```
2. **Reload shell configuration**:

   ```
   source ~/.bashrc
   # or
   source ~/.zshrc
   ```
3. **Manually add to PATH** (if needed):

   ```
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

```
wsl coderabbit --version
wsl -e bash -c "cd ~/projects/my-repo && coderabbit"
```

### Set up VS Code Remote - WSL

For the best development experience:

1. Install the "Remote - WSL" extension in VS Code
2. Open a WSL terminal and navigate to your project
3. Run `code .` to open VS Code in WSL mode
4. Use the integrated terminal to run CodeRabbit commands
