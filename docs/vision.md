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

- [ ] Define core object types: Asset, Location, Event, Signal, Action, Policy
- [ ] Design SQL schema: inventory, inventory_policy, sales_history, products, suppliers, routes, events, agent_decisions
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
- [ ] Escalation: if all scenarios exceed constraints, return None + log
- [ ] Decision log with full causal chain

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
