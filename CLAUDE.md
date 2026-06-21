# CLAUDE.md -- pm-zero v10 (Claude Code only, Windows PowerShell)

ASCT (Agentic Supply Chain Twin) -- Python / FastAPI project.

## Language
- Reports, error reports, manual confirmation requests: Japanese.
- Code identifiers and command names: English.
- When 3+ HIGH assumptions accumulate, ask immediately.

## Source of Truth (read on demand)
- Intent: docs/vision.md | Tasks: tasks.md | State: docs/state.md
- Decisions: docs/decisions.md | Failures: docs/issues.md | Map: docs/repo-map.md
- Domain vocabulary: CONTEXT.md | Report: HANDOFF-JA.md

## Startup Read
- Read this file, docs/state.md, docs/decisions.md, docs/repo-map.md Summary. Nothing else by default.

## Continuity (compaction assumed at ~40-50%)
- Checkpoint to tasks.md + docs/state.md and commit after each logical unit.
- When compacting, always preserve: active task ID, modified files list, verify command.
- Keep this file lean; load detail on demand with @path or rg. Use subagents for wide reading.

## Autonomy
- Allow-by-default for safe ops; deny secrets and the dangerous set (see .claude/settings.json).
- Newly added MCP/tools: auto-approve safe calls; do not ask the human per tool.
- Human gate only for irreversible real-world acts (real money, prod credentials, publishing personal data).

## Task Ledger
- tasks.md is the only execution ledger; main agent is the only writer.
- Every ready task: owner, dependencies, write scope, acceptance, verification, evidence.

## Parallelism
- Parallelize only on disjoint write scopes (or isolated worktrees). Same file -> serialize.
- Subagents cannot prompt for permission; run them under allow-by-default or read-only.
- Default cap: <=3 concurrent worker subagents; raise only if scopes are disjoint and budget allows.

## Model Routing
- Opus 4.8: orchestration, architecture, critical reasoning, self-review.
- Sonnet 4.6: day-to-day implementation, refactor, tests.
- Haiku 4.5: exploration, file reads, simple edits.

## Subagent Routing (token-budget-aware)
- Default: work in main context with Sonnet. Spawn subagents only when benefit > spawn cost.
- Spawn for: research/exploration (context isolation), parallel disjoint-scope work, mandatory self-review.
- Do NOT spawn for: single-file fixes, small edits, first-attempt error debugging, tasks faster to do directly.
- Ad-hoc work (no tasks.md entry): Sonnet in main context. Subagent only for multi-file research or after 2 failed attempts.
- Opus = self-review, architecture, complex failures only. Lower /effort for routine work.

## Self-Review (no human reviewer)
- Spawn a fresh Opus subagent (no implementation context) to review.
- Mandatory for: auth, billing, DB schema, RLS/permissions, deploy, security, 300+ line diff,
  new external API, production data, personal information.

## Self-Evolution
- Log failures in docs/issues.md. On 3 repeats, web-search a fix and record the source URL.
- Promote always-applicable lessons into this file; reference-level lessons into docs/lessons.md.

## Engineering Role
- Act as a principal-level full-stack engineer. Readable, testable, minimal, correct code.
- No placeholder code or TODOs. Every committed function works.

## Thinking Protocol
- Decompose into atomic subtasks; challenge assumptions from first principles; prefer the simplest correct solution.
- Compare 3 implementation skeletons (correctness, simplicity, testability, cost); choose one explicitly.
- Chain-of-Verification: draft, plan failure-revealing checks, verify independently, revise on verified facts only.
- Verify the real call shape of an external API/library before using it; run a minimal test when uncertain.
- Short progress checks, not one long reasoning dump.

## Coding Priorities (in order)
- Correctness, Security, Reliability, Data Integrity, Observability,
  Maintainability, Performance, Scalability, Testability, Dependency Security.

## Commands (Python / FastAPI)
- install: pip install -e ".[dev]" | lint: ruff check src tests | format: ruff format src tests
- typecheck: pyright src | test: pytest | test-cov: pytest --cov=src
- dev: uvicorn src.main:app --reload | migrate: alembic upgrade head | seed: python -m src.seed.generate
- verify: node scripts/verify.mjs | setup: node scripts/setup.mjs
- Use only commands that exist in this repository.

## Shell
- PowerShell for all operations. Windows paths with backslash. Node scripts via node scripts/name.mjs.
- RTK (Rust Token Killer), when active as a PreToolUse hook (rtk init -g), compresses CLI output
  (60-90% savings) transparently. No manual rtk prefixing. Run `rtk gain` to check savings.

## Git (full auto -- see docs/decisions.md and below)
- Never commit to main. Branch per task: <type>/<short-description>.
- Commit after each logical unit; push after every commit; open PR to main automatically.
- Stage only files in the task's Write Scope. Never stage .env* or secrets.
- Pre-push: confirm .gitignore covers secrets; run gitleaks if available.
- Merge: gate on final verify green + fresh-Opus self-review passed.
  Low/medium risk: squash-merge to main and delete branch.
  High-risk classes (auth, billing, DB schema, RLS/permissions, deploy, security,
  300+ line diff, new external API, production data, personal information):
  stop before any irreversible real-world side effect and surface a Japanese summary.

## Execution Boundaries
- Handle every error explicitly. Safe values only in output.
- .env.example is the template; runtime reads actual env values.
- Irreversible real-world acts (real money, prod credentials, publishing personal data) are human-gated.
- All other operations are AI-executed without asking.
