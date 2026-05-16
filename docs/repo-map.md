# repo-map.md -- pm-zero v9.4 Repository Map

## Read Policy
- Session start: read Summary only.
- Before editing: read the section for the target area when target files are unclear.
- When navigation is unclear: read Entry Points and Directory Map.
- After structural changes: update only the affected section.

## Summary
- App type: Python supply-chain simulation/API/dashboard prototype.
- Main runtime: Python 3.11+, FastAPI, Streamlit, SQLite/Alembic.
- Package manager: pip via pyproject.toml.
- Primary source directory: src/.
- Primary test directory: tests/.
- Main entry points: src/main.py, src/dashboard.py, alembic.ini.
- Verification command: node scripts/verify.mjs.

## Directory Map
| Path | Purpose | Edit Frequency | Notes |
|---|---|---|---|
| src/ | Product source | high | Agents, orchestrator, API, models, config, seed, dashboard. |
| tests/ | pytest coverage | high | Keep tests aligned with src areas. |
| configs/ | Sample company and scenario config | medium | Do not store secrets. |
| migrations/ | Alembic migrations | medium | Schema changes need explicit task evidence. |
| docs/ | pm-zero project memory | medium | Vision, state, decisions, issues, repo map. |
| scripts/ | Setup and verification automation | medium | Tooling only; not product runtime. |

## Entry Points
| Area | File | Purpose |
|---|---|---|
| API | src/main.py | FastAPI app entry. |
| Dashboard | src/dashboard.py | Streamlit UI entry. |
| Database | alembic.ini | Migration configuration. |
| Verification | scripts/verify.mjs | Unified repo checks. |

## Common Workflows
| Workflow | Read First | Edit Usually | Verify |
|---|---|---|---|
| API change | docs/vision.md, src/main.py | src/api/, src/models/, tests/ | pytest |
| Agent logic | docs/vision.md, CONTEXT.md | src/agents/, src/orchestrator/, tests/ | pytest |
| Config parser | CONTEXT.md | src/config/, configs/, tests/ | ruff check src tests; pytest |
| pm-zero docs | AGENTS.md | tasks.md, docs/, scripts/ | git diff --check |

## Generated / External Files
| Path | Rule |
|---|---|
| .venv/, __pycache__/, .pytest_cache/, .ruff_cache/ | Ignore. |
| *.db, *.sqlite3 | Ignore local databases. |
| logs/, screenshots/ | Ignore generated evidence unless explicitly requested. |
| .env, .env.* except .env.example | Ignore secrets. |

## Update Rules
- Keep Summary under 20 lines.
- Keep each directory note concrete.
- Move rationale to docs/decisions.md.
