# ASCT: Agentic Supply Chain Twin

ASCT is a zero-cost prototype of an agentic supply chain decision engine. It
models companies, locations, products, inventory, events, signals, scenarios,
CEO-level decisions, and human escalations in a traceable ontology-style system.

The project is built to demonstrate a Palantir-inspired pattern: define the
business objects first, connect them through typed relationships, then let
specialist agents propose competing actions that an orchestrator resolves.

## What It Does

- Creates a SQLite-backed supply chain twin for two sample companies.
- Generates deterministic seed data for companies, locations, products,
  suppliers, inventory policies, inventory, sales history, events, and signals.
- Runs four specialist agents:
  - `DemandForecaster`
  - `SupplyRiskAssessor`
  - `InventoryOptimizer`
  - `LogisticsPlanner`
- Scores scenarios through a `CEOOrchestrator`.
- Escalates unsafe or ambiguous cases to a human review flow.
- Exposes FastAPI endpoints and a Streamlit dashboard.
- Keeps causal chains traceable from `Event` to `Signal` to `Scenario` to
  `Decision` or `Escalation`.

## Architecture

```text
Event
  -> Signal
  -> RunComposer
  -> PluginRegistry
  -> Specialist Agents
  -> Scenario[]
  -> CEOOrchestrator
  -> CEODecision or EscalationRecord
```

Core layers:

- `src/models/`: SQLAlchemy ontology and persistence models.
- `src/agents/`: specialist agents that produce scenario proposals.
- `src/orchestrator/`: conflict resolution, confidence, escalation, and run
  composition.
- `src/config/`: YAML config loading, validation, and Japanese rule parsing.
- `src/seed/`: deterministic sample data generation.
- `src/api/`: FastAPI route modules.
- `src/dashboard.py`: Streamlit dashboard.
- `configs/`: company-specific YAML business rules.
- `tests/`: unit and integration tests.

## Ontology Model

Primitive object types:

- `Asset`: represented by products, inventory, suppliers, and policies.
- `Location`: represented by companies, warehouses, factories, offices, and
  routes.
- `Event`: represented by demand spikes, supply disruptions, route disruptions,
  inventory alerts, weather events, seasonal changes, and reorder triggers.

Derived object types:

- `Signal`: typed impact from an event, with dimension, target, delta, duration,
  and confidence.
- `Action`: represented by CEO decisions or human-resolved escalations.

## Requirements

- Python 3.11+
- SQLite
- Node.js only for optional repository scripts

Install dependencies:

```bash
pip install -e ".[dev]"
```

## Setup

Apply migrations:

```bash
alembic upgrade head
```

Generate seed data:

```bash
python -m src.seed.generate
```

Run the API:

```bash
uvicorn src.main:app --reload
```

Run the dashboard:

```bash
streamlit run src/dashboard.py
```

Useful URLs:

- API health: `http://127.0.0.1:8000/health`
- Dashboard: `http://127.0.0.1:8501`

## API Overview

- `POST /api/events`: create an event and run the agent pipeline.
- `GET /api/decisions`: list CEO decisions.
- `GET /api/decisions/{id}`: inspect a decision and causal chain.
- `GET /api/escalations/pending`: list pending human escalations.
- `PUT /api/escalations/{id}/resolve`: resolve an escalation.
- `GET /api/dashboard/status`: dashboard summary data.
- `GET /api/companies`: list companies.
- `GET /api/config/{company_id}`: load company config.
- `POST /api/config/parse-nl`: parse simple Japanese config instructions.

## Verification

Run the standard quality checks:

```bash
ruff check src/ tests/
pytest
pyright src/
```

Current expected result:

- Ruff: no issues
- Pytest: 49 passed
- Pyright: 0 errors

## Design Principles

- Typed signals over raw numbers.
- Full causal chains for explainability.
- External configuration for company-specific business rules.
- Intentional conflict between specialist agents.
- Confidence-gated decisions and human escalation when uncertain.
- Zero-cost local stack using SQLite, FastAPI, Streamlit, and YAML.

## Example Company Configs

- `configs/company_1.yaml`: Freshfield Foods, food and perishables.
- `configs/company_2.yaml`: NexTech Components, electronics and components.

Each config defines scoring weights, constraints, confidence rules, escalation
settings, scheduling, inventory policies, locations, and suppliers.

## Project Status

All planned implementation phases are complete:

- Phase 1: schema and Alembic migration
- Phase 2: seed data generation
- Phase 3: four specialist agents
- Phase 4: CEO orchestrator and escalation
- Phase 5: config layer and Japanese parser
- Phase 6: API and Streamlit dashboard

## License

MIT
