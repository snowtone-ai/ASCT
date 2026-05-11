# Claude Code Adapter -- pm-zero v9.2

@AGENTS.md

## Claude-specific
- Claude Code reads CLAUDE.md. Common rules: AGENTS.md is the single source.
- Prioritize: planning, design, review, prose quality judgment.
- Maintain separate branch from Codex CLI at all times.
- Skill commands: read .claude/skills/index.md for the relevant section.
- Auto-execute all file, git, build, test, lint operations immediately.

## Shell Policy
- Primary: PowerShell for all project operations (git, pip, python, pytest, build, test, lint).
- Use the same PowerShell environment for Windows path access and system-level tasks.
- Default to PowerShell when either shell can accomplish the task.
- Project paths use Windows paths with backslash (\) in PowerShell.

## Repository Navigation
- Read REPO-GUIDE.md first on session start to understand project structure.
- Update REPO-GUIDE.md when directory structure changes.

## Optimized for
- Claude Code CLI v2.1.101
- Opus 4.6 model
- VSCode on Windows
- PowerShell terminal
- bypassPermissions mode
