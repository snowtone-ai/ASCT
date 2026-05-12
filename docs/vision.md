# vision.md -- ASCT (Agentic Supply Chain Twin)

## Mission

ASCT is a next-generation supply chain management engine where multi-agent AI
autonomously makes decisions (ordering, allocation, intervention) by integrating
real-world uncertainty signals (weather, SNS trends, accidents) with internal
resource data (inventory, logistics, personnel).

## Success Criteria

1. System demonstrates autonomous decision-making on seed data from day one.
2. Every agent decision is explainable in plain Japanese to a non-technical user.
3. Adding a new agent requires zero changes to existing agent code.
4. All decisions carry confidence scores computed dynamically from data quality.
5. Full causal chain is traceable: Event → Signal → Agent Scenario → CEO Decision.
6. System runs at zero monetary cost (SQLite, Streamlit, no paid APIs).

## Failure Cases

1. Agent makes a decision it cannot explain via causal chain.
2. Confidence score is hardcoded rather than computed from data freshness/source.
3. Adding a new agent requires modifying existing agent files.
4. Agents never conflict (missing perspective).
5. Business rules are hardcoded in agent logic instead of external config.
6. Raw numbers flow between agents without type/dimension/target metadata.

## Core Design Principles (non-negotiable)

### 1. Typed Signals over raw numbers
Every data point flowing between agents must carry type, dimension, target, delta,
duration, and confidence. Example: `SupplyGap(dimension="volume", delta=-0.10,
target="SupplierA", confidence=0.95)` is actionable. A raw "-10%" is not.

### 2. Causal chains for decision transparency
Every action must be traceable: Event → Gap/Spike → Action.
If an agent cannot explain WHY it made a decision by traversing the causal chain,
the architecture is wrong.

### 3. Separation of config and logic
Everything that varies per client (weights, constraints, thresholds, optimal
inventory levels) lives in external config (YAML or DB). Core agent logic never
contains hardcoded business rules.

### 4. Intentional conflict between agents
Agents must have different objective functions and argue. If agents never conflict,
someone's perspective is missing. A CEO-level orchestrator resolves conflicts using
weighted scoring against constraints.

### 5. Confidence-gated actions
No agent acts on a signal below min_confidence threshold. Confidence degrades with
data staleness, manual entry, perishability, and historical error rate. It must be
computed dynamically, not hardcoded.

## Ontology Layer

Design modeled on Palantir Foundry's ontology-first approach: define what objects
mean before touching data.

### Primitive Object Types (3)

| Type | Definition | Examples |
|---|---|---|
| Asset | What exists | Inventory items, vehicles, equipment, personnel |
| Location | Where it exists | Supplier, factory, warehouse, distribution center, store |
| Event | What happened | Typhoon warning, SNS demand spike, supplier outage, traffic disruption |

### Derived Types (2)

**Signal** — a typed impact of an Event on the supply chain.
Fields: `type, dimension, delta, target, duration, confidence (0.0–1.0)`

| Signal Type | Meaning | Dimension |
|---|---|---|
| SupplyGap | Supply-side shortfall | volume or cost |
| DemandSpike | Demand-side surge | demand |
| RouteDisruption | Logistics path degradation | time or cost |
| InventoryAlert | Stock level deviation from policy | quantity |
| SeasonalShift | Predictable demand pattern change | demand |

**Action** — a decision made by an agent in response to Signals.
Fields: `type, target, quantity, rationale, triggered_by (causal chain reference)`

Every Signal carries confidence (0.0–1.0), computed dynamically from data staleness,
input method (sensor vs manual), product perishability, and historical error rate.

## Supply Chain Flow

```
Material flow (left → right):
  [Supplier] → [Factory] → [Warehouse/DC] → [Store] → [Customer]

Information flow (right → left):
  [Customer] → [Store] → [Warehouse/DC] → [Factory] → [Supplier]
```

The information propagation delay and distortion across this chain is the core
problem ASCT solves. Analogous to Kinaxis RapidResponse's concurrent planning:
all supply chain components are linked and updated in real-time, not sequentially.

### External Variables (affect the chain from outside)

Weather/natural disasters, SNS trends, traffic conditions, fuel prices,
geopolitical risk, regulatory changes, local events (festivals, strikes)

### Internal Variables (state of the chain itself)

Current inventory by SKU, lead times, production capacity, worker shifts,
equipment utilization, defect rates, warehouse utilization, transport routes/costs

## Agent Tier Architecture

Agents are organized in two tiers. Inspired by Blue Yonder's "Digital Colleagues"
concept where specialized AI agents alert planners about supply chain anomalies,
but ASCT goes further: agents don't just alert — they propose competing scenarios
that a CEO orchestrator resolves.

### Tier 1 — Specialist Agents (local optimization)

Each agent has a single objective function and argues for it.
Intentional conflict between agents is a design feature, not a bug.
Conflict makes tradeoffs visible and quantifiable.

| Agent | Objective | Primary Costs | Triggers | Key Inputs |
|---|---|---|---|---|
| DemandForecaster | min stockout_cost | stockout (primary), holding (secondary) | demand_spike, seasonal_change | sales_history, inventory, SNS, weather |
| SupplyRiskAssessor | min disruption impact | stockout + transport (disruption spillover) | supply_disruption, weather_event | supplier reliability, lead times, events |
| InventoryOptimizer | min (stockout_cost + holding_cost) | stockout + holding (primary), transport (reorder) | inventory_alert, demand_spike | inventory, inventory_policy, signal queue |
| LogisticsPlanner | min transport_cost | transport (primary), stockout (delay-induced) | route_disruption, reorder_trigger | routes, fuel prices, weather, traffic |

Why 4 agents, not 3: SupplyRiskAssessor and LogisticsPlanner handle fundamentally
different domains. A factory fire at a supplier (supply risk) requires different
analysis than a typhoon blocking a delivery route (logistics). Merging them would
create an agent with conflicting objectives, violating Principle 4.

### Tier 2 — CEO Orchestrator (global optimization)

Receives all specialist scenarios as a list. Scores using weighted objective +
constraint check. Returns globally optimal action, or `None` (escalate to human)
if all scenarios violate constraints.

**Scenario Contract** (all Tier 1 agents must return this shape):

```python
{
    "name":           str,    # agent name + action summary
    "stockout_cost":  float,  # estimated opportunity loss (JPY)
    "holding_cost":   float,  # estimated inventory carry cost (JPY)
    "transport_cost": float,  # estimated logistics cost (JPY)
    "total_cost":     float,  # sum of above
    "confidence":     float,  # 0.0–1.0, dynamically computed
}
```

**Cost-Filling Rule**: Every agent estimates all 3 cost fields. Primary costs
(the agent's specialty) are computed with full analysis. Secondary costs use
baseline estimates (current state projection) or zero if no impact. This
ensures CEO can compare scenarios on equal footing across all dimensions.

**CEO Scoring Function**:
```
score = w_stockout × stockout_cost + w_holding × holding_cost + w_transport × transport_cost
```

Disqualify if: `confidence < min_confidence` OR `total_cost > max_budget` OR
`transport_cost > max_transport_cost`. If all scenarios disqualified → return
`None` and log for human review.

**Scenario → Action Lifecycle**: Agents produce Scenarios (proposals). CEO
selects the best Scenario, which becomes an Action (decision). Human-resolved
escalations also produce Actions with `source="human"`. Every Action is logged
with full causal chain:
`Event → Signal → Agent scenarios considered → Action chosen → Reason`

## Dual Time Horizon

Two planning layers run in parallel over the same agent codebase, inspired by
Kinaxis RapidResponse's concurrent planning where strategic and tactical planning
happen simultaneously rather than sequentially.

### Strategic Layer (scheduled)

- **Purpose**: Demand forecasting, reorder planning, resource allocation
- **Primary agents**: DemandForecaster, InventoryOptimizer
- **Trigger**: Configurable schedule (daily/weekly batch via API endpoint)
- **Action urgency**: Low — plans queued for review or batch execution
- **Typical signals**: SeasonalShift, InventoryAlert (slow drift)

### Emergency Layer (event-driven, real-time)

- **Purpose**: Anomaly detection, immediate intervention, urgent reorder
- **Primary agents**: All agents + CEO in fast loop
- **Trigger**: Event-driven (Signal with confidence ≥ threshold)
- **Action urgency**: High — immediate execution or human escalation
- **Typical signals**: SupplyGap, DemandSpike, RouteDisruption (sudden)

Both layers share the same agent codebase and scenario contract.
The difference is trigger frequency and action urgency, not agent logic.
If confidence < min_threshold AND priority = emergency → human notification
(log + flag, no autonomous action).

## Human Escalation Framework

ASCT is autonomous-first, but certain conditions require human judgment.
The system must fail safe: when uncertain, escalate rather than act.

### Escalation Triggers (3 types)

| Trigger | Condition | Priority |
|---|---|---|
| `low_confidence` | Signal confidence < min_confidence AND event priority = emergency | high |
| `no_viable_action` | CEO disqualifies all scenarios (constraint violations) | high |
| `ambiguous_recommendation` | Top 2 scenario scores differ by less than `ambiguity_threshold` | medium |

### Escalation Record

Each escalation is a first-class object stored in the database:

```python
{
    "id":                   int,
    "created_at":           datetime,
    "trigger_type":         str,      # "low_confidence" | "no_viable_action" | "ambiguous_recommendation"
    "event_id":             int,      # FK to originating Event
    "scenarios_considered": list,     # All scenarios CEO evaluated
    "priority":             str,      # "high" | "medium"
    "status":               str,      # "pending" | "acknowledged" | "resolved" | "overridden" | "auto_expired"
    "resolution":           dict,     # Human's chosen action (null until resolved)
    "resolved_by":          str,      # Human identifier (null until resolved)
    "resolved_at":          datetime, # (null until resolved)
}
```

### Escalation State Machine

```
pending → acknowledged → resolved     (human selects a scenario or custom action)
                       → overridden    (human overrides with manual decision)
        → auto_expired                 (no response within auto_acknowledge_hours)
```

- `auto_expired` escalations are logged but take no action (fail-safe).
- Resolved/overridden escalations create an Action with `source="human"` in the
  causal chain, maintaining full traceability.

### Escalation in the Execution Flow

```
CEO evaluates all Scenario[]
  → Best scenario passes constraints   → execute as Action
  → Top 2 scores within threshold      → Escalation(trigger=ambiguous_recommendation)
  → All scenarios fail constraints      → Escalation(trigger=no_viable_action)
  → Confidence < threshold + emergency  → Escalation(trigger=low_confidence)
```

### Escalation Visibility

- **Dashboard**: Pending escalations shown as alert cards with countdown timer
- **API**: `GET /api/escalations/pending` for external system polling
- **Decision Explorer**: Resolved escalations visible in causal chain with
  human override annotation

### Notification Strategy

**Default (zero-cost)**: Streamlit dashboard shows pending escalations as alert
cards. REST API `GET /api/escalations/pending` enables external system polling.

**Optional Slack integration**: If `escalation.slack_webhook_url` is configured
in company YAML, the system POSTs escalation alerts to Slack via Incoming
Webhook (free, no bot token required). Message includes: trigger type, event
summary, top scenarios with scores, and a link to the dashboard for resolution.
If webhook is empty or POST fails, falls back silently to DB + dashboard only.

## Target Users

- Non-technical supply chain managers (Japanese-speaking)
- Operations directors who need transparent AI decision visibility
- System administrators onboarding new client companies

## Constraints

- Python and SQL are the primary languages
- Zero-cost stack: SQLite, Streamlit, no paid APIs
- Every agent decision explainable in plain Japanese
- Demonstrable with seed data from day one
- Modular: adding a new agent requires zero changes to existing code

## Tech Stack

- Backend: Python (FastAPI), SQLite (dev) / PostgreSQL (prod)
- Frontend: Streamlit
- Config: YAML files + DB-backed config store
- NL Parser: Rule-based Japanese keyword extraction (zero-cost)
- Testing: pytest + ruff
- Migrations: Alembic

## Implementation Phases

| Phase | Scope |
|---|---|
| 1 | Schema: SQL models + Alembic migrations |
| 2 | Seed data: 2 companies × 3 locations × 5 products × 30 days |
| 3 | Agent logic: one agent at a time, tested against seed data |
| 4 | CEO Orchestrator: conflict resolution, decision logging |
| 5 | Config layer: YAML schema + NL parser |
| 6 | Frontend: Streamlit dashboard |

## Checklist -- Phase 1: Ontology & Data Model

- [ ] Define core object types: Asset, Location, Event, Signal, Action, Escalation, Policy
- [ ] Design SQL schema: inventory, inventory_policy, sales_history, products, suppliers, routes, events, agent_decisions, escalations
- [ ] Every table has: id, created_at, updated_at, source (source = "sensor" | "manual" | "api")
- [ ] Define confidence calculation rules as separate config

## Checklist -- Phase 2: Agent Architecture

For each agent specify:
- Objective function (what it minimizes/maximizes)
- Input signals it consumes
- SQL queries it runs
- Output scenario shape (name, stockout_cost, holding_cost, transport_cost, total_cost, confidence)
- Escalation condition

## Checklist -- Phase 3: CEO Orchestrator

- [ ] score_scenario(scenario, config) — weighted scoring
- [ ] Constraint checking (budget, stockout_rate, transport_cost, min_confidence)
- [ ] Conflict resolution: receive all scenarios, return optimal action
- [ ] Escalation: 3 triggers (low_confidence, no_viable_action, ambiguous_recommendation)
- [ ] Escalation state machine: pending → acknowledged → resolved/overridden/auto_expired
- [ ] Escalation API: GET /api/escalations/pending for external polling
- [ ] Decision log with full causal chain (including human override annotation)

## Checklist -- Phase 4: Config Layer

- [ ] company_{id}.yaml schema: weights, constraints, confidence rules, policies
- [ ] NL config parser (rule-based Japanese keyword extraction)
- [ ] Config validation (weights sum to 1.0, thresholds in range)

## Checklist -- Phase 5: Full-Stack Application

### Launch Screen (Dashboard)
- [ ] Real-time supply chain status dashboard
- [ ] Current inventory health per location (CRITICAL / EXCESS / OK)
- [ ] Active events and their confidence scores
- [ ] CEO agent's last N decisions with causal chain visible

### Company Onboarding Flow
- [ ] Step 1: Company profile (industry, product categories, locations)
- [ ] Step 2: Inventory policy config — form-based OR natural language ("牛乳は最低20個、最大80個を維持したい")
- [ ] Step 3: Objective weight config — slider UI + NL override
- [ ] Step 4: Constraint configuration
- [ ] Step 5: Preview — show how system would have behaved on sample data

### Agent Decision Explorer
- [ ] For any past CEO decision: show full causal chain (Event → Signal → Agent scenarios → Choice)
- [ ] Show which agents argued for/against
- [ ] Show what alternative decisions would have cost

## Project Goals

- Product completion with working seed data demonstrations
- Seed data INSERT statements for 2 companies
- Design decision documentation accessible to non-engineer developers
