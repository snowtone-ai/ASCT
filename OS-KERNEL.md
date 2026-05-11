# OS-KERNEL.md

## Quality Gates
1. Spec / Reference Gate
2. Code Gate
3. Architecture Gate
4. Test Gate
5. Error Gate
6. Security Gate
7. Observability Gate
8. Handoff Gate

## Verification Modes
- quick: doc edits, small config changes → confirm target files, state impact scope
- standard: normal implementation → ruff check, pyright, pytest, related tests
- final: pre-merge, pre-push → full verify, e2e, browser smoke, screenshot

## Cross-vendor Review Triggers
- Authentication
- Billing
- DB schema
- RLS / permissions
- Deploy
- Security
- 300+ line diff
- New external API
- 3 consecutive errors
- Production data, personal info, public URL impact

## Shell Policy
- Primary shell: PowerShell for all project operations.
- Shell: PowerShell on the Windows host.
- Default to PowerShell when either shell can accomplish the task.
- Node.js scripts (.mjs) run from PowerShell via the `node` command.
- Python commands run from PowerShell via `python` / `pip` / `pytest` / `uvicorn`.

## PowerShell Rules (project operations)
- Use PowerShell cmdlets or Windows CLI tools consistently.
- Path separator: backslash (\) for Windows paths.
- Environment variables: $env:KEY = "val".
- Redirect stderr: 2>$null.
- Create directories: New-Item -ItemType Directory -Force.
- Chain commands: cmd1; if ($LASTEXITCODE -eq 0) { cmd2 }.
- Node.js scripts run with `node scripts/name.mjs`.
- Python scripts run with `python -m module.name` or `python scripts/name.py`.
