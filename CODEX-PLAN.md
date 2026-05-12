# CODEX-PLAN.md — ASCT Implementation Plan for CodeX CLI

## Your Role

You are the implementation executor for ASCT (Agentic Supply Chain Twin).
All design decisions are final and documented in `docs/decisions.md` (D-001 through D-010).
Your job: write Python code, tests, and migrations. Do not redesign.

## Rules

1. Read `AGENTS.md` before every phase. Follow all execution rules.
2. Read `REPO-GUIDE.md` to understand the target directory structure.
3. Read `CONTEXT.md` for domain vocabulary. Use these exact terms in code.
4. Read `configs/company_1.yaml` and `configs/company_2.yaml` for config schema reference.
5. One branch per phase. PR to `develop` after each phase passes tests.
6. Target: 300 lines/file max, 50 lines/function max.
7. Every new module gets a corresponding test file.
8. After completing each phase, update `docs/state.md` (mark done, note branch).
9. Run `ruff check src/ tests/` and `pytest` before every commit. Zero errors.

## Verification Command

After each phase:
```bash
pip install -e ".[dev]" && ruff check src/ tests/ && pytest -v
```

---

## Phase 1: Schema — SQL Models + Alembic Migrations

**Branch**: `feature/phase-1-schema`

**Goal**: All SQLAlchemy ORM models + initial Alembic migration. No business logic.

### Steps

1. Create `src/database.py`
   - SQLAlchemy engine (SQLite for dev)
   - `SessionLocal` factory
   - `Base = declarative_base()`

2. Create `src/models/base.py`
   - Mixin class with shared columns: `id` (int PK), `created_at`, `updated_at`, `source` (enum: "sensor"|"api"|"manual")

3. Create `src/models/company.py`
   - `Company`: name, industry, currency
   - `Location`: name, type (warehouse|factory|office), lat, lon, FK to Company
   - `Route`: origin_id, destination_id (FKs to Location), distance_km, typical_hours

4. Create `src/models/product.py`
   - `Product`: name, category, unit, FK to Company
   - `Supplier`: name, products (JSON list), reliability_score, lead_time_hours, FK to Company

5. Create `src/models/inventory.py`
   - `Inventory`: product_id, location_id, quantity, last_checked_at
   - `InventoryPolicy`: product_id, location_id, reorder_point, reorder_quantity, max_stock, spoilage_rate_per_day
   - `SalesHistory`: product_id, location_id, date, quantity_sold, revenue

6. Create `src/models/event.py`
   - `Event`: event_type (enum: demand_spike, seasonal_change, supply_disruption, weather_event, route_disruption, inventory_alert, reorder_trigger), description, priority (enum: scheduled|emergency), data (JSON), company_id
   - `Signal`: event_id (FK), signal_type (enum: SupplyGap|DemandSpike|RouteDisruption|InventoryAlert|SeasonalShift), dimension, delta (float), target, duration_hours, confidence (float 0.0-1.0)

7. Create `src/models/decision.py`
   - `AgentDecision`: agent_name, event_id (FK), scenarios (JSON list of Scenario dicts), selected_scenario (JSON), confidence
   - `CEODecision`: event_id (FK), all_scenarios (JSON), selected_action (JSON), score, rationale, causal_chain (JSON)

8. Create `src/models/escalation.py`
   - `EscalationRecord`: trigger_type (enum: low_confidence|no_viable_action|ambiguous_recommendation), event_id (FK), scenarios_considered (JSON), priority (enum: high|medium), status (enum: pending|acknowledged|resolved|overridden|auto_expired), resolution (JSON nullable), resolved_by (str nullable), resolved_at (datetime nullable)

9. Create `src/models/__init__.py` — import all models

10. Generate Alembic migration:
    ```bash
    alembic revision --autogenerate -m "initial schema"
    alembic upgrade head
    ```

11. Write `tests/test_models.py`
    - Test: create one instance of each model, commit, query back
    - Test: all shared columns (id, created_at, updated_at, source) exist
    - Test: foreign key constraints work

### Acceptance Criteria
- `alembic upgrade head` creates all tables without error
- `pytest tests/test_models.py` passes
- `ruff check src/models/` clean

---

## Phase 2: Seed Data Generation

**Branch**: `feature/phase-2-seed`

**Goal**: Generate realistic seed data for 2 companies, 3 locations each, 5 product types, 30 days of sales history.

### Steps

1. Create `src/seed/generate.py`
   - Read `configs/company_1.yaml` and `configs/company_2.yaml`
   - Create Company, Location, Supplier, Product rows from config
   - Generate InventoryPolicy rows from config `inventory_policies`
   - Generate 30 days of SalesHistory with realistic patterns:
     - Weekday/weekend variation
     - Product-specific volume (perishables: high turnover, electronics: lower)
     - Random noise ±15%
   - Generate current Inventory state (derived from sales history)
   - Generate 5-10 sample Events (mix of scheduled and emergency types)
   - Generate corresponding Signals for each Event

2. Create `src/seed/__init__.py`

3. Write `tests/test_seed.py`
   - Test: seed generates expected row counts
   - Test: all foreign keys valid
   - Test: sales history spans 30 days
   - Test: inventory quantities are non-negative

### Acceptance Criteria
- `python -m src.seed.generate` populates DB without error
- `pytest tests/test_seed.py` passes
- Seed data is deterministic (seeded random)

---

## Phase 3a: DemandForecaster Agent

**Branch**: `feature/phase-3a-demand-forecaster`

**Goal**: First agent implementation. Establishes the BaseAgent pattern all others follow.

### Steps

1. Create `src/agents/base.py`
   - `BaseAgent` ABC with:
     - `TRIGGERS: list[str]` class attribute
     - `evaluate(self, context: dict) -> list[dict]` abstract method (returns list of Scenario dicts)
     - `name: str` property
   - `Scenario` TypedDict: `{name, stockout_cost, holding_cost, transport_cost, total_cost, confidence}`

2. Create `src/agents/__init__.py`
   - `PluginRegistry` class
   - Auto-discover: scan `src/agents/*.py`, import, find BaseAgent subclasses
   - `get_agents_for_event(event_type: str) -> list[BaseAgent]` — match via TRIGGERS

3. Create `src/agents/demand_forecaster.py`
   - `TRIGGERS = ["demand_spike", "seasonal_change"]`
   - `evaluate()`:
     - Query SalesHistory for trend (last 7 vs previous 7 days)
     - Query current Inventory
     - If demand trend up + inventory below reorder_point → high stockout_cost scenario
     - If demand trend up + inventory OK → moderate scenario
     - Return 1-2 Scenarios with computed costs
   - Primary costs: stockout_cost (computed), holding_cost (current state)
   - Secondary: transport_cost = 0 (not this agent's domain)
   - Confidence: use `src/orchestrator/confidence.py`

4. Create `src/orchestrator/confidence.py`
   - `calculate_confidence(base: float, data_age_hours: float, source: str, perishability_factor: float, historical_accuracy: float, config: dict) -> float`
   - Formula: `base × staleness_factor × source_multiplier × perishability_factor × historical_accuracy`
   - `staleness_factor = 0.5 ^ (age_hours / half_life_hours)` (exponential decay from config)
   - All params from company config

5. Write `tests/test_agents/test_demand_forecaster.py`
   - Test: returns valid Scenario shape
   - Test: TRIGGERS contains expected event types
   - Test: scenarios have non-negative costs
   - Test: confidence is between 0.0 and 1.0

6. Write `tests/test_orchestrator/test_confidence.py`
   - Test: fresh data → high confidence
   - Test: stale data → lower confidence
   - Test: manual source → penalty applied
   - Test: perishable product → penalty applied

### Acceptance Criteria
- Agent discovered by PluginRegistry
- Returns valid Scenarios against seed data
- All tests pass

---

## Phase 3b: SupplyRiskAssessor Agent

**Branch**: `feature/phase-3b-supply-risk-assessor`

### Steps

1. Create `src/agents/supply_risk_assessor.py`
   - `TRIGGERS = ["supply_disruption", "weather_event"]`
   - `evaluate()`:
     - Query Supplier reliability_score and lead_time_hours
     - Assess disruption impact: stockout_cost (can't fulfill) + transport_cost (alternate sourcing)
     - If supplier reliability < threshold → high disruption scenario
     - Return 1-2 Scenarios
   - Primary costs: stockout_cost + transport_cost (disruption spillover)
   - Secondary: holding_cost (current state)

2. Write `tests/test_agents/test_supply_risk_assessor.py`

---

## Phase 3c: InventoryOptimizer Agent

**Branch**: `feature/phase-3c-inventory-optimizer`

### Steps

1. Create `src/agents/inventory_optimizer.py`
   - `TRIGGERS = ["inventory_alert", "demand_spike"]`
   - `evaluate()`:
     - Query Inventory vs InventoryPolicy
     - Calculate stockout_cost (below reorder) + holding_cost (above max)
     - Propose reorder scenario or reduction scenario
     - Transport_cost: estimated reorder shipping cost
   - Primary costs: stockout_cost + holding_cost
   - Secondary: transport_cost (reorder cost estimate)

2. Write `tests/test_agents/test_inventory_optimizer.py`

---

## Phase 3d: LogisticsPlanner Agent

**Branch**: `feature/phase-3d-logistics-planner`

### Steps

1. Create `src/agents/logistics_planner.py`
   - `TRIGGERS = ["route_disruption", "reorder_trigger"]`
   - `evaluate()`:
     - Query Routes, fuel prices, weather conditions
     - Calculate transport_cost for available routes
     - Assess stockout_cost from delivery delays
     - Propose optimal route scenario
   - Primary costs: transport_cost
   - Secondary: stockout_cost (delay-induced)

2. Write `tests/test_agents/test_logistics_planner.py`

---

## Phase 4: CEO Orchestrator + RunComposer + Escalation

**Branch**: `feature/phase-4-ceo`

**Goal**: Tie all agents together. This is the core decision engine.

### Steps

1. Create `src/orchestrator/run_composer.py`
   - `RunComposer.run(event: Event, config: dict) -> CEODecision | EscalationRecord`
   - Use PluginRegistry to find agents matching event type
   - Execute each agent synchronously, collect Scenario lists
   - Pass all scenarios to CEOOrchestrator
   - If emergency event: bypass any batching, execute immediately

2. Create `src/orchestrator/ceo.py`
   - `score_scenario(scenario: dict, config: dict) -> float`
     - `score = w_stockout × stockout_cost + w_holding × holding_cost + w_transport × transport_cost`
     - Weights from `config["weights"]`
   - `check_constraints(scenario: dict, config: dict) -> bool`
     - Disqualify if: confidence < min_confidence OR total_cost > max_budget_jpy OR transport_cost > max_transport_cost_jpy
   - `resolve(scenarios: list[dict], event: Event, config: dict) -> CEODecision | EscalationRecord`
     - Filter by constraints → score remaining → select lowest score
     - If top 2 scores within ambiguity_threshold → Escalation(ambiguous_recommendation)
     - If all disqualified → Escalation(no_viable_action)
     - If best confidence < min_confidence AND emergency → Escalation(low_confidence)
     - Otherwise → CEODecision with full causal chain

3. Create `src/orchestrator/escalation.py`
   - `create_escalation(trigger_type, event, scenarios, config) -> EscalationRecord`
   - `notify_slack(escalation, config)` — POST to webhook if configured, silent on failure
   - `resolve_escalation(escalation_id, resolution, resolved_by) -> EscalationRecord`

4. Write `tests/test_orchestrator/test_ceo.py`
   - Test: best scenario selected correctly
   - Test: constraint violation disqualifies scenario
   - Test: all disqualified → escalation
   - Test: ambiguous scores → escalation
   - Test: scoring formula matches expected output

5. Write `tests/test_orchestrator/test_run_composer.py`
   - Test: correct agents selected for event type
   - Test: emergency events processed immediately
   - Test: end-to-end: event → scenarios → decision

6. Write `tests/test_orchestrator/test_escalation.py`
   - Test: escalation record created with correct fields
   - Test: Slack webhook called when configured
   - Test: silent fallback when webhook fails
   - Test: escalation resolution updates status

### Acceptance Criteria
- End-to-end: create Event → RunComposer → agents → CEO → Decision/Escalation
- Full causal chain logged in CEODecision
- All escalation triggers work correctly

---

## Phase 5: Config Layer

**Branch**: `feature/phase-5-config`

### Steps

1. Create `src/config/loader.py`
   - `load_company_config(company_id: int) -> dict` — read YAML, validate, return
   - Support config override from DB (future)

2. Create `src/config/validator.py`
   - `validate_config(config: dict) -> list[str]` — return list of errors
   - Check: weights sum to 1.0
   - Check: thresholds in valid ranges (0.0-1.0 for confidence, positive for costs)
   - Check: required keys present

3. Create `src/config/nl_parser.py`
   - `parse_japanese_config(text: str) -> dict` — extract config updates from Japanese text
   - Keyword dictionary: "欠品" → stockout, "輸送コスト" → transport, "最優先" → weight=high
   - Pattern templates for inventory policies: "最低N個" → reorder_point, "最大N個" → max_stock

4. Write tests for all three modules

---

## Phase 6: API + Streamlit Frontend

**Branch**: `feature/phase-6-frontend`

### Steps

1. Create FastAPI routes:
   - `src/api/routes_events.py` — POST /api/events (triggers agent run)
   - `src/api/routes_decisions.py` — GET /api/decisions, GET /api/decisions/{id}
   - `src/api/routes_escalations.py` — GET /api/escalations/pending, PUT /api/escalations/{id}/resolve
   - `src/api/routes_dashboard.py` — GET /api/dashboard/status
   - `src/api/routes_company.py` — CRUD company config
   - `src/api/routes_config.py` — GET/PUT config, POST /api/config/parse-nl

2. Update `src/main.py` — register all routers

3. Create Streamlit dashboard (`src/dashboard.py`):
   - Inventory health per location (CRITICAL/EXCESS/OK)
   - Active events with confidence scores
   - Last N CEO decisions with causal chain
   - Pending escalations as alert cards
   - Decision explorer: click any decision → see full Event → Signal → Scenarios → Action chain

4. Write API integration tests

### Acceptance Criteria
- `uvicorn src.main:app` starts without error
- All API endpoints return expected responses
- Streamlit dashboard renders with seed data
- Escalation cards visible when escalations exist

---

## Phase Execution Order

```
Phase 1 (schema) → Phase 2 (seed) → Phase 3a → 3b → 3c → 3d → Phase 4 (CEO) → Phase 5 (config) → Phase 6 (frontend)
```

Each phase must pass `ruff check` + `pytest` before merge.
Each phase gets its own branch and PR to `develop`.
