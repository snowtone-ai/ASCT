# Project AGENTS.md -- pm-zero v9.4

## Language
- Completion reports, error reports, and manual confirmation requests: Japanese.
- Code identifiers and command names: English.
- When 3+ HIGH assumptions accumulate, ask immediately.

## Source of Truth
- Product intent: docs/vision.md
- Execution tasks: tasks.md
- Current state: docs/state.md
- Decisions: docs/decisions.md
- Failures: docs/issues.md
- Repository map: docs/repo-map.md
- Report: HANDOFF-JA.md

## Startup Read
- Read this file.
- Read docs/state.md.
- Read docs/decisions.md.
- Read docs/repo-map.md Summary.

## Repository Navigation
- Read detailed repo-map sections only when target files are unclear.
- Update docs/repo-map.md after structural changes.
- Use rg before broad manual browsing.

## Task Ledger Rule
- Planning output goes to tasks.md.
- Implementation starts from tasks marked ready.
- Each ready task includes owner, dependencies, write scope, acceptance, verification, and evidence.
- Coordinator updates tasks.md.
- Worker agents report results to the coordinator.

## Scope Lock Rule
- One coordinator owns tasks.md and docs/state.md.
- Workers edit only their assigned write scope.
- Parallel work requires disjoint write scopes or isolated worktrees.
- Tasks touching the same file are serialized.

## Quality Standards
- Keep files and functions small enough to review.
- After 3 consecutive identical errors, record in docs/issues.md and pause.
- Auth, billing, DB schema, RLS/permissions, deploy, security, 300+ line diff, and new external API require cross-vendor review.
- Generated, build, cache, dependency, and secret files must stay ignored.

## Commands
- install: pip install -e ".[dev]"
- lint: ruff check src tests
- typecheck: pyright src
- test: pytest
- verify: node scripts/verify.mjs
- setup: node scripts/setup.mjs

Use only commands that exist in this repository.

## Execution Boundaries
- Use PowerShell.
- Use standard push with branch tracking.
- Keep safe values only in output.
- Use .env.example as template; runtime reads actual env values.
- Authentication, billing, production deploy final approval, and personal data handling are human tasks.
- Product code changes require an explicit task in tasks.md.

## Model Routing
- Default planning: Claude Code.
- Default implementation: Codex CLI.
- Either agent can perform the full workflow when needed.
- Critical changes require review by a model or vendor different from the implementer.
