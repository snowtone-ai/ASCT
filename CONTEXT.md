# CONTEXT.md -- ASCT Domain Vocabulary

## Purpose
Shared domain language consumed by all skills and agents.
Reduces token usage by establishing common terms once.

## Project Terms
- ASCT: Agentic Supply Chain Twin. The system being built.
- Seed Data: Pre-generated realistic sample data for 2 companies, 3 locations each, 5 product types, 30 days of sales history.
- Company Config: Per-company YAML configuration defining weights, constraints, thresholds, and policies.

## Ontology Terms (Palantir-inspired)
Primitive types:
- Asset: What exists. Maps to products, inventory, vehicles, equipment, personnel.
- Location: Where it exists. Maps to suppliers, factories, warehouses, distribution centers, stores.
- Event: What happened. Maps to external occurrences (typhoon, SNS spike, supplier outage, traffic disruption).

Derived types:
- Signal: A typed impact of an Event on the supply chain. Fields: type, dimension, delta, target, duration, confidence (0.0–1.0).
- Action: A decision made by an agent in response to Signals. Fields: type, target, quantity, rationale, triggered_by.

## Signal Types
- SupplyGap: Supply-side shortfall. Dimension: volume or cost. Example: SupplyGap(dimension="volume", delta=-0.10, target="SupplierA", confidence=0.95).
- DemandSpike: Demand-side surge. Dimension: demand. Example: DemandSpike(dimension="demand", delta=+0.30, target="fresh_produce", confidence=0.82).
- RouteDisruption: Logistics path degradation. Dimension: time or cost. Example: RouteDisruption(dimension="time", delta=+12.0, target="Tokyo-Osaka", confidence=0.70).
- InventoryAlert: Stock level deviation from policy. Dimension: quantity. Example: InventoryAlert(dimension="quantity", delta=-50, target="dairy@Tokyo_DC", confidence=0.91).
- SeasonalShift: Predictable demand pattern change. Dimension: demand. Example: SeasonalShift(dimension="demand", delta=+0.15, target="beverages", confidence=0.88).

## Architecture Terms
- CausalChain: The traceable path Event → Signal → Agent Scenario → CEO Decision.
- Scenario: An agent's proposed action with shape: {name, stockout_cost, holding_cost, transport_cost, total_cost, confidence}. Contract between Tier 1 agents and Tier 2 CEO.
- BaseAgent: Abstract base class. Each agent implements evaluate(context) -> list[Scenario].
- TRIGGERS: Class attribute on agents declaring which event types activate them.
- RunComposer: Maps incoming events to relevant agents via TRIGGERS, executes synchronously. Routes emergency events immediately, batches scheduled events.
- CEOOrchestrator: Tier 2. Scores all agent scenarios with weighted formula, applies constraints, selects optimal action.
- ConfidenceScore: Dynamic value = base × staleness_factor × source_factor × perishability_factor × historical_accuracy. All parameters from config.
- EventIngestor: API endpoint or scheduled check that receives external events and triggers agent runs.
- PluginRegistry: Auto-discovery mechanism in src/agents/__init__.py that loads all agent modules.

## Agent Tier System
Tier 1 — Specialist Agents (local optimization, single objective each):
- DemandForecaster: Minimizes stockout_cost. Triggers: demand_spike, seasonal_change. Inputs: sales_history, inventory, SNS, weather.
- SupplyRiskAssessor: Minimizes supply_disruption_cost. Triggers: supply_disruption, weather_event. Inputs: supplier reliability, lead times, event signals.
- InventoryOptimizer: Minimizes (stockout_cost + holding_cost). Triggers: inventory_alert, demand_spike. Inputs: inventory, inventory_policy, signal queue.
- LogisticsPlanner: Minimizes (transport_cost + delivery_risk). Triggers: route_disruption, reorder_trigger. Inputs: routes, fuel prices, weather, traffic.

Tier 2 — CEO Orchestrator (global optimization):
- Receives list[Scenario] from all Tier 1 agents. Scores via weighted formula. Returns optimal action or None (human escalation).

## Dual Time Horizon
- Strategic Layer: Scheduled (daily/weekly). Agents: DemandForecaster, InventoryOptimizer. Low urgency, queued for review.
- Emergency Layer: Event-driven (real-time). All agents + CEO fast loop. High urgency, immediate execution or escalation.
- Both layers share the same agent codebase. Difference is trigger frequency and action urgency.

## Supply Chain Flow
- Material flow: Supplier → Factory → Warehouse/DC → Store → Customer (left to right).
- Information flow: Customer → Store → Warehouse/DC → Factory → Supplier (right to left).
- External variables: Weather, SNS trends, traffic, fuel prices, geopolitical risk, regulations, local events.
- Internal variables: Inventory by SKU, lead times, capacity, shifts, utilization, defect rates, routes/costs.

## Data Source Types
- sensor: Automated data from IoT/systems. Highest confidence bonus.
- api: Data from external APIs. Standard confidence.
- manual: Human-entered data. Confidence penalty applied.

## Event Priority Types
- scheduled: Regular updates (inventory checks, reorder triggers). Can be batched.
- emergency: Disruptions requiring immediate response. Bypass queue.

## User-Facing Terms
- 欠品リスク (Stockout Risk): Risk of inventory dropping below minimum policy level.
- 保管コスト (Holding Cost): Cost of maintaining excess inventory.
- 輸送コスト (Transport Cost): Logistics and shipping costs.
- 供給途絶リスク (Supply Disruption Risk): Risk of supplier inability to deliver.
- 信頼度 (Confidence): Dynamic score indicating data/decision reliability.
- 因果チェーン (Causal Chain): Japanese term for CausalChain shown in UI.
- 戦略レイヤー (Strategic Layer): Scheduled planning cycle.
- 緊急レイヤー (Emergency Layer): Real-time event-driven response.

## Update Rules
- Add terms when a new domain concept appears 3+ times in conversation.
- Keep definitions under 20 words each.
- Review and prune after each major feature completion.
