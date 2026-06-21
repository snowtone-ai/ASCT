# repo-map.md -- pm-zero v10 Repository Map (ASCT)

## Read Policy
- Session start: read Summary only.
- Before editing: read the section for the target area when target files are unclear.
- When navigation is unclear: read Entry Points and Directory Map.
- After structural changes: update only the affected section.
- Prefer a research subagent over reading many files in the main context.

## Summary
- App type: Agentic Supply Chain Twin (multi-agent decision engine + dashboard)
- Main runtime: Python 3 / FastAPI
- Package manager: pip (pyproject.toml)
- Primary source directory: src/
- Primary test directory: tests/
- Main entry points: src/main.py (API), src/dashboard.py (Streamlit, Phase 6)
- Verification command: node scripts/verify.mjs

## Directory Map
| Path | Purpose | Edit Frequency | Notes |
|---|---|---|---|
| src/models/ | SQLAlchemy ORM models | high | base.py shares id/created_at/updated_at/source |
| src/agents/ | Pluggable agent modules | high | PluginRegistry auto-discovers; BaseAgent ABC |
| src/orchestrator/ | CEO decision core | high | ceo.py, run_composer.py, confidence.py |
| src/config/ | Config management | medium | YAML+DB merge, validator, rule-based JA NL parser |
| src/api/ | FastAPI routes | medium | dashboard/company/decisions/events/config |
| src/seed/ | Seed data generator | low | python -m src.seed.generate |
| configs/ | Per-company YAML | medium | company_1 (food), company_2 (electronics) |
| tests/ | pytest suite | high | test_agents/orchestrator/api/config |
| alembic/ | DB migrations | medium | alembic upgrade head |
| docs/ | Project memory | medium | vision/state/decisions/issues/repo-map |
| scripts/ | Automation (Node) | low | setup.mjs, verify.mjs, lib/redact.mjs |
| .claude/ | Claude Code config | low | settings.json, hooks/, skills/ |

## Entry Points
| Area | File | Purpose |
|---|---|---|
| API | src/main.py | FastAPI app entrypoint |
| DB | src/database.py | SQLAlchemy engine & session |
| Agents | src/agents/__init__.py | PluginRegistry auto-discovery |
| Agent contract | src/agents/base.py | BaseAgent.evaluate(context) -> list[Scenario] |
| Orchestration | src/orchestrator/ceo.py | score_scenario(), resolve_conflicts() |
| Event mapping | src/orchestrator/run_composer.py | event type -> agents via TRIGGERS |
| Confidence | src/orchestrator/confidence.py | base x staleness x source x perishability x historical |

## Common Workflows
| Workflow | Read First | Edit Usually | Verify |
|---|---|---|---|
| Add an agent | base.py, CONTEXT.md | src/agents/<name>.py, tests/test_agents/ | ruff + pytest |
| Schema change | src/models/*, vision.md | src/models/, alembic/ | alembic upgrade head; pytest |
| Config change | src/config/loader.py | configs/*.yaml, src/config/ | pytest test_config |
| API endpoint | src/api/, src/main.py | src/api/routes_*.py | pytest test_api |

## Generated / External Files
| Path | Rule |
|---|---|
| .codegraph/ | Generated index; ignored, never edit |
| alembic/versions/ | Generated migrations; review before commit |
| .env* | Secrets; never read or commit (template: .env.example) |

## Key Patterns
| Pattern | Location | Description |
|---|---|---|
| Plugin Registry | src/agents/__init__.py | Auto-discovers *.py in agents/ |
| TypedSignal | src/models/event.py | Typed point: dimension, target, delta, confidence |
| CausalChain | src/models/decision.py | Event -> Signal -> Scenario -> Decision |
| Config-Driven | configs/*.yaml | Business rules externalized; logic never hardcodes |

## Update Rules
- Keep Summary under 20 lines.
- Keep each directory note concrete.
- Move rationale to docs/decisions.md.
