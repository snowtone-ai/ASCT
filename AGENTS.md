# Project AGENTS.md -- pm-zero v9.2

## Language
- Completion reports, error reports, manual confirmation requests: Japanese.
- Code identifiers: English.
- When 3+ HIGH assumptions accumulate, ask immediately.

## Source of Truth
- Spec: docs/vision.md
- Current state: docs/state.md
- Decisions: docs/decisions.md
- Failures: docs/issues.md
- Quality: OS-KERNEL.md
- Domain vocabulary: CONTEXT.md
- Report: HANDOFF-JA.md

## Execution Rules
- One AI holds write lock at a time.
- Read docs/state.md and docs/decisions.md before implementation.
- Ground UI/API/DB/critical workflows with 3 real examples in docs/decisions.md before implementation.
- Target 300 lines per file, 50 lines per function.
- Add tests for every new feature.
- After 3 consecutive errors, record in docs/issues.md Escalation and pause.
- Declare verification mode (quick / standard / final) before completion.
- Final report follows HANDOFF-JA.md.

## Commands
- install: pip install -e ".[dev]"
- lint: ruff check src/ tests/
- format: ruff format src/ tests/
- typecheck: pyright src/
- test: pytest
- test-cov: pytest --cov=src
- dev: uvicorn src.main:app --reload
- migrate: alembic upgrade head
- seed: python -m src.seed.generate
- verify: node scripts/verify.mjs
- setup: node scripts/setup.mjs

## Execution Boundaries
- Use standard push only (standard git push, with branch tracking).
- Handle every error explicitly.
- Keep safe values only in output.
- Use .env.example as template; read actual .env through application runtime only.
- Authentication, billing, production deploy final approval, and personal data handling: human tasks.
- All other operations: AI auto-executes.

## Model Routing
- Ambiguous design: Claude Code Thinking
- Clear implementation: Codex CLI / Claude Code
- Lightweight fixes: lightweight model
- Critical changes: review by a model different from the implementer
- Auth, billing, DB, permissions, deploy, security, 300+ line diff: cross-vendor review required.
