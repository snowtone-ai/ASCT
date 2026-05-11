# REPO-GUIDE.md — AI Navigation Map

> Read this file first when entering the repository.

## Directory Structure

```
ASCT/
├── src/                        # Python application source
│   ├── main.py                 # FastAPI entrypoint
│   ├── database.py             # SQLAlchemy engine & session
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py             # Shared columns: id, created_at, updated_at, source
│   │   ├── company.py          # Company, Location, Route
│   │   ├── product.py          # Product, Supplier
│   │   ├── inventory.py        # Inventory, InventoryPolicy
│   │   ├── event.py            # Event, Signal (TypedSignal)
│   │   └── decision.py         # AgentDecision, CEODecision, CausalChain
│   ├── agents/                 # Pluggable agent modules
│   │   ├── __init__.py         # PluginRegistry (auto-discovers agents)
│   │   ├── base.py             # BaseAgent ABC: evaluate(context) -> list[Scenario]
│   │   ├── demand_forecaster.py
│   │   ├── supply_risk_assessor.py
│   │   ├── inventory_optimizer.py
│   │   └── logistics_planner.py
│   ├── orchestrator/           # Decision-making core
│   │   ├── ceo.py              # CEOOrchestrator: score_scenario(), resolve_conflicts()
│   │   ├── run_composer.py     # Event → Agent mapping via TRIGGERS
│   │   └── confidence.py       # Config-driven confidence calculation
│   ├── config/                 # Configuration management
│   │   ├── loader.py           # YAML + DB config merge
│   │   ├── validator.py        # Weight sum = 1.0, threshold ranges
│   │   └── nl_parser.py        # Japanese NL → YAML (rule-based, zero LLM)
│   ├── api/                    # FastAPI route modules
│   │   ├── routes_dashboard.py # Dashboard data endpoints
│   │   ├── routes_company.py   # Company onboarding
│   │   ├── routes_decisions.py # Decision explorer
│   │   ├── routes_events.py    # Event ingestion (triggers agent runs)
│   │   └── routes_config.py    # Config management
│   └── seed/
│       └── generate.py         # Seed data generator
├── configs/                    # Per-company YAML configurations
│   ├── company_1.yaml          # Food company (Freshfield Foods)
│   └── company_2.yaml          # Electronics company (NexTech Components)
├── tests/                      # pytest test suite
│   ├── conftest.py             # Shared fixtures
│   ├── test_agents/            # Agent unit tests
│   ├── test_orchestrator/      # CEO + RunComposer tests
│   ├── test_api/               # API integration tests
│   └── test_config/            # Config loader/validator tests
├── docs/                       # Project documentation
│   ├── vision.md               # Mission, principles, phase checklists
│   ├── state.md                # Current project state (single-writer)
│   ├── decisions.md            # Architecture decision log
│   └── issues.md               # Error/issue tracker
├── scripts/                    # pm-zero orchestration (Node.js)
│   ├── setup.mjs               # Directory structure creator
│   ├── verify.mjs              # Unified verification runner
│   └── lib/redact.mjs          # Secret redaction utility
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Dependencies, ruff/pytest config
├── AGENTS.md                   # Primary directive for all AI agents
├── CLAUDE.md                   # Claude Code adapter
├── CONTEXT.md                  # Domain vocabulary
├── OS-KERNEL.md                # Quality gates & verification modes
├── MEMORY.md                   # External memory references
├── HANDOFF-JA.md               # Japanese handoff report template
└── REPO-GUIDE.md               # This file
```

## Execution Flow

```
Event Ingestor (API / schedule)
  → RunComposer (event type → agent selection via TRIGGERS)
    → Agent A, B, C... (sync execution, each returns Scenario[])
      → CEOOrchestrator (weighted scoring → optimal action)
        → DB Write (decision + causal chain log)
```

## Key Patterns

| Pattern | Location | Description |
|---|---|---|
| Plugin Registry | `src/agents/__init__.py` | Auto-discovers `*.py` in agents/ directory |
| BaseAgent ABC | `src/agents/base.py` | All agents implement `evaluate(context) -> list[Scenario]` |
| TRIGGERS | Each agent class | Class attribute declaring which event types activate the agent |
| TypedSignal | `src/models/event.py` | Typed data point with dimension, target, delta, confidence |
| CausalChain | `src/models/decision.py` | Full trace: Event → Signal → Scenario → Decision |
| Config-Driven | `configs/*.yaml` | All business rules externalized; logic reads config, never hardcodes |
| Confidence Formula | `src/orchestrator/confidence.py` | `base × staleness × source × perishability × historical_accuracy` |

## Commands

```bash
pip install -e ".[dev]"          # Install with dev dependencies
ruff check src/                  # Lint
pytest                           # Test
uvicorn src.main:app --reload    # Run API server
streamlit run src/dashboard.py   # Run frontend (Phase 6)
alembic upgrade head             # Apply migrations
python -m src.seed.generate      # Generate seed data
```

## Config Structure

Each company YAML in `configs/` contains:
- `weights`: Agent scoring weights (must sum to 1.0)
- `constraints`: Min stock days, max lead time, budget limits
- `confidence`: Staleness decay, source multipliers, thresholds
- `inventory_policies`: Per-product reorder points and quantities
- `locations` / `suppliers`: Company-specific entities
