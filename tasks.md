# tasks.md -- pm-zero v9.4 Execution Ledger

## Goal Binding
- Vision source: docs/vision.md
- Active goal: Refactor ASCT internals without changing product behavior or external interfaces.
- Planning owner: Codex CLI
- Implementation owner: Codex CLI
- Review owner: Codex CLI self-audit

## Status Vocabulary
- proposed: idea exists, not ready
- ready: owner, dependencies, write scope, acceptance, verification, and expected evidence are clear
- doing: one owner is actively working
- blocked: needs decision, dependency, credential, environment, or human action
- review: implementation complete, review pending
- done: accepted by reviewer
- verified: evidence recorded

## Parallelization Rules
- Coordinator owns tasks.md.
- Worker agents own only their assigned Write Scope.
- Parallel implementation requires disjoint Write Scopes or isolated worktrees.
- If two tasks need the same file, serialize them.
- Subagents return reports; coordinator updates tasks.md.

## Tasks
| ID | Status | Owner | Depends On | Write Scope | Acceptance | Verification | Evidence |
|---|---|---|---|---|---|---|---|
| T001 | verified | Codex CLI | none | AGENTS.md, CLAUDE.md, HANDOFF-JA.md, tasks.md, docs/state.md, docs/repo-map.md, docs/decisions.md, scripts/setup.mjs, scripts/verify.mjs, .claude/settings.json, .gitignore | pm-zero v9.4 source-of-truth files exist, old project-local hook/config scaffolds are not required, and product code is untouched | git diff --check; node scripts/verify.mjs | 2026-05-17: node scripts/verify.mjs passed; git diff --check passed before commit. |
| T002 | verified | Codex CLI | T001 | src/seed/generate.py, tasks.md | Seed YAML loading has an explicit typed boundary and invalid top-level config shapes fail with a clear error before database writes | ruff check src tests; pyright src; pytest | 2026-05-17: ruff passed; pyright passed; pytest 49 passed. |

## Blockers
| ID | Task | Blocker | Needed decision | Owner |
|---|---|---|---|---|

## Review Notes
| Task | Reviewer | Result | Follow-up |
|---|---|---|---|
