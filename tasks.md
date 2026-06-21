# tasks.md -- pm-zero v10 Execution Ledger

## Goal Binding
- Active goal: Build ASCT (Agentic Supply Chain Twin) per docs/vision.md, phase by phase.
- Owner: Claude Code (main agent)

## Status Vocabulary
- proposed: idea exists, not ready
- ready: owner, dependencies, write scope, acceptance, verification, and expected evidence are clear
- doing: actively being worked
- blocked: needs decision, dependency, credential, environment, or irreversible human action
- review: implementation complete, self-review pending
- done: accepted by self-review
- verified: evidence recorded

## Tasks
| ID | Status | Owner | Depends On | Write Scope | Acceptance | Verification | Evidence |
|---|---|---|---|---|---|---|---|
| T001 | ready | main | none | src/models/**, alembic/**, tests/test_models/** | Core schema (Asset, Location, Event, Signal, Action, Policy) with id/created_at/updated_at/source on every table; Alembic migration applies cleanly | standard: ruff + pyright + pytest; alembic upgrade head | pending |
| T002 | proposed | main | T001 | src/seed/**, tests/test_seed/** | Seed data: 2 companies x 3 locations x 5 products x 30 days sales history | standard: pytest; row-count check | pending |
| T003 | proposed | main | T001 | src/agents/demand_forecaster.py, tests/test_agents/** | DemandForecaster minimizes stockout risk; triggers demand_spike, seasonal_change | standard: pytest | pending |
| T004 | proposed | main | T001 | src/agents/supply_risk_assessor.py, tests/test_agents/** | SupplyRiskAssessor minimizes supply disruption cost | standard: pytest | pending |
| T005 | proposed | main | T001 | src/agents/inventory_optimizer.py, tests/test_agents/** | InventoryOptimizer minimizes holding cost under stockout constraint | standard: pytest | pending |
| T006 | proposed | main | T001 | src/agents/logistics_planner.py, tests/test_agents/** | LogisticsPlanner minimizes transport cost | standard: pytest | pending |
| T007 | proposed | main | T003,T004,T005,T006 | src/orchestrator/**, tests/test_orchestrator/** | CEOOrchestrator: weighted scoring, constraint checks, conflict resolution, causal-chain decision log | standard: pytest | pending |
| T008 | proposed | main | T001 | src/config/**, configs/**, tests/test_config/** | Config layer: YAML schema, rule-based JA NL parser, validation (weights sum 1.0) | standard: pytest | pending |
| T009 | proposed | main | T007,T008 | src/api/**, src/dashboard.py, tests/test_api/** | Streamlit dashboard + FastAPI endpoints; causal chain visible | final: verify + browser smoke | pending |

## Blockers
| ID | Task | Blocker | Needed decision | Owner |
|---|---|---|---|---|
| - | - | none | - | - |

## Review Notes
| Task | Reviewer (model) | Result | Follow-up |
|---|---|---|---|
| - | - | - | - |
